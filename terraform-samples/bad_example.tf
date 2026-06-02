# This file has intentional security issues for testing

resource "azurerm_storage_account" "example" {
  name                     = "mystorageaccount"
  resource_group_name      = "my-rg"
  location                 = "East US"
  account_tier             = "Standard"
  account_replication_type = "LRS"
  
  # Security issue: blob public access enabled
  allow_nested_items_to_be_public = true
}

resource "azurerm_network_security_group" "example" {
  name                = "my-nsg"
  location            = "East US"
  resource_group_name = "my-rg"

  security_rule {
    name                       = "allow-all"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Allow"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "0.0.0.0/0"
    destination_address_prefix = "*"
  }
}

resource "azurerm_key_vault" "example" {
  name                = "my-keyvault"
  location            = "East US"
  resource_group_name = "my-rg"
  tenant_id           = "my-tenant-id"
  sku_name            = "standard"
}