---
title: How to Secure Nginx with SSL Using Certbot on Ubuntu
description: Securing your website with SSL (Secure Sockets Layer) is crucial
  for encrypting data and ensuring secure communication between a web server and
  users.
image: /images/blog/how-to-secure-nginx-with-ssl-using-certbot-on-ubuntu.webp
layout: post
permalink: blog/:title
author: Shyam Mohan
category: DevOps
date: 2025-01-15T13:37:00.000Z
---


## Introduction
Securing your website with SSL (Secure Sockets Layer) is crucial for encrypting data and ensuring secure communication between a web server and users. In this guide, we will cover how to install and configure SSL for Nginx using Certbot on an Ubuntu server. We'll also explain what Nginx, SSL, and Certbot are, how Certbot works, and how to enable auto-renewal. Additionally, we'll discuss how to configure SSL for wildcard and subdomains.

---
## What is Nginx?
Nginx is a high-performance web server that also functions as a reverse proxy, load balancer, and caching server. It is widely used for hosting websites and applications due to its efficiency, scalability, and ability to handle multiple requests simultaneously.

---
## What is SSL?
SSL (Secure Sockets Layer) is a security protocol that encrypts data transferred between a user's browser and a web server. It ensures privacy, data integrity, and authentication. Modern SSL implementations use TLS (Transport Layer Security), but the term "SSL" is still commonly used.

---
## What is Certbot?
Certbot is an open-source tool developed by the Electronic Frontier Foundation (EFF) that automates obtaining and renewing SSL/TLS certificates from Let's Encrypt. It simplifies the process of securing web servers and ensures certificates remain valid without manual intervention.

---
## How Certbot Works
Certbot works by:
1. Verifying domain ownership via HTTP or DNS challenges.
2. Requesting an SSL certificate from Let's Encrypt.
3. Automatically configuring Nginx to use the certificate.
4. Setting up auto-renewal to ensure continuous security.

---
## Installing SSL on Nginx Using Certbot
Follow these steps to secure your Nginx server with SSL on Ubuntu:

### Step 1: Update the System
Ensure your system packages are up to date:
```bash
sudo apt update && sudo apt upgrade -y
```

### Step 2: Install Nginx
If Nginx is not installed, install it using:
```bash
sudo apt install nginx -y
```
Enable and start Nginx:
```bash
sudo systemctl enable nginx
sudo systemctl start nginx
```

### Step 3: Install Certbot and Nginx Plugin
Install Certbot and the Nginx plugin:
```bash
sudo apt install certbot python3-certbot-nginx -y
```

### Step 4: Obtain an SSL Certificate
Run the following command, replacing `yourdomain.com` with your actual domain:
```bash
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```
Certbot will prompt you to enter your email, agree to the terms of service, and choose whether to redirect HTTP to HTTPS.

### Step 5: Verify SSL Installation
After installation, test your website by visiting:
```
https://yourdomain.com
```
You can also check the status of the certificate:
```bash
sudo certbot certificates
```

---
## Auto-Renewing SSL Certificates
Let's Encrypt certificates are valid for 90 days. Certbot includes a built-in renewal system that runs automatically. To test the renewal process, run:
```bash
sudo certbot renew --dry-run
```
By default, Certbot sets up a cron job for automatic renewal. You can check the cron job with:
```bash
sudo systemctl list-timers
```

---
## Adding SSL for Wildcard or Subdomains
To secure all subdomains (wildcard SSL), use the DNS challenge method:
```bash
sudo certbot -d "*.yourdomain.com" --manual --preferred-challenges dns certonly
```
You will need to add a TXT record to your domain’s DNS settings as instructed by Certbot. Once verified, update your Nginx configuration to use the wildcard certificate.

For subdomains, simply specify each subdomain in the `-d` flag when running Certbot:
```bash
sudo certbot --nginx -d sub1.yourdomain.com -d sub2.yourdomain.com
```

---
## Automating SSL Installation with a Shell Script
To automate the entire process, you can use the following shell script:
```bash
#!/bin/bash

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install Nginx
echo "Installing Nginx..."
sudo apt install nginx -y
sudo systemctl enable nginx
sudo systemctl start nginx

# Install Certbot
echo "Installing Certbot and Nginx plugin..."
sudo apt install certbot python3-certbot-nginx -y

# Obtain SSL Certificate
echo "Obtaining SSL certificate..."
read -p "Enter your domain (e.g., example.com): " domain
sudo certbot --nginx -d $domain -d www.$domain

# Set up auto-renewal
echo "Setting up auto-renewal..."
sudo certbot renew --dry-run

# Restart Nginx
echo "Restarting Nginx..."
sudo systemctl restart nginx

echo "SSL setup completed successfully!"
```
Save this script as `setup_ssl.sh`, then run:
```bash
chmod +x setup_ssl.sh
./setup_ssl.sh
```

---
## Conclusion
Adding SSL to your Nginx server using Certbot is a straightforward process that greatly enhances your website’s security. With automatic renewal, you can ensure uninterrupted protection without manual intervention. Whether securing a single domain, subdomains, or a wildcard domain, Certbot makes SSL management easy and efficient.

Now that your website is secured, regularly monitor SSL status to ensure a smooth and secure browsing experience for your users!


🚀 Boost Your Business with Expert DevOps Services from Kubeify! 🚀

Struggling with inefficient deployments, downtime, or slow CI/CD pipelines? Kubeify helps businesses streamline operations with cutting-edge DevOps, Kubernetes, and cloud automation solutions.

✅ Faster, reliable deployments 
✅ Scalable & secure cloud infrastructure 
✅ Optimized CI/CD workflows

Let’s collaborate to enhance your DevOps strategy and accelerate innovation. We’d love to explore opportunities to work together!

💬 Schedule a meeting here https://kubeify.com/schedule-meeting

#DevOps #Kubernetes #CloudAutomation #CI_CD #Kubeify #TechInnovation
