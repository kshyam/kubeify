---
title: "Building a Practical MLOps Pipeline on Kubernetes"
description: "A practical business guide to building a practical mlops pipeline on kubernetes"
image: /images/blog/building-a-practical-mlops-pipeline-on-kubernetes.webp
layout: post
permalink: blog/:title
author: Shyam
category: Kubernetes
date: 2026-11-07T10:00:00+05:30
---

A production machine learning system is not a model. It is a pipeline that produces the model, a serving layer that answers requests, a monitoring loop that notices when answers degrade, and a set of permissions and budgets that keep the whole thing from becoming an unowned expense. Kubernetes handles orchestration and serving well. It does not supply the rest for free, and teams that assume it does end up with a cluster full of experiments and no clear owner.

For a business owner, the useful question is not which MLOps tool to install. It is which decisions will still be defensible when the team changes and the bill arrives. The sections below focus on those decisions.

## Draw the lifecycle before choosing components

Write down four stages: data preparation, training, artifact storage, and inference. For each, name the owner, the input, the output, and the acceptable failure mode. A training job can fail and retry; a real-time prediction endpoint cannot silently return stale results. This sounds like process work, but it determines architecture. If nobody owns the artifact store, you will rebuild models you cannot reproduce. If nobody owns the serving contract, every model update becomes an outage risk.

A practical split is to keep training and serving as separate deployments with separate resource profiles. Training is bursty and benefits from large machines. Serving is steady and benefits from small, replicated pods. Running both in one namespace under one quota invites a training job to starve the API it is supposed to improve.

## Use the right workload primitive

