---
title: "How to Tell Which AI Agent Workloads Can Safely Run on Spot Instances"
description: "A practical business guide to how to tell which ai agent workloads can safely run on spot instances"
image: /images/blog/how-to-tell-which-ai-agent-workloads-can-safely-run-on-spot-instances.webp
layout: post
permalink: blog/:title
author: Shyam
category: Kubernetes
date: 2026-11-27T10:00:00+05:30
---

Spot instances are spare cloud compute sold at a discount. The catch is in the name: the provider can take that capacity back. For a business owner building DevOps on a budget, that trade looks good until an agent dies halfway through a customer request and nobody can reconstruct what it did.

The decision that matters is which workloads can lose a machine without losing work, data, or trust. Some can. Some never should. The difference comes down to how each handles state, time, and failure.

## What interruption actually means

When EC2 reclaims a spot instance, it can terminate, stop, or hibernate it. You set that behavior in the request, along with whether the request is one-time or persistent. A persistent request is resubmitted after an interruption; a one-time request is not. AWS documents both in its guide to [creating a Spot Instance request](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-requests.html).

Interruption is not a rare edge case. AWS says it is always possible, and its [Spot Instance interruptions](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-interruptions.html) page lists capacity reclamation, price limits, and unmet request constraints as causes. Set a maximum price below the going rate and you will be interrupted more often than if you leave it unset.

The warning is short. AWS issues an interruption notice two minutes before the instance is stopped or terminated, delivered as an EventBridge event and through instance metadata, and recommends checking for it every five seconds. Notices are emitted on a best-effort basis. See [Spot Instance interruption notices](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-instance-termination-notices.html). Two minutes is enough to flush a buffer and write a checkpoint. It is not enough to drain a conversation or finish a training step.

AWS's [best practices](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-best-practices.html) draw the line plainly. Spot suits stateless, fault-tolerant, flexible work. It does not suit workloads that are stateful, fault-intolerant, tightly coupled between nodes, or unable to tolerate a gap in target capacity. Most agent systems have at least one component on the wrong side of that list.

## Sort your agents into three buckets

List every agent you run, then ask: if this process vanished right now, what would be lost?

**Bucket one: safe by design.** Batch embedding generation, overnight indexing, synthetic data generation, evaluation sweeps, and reports written to object storage. Each task has a defined input and output. If the machine dies, you rerun it. Nothing outside the task remembers the attempt.

**Bucket two: safe with safeguards.** Fine-tuning, large retrieval rebuilds, multi-step planning runs, and pipelines that chain tool calls. These work on spot only with checkpoints in durable storage and tasks that can be retried without duplicate effects. A training job that checkpoints at intervals resumes from the last checkpoint. A planning run that records each step to a queue picks up where it stopped. Without those mechanisms, the workload belongs in bucket three.

**Bucket three: keep on steady capacity.** A customer-facing agent holding a conversation in memory. An agent that issues payments, sends emails, or writes to your CRM. A coordinator that owns a lock other workers depend on. Anything where a half-completed action is worse than no action. Two minutes will not unwind a side effect that already reached a third party. Be honest here: one duplicated invoice or leaked draft email will cost more than the compute savings.

## The safeguards that decide the answer

For bucket two, your team needs three things before moving anything.

**Checkpoint and resume.** Write progress to storage that survives the instance, then test the restore path by killing a job on purpose. A checkpoint nobody has restored is a wish, not a feature.

**Idempotency.** Give each unit of work a stable identifier and make repeated execution safe. If an agent posts a message, writes a record, or charges a card, the second attempt must be recognized as the same attempt. Otherwise retries duplicate side effects and damage trust.

**Queue-based decoupling.** Put tasks on a queue and let workers claim them. When a node disappears, unfinished work returns to the queue. If no spot capacity is available, the work waits rather than failing.

