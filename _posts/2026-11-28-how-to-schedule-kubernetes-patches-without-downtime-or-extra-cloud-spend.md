---
title: "How to Schedule Kubernetes Patches Without Downtime or Extra Cloud Spend"
description: "A practical business guide to how to schedule kubernetes patches without downtime or extra cloud spend"
image: /images/blog/how-to-schedule-kubernetes-patches-without-downtime-or-extra-cloud-spend.webp
layout: post
permalink: blog/:title
author: Shyam
category: Kubernetes
date: 2026-11-28T10:00:00+05:30
---

Patching a Kubernetes cluster sounds routine until it lands on a Friday afternoon. A kernel fix needs to reach every worker node. The control plane is a few releases behind. Someone has to click go, and everyone hopes checkout stays up. For a business owner the risk runs both ways: an outage hits revenue and trust, while the "safe" answer of keeping spare nodes warm quietly inflates the cloud bill every month.

You do not have to pick one. Kubernetes already has the pieces to move workloads off a node without dropping requests, and most cost nothing to configure. The work is in the setup and the schedule.

## Know what you are patching

"Patch Kubernetes" covers three different jobs.

Worker node patches touch the operating system, kernel, container runtime, or kubelet. With kubeadm, the documented flow upgrades control plane nodes one at a time, drains each node, upgrades kubelet and kubectl, then uncordons it. Workers follow the same one-at-a-time pattern. Skipping minor versions is unsupported, and the project recommends moving to patch releases promptly to stay secure ([kubeadm upgrade guide](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/)).

Control plane patches touch the API server, scheduler, controller manager, and etcd. A managed service handles most of this, but still wants a window. On a self-managed cluster, in-flight API requests can stall while etcd restarts, so the guide suggests stopping the API server briefly beforehand to let them finish.

Application patches are separate. Changing a container image triggers a Deployment rollout, not a node patch. Both replace pods, and both can break traffic if the app is not ready.

Give each job its own calendar and owner. Mixing them is how a five-minute OS patch becomes an incident.

## The business case

An unplanned outage costs orders and credibility. A window in your quietest hours has a known, bounded cost. Move from the first to the second.

