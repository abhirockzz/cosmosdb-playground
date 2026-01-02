# Deploy Your Playground Instance in Azure

## Prerequisites

- An Azure subscription
- Basic familiarity with Azure CLI and SSH

## Deployment Steps

### Create an Azure VM

Start by creating a resource group and an Ubuntu VM with a public DNS name. Feel free to customize the resource names, region, and VM size as needed:

```bash
export RESOURCE_GROUP="cosmosdb-playground-rg"
export VM_NAME="cosmosdb-playground-vm"
export AZURE_REGION="australiaeast"
export VM_DNS_LABEL="cosmosdb-playground"

az group create --name $RESOURCE_GROUP --location $AZURE_REGION

az vm create \
  --resource-group $RESOURCE_GROUP \
  --name $VM_NAME \
  --image Ubuntu2404 \
  --size Standard_D2s_v3 \
  --admin-username azureuser \
  --generate-ssh-keys \
  --public-ip-address-dns-name $VM_DNS_LABEL
```

This creates a VM accessible at `<dns-label>.<region>.cloudapp.azure.com`.

### SSH into the VM and install Docker and Docker Compose

```bash
# Get VM IP and connect
VM_IP=$(az vm show --resource-group $RESOURCE_GROUP --name $VM_NAME --show-details --query publicIps -o tsv)
ssh azureuser@$VM_IP

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo apt install docker-compose -y

# Reconnect to apply group changes
exit
ssh azureuser@$VM_IP
```

### Start the Playground

Clone the repository and launch all services:

```bash
git clone https://github.com/abhirockzz/cosmosdb-playground
cd cosmosdb-playground

docker compose build
docker compose up -d

# Verify services are running
docker compose ps
```

**Configure Network Access**

Open port 80 to allow HTTP traffic:

```bash
az vm open-port --resource-group $RESOURCE_GROUP --name $VM_NAME --port 80
```

Your playground should be accessible at `http://<dns-label>.<region>.cloudapp.azure.com`.

If you can't access the playground URL, you may need to open port 80 on both Network Security Groups (NSG):

```bash
# Open port 80 on subnet NSG
SUBNET_NSG=$(az network nsg list \
  --resource-group $RESOURCE_GROUP \
  --query "[?contains(name, 'VNET')].name" -o tsv)

az network nsg rule create \
  --resource-group $RESOURCE_GROUP \
  --nsg-name "$SUBNET_NSG" \
  --name Allow-HTTP-80 \
  --priority 200 \
  --source-address-prefixes '*' \
  --destination-port-ranges 80 \
  --access Allow \
  --protocol Tcp \
  --direction Inbound
```

## Clean Up Resources

To avoid incurring charges, delete the resource group when you're done:

```bash
az group delete --name $RESOURCE_GROUP --yes --no-wait
```

## Managing Your Deployment

Once deployed, you can manage the playground using standard Docker Compose commands:

```bash
# View logs
docker compose logs -f

# Restart services
docker compose restart

# Stop services
docker compose down

# Update to latest version
git pull
docker compose build
docker compose up -d
```

The containerized architecture makes updates and maintenance simple — just pull the latest changes and restart the containers.