Kubernetes gives you several controllers, and choosing the wrong one is a common source of waste. Batch feature engineering and training fit Jobs and CronJobs, or a workflow engine such as [Argo Workflows](https://argo-workflows.readthedocs.io/en/latest/) when steps have dependencies. Long-running inference fits a Deployment with a Service in front, and a HorizontalPodAutoscaler when traffic varies. Stateful stores such as a feature database or a model cache fit StatefulSets and need persistent volumes with a real backup plan.

The tradeoff is operational surface area. A workflow engine adds a controller, a UI, and a permission model. A single Job is simpler but has no retries across steps, no artifact passing, and no lineage. Start with Jobs if you run fewer than a handful of pipelines per day and the steps are independent. Add the workflow engine when coordination cost exceeds the cost of running it.

## Make artifacts immutable and environments reproducible

The most expensive MLOps failure is a model you cannot rebuild. Pin the container image by digest, store the model artifact in a registry, and record the data snapshot or query that produced it. A model registry such as [MLflow](https://mlflow.org/docs/latest/) can track versions and stage transitions; object storage with a naming convention can do the same job with more discipline. The point is not the tool. It is that a model version maps to an exact image, exact weights, and exact data reference.

Immutable artifacts also simplify security review. If a serving pod runs an image identified by digest, you can scan that digest, sign it, and verify it at admission time. If it runs `latest`, none of those controls mean anything.

## Treat security as part of the pipeline

Three controls give most of the value and are frequently skipped.

First, use Kubernetes RBAC to separate who can create workloads from who can read secrets. A data scientist who can deploy a pod that mounts production credentials has effectively been given those credentials. Namespace-scoped roles, with a small number of break-glass cluster roles, keep that boundary intact.

Second, do not treat Secrets as encrypted storage. [Kubernetes Secrets](https://kubernetes.io/docs/concepts/configuration/secret/) are base64-encoded API objects; base64 is encoding, not encryption. Enable [encryption at rest](https://kubernetes.io/docs/tasks/administer-cluster/encrypt-data/) for the API server and restrict read access. Better still, keep long-lived credentials in an external secret manager and sync short-lived values into the cluster.

Third, apply [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/) and [network policies](https://kubernetes.io/docs/concepts/services-networking/network-policies/). The restricted profile blocks privileged containers, host mounts, and running as root, which removes a large class of container escapes. A default-deny network policy, with explicit allows between the inference service and its dependencies, limits lateral movement if a pod is compromised.

The tradeoff is friction. Strict policies break images that write to their own filesystem or need root at startup. The fix is to rebuild those images, not to weaken the policy cluster-wide. Add an admission policy tool such as Kyverno or Gatekeeper when you need rules beyond the built-in profiles, and expect to spend time on exceptions.

## Control cost with requests, limits, and autoscaling

Cost problems in Kubernetes almost always trace back to missing or wrong [resource requests](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/). The scheduler places pods using requests, not actual usage. Without requests, a node can be oversubscribed and latency spikes look mysterious. With requests set too high, you pay for capacity nobody uses.

Set requests from observed usage, set memory limits close to requests to avoid eviction surprises, and measure before you tune. CPU limits deserve care. A tight CPU limit throttles inference even when the node has spare capacity, which shows up as tail latency rather than obvious errors. Many teams set CPU requests and leave CPU limits unset for latency-sensitive serving, while keeping memory limits.

Autoscaling has two layers. The HorizontalPodAutoscaler adds pods based on metrics, and the [cluster autoscaler](https://kubernetes.io/docs/concepts/cluster-administration/cluster-autoscaling/) adds nodes when pods cannot be scheduled. Both need correct requests to work. Scale-to-zero is attractive for sporadic internal tools, but cold starts hurt interactive use. A queue-based autoscaler such as KEDA helps for batch and event-driven work.

Storage is the quiet cost. Model checkpoints, feature snapshots, and container images accumulate. Apply lifecycle rules to object storage, keep only the model versions you can justify, and delete stale images from your registry. Use namespace quotas so one team cannot consume the shared cluster.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: fraud-model
spec:
  replicas: 2
  selector:
    matchLabels:
      app: fraud-model
  template:
    metadata:
      labels:
        app: fraud-model
    spec:
      containers:
        - name: server
          image: registry.example.com/fraud-model@sha256:REPLACE_WITH_DIGEST
          ports:
            - containerPort: 8080
          resources:
            requests:
              cpu: "500m"
              memory: "1Gi"
            limits:
              memory: "2Gi"
          readinessProbe:
            httpGet:
              path: /healthz
              port: 8080
```

The snippet is deliberately boring: a digest-pinned image, a memory limit, a CPU request, and a readiness probe. Those four details prevent most of the incidents that make ML platforms look unreliable.

## Instrument the model, not just the pod

Pod metrics tell you whether the service is up. They do not tell you whether predictions are useful. Log inputs and outputs with privacy controls, track prediction distributions, and compare them against training data over time. When a drift alert fires, you need a rollback path that does not require a rebuild.

Run new model versions as a canary behind the same service and shift traffic gradually. Keep the previous image digest ready. A rollback should be a deployment change measured in minutes, not a retraining project measured in weeks.

## Decide what to build and what to buy

Managed Kubernetes removes control-plane operations but not the MLOps work. A managed notebook or model endpoint service removes more, at the cost of portability and per-request pricing. The decision hinges on team size and differentiation. If your model is the product, own the serving path and the data loop. If the model supports a business process, buy the managed service and spend the engineering time on the process.

Whichever path you choose, write down the exit conditions: what usage level makes the managed option more expensive than running it yourself, and what skills you need on staff before you move.

## Frequently Asked Questions

### Do we need Kubernetes for machine learning?

No. A single VM with a scheduled script and a small API is a legitimate production system for many models. Kubernetes becomes worthwhile when you have multiple services, variable load, or a platform team that already operates it. The cost is real: someone must own upgrades, policy, and capacity.

### Should training and inference share a cluster?

They can, with separate namespaces, quotas, and node pools. The risk is noisy-neighbor effects: a large training job can consume memory and network that serving depends on. If inference has strict latency requirements, isolate it.

### How do we keep model updates from breaking production?

Version everything, test the serving contract, and roll out with a canary. Treat the model file as a deployable artifact with a digest, not a file copied onto a server.

### What is the minimum viable security baseline?

RBAC scoped to namespaces, encryption at rest for secrets, restricted pod security, default-deny network policies, and image scanning before deployment. Add signed images and admission policies as the team grows.

### How do we stop costs from drifting?

Set requests from measured usage, apply quotas per namespace, add lifecycle rules to storage, and review the bill monthly against a named owner. Cost visibility without ownership does not change behavior.

## Next step

If you want a second opinion before you commit to a platform design, bring your current architecture, your model inventory, and your cloud bill. We will walk through the tradeoffs together and leave you with decisions you can defend. [Talk to Kubeify](https://kubeify.com/contact).
