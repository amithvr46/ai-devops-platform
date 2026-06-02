import os
import sys

def review_terraform_code(terraform_code):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key and api_key.startswith("sk-ant-"):
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            prompt = "You are a senior DevOps engineer. Review this Terraform code for security issues, misconfigs, missing tags, and best practices.\n\nFormat response as:\n## AI Terraform Review\n### Critical Issues\n### Warnings\n### Passed Checks\n### Recommendations\n\nCode:\n" + terraform_code
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            print(f"API call failed ({e}), using mock response\n")
            return get_mock_review(terraform_code)
    else:
        print("No API key found, using mock response\n")
        return get_mock_review(terraform_code)

def get_mock_review(terraform_code):
    issues = []
    warnings = []
    passed = []

    if "0.0.0.0/0" in terraform_code:
        issues.append("NSG rule allows ALL inbound traffic from 0.0.0.0/0 — exposes to entire internet")
    if "allow_nested_items_to_be_public = true" in terraform_code:
        issues.append("Storage account has public blob access enabled — data accessible without authentication")
    if "purge_protection" not in terraform_code and "key_vault" in terraform_code.lower():
        issues.append("Key Vault missing purge_protection_enabled = true")
    if "network_acls" not in terraform_code and "key_vault" in terraform_code.lower():
        issues.append("Key Vault has no network restrictions — accessible from public internet")
    if "tags" not in terraform_code:
        warnings.append("No tags defined — required for cost tracking and compliance")
    if "soft_delete" not in terraform_code and "key_vault" in terraform_code.lower():
        warnings.append("Key Vault soft_delete_retention_days not configured")
    if "resource_group_name" in terraform_code:
        passed.append("Resource group name properly referenced")
    if "location" in terraform_code:
        passed.append("Location properly configured")
    if len(issues) == 0:
        passed.append("No critical security issues found")

    review = "## AI Terraform Code Review\n"
    review += "(Mock response — add API credits for live Claude review)\n\n"
    review += "### Critical Issues\n"
    review += "\n".join(f"- {i}" for i in issues) if issues else "- None found"
    review += "\n\n### Warnings\n"
    review += "\n".join(f"- {w}" for w in warnings) if warnings else "- None found"
    review += "\n\n### Passed Checks\n"
    review += "\n".join(f"- {p}" for p in passed)
    review += "\n\n### Recommendations\n"
    review += "- Add tags: environment, owner, project, managed-by\n"
    review += "- Enable purge protection on Key Vault\n"
    review += "- Restrict NSG rules to specific IPs instead of 0.0.0.0/0\n"
    review += "- Disable public blob access on storage accounts\n"
    review += "- Add network_acls to Key Vault\n"
    return review

def main():
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        try:
            with open(file_path, 'r') as f:
                terraform_code = f.read()
            print(f"Reviewing: {file_path}\n")
        except FileNotFoundError:
            print(f"File not found: {file_path}")
            sys.exit(1)
    else:
        print("Usage: python scripts/pr_reviewer.py <terraform-file>")
        sys.exit(1)

    print("Running AI review...\n")
    review = review_terraform_code(terraform_code)
    print("=" * 60)
    print(review)
    print("=" * 60)

    with open("review_output.md", 'w') as f:
        f.write(review)
    print("\nReview saved to review_output.md")

if __name__ == "__main__":
    main()