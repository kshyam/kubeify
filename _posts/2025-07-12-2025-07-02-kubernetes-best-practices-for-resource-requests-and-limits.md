---
title: Kubernetes Best Practices for Resource Requests and Limits
description: Kubernetes simplifies application deployment and scaling—but
  without properly setting resource requests and limits, you risk overloading
  nodes, wasting cloud budget, or causing unpredictable pod evictions.
image: /images/blog/kubernetes-best-practices-for-resource-requests-and-limits.webp
layout: post
permalink: /blog/:title
author: Shyam Mohan
category: Kubernetes
date: 2025-07-02T08:23:00.000Z
---
Kubernetes simplifies application deployment and scaling—but without properly setting resource requests and limits, you risk overloading nodes, wasting cloud budget, or causing unpredictable pod evictions.

## Table of Contents

1.  Introduction  
      
    
2.  What Are Resource Requests and Limits in Kubernetes?  
      
    
3.  Why Are Resource Requests and Limits Important?  
      
    
4.  The Risks of Not Setting Requests and Limits  
      
    
5.  How Kubernetes Uses Requests and Limits  
      
    
6.  Best Practices for Setting Resource Requests  
      
    
7.  Best Practices for Setting Resource Limits  
      
    
8.  Right-Sizing Strategies: CPU vs Memory  
      
    
9.  Tools for Monitoring and Optimization  
      
    
10.  Real-World Example: Preventing Node Overload  
      
    
11.  CI/CD Considerations for Resource Management  
      
    
12.  Mistakes to Avoid  
      
    
13.  Conclusion  
      
    
14.  FAQs  
      
    

## 1. Introduction

Kubernetes simplifies application deployment and scaling—but without properly setting resource requests and limits, you risk overloading nodes, wasting cloud budget, or causing unpredictable pod evictions.

This guide dives deep into the best practices for configuring resource requests and limits in Kubernetes to ensure high performance, stability, and cost efficiency—especially in production environments.

## 2. What Are Resource Requests and Limits in Kubernetes?

In Kubernetes, each container can be assigned two main resource parameters:

-   Resource Requests: The minimum amount of CPU/memory Kubernetes guarantees a container will get.  
      
    
-   Resource Limits: The maximum amount a container can use before being throttled or terminated.  
      
    

These are typically defined in the container spec:

resources:

requests:

memory: "512Mi"

cpu: "500m"

limits:

memory: "1Gi"

cpu: "1000m"

  

CPU is measured in millicores (500m = 0.5 core), and memory in bytes (e.g., Mi, Gi).

## 3. Why Are Resource Requests and Limits Important?

Setting accurate requests and limits helps you:

-   ✅ Avoid overprovisioning (wasting resources)  
      
    
-   ✅ Prevent underprovisioning (causing instability or OOM errors)  
      
    
-   ✅ Ensure fair scheduling across pods  
      
    
-   ✅ Enable autoscaling to function properly  
      
    
-   ✅ Maintain cluster health and predictability  
      
    
-   ✅ Optimize cost, especially in managed services like GKE, EKS, or AKS  
      
    

## 4. The Risks of Not Setting Requests and Limits

Failing to define proper values leads to:

-   ❌ Pod eviction under memory pressure  
      
    
-   ❌ Unfair scheduling by kube-scheduler  
      
    
-   ❌ Throttling of CPU-bound apps  
      
    
-   ❌ Unpredictable performance  
      
    
-   ❌ Cluster-wide resource imbalance  
      
    
-   ❌ Higher cloud bills due to oversized nodes  
      
    

## 5. How Kubernetes Uses Requests and Limits

-   Scheduler Behavior: The scheduler places pods based on requests, not limits.  
      
    
-   Kubelet Behavior: Enforces limits at runtime using cgroups.  
      
    
-   OOM Killer: If a pod exceeds its memory limit, it will be terminated with an "OOMKilled" status.  
      
    
-   CPU Throttling: CPU limits aren’t fatal but can reduce performance as containers get throttled.  
      
    

## 6. Best Practices for Setting Resource Requests

### 🔹 Use Monitoring Tools

Gather metrics from Prometheus, Metrics Server, or Datadog to observe real usage patterns.

### 🔹 Start With Observed Baselines

