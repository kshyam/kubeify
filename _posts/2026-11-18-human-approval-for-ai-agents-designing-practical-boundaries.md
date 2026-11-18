---
title: "Human Approval for AI Agents: Designing Practical Boundaries"
description: "A practical business guide to human approval for ai agents: designing practical boundaries"
image: /images/blog/human-approval-for-ai-agents-designing-practical-boundaries.webp
layout: post
permalink: blog/:title
author: Shyam
category: Kubernetes
date: 2026-11-18T10:00:00+05:30
---

An AI agent that can merge a pull request is an engineer who never sleeps and has never met your customers. That isn't a reason to keep it out of your pipeline. It's a reason to decide, before you hand over the keys, which choices it gets to make alone.

If you're building DevOps to bring costs down, the appeal is easy to see. Agents can write a Terraform change, open a pull request, read the test output, and retry when something breaks. The expensive part was never the typing. It was waiting for someone to notice. But an agent that can spend money or change permissions needs a point where a person says yes. The work is designing that point so it protects you without becoming a queue of approvals nobody reads.

## What approval should actually mean

A good approval gate is a decision, not a formality. Someone has to see what is changing, understand the effect, and be able to say no without a fight. If reviewers click approve because the build is red and the deploy window is closing, you don't have a control. You have a delay.

Write down which actions are cheap to reverse and which aren't. Adding a label to a staging deployment is cheap. Granting a role, applying a schema migration, or changing a public ingress rule is not. The second group gets a human. The first usually doesn't, because the agent can roll it back itself.

This matters for cost. Every manual gate consumes attention, and attention is what you were trying to save by automating the pipeline. Put it where reversal is expensive.

## Where to put the boundary

The strongest boundary is the one the system enforces, not the one a prompt asks for. "Ask before deploying to production" is a fine default, but an agent can misread it, lose it in a long context, or work around it when a retry goes sideways. Put the rule in the layer that grants access.

Kubernetes gives you two useful places to do that. Role-based access control (RBAC) decides what an identity can call. The [Kubernetes RBAC documentation](https://kubernetes.io/docs/reference/access-authn-authz/rbac/) is explicit that permissions are purely additive, with no deny rules, and that a Role is namespaced while a ClusterRole is not. In practice, give the agent a service account with a narrow Role: read deployments in a staging namespace, perhaps patch one named ConfigMap. Avoid wildcards. The same page warns that wildcards grant access to future resource types too, which is a quiet way to hand out more than you meant to.

For changes that need a person, keep the approval in CI rather than in the cluster credential. The agent gets a token that can propose a change and open a pull request. A human reviews it, then a separate job with wider credentials applies it. Those are two identities. The agent never holds the production credential, so there's nothing for a confused prompt to misuse.

A second layer catches what slips through. Admission webhooks can reject an API request before it's stored. The [dynamic admission control documentation](https://kubernetes.io/docs/reference/access-authn-authz/extensible-admission-controllers/) describes validating webhooks, which run after objects are modified and can reject requests to enforce policy. Use one to refuse images from untrusted registries, or to block a public Service in a namespace where it isn't expected. That page also covers webhook timeouts and the failure policy that applies when the webhook can't be reached. Decide that deliberately. A webhook that fails open isn't a control; one that fails closed can stop routine deploys when the policy service is down.

Outside Kubernetes, the equivalent split is a plan anyone can request and an apply only a reviewer can trigger. Most teams have this already. The change is that an agent may write the plan, so review the diff, not who typed it.

## The tradeoffs you're accepting

Saying yes to a gate means saying no to some speed. A release that could have gone out in ten minutes waits for someone to look at it. During business hours that's a small price. At 2 a.m. it means the fix waits until morning, or someone gets woken up. Pick one. You can't have instant autonomous deploys and a meaningful human check.

Approval fatigue is easy to underestimate. A reviewer seeing twenty requests a day will skim by the fifth. Noisy agent output makes the gate worse, not better. Keep the packet small: the diff, the environment, the expected effect, the rollback step. If a reviewer can't answer "what breaks if this is wrong" in a minute, the change is too large or the description too thin.

There's also a tradeoff between consistency and judgment. A fixed rule blocks the harmless exception along with everything else. Letting humans override is useful, but record the override and why. Otherwise the exception becomes the default and the boundary moves.

## Security failures to design against

The first failure is an overbroad credential. It's tempting to give the agent a cluster-admin-style role so it never gets stuck. The RBAC docs describe cluster-admin as allowing any action on any resource, and the built-in edit role can access Secrets and run Pods as any service account in a namespace. Either one turns a small misunderstanding into a cluster-wide problem. Scope by namespace and verb, and revisit the role when the agent's job changes.

The second is a bypass path. If the agent can edit the webhook configuration, create a service account, or use a kubeconfig left in a CI variable, the gate is decoration. Lock down who changes the policy, and keep those credentials away from the automation they govern. Same for break-glass access: keep it, test it, make it loud.

The third is silence. An agent can fail in a way that looks like success, especially when it retries. Log the request, identity, decision, and resulting change in one searchable place. Kubernetes audit logging captures API activity, and CI already records who approved a run. Joining them is more useful than another dashboard.

## What the boundary costs, and what it saves

The direct cost is small: a service account, a policy rule, a protected environment, and someone's review time. The indirect cost is latency and on-call disruption when approvals land outside working hours. Budget for both. As approvals grow, so does review load, and that's a real line item even if it never appears on an invoice.

What it saves is the tail risk. A bad change that reaches production costs engineer hours, customer trust, and sometimes cloud spend when a runaway job provisions resources. You don't need a number for that risk to justify a cheap gate. You'd rather pay a minute of review than find out what an unreviewed change can do.

There's a cost angle the other way too. Automation nobody trusts gets turned off after the first incident. A narrow boundary makes it easier to keep the agent running, and that's where the savings come from.

## A decision you can make this week

List the top five actions your agent can take. For each, write whether a person must approve it, who that person is, and how it gets reversed. Then check that the controls match the list. If an action says "human approval" but the agent holds a credential that can do it anyway, that's a wish. Fix the credential first, then put the approval just before the irreversible step. Start with production access and permission changes.

## Frequently Asked Questions

**Should every agent action require approval?**
No. Reading logs, running tests, or restarting a staging pod don't need a human. Reserve approval for changes that cost money, change access, touch production data, or are hard to undo.

**Isn't a prompt asking for confirmation enough?**
It's a hint, not a guarantee. Prompts get ignored or lost in long sessions. Put the rule in the credential or admission layer so the system refuses the action even if the agent forgets.

**Who should approve?**
Someone who understands the blast radius and can say no. Often an engineer for technical changes, an owner for spend. Avoid making the author the sole approver.

**What if approvals slow urgent fixes?**
Define a narrow break-glass path in advance, with a short expiry and a log somebody reviews later. Don't improvise during an incident.

**Do I need a webhook?**
Not always. If all infrastructure changes go through CI, protecting the apply step may be enough. Admission policy earns its place when changes can reach the cluster another way.

**How do I know the boundary works?**
Try the blocked action with the agent's credentials. If it succeeds, you found a gap. Repeat after any change to roles or permissions.

If you're working out where a human belongs in your delivery pipeline, we can help you map the boundaries against the systems you already run. Visit [https://kubeify.com/contact](https://kubeify.com/contact) to start the conversation.
