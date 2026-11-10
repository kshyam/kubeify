---
title: "Kubernetes Resource Requests and Limits for AI Applications"
description: "A practical business guide to kubernetes resource requests and limits for ai applications"
image: /images/blog/kubernetes-resource-requests-and-limits-for-ai-applications.webp
layout: post
permalink: blog/:title
author: Shyam
category: Kubernetes
date: 2026-11-10T10:00:00+05:30
---

Most Kubernetes cost and reliability problems start in two fields: `requests` and `limits`. For ordinary web services, getting them wrong is annoying. For AI workloads, it is expensive. Model servers hold large weights in memory, traffic arrives in bursts, and GPU nodes usually cost more per hour than CPU nodes. A request that is too small causes crashes and evictions. A request that is too large leaves expensive hardware idle while the scheduler refuses other work.

This article explains what the settings do, the tradeoffs involved, and how to make decisions you can defend to finance as well as engineering.

## What requests and limits actually control

A request is a scheduling promise. The scheduler adds up container requests and only places a Pod on a node with enough unallocated capacity. A node can be idle and still refuse a Pod if its remaining requested capacity is too small; requests reserve capacity in the scheduler's accounting, not necessarily in hardware.

A limit is an enforcement ceiling. The kubelet and container runtime configure kernel control groups, and the kernel enforces the number. CPU and memory behave differently, which causes most surprises; the official [resource management documentation](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) covers both. A limit set without a request is copied into the request field unless admission has defaulted it, so an accidental limit becomes an accidental reservation.

## CPU is compressible, memory is not

CPU limits are enforced by throttling: a container that reaches its limit is slowed, not killed. That beats termination, but throttling destroys tail latency, and p99 response time can stretch while average utilization looks healthy. CPU requests act as weights under contention, so a larger request gets a larger share.

Memory limits are enforced through out-of-memory handling. A container that exceeds its limit may be killed when the kernel detects pressure. Enforcement is reactive, so it can briefly exceed the limit first, producing restarts, failed requests, or corrupted in-progress jobs.

For AI services, memory is the setting to get right first. Weights, tokenizer state, batching buffers, and framework overhead all count. A model that loads at 6 GiB may need 8 GiB under concurrent load because of KV cache growth. Setting the limit at the idle footprint produces crashes that appear only under traffic.

CPU limits deserve restraint. If latency matters, set requests carefully and omit limits or set them high enough to absorb bursts. That trades cluster predictability for responsiveness, rather than paying for headroom you rarely use.

## Quality of Service classes and eviction order

Every Pod gets a Quality of Service class. A Pod is Guaranteed only when every container has CPU and memory requests equal to their limits, both above zero. A Pod with at least one request or limit is Burstable; one with none is BestEffort.