Don’t guess—analyze CPU & memory usage during load testing or production hours.

### 🔹 Use the 90th Percentile

Set requests around the 90th percentile of average usage to balance stability and cost.

### 🔹 Avoid Defaults or Copy-Paste

Generic values like 100m for all pods is bad practice. Customize per application.

## 7. Best Practices for Setting Resource Limits

### 🔹 Set Limits Slightly Higher than Requests

Example: If your request is 500Mi, set the limit to 800Mi–1Gi to allow for spikes without risking OOM kills.

### 🔹 Do Not Omit Limits in Multi-Tenant Environments

Without limits, a single rogue pod can starve others.

### 🔹 Be Careful With CPU Limits

CPU throttling can cause latency and jitter—test your services under limit constraints.

## 8. Right-Sizing Strategies: CPU vs Memory

### Memory:

-   Memory usage is sticky—once allocated, it’s rarely released.  
      
    
-   Right-size by measuring working set size, not peak.  
      
    

### CPU:

-   CPU is burstable and shared.  
      
    
-   Set CPU requests based on steady-state needs; allow limits to absorb burst load.  
      
    

## 9. Tools for Monitoring and Optimization

Tool

Purpose

Goldilocks

Recommends optimal CPU/memory settings

Prometheus + Grafana

Visualize container resource usage

Kube Metrics Server

Lightweight metrics collection

Kubecost

Cost analysis based on resource usage

Vertical Pod Autoscaler (VPA)

Suggests/request/limit values automatically

## 10. Real-World Example: Preventing Node Overload

A dev team deployed a microservice-heavy workload without proper limits. Over time, one pod consumed 90% of node memory due to a memory leak, leading to eviction of critical services.

Fix:

-   Set requests.memory: 300Mi  
      
    
-   Set limits.memory: 600Mi  
      
    
-   Monitored usage via Grafana dashboards  
      
    

Result: No more OOM kills, and cost savings through right-sized nodes.

## 11. CI/CD Considerations for Resource Management

-   Use static analysis or OPA Gatekeeper to enforce resource fields in manifests.  
      
    
-   Validate YAML in pull requests to check for missing or oversized values.  
      
    
-   Introduce canary deployments to validate performance under set limits.
    

## 12. Mistakes to Avoid

🚫 Setting requests too low → Unstable performance  
🚫 Setting limits too tight → Frequent throttling/OOM  
🚫 Skipping requests → Scheduler can't place pod properly  
🚫 Uniform values for all pods → Wasted resources  
🚫 Ignoring autoscaling → Missed optimization potential

## 13. Conclusion

Properly configuring resource requests and limits is one of the most powerful, yet often overlooked, practices in Kubernetes optimization. It affects not only the reliability of your services but also your bottom line—especially in cloud environments.

Start small. Measure. Adjust. Automate. Over time, you'll gain a more efficient, stable, and scalable Kubernetes infrastructure.

  

## 14. FAQs

### 1. What happens if I don't set requests and limits in Kubernetes?

Kubernetes may schedule pods inefficiently, and they can be evicted or throttled during resource contention.

### 2. Should I set CPU limits in Kubernetes?

Yes, but cautiously. CPU limits can throttle apps. For latency-sensitive apps, test performance under constrained conditions.

### 3. Is memory limit mandatory in production?

Highly recommended. Without it, a memory leak can crash the node.

### 4. Can I use autoscaling without setting requests?

No. HPA (Horizontal Pod Autoscaler) relies on resource requests to calculate thresholds.

### 5. How do I know what values to set for requests?

Use metrics from tools like Prometheus or Goldilocks based on actual usage.

### 6. What's the difference between requests and limits?

Requests are guaranteed minimums; limits are enforced maximums.

### 7. Does Kubernetes kill a pod when it hits its CPU limit?

No. CPU is throttled, not terminated. Memory overuse results in termination.

### 8. Should I use the same values for requests and limits?

Not always. It’s better to give room for spikes with higher limits.

### 9. Are there tools that auto-tune requests and limits?

Yes. Tools like Goldilocks, VPA, and Kubecost help automate right-sizing.

### 10. How often should I update requests and limits?

Regularly—especially after updates, usage changes, or performance issues.
