## AI Terraform Code Review
(Mock response — add API credits for live Claude review)

### Critical Issues
- NSG rule allows ALL inbound traffic from 0.0.0.0/0 — exposes to entire internet
- Storage account has public blob access enabled — data accessible without authentication
- Key Vault missing purge_protection_enabled = true
- Key Vault has no network restrictions — accessible from public internet

### Warnings
- No tags defined — required for cost tracking and compliance
- Key Vault soft_delete_retention_days not configured

### Passed Checks
- Resource group name properly referenced
- Location properly configured

### Recommendations
- Add tags: environment, owner, project, managed-by
- Enable purge protection on Key Vault
- Restrict NSG rules to specific IPs instead of 0.0.0.0/0
- Disable public blob access on storage accounts
- Add network_acls to Key Vault
