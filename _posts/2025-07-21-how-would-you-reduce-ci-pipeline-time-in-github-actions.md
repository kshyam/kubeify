---
title: How would you reduce CI pipeline time in GitHub Actions?
description: Reducing CI pipeline time in GitHub Actions is essential for
  maintaining high developer velocity, improving feedback loops, and cutting
  down cloud resource costs.
image: /images/blog/github-actions.png
layout: post
permalink: blog/:title
author: Shyam Mohan K
category: CICD
date: 2025-07-19T14:18:00.000+05:30
---
Reducing CI pipeline time in **GitHub Actions** is essential for maintaining **high developer velocity**, improving feedback loops, and cutting down cloud resource costs. Here’s a detailed approach with **strategies and best practices**:

---

## ✅ Strategies to Reduce CI Pipeline Time in GitHub Actions

### 1. **Parallelize Jobs**

* Use **job-level parallelism** to run tests, builds, and linters simultaneously.

```yaml
jobs:
  lint:
    ...
  test:
    ...
  build:
    ...
```

* Use **matrix builds** for parallel execution across versions/platforms.

```yaml
strategy:
  matrix:
    node: [16, 18, 20]
```

---

### 2. **Use Caching Effectively**

* Cache dependencies (npm, Maven, Bundler, pip) to avoid re-downloading them every run.

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

* Cache build artifacts if reused between jobs.

---

### 3. **Avoid Unnecessary Job Execution**

* Use `paths`, `paths-ignore`, or `if:` conditionals to skip workflows on unrelated changes.

```yaml
on:
  push:
    paths:
      - 'src/**'
      - '.github/workflows/**'
```

* Add job-level condition checks:

```yaml
if: github.event_name == 'push' && github.ref == 'refs/heads/main'
```

---

### 4. **Split CI and CD Pipelines**

* Separate CI (build, test) from CD (deploy) workflows.

  * CI can run on every PR.
  * CD only runs on merge to `main` or manual dispatch.

---

### 5. **Fail Fast & Early**

* Use `continue-on-error: false` (default) to halt jobs when a failure occurs.
* Run **lint and unit tests first**, so failures prevent unnecessary steps.

---

### 6. **Use Lightweight Runners**

* Self-hosted runners can reduce cold start time.
* Use runners with pre-installed dependencies/tools for faster job bootstrapping.

---

### 7. **Use Reusable Workflows and Composite Actions**

* Reuse workflows instead of duplicating logic across multiple projects.
* Composite actions reduce code duplication and streamline logic, making workflows faster and easier to maintain.

---

### 8. **Use Artifact Uploads and Downloads**

If build artifacts are required in later jobs (e.g., Docker images or binaries), upload them instead of rebuilding.

```yaml
- uses: actions/upload-artifact@v4
- uses: actions/download-artifact@v4
```

---

### 9. **Optimize Test Strategy**

