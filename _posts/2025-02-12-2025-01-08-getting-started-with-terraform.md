---
title: 2025-01-08-Getting Started with Terraform
description: Terraform is an Infrastructure as Code (IaC) tool that allows you
  to define and provision cloud resources in a declarative way. It supports AWS,
  Azure, Google Cloud, DigitalOcean, Kubernetes, and many more.
image: /images/blog/getting-started-with-terraform.webp
layout: post
permalink: blog/:title
author: Shyam Mohan
category: DevOps
date: 2025-01-08T19:54:00.000Z
---
# **Getting Started with Terraform 🚀**

Terraform is an **Infrastructure as Code (IaC)** tool that allows you to define and provision cloud resources in a **declarative** way. It supports **AWS, Azure, Google Cloud, DigitalOcean, Kubernetes**, and many more.

---

## **Step 1: Install Terraform**
Follow the [installation guide](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli) based on your OS:

- **Ubuntu/Debian**
  ```bash
  sudo apt update && sudo apt install -y terraform
  ```
- **MacOS**
  ```bash
  brew install terraform
  ```
- **Windows** (via Chocolatey)
  ```powershell
  choco install terraform
  ```

Verify the installation:
```bash
terraform version
```

---

## **Step 2: Create a Terraform Project**
1. **Create a new directory for your Terraform configuration**
   ```bash
   mkdir terraform-project && cd terraform-project
   ```

2. **Create a Terraform configuration file**
   ```bash
   touch main.tf
   ```

---

## **Step 3: Write Your First Terraform Configuration**
Open `main.tf` and define a basic DigitalOcean Kubernetes cluster:

```hcl
provider "digitalocean" {
  token = var.do_token
}

variable "do_token" {}

resource "digitalocean_kubernetes_cluster" "my_cluster" {
  name   = "my-k8s-cluster"
  region = "nyc3"
  version = "1.29.0-do.0"

  node_pool {
    name       = "worker-pool"
    size       = "s-2vcpu-4gb"
    node_count = 2
  }
}
```

---

## **Step 4: Initialize Terraform**
Run the following command:
```bash
terraform init
```
This downloads the required Terraform provider plugins.

---

## **Step 5: Preview the Changes**
```bash
terraform plan
```
This will **show the resources Terraform will create**.

---

## **Step 6: Apply the Changes**
```bash
terraform apply
```
Terraform will ask for confirmation. Type **"yes"** to proceed.

Once completed, you will have a **Kubernetes cluster running on DigitalOcean**! 🎉

---

## **Step 7: Destroy the Infrastructure (Optional)**
If you want to delete everything created by Terraform, run:
```bash
terraform destroy
```

---



If you're getting the error **"Unable to locate package terraform"**, it means that Terraform is either not available in your package repositories or your package list is outdated. Follow these steps to install Terraform properly based on your OS:

---

## **Ubuntu/Debian Installation**
### **Step 1: Update Package List**
```bash
sudo apt update && sudo apt upgrade -y
```

### **Step 2: Install Required Packages**
```bash
sudo apt install -y gnupg software-properties-common
```

### **Step 3: Add HashiCorp Repository**
```bash
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
```

### **Step 4: Install Terraform**
```bash
sudo apt update
sudo apt install -y terraform
```

### **Step 5: Verify Installation**
```bash
terraform version
```

---

## **CentOS/RHEL Installation**
### **Step 1: Install Yum Utilities**
```bash
sudo yum install -y yum-utils
```

### **Step 2: Add HashiCorp Repository**
```bash
sudo yum-config-manager --add-repo https://rpm.releases.hashicorp.com/RHEL/hashicorp.repo
```

### **Step 3: Install Terraform**
```bash
sudo yum install -y terraform
```

### **Step 4: Verify Installation**
```bash
terraform version
```

---

## **MacOS Installation**
Use Homebrew:
```bash
brew tap hashicorp/tap
brew install hashicorp/tap/terraform
```

---

## **Windows Installation**
1. Download the latest Terraform binary from [Terraform Downloads](https://developer.hashicorp.com/terraform/downloads).
2. Extract it and add the Terraform executable to your **system PATH**.

---

After installation, retry:
```bash
terraform init
terraform apply
```

Let me know if you need more help! 🚀