On Kubernetes, taint spot nodes and add tolerations only to interruptible pods, so ordinary services stay off them. The [taints and tolerations](https://kubernetes.io/docs/concepts/scheduling-eviction/taint-and-toleration/) docs explain how `NoSchedule` and `NoExecute` differ, which matters when you want pods kept off a node versus evicted from it. Set requests and limits on every agent pod: requests drive placement, and exceeding a memory limit can kill a container, as the [resource management guide](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) explains.

A PodDisruptionBudget limits replicas lost during a voluntary eviction, but the [PDB documentation](https://kubernetes.io/docs/tasks/run-application/configure-pdb/) states that a budget does not guarantee availability and protects only against voluntary evictions, not all causes of unavailability. Spot reclamation is outside its scope.

## Cost: what you save versus what you spend

The discount is real. So are the costs that do not appear on the compute line.

Engineering time comes first. Checkpointing and retries take work. If your team spends a week on it, that week is part of the price. Checkpoint I/O comes next: writing state on every step costs storage requests and network time. Write too often and you eat the savings; too rarely and you lose too much work. Choose the interval by measuring how long a unit of work takes to redo.

Then observation. Interruptions generate retries and stale tasks. You need metrics for interruption rate, retry count, and completion time, plus alerts when a queue stops draining. Without them you learn about problems from customer complaints.

Run a mixed fleet. Keep steady capacity for bucket three and the control plane; let buckets one and two use spot. AWS recommends flexibility across many instance types and Availability Zones, and its `price-capacity-optimized` strategy draws from pools with more available capacity, according to the same [best practices](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/spot-best-practices.html) page. A request pinned to one instance type in one zone is far more fragile.

## Security: reclaimed machines are still your machines

Spot does not weaken instance isolation. While running, it behaves like any other EC2 instance. What changes is churn: more machines, more credentials issued, more chances for stale state.

Require IMDSv2 on every spot node. Version 2 uses a session token, and you can configure instances to reject tokenless requests, as the [IMDS documentation](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-instance-metadata-service.html) shows. If an agent has a server-side request forgery flaw, instance credentials are one of the first things an attacker will reach for.

Grant short-lived, narrowly scoped credentials. An agent that only reads one bucket should not hold a role that can write to your account. Avoid baking long-lived keys into images that get launched repeatedly. Treat local disks as disposable: keep secrets out of instance store and ship audit logs centrally before the node is reclaimed. Build deduplication into the write path so a retried agent does not create a second document or a second entry in a vector index.

## A decision checklist

Before moving any workload to spot:

1. Can the work be expressed as discrete tasks with defined inputs and outputs?
2. Does it hold state that exists only in memory?
3. Can every side effect be safely repeated?
4. Has a checkpoint been restored in a real test?
5. Can the work wait if no spot capacity is available?
6. Are credentials scoped to the minimum and IMDSv2 enforced?
7. Do you track interruptions, retries, and queue depth?

If you cannot answer yes to most of these, the workload is not ready. That is a useful boundary, not a failure.

## Frequently Asked Questions

**Are spot instances less secure than regular instances?**

No. While running, they are the same compute. The extra risk comes from churn, which IMDSv2 and short-lived credentials address.

**Can I fail over to on-demand when spot disappears?**

AWS discourages treating on-demand as a live failover, because it can drive interruptions for your other spot instances and the same type may not be available on-demand in that zone. Keep steady capacity as a baseline instead.

**Does a PodDisruptionBudget protect me from spot interruption?**

No. It protects only against voluntary evictions. Checkpointing and retries are what protect you.

**What about agents that call external APIs?**

Those belong in bucket three unless the calls are idempotent or keyed by a stable request identifier. A duplicated call to a payment or messaging API is a real business cost.

**How do I know if my team is ready?**

Start with one batch workload from bucket one. Add metrics, test a deliberate interruption, measure the recovery, then move to bucket two one workload at a time.

Spot can cut compute costs for the right workloads. Those workloads share a property: losing a machine is an event they were built to survive. If your agents are not built that way yet, make them resilient first, then move them. That order matters more than the discount.

If you want help mapping your agent workloads to the right capacity, talk to us. Visit [Kubeify's contact page](https://kubeify.com/contact) and tell us what you are running.
