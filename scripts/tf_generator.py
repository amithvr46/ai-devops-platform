# Feature 2 — AI Terraform Generator
# Type plain English -> get production-ready Terraform code
# Uses Claude API in production, mock response for local testing

import os
import sys

def generate_terraform(description: str) -> str:
    """Generate Terraform code from plain English description."""
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if api_key and api_key.startswith("sk-ant-"):
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            prompt = (
                "You are a senior Azure DevOps engineer. "
                "Generate production-ready Terraform code for Azure based on this description:\n\n"
                + description +
                "\n\nRules:\n"
                "- Use azurerm provider\n"
                "- Include variables.tf and outputs.tf sections\n"
                "- Add proper tags: environment, owner, managed-by\n"
                "- Follow security best practices\n"
                "- Add comments explaining each resource\n"
                "- No hardcoded secrets\n\n"
                "Return only valid Terraform code with comments."
            )
            message = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            print(f"API call failed ({e}), using mock response\n")
            return get_mock_terraform(description)
    else:
        print("No API key found, using mock response\n")
        return get_mock_terraform(description)


def get_mock_terraform(description: str) -> str:
    """Mock Terraform output for testing without API credits."""
    
    desc_lower = description.lower()
    
    # Detect what the user is asking for
    wants_vnet = any(w in desc_lower for w in ["vnet", "network", "virtual network"])
    wants_aks = any(w in desc_lower for w in ["aks", "kubernetes", "k8s", "cluster"])
    wants_storage = any(w in desc_lower for w in ["storage", "blob", "bucket"])
    wants_vm = any(w in desc_lower for w in ["vm", "virtual machine", "server"])

    code = f'# Auto-generated Terraform by AI DevOps Platform\n'
    code += f'# Description: {description}\n'
    code += f'# (Mock response — add API credits for live Claude generation)\n\n'
    
    code += '''terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "~> 3.0"
    }
  }
}

provider "azurerm" {
  features {}
}

# Variables
variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "rg-generated-dev"
}

variable "location" {
  description = "Azure region"
  type        = string
  default     = "East US"
}

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

# Tags applied to all resources
locals {
  tags = {
    environment = var.environment
    owner       = "amith-busireddy"
    managed-by  = "terraform"
    generated   = "ai-devops-platform"
  }
}

# Resource Group
resource "azurerm_resource_group" "main" {
  name     = var.resource_group_name
  location = var.location
  tags     = local.tags
}
'''

    if wants_vnet or wants_aks:
        code += '''
# Virtual Network
resource "azurerm_virtual_network" "main" {
  name                = "vnet-generated-${var.environment}"
  address_space       = ["10.0.0.0/16"]
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  tags                = local.tags
}

# Subnet
resource "azurerm_subnet" "main" {
  name                 = "snet-main"
  resource_group_name  = azurerm_resource_group.main.name
  virtual_network_name = azurerm_virtual_network.main.name
  address_prefixes     = ["10.0.1.0/24"]
}
'''

    if wants_aks:
        code += '''
# AKS Cluster
resource "azurerm_kubernetes_cluster" "main" {
  name                = "aks-generated-${var.environment}"
  location            = var.location
  resource_group_name = azurerm_resource_group.main.name
  dns_prefix          = "aks-generated"

  default_node_pool {
    name                = "systempool"
    node_count          = 2
    vm_size             = "Standard_D2s_v3"
    vnet_subnet_id      = azurerm_subnet.main.id
    enable_auto_scaling = true
    min_count           = 1
    max_count           = 5
  }

  identity {
    type = "SystemAssigned"
  }

  tags = local.tags
}

# Outputs
output "cluster_name" {
  value = azurerm_kubernetes_cluster.main.name
}

output "kube_config" {
  value     = azurerm_kubernetes_cluster.main.kube_config_raw
  sensitive = true
}
'''

    if wants_storage:
        code += '''
# Storage Account
resource "azurerm_storage_account" "main" {
  name                     = "stgenerated${var.environment}"
  resource_group_name      = azurerm_resource_group.main.name
  location                 = var.location
  account_tier             = "Standard"
  account_replication_type = "LRS"

  # Security: disable public access
  allow_nested_items_to_be_public = false

  tags = local.tags
}

output "storage_account_name" {
  value = azurerm_storage_account.main.name
}
'''

    if wants_vm:
        code += '''
# Virtual Machine
resource "azurerm_linux_virtual_machine" "main" {
  name                = "vm-generated-${var.environment}"
  resource_group_name = azurerm_resource_group.main.name
  location            = var.location
  size                = "Standard_B2s"
  admin_username      = "adminuser"

  # No password — use SSH key only (security best practice)
  disable_password_authentication = true

  admin_ssh_key {
    username   = "adminuser"
    public_key = file("~/.ssh/id_rsa.pub")
  }

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "Canonical"
    offer     = "UbuntuServer"
    sku       = "18.04-LTS"
    version   = "latest"
  }

  tags = local.tags
}
'''

    if not any([wants_vnet, wants_aks, wants_storage, wants_vm]):
        code += '''
# Generic Azure Resource
# Tip: Be specific in your description for better results
# Examples:
#   "Create an AKS cluster with 2 nodes"
#   "Create a storage account with private access"
#   "Create a VNet with 3 subnets"
'''

    return code


def main():
    if len(sys.argv) > 1:
        # Description passed as command line argument
        description = " ".join(sys.argv[1:])
    else:
        print("AI Terraform Generator")
        print("=" * 40)
        description = input("Describe what you want to create: ")

    print(f"\nGenerating Terraform for: {description}\n")
    print("AI is writing your code...\n")
    
    terraform_code = generate_terraform(description)
    
    print("=" * 60)
    print(terraform_code)
    print("=" * 60)
    
    # Save to file
    output_file = "generated_terraform.tf"
    with open(output_file, 'w') as f:
        f.write(terraform_code)
    print(f"\nTerraform code saved to {output_file}")
    print("Run 'terraform init' and 'terraform plan' to review before applying")


if __name__ == "__main__":
    main()