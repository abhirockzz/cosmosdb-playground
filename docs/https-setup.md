# Optional: Set up Cosmos DB playground on Azure VM with HTTPS using Let's Encrypt

This section shows how to add free SSL certificates to enable HTTPS access to your playground deployment. Make sure you have already deployed the playground on an Azure VM by following the [Azure Deployment Instructions](./azure-deployment.md).

## Prerequisites

- VM must be accessible via the FQDN (for example, `my-cosmosdb-playground.australiaeast.cloudapp.azure.com`)
- Port 443 must be open in Azure NSG (in addition to port 80)

## Open Port 443

```bash
# Open port 443 on NIC NSG
az vm open-port \
  --resource-group $RESOURCE_GROUP \
  --name $VM_NAME \
  --port 443
  --priority 901

# Open port 443 on subnet NSG (if exists)
SUBNET_NSG=$(az network nsg list \
  --resource-group $RESOURCE_GROUP \
  --query "[?contains(name, 'VNET')].name" -o tsv)

if [ ! -z "$SUBNET_NSG" ]; then
  az network nsg rule create \
    --resource-group $RESOURCE_GROUP \
    --nsg-name "$SUBNET_NSG" \
    --name Allow-HTTPS-443 \
    --priority 201 \
    --source-address-prefixes '*' \
    --destination-port-ranges 443 \
    --access Allow \
    --protocol Tcp \
    --direction Inbound
fi
```

## Install Certbot on VM

SSH into your VM and install Certbot:

```bash
# Update packages
sudo apt update

# Install Certbot
sudo apt install certbot -y

# Verify installation
certbot --version
```

## Obtain SSL Certificate

Stop nginx container temporarily to allow Certbot to use port 80:

```bash
cd ~/cosmosdb-playground
docker compose stop nginx
```

Request certificate using your VM's fully qualified domain name (FQDN):

```bash
# Set your FQDN (should match your VM's public DNS name)
export DOMAIN_NAME="cosmosdb-playground.australiaeast.cloudapp.azure.com"
export EMAIL="your-email@example.com"

# Obtain certificate
sudo certbot certonly \
  --standalone \
  --preferred-challenges http \
  --email $EMAIL \
  --agree-tos \
  --no-eff-email \
  -d $DOMAIN_NAME
```

> Replace the email address with your actual email. The FQDN should be in the format: `<dns-label>.<region>.cloudapp.azure.com`

Certificates will be stored at:

- Certificate: `/etc/letsencrypt/live/$DOMAIN_NAME/fullchain.pem`
- Private Key: `/etc/letsencrypt/live/$DOMAIN_NAME/privkey.pem`

Sample output:

```text
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/cosmosdb-playground.australiaeast.cloudapp.azure.com/fullchain.pem
Key is saved at:         /etc/letsencrypt/live/cosmosdb-playground.australiaeast.cloudapp.azure.com/privkey.pem
```

## Update SSL Override File

Update the certificate paths in `docker-compose.ssl.yml` to match your FQDN:

```bash
cd ~/cosmosdb-playground

# Replace the placeholder with your actual FQDN (uses $DOMAIN_NAME from Step 3)
sed -i "s|your-domain-name|$DOMAIN_NAME|g" docker-compose.ssl.yml
```

Verify the update:

```bash
grep "letsencrypt" docker-compose.ssl.yml
```

## Deploy with HTTPS

Start services with the SSL override file to enable HTTPS:

```bash
cd ~/cosmosdb-playground

# Option 1: Use the convenience script
./start-with-ssl.sh

# Option 2: Run docker-compose manually
docker-compose down
docker-compose -f docker-compose.yml -f docker-compose.ssl.yml up -d
```

Verify the services are running:

```bash
# Check status
docker-compose ps

# Check logs for any errors
docker compose logs nginx
```

Access your playground via HTTPS. You should see:

- ✅ Valid SSL certificate
- ✅ HTTP automatically redirects to HTTPS
- ✅ Playground loads and works normally

## Setup Auto-Renewal

Let's Encrypt certificates expire every 90 days. Setup automatic renewal:

```bash
# Test renewal (dry run)
sudo certbot renew --dry-run

# Setup automatic renewal with systemd timer (already enabled by default)
sudo systemctl status certbot.timer

# Verify timer is active
sudo systemctl list-timers | grep certbot
```

The `certbot` package automatically installs a systemd timer that runs twice daily to check and renew certificates.

**Manual Renewal (if needed):**

```bash
# Stop nginx to free port 80
cd ~/cosmosdb-playground
docker-compose stop nginx

# Renew certificate
sudo certbot renew

# Restart nginx
docker-compose start nginx
```

## Switching Between HTTP and HTTPS

**To run with HTTP only (default):**

```bash
docker-compose up -d
```

**To run with HTTPS:**

```bash
docker-compose -f docker-compose.yml -f docker-compose.ssl.yml up -d
```

**To switch back to HTTP:**

```bash
docker-compose down
docker-compose up -d
```

## Troubleshooting

**Certificate errors:**

```bash
# Verify certificate files exist
sudo ls -la /etc/letsencrypt/live/$DOMAIN_NAME/

# Check certificate expiry
sudo certbot certificates
```

**nginx SSL errors:**

```bash
# Test nginx config
docker-compose -f docker-compose.yml -f docker-compose.ssl.yml exec nginx nginx -t

# Check SSL-specific logs
docker-compose logs nginx | grep -i ssl
```

**Port 443 not accessible:**

```bash
# Verify port is open
az network nsg rule list \
  --resource-group $RESOURCE_GROUP \
  --nsg-name <nsg-name> \
  --query "[?destinationPortRange=='443'].{Name:name, Access:access, Priority:priority}"
```

**Override file not applying:**

```bash
# Verify you're using the -f flags correctly
docker-compose -f docker-compose.yml -f docker-compose.ssl.yml config
```