The money leak is less obvious. The reflex when downtime feels unacceptable is to double everything: a second cluster, warm spare nodes, or permanent headroom. The Kubernetes docs name that trade directly. Failing over to a complete replica cluster avoids downtime, but it can be costly in duplicated nodes and in the human effort to switch over. Disruption-tolerant applications plus Pod Disruption Budgets also avoid downtime, with minimal resource duplication ([disruptions documentation](https://kubernetes.io/docs/concepts/workloads/pods/disruptions/)).

Buy safety with idle hardware and you pay every month. Build it into the application and you pay in engineering time once.

## Build the safety net first

A drain only works if the app can lose a pod. Three settings do most of the work.

Run at least two replicas of anything customer-facing, and spread them across nodes using topology spread constraints or pod anti-affinity. Three replicas on one node go down together when you drain it.

Add readiness probes. A starting pod is not a serving pod. The Deployment controller uses readiness to judge a rollout, and Services use it to decide where traffic goes.

Set a PodDisruptionBudget. A PDB limits how many replicas can be down during a voluntary disruption such as a drain. The docs describe a Deployment with five replicas and a PDB allowing four: the eviction API permits one pod down, not two. `kubectl drain` sends eviction requests, retries rejected ones, and waits for the budget. PDBs do not stop involuntary failures, though those count against the budget, and deleting a pod directly bypasses it. Automate with eviction, not delete.

```yaml
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: checkout-api
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: checkout-api
```

Match the selector to your Deployment exactly. A budget pointed at the wrong pods protects nothing.

Graceful shutdown matters as much. Eviction honors `terminationGracePeriodSeconds`. If your process ignores SIGTERM and takes a minute to exit, every drain takes a minute. Add a preStop hook, stop accepting new work early, let in-flight requests finish.

## Patch in place or replace the node?

In-place patching upgrades packages or the kubelet on each node and returns it to service. It uses hardware you already pay for. The cost is drift between nodes and a half-upgraded machine if a package step fails. Keep a rollback path.

Node replacement builds a fresh image with the patches, drains an old node, deletes it, and lets the scheduler fill the new one. Every node starts from a known state. The cost is brief overlap and the time a new node takes to join and pull images. Replace one at a time and the overlap can be near zero, but the drain stalls if pods have nowhere to go. That is where a spare node appears, and where spend returns.

A middle path is burst capacity that scales up only during the window. It works if your autoscaler removes empty nodes quickly. If it does not, you pay for a spare all week.

For application rollouts, tune the strategy. A Deployment defaults to 25% max unavailable and 25% max surge, keeping at least 75% of desired pods up. Raising surge buys speed using temporary capacity. Both values cannot be zero, or the rollout cannot progress. Terminating pods are not counted as available, so real usage can briefly exceed `replicas + maxSurge` until the grace period ends ([Deployments documentation](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)).

## Schedule without buying capacity

Use your own traffic data. If orders dip between 2am and 4am in your main market, that is the window. Patch one node, watch errors and latency, then continue. A window you can stop beats a fast one you cannot.

Cap concurrency. Two simultaneous drains halve the places pods can land. All at once defeats the PDB: the second drain blocks until replacements are ready, leaving pending pods and no room.

Use provider maintenance windows for control plane work, and put those settings under change control. If your own automation runs on a schedule, align it to the same window and stop failed runs from retrying forever.

Do not let the interval stretch too far. Waiting lowers the chance of a bad update but extends the time a known flaw stays reachable. Treat critical fixes as urgent work and routine patches as planned work with a cadence you hold. The kubeadm guidance on prompt patch releases is worth reading before you set that cadence ([kubeadm upgrade guide](https://kubernetes.io/docs/tasks/administer-cluster/kubeadm/kubeadm-upgrade/)).

Decide who can stop the window, how you verify success, and what you roll back to. Afterwards, confirm every node reports Ready and that the version changed. A node left cordoned silently removes capacity.

## Decisions to make now

Set a cadence per environment. Add PDBs to services that matter. Spread replicas. Check probes and shutdown time. Choose in-place or replacement and document the rollback. Set the maintenance window and align automation. Then measure one cycle: drain time, failed requests, and whether node count returned to normal.

The schedule is the last step, not the first.

## Frequently Asked Questions

### Does a PodDisruptionBudget guarantee zero downtime?

No. It limits voluntary disruptions such as a drain. It cannot stop hardware failure, a network partition, or a direct pod deletion. You still need replicas, probes, and routing that avoids a failing instance.

### Can I patch every node at once if I have spare capacity?

Technically yes, but the spare nodes sit idle the rest of the month. One node at a time with a PDB gets the same availability from capacity you already run.

### Do I need a second cluster?

Only if you need a full environment to fail over, as in a disaster recovery plan. For routine patching, the docs treat a replica cluster as one option and disruption-tolerant applications with PDBs as another that needs minimal duplication.

### Do application rollouts carry the same risk?

They can, if the pod template changes before new pods are ready. The 75% default assumes accurate probes and graceful shutdown. Tune `maxSurge` and `maxUnavailable` to the capacity you actually have.

### How often should I patch?

Base it on your own risk tolerance and the severity of the fix. Critical fixes deserve an urgent path; routine updates belong on a cadence you keep. The Kubernetes project recommends prompt patch releases and a supported minor release.

### What if the drain never finishes?

Usually the PDB will not allow another eviction because replacements are not ready, there is no node with room, or a pod is shutting down slowly. Fix those rather than deleting pods to force it.

## Make patching boring

Zero-downtime patching is mostly a few decisions made before the window opens. If you want a second pair of eyes on your setup, your maintenance window, or where your spare capacity is going, talk to us at [https://kubeify.com/contact](https://kubeify.com/contact).