* Use test splitting or test parallelism tools (e.g., `pytest-xdist`, `jest --runInBand`).
* Run only affected tests using tools like [knapsack-pro](https://knapsackpro.com/), [test impact analysis](https://learn.microsoft.com/en-us/azure/devops/pipelines/test/test-impact-analysis), or custom logic.

---

### 10. **Reduce Docker Layer Rebuilds**

* In Docker-based workflows, optimize `Dockerfile` with:

  * Layer caching
  * Multi-stage builds
  * `.dockerignore` to limit context size

---

### 🚀 Bonus Tips

* Use **scheduled workflows** (nightly builds) for heavy e2e tests instead of on every PR.
* **Use `workflow_dispatch` or `repository_dispatch`** for manually triggered or conditional long-running jobs.
* **Avoid too many nested steps**; prefer small, quick tasks.

---

## 🔥 Real-World Impact

| Optimization                | Time Saved              |
| --------------------------- | ----------------------- |
| Caching npm deps            | \~30-90 seconds         |
| Skipping jobs using `paths` | Up to 100%              |
| Parallel matrix testing     | \~50-70% reduction      |
| Using self-hosted runners   | \~10-30 seconds per job |

---


## ✅ Sample GitHub Actions Workflow (Optimized for Speed)

```yaml
# File: .github/workflows/ci.yaml
name: CI Pipeline

on:
  push:
    branches: [main]
    paths:
      - 'src/**'
      - '.github/workflows/**'
  pull_request:
    paths:
      - 'src/**'
      - '.github/workflows/**'
  workflow_dispatch:

jobs:
  lint:
    name: Lint Code
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Run Linter
        run: npm run lint

  test:
    name: Run Unit Tests
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node: [18, 20]
        os: [ubuntu-latest]
    steps:
      - uses: actions/checkout@v4

      - name: Use Node.js ${{ matrix.node }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run Tests
        run: npm test

  build:
    name: Build Application
    runs-on: ubuntu-latest
    needs: [test]
    if: github.ref == 'refs/heads/main'
    steps:
      - uses: actions/checkout@v4

      - name: Set up Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: 'npm'

      - name: Cache Build Artifacts
        uses: actions/cache@v4
        with:
          path: .next/cache
          key: ${{ runner.os }}-next-${{ hashFiles('**/package-lock.json') }}

      - name: Build App
        run: npm run build

      - name: Upload Build Artifacts
        uses: actions/upload-artifact@v4
        with:
          name: app-build
          path: .next/

  notify:
    name: Slack Notification
    runs-on: ubuntu-latest
    if: failure()
    steps:
      - name: Send Slack Alert
        run: |
          curl -X POST -H 'Content-type: application/json' \
          --data '{"text":"🚨 CI failed for ${{ github.repository }} on ${{ github.ref }}"}' \
          ${{ secrets.SLACK_WEBHOOK }}
```

---

## 📊 CI Pipeline Benchmarking Template

Use this to measure and track improvements as you optimize.

| Job Name       | Time Before | Time After | % Improvement | Optimization Applied     |
| -------------- | ----------- | ---------- | ------------- | ------------------------ |
| `checkout`     | 15s         | 15s        | 0%            | -                        |
| `lint`         | 30s         | 20s        | 33%           | Fast-fail, fewer files   |
| `test`         | 180s        | 80s        | 55%           | Matrix, cache            |
| `build`        | 150s        | 100s       | 33%           | Dependency & layer cache |
| `notify`       | 10s         | 10s        | 0%            | -                        |
| **Total Time** | \~385s      | \~225s     | \~42%         | Multiple improvements    |

---

## 📁 Folder Structure (Monorepo-Friendly)

```
.github/
└── workflows/
    └── ci.yaml
src/
  ├── service-a/
  ├── service-b/
  └── ...
package-lock.json
Dockerfile
```

---

## ✅ Tips to Track Performance Over Time

* Use GitHub Actions **"Usage" tab** for execution time stats.
* Integrate with **Datadog, Prometheus, or Honeycomb** for deeper pipeline observability.
* Use **GitHub Actions API** or tools like [act](https://github.com/nektos/act) for local dry runs.


---

Great! Here's a **GitHub Actions deployment workflow (CD)** that supports:

* Deployment to **Kubernetes** using **Helm**
* **Canary rollout** strategy
* Optional **manual approval for production**
* **Rollback** support using ArgoCD or Helm (based on your stack)

This example assumes you're using **Helm** for deployment and GitHub Actions for automation. ArgoCD integration is included optionally.

---

## 🚀 GitHub Actions Deployment Workflow (`cd.yaml`)

```yaml
# File: .github/workflows/cd.yaml
name: Deploy to Kubernetes

on:
  workflow_dispatch:
    inputs:
      environment:
        type: choice
        description: 'Select environment'
        required: true
        options:
          - staging
          - production
      version:
        description: 'Docker Image Tag (e.g., v1.2.3)'
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: ${{ github.event.inputs.environment }}
      url: https://your-app.example.com

    steps:
      - name: Checkout Repo
        uses: actions/checkout@v4

      - name: Set Context & Variables
        run: |
          echo "ENVIRONMENT=${{ github.event.inputs.environment }}" >> $GITHUB_ENV
          echo "VERSION=${{ github.event.inputs.version }}" >> $GITHUB_ENV

      - name: Set up kubectl
        uses: azure/setup-kubectl@v4
        with:
          version: 'latest'

      - name: Set up Helm
        uses: azure/setup-helm@v4
        with:
          version: 'v3.13.0'

      - name: Configure Kubeconfig
        run: |
          echo "${{ secrets.KUBECONFIG_BASE64 }}" | base64 -d > kubeconfig
          export KUBECONFIG=$PWD/kubeconfig

      - name: Helm Canary Deployment
        run: |
          helm upgrade --install my-app ./helm-chart \
            --namespace $ENVIRONMENT \
            --set image.tag=$VERSION \
            --set deploymentStrategy=canary

  approval:
    needs: deploy
    if: github.event.inputs.environment == 'production'
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://your-app.example.com
    steps:
      - name: Manual Approval
        uses: hmarr/auto-approve-action@v3
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}

  rollback:
    needs: deploy
    if: failure()
    runs-on: ubuntu-latest
    steps:
      - name: Rollback via Helm
        run: |
          helm rollback my-app 1 --namespace $ENVIRONMENT
```

---

## 🧠 Notes & Best Practices

### ✅ Helm-Based Canary Strategy

Your `values.yaml` must support:

```yaml
deploymentStrategy: "canary"

canary:
  enabled: true
  weight: 10
```

You can control traffic % using Istio, Linkerd, or nginx annotations if needed.

---

### 🔄 Rollback Strategy

You can rollback using:

* `helm rollback` (as in the example above)
* Or trigger ArgoCD:

```bash
argocd app rollback my-app --revision <old-revision>
```

---

### 🔒 Secrets Needed

Set the following in your GitHub repository secrets:

* `KUBECONFIG_BASE64` (your base64 encoded kubeconfig)
* `GITHUB_TOKEN`
* Optional: `ARGOCD_TOKEN`, `ARGOCD_SERVER` for ArgoCD CLI integration