Under node pressure, Kubernetes evicts BestEffort first, then Burstable, then Guaranteed, as documented in the [Pod QoS guide](https://kubernetes.io/docs/concepts/workloads/pods/pod-qos/). For production inference, Guaranteed is often worth the reduced flexibility because capacity becomes predictable. For batch training or offline embedding, Burstable is usually better: you get a scheduling floor while the job uses spare capacity.

One common mistake: a Pod with memory requests equal to limits but CPU requests below limits is still Burstable, not Guaranteed.

## GPUs change the math

GPUs are extended resources. Device plugins advertise them, pods request them as whole numbers, they cannot be overcommitted, and requests must equal limits when both are present. The [GPU scheduling guide](https://kubernetes.io/docs/tasks/manage-gpus/scheduling-gpus/) covers the mechanics.

The cost implication is blunt: the scheduler cannot share a GPU the way it shares CPU. A GPU requested by one Pod is unavailable to others even if the model uses a fraction of its memory. The result can be low GPU utilization alongside high spend. The fix is workload design: batch requests, pack small models onto one device where the runtime supports it, or use time-slicing or MIG-style partitioning where hardware and drivers allow.

The other trap is under-requesting CPU and memory beside the GPU. A Pod can hold an expensive GPU while starving on host memory, or spend minutes loading weights because its CPU request is tiny. Size supporting resources for model load, not just steady-state inference.

## Autoscaling depends on honest requests

The Horizontal Pod Autoscaler calculates utilization as a percentage of the request. Inflated requests make utilization look low, so it under-reacts. Requests that are too small make a modest spike trigger aggressive scaling, then thrashing. The request becomes the baseline for automated decisions.

The cluster autoscaler provisions nodes from unschedulable Pods and their requests. Inflated requests buy nodes you do not need; requests that are too small leave Pods pending on a node that has room in accounting but not in reality. The Vertical Pod Autoscaler can recommend values from observed usage. Kubernetes also supports in-place resizing of container resources. Treat recommendations as evidence, not commands; one based on a quiet week will be wrong during a launch.

## Security is part of the resource conversation

Resource settings are a security control, not only a cost control. A workload with no memory limit can consume a node's memory and trigger out-of-memory conditions that affect unrelated services. A workload with no CPU limit can starve neighbors. In a shared cluster, that is a denial-of-service risk whether or not it is intentional.

Use `ResourceQuota` to cap consumption per namespace and `LimitRange` to set defaults and minimums. These guardrails matter when developers deploy without review, and they stop one experiment from consuming capacity reserved for revenue-generating inference. For multi-tenant platforms, treat GPU quotas as a first-class control; a tenant that can request every GPU can block everyone else.

## Making the cost tradeoff explicit

Two failure modes have opposite price tags. Over-requesting buys reliability with money: nodes sit partly idle, but workloads rarely fail. Under-requesting buys density with risk: the bill drops until traffic arrives, then latency and restarts rise.

Separate workloads by the consequence of failure. Customer-facing inference should have memory headroom, Guaranteed or well-configured Burstable settings, and enough CPU to avoid peak throttling. Batch jobs should use lower requests, tolerate eviction, and run on cheaper capacity where they can checkpoint and resume.

Then measure unit economics, not just the monthly bill. Cost per thousand inferences, per training job, and per active tenant expose whether density gains are real. A cluster that looks cheap per node can be expensive per request if it keeps restarting.

A starting manifest might look like this:

```yaml
resources:
  requests:
    cpu: "2"
    memory: "8Gi"
  limits:
    memory: "10Gi"
```

The memory limit sits above the request to absorb spikes; the request reflects what the scheduler must reserve. The CPU limit is omitted so the container can burst; add one only for hard fairness between tenants.

## A workable process

Start with observed data, not guesses. Run it under realistic load, record peak memory and CPU, and set requests near a typical peak with room for growth. Set memory limits above the observed peak, then test what happens when the limit is reached. Confirm the container fails cleanly and restarts rather than corrupting state.

Review settings after every model change. A new model version, a larger context window, or a new batching strategy can invalidate old numbers. Put resource review into the release checklist. Make defaults safe with namespace quotas and policy requiring requests and limits. The goal is not perfect utilization but predictable spend and behavior under load.

## Frequently Asked Questions

**Should I always set a memory limit?**

Set one for anything on a shared node, especially untrusted or experimental workloads. Without it, a memory leak can take down neighbors. A limit too close to normal usage turns a spike into a restart, so leave measured headroom and test the failure path.

**Why does my Pod stay pending when the node has free CPU?**

The scheduler uses requests, not live usage. If existing Pods have reserved the node's allocatable capacity, a new Pod will not fit even when hardware is idle. Check requested versus allocatable capacity, not just CPU graphs.

**Is a CPU limit necessary for latency-sensitive inference?**

Not always. CPU limits cause throttling, which can hurt tail latency. A common approach is to set CPU requests for fairness and omit or raise limits for latency-critical services, then control cost through replicas and quotas.

**How do GPU requests affect cost?**

A GPU request reserves a whole device, so unused GPU memory is still billed. Improve economics through batching, packing multiple models per device where supported, or partitioning hardware. Size CPU and memory so the GPU is not waiting on data loading.

**Who should own these settings?**

Platform teams should provide defaults, quotas, and guardrails. Application teams should own the numbers for their workloads because they understand traffic and model behavior. A monthly review comparing requests with actual usage keeps both sides honest.

If you want help turning these decisions into a cost-aware platform your team can operate, [talk to Kubeify](https://kubeify.com/contact).
