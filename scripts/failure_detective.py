# Feature 3 — AI Failure Detective
# Reads pipeline failure logs and explains root cause + fix
# Uses Claude API in production, mock response for local testing

import os
import sys

def analyze_failure(log_content: str) -> str:
    """Analyze pipeline failure logs using Claude API."""
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if api_key and api_key.startswith("sk-ant-"):
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            prompt = (
                "You are a senior DevOps engineer analyzing a CI/CD pipeline failure.\n"
                "Read these logs and provide:\n"
                "1. Root cause — what exactly went wrong\n"
                "2. Exact fix — step by step how to fix it\n"
                "3. Prevention — how to stop this happening again\n\n"
                "Format as:\n"
                "## Pipeline Failure Analysis\n"
                "### Root Cause\n"
                "### How to Fix\n"
                "### How to Prevent\n\n"
                "Logs:\n" + log_content
            )
            message = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            print(f"API call failed ({e}), using mock response\n")
            return get_mock_analysis(log_content)
    else:
        print("No API key found, using mock response\n")
        return get_mock_analysis(log_content)


def get_mock_analysis(log_content: str) -> str:
    """Mock failure analysis for testing without API credits."""
    
    log_lower = log_content.lower()
    
    # Detect common failure patterns
    if "state lock" in log_lower or "lock" in log_lower:
        root_cause = "Terraform state lock conflict — a previous pipeline run was cancelled mid-apply, leaving a lock in the state backend."
        fix = ("1. Find the lock ID in the error message\n"
               "2. Run: terraform force-unlock <LOCK_ID>\n"
               "3. Verify no other pipeline is running\n"
               "4. Re-run the pipeline")
        prevention = "Add lock_timeout = '5m' to your backend config. Use pipeline concurrency controls to prevent parallel runs."

    elif "authentication" in log_lower or "unauthorized" in log_lower or "401" in log_lower:
        root_cause = "Authentication failure — Azure credentials are expired, missing, or incorrectly configured in the pipeline."
        fix = ("1. Check GitHub Secrets for AZURE_CREDENTIALS\n"
               "2. Verify the service principal hasn't expired\n"
               "3. Re-generate credentials: az ad sp create-for-rbac\n"
               "4. Update the GitHub Secret with new credentials")
        prevention = "Set up credential expiry alerts. Rotate service principal credentials every 90 days."

    elif "resource not found" in log_lower or "404" in log_lower:
        root_cause = "Resource not found — a referenced Azure resource doesn't exist or was deleted outside of Terraform."
        fix = ("1. Run: terraform refresh to sync state with Azure\n"
               "2. Check if resource was manually deleted in Azure portal\n"
               "3. If deleted: run terraform apply to recreate it\n"
               "4. If renamed: update the resource reference in code")
        prevention = "Never modify Terraform-managed resources manually in Azure portal. Always use terraform apply."

    elif "quota" in log_lower or "limit exceeded" in log_lower:
        root_cause = "Azure subscription quota exceeded — you've hit the limit for this resource type in this region."
        fix = ("1. Run: az vm list-usage --location eastus -o table\n"
               "2. Identify which quota is exceeded\n"
               "3. Request quota increase in Azure portal\n"
               "4. Or reduce resource count in Terraform variables")
        prevention = "Monitor quota usage with Azure Monitor alerts. Request quota increases proactively before hitting limits."

    elif "timeout" in log_lower or "timed out" in log_lower:
        root_cause = "Pipeline timeout — a Terraform operation took longer than the allowed time limit."
        fix = ("1. Check Azure portal for the resource provisioning status\n"
               "2. If still creating: wait and re-run pipeline\n"
               "3. If stuck: manually delete the resource and re-apply\n"
               "4. Increase pipeline timeout in workflow YAML")
        prevention = "Set realistic timeouts. AKS creation takes 10-15 minutes. Set pipeline timeout to at least 30 minutes."

    elif "invalid" in log_lower or "syntax" in log_lower:
        root_cause = "Terraform configuration error — invalid syntax or invalid value in one of the .tf files."
        fix = ("1. Run: terraform validate to identify exact error\n"
               "2. Check the file and line number in the error\n"
               "3. Fix the syntax error\n"
               "4. Run: terraform fmt to auto-format the code")
        prevention = "Run terraform validate and terraform fmt locally before pushing. Add pre-commit hooks."

    else:
        root_cause = "Unknown failure — could not match a known error pattern in the logs."
        fix = ("1. Read the full error message carefully\n"
               "2. Search the exact error message online\n"
               "3. Check Azure Service Health for outages\n"
               "4. Run terraform plan locally to reproduce")
        prevention = "Add detailed logging to your pipeline. Use terraform plan -detailed-exitcode for better error output."

    analysis = "## Pipeline Failure Analysis\n"
    analysis += "(Mock response — add API credits for live Claude analysis)\n\n"
    analysis += f"### Root Cause\n{root_cause}\n\n"
    analysis += f"### How to Fix\n{fix}\n\n"
    analysis += f"### How to Prevent\n{prevention}\n"
    
    return analysis


def main():
    if len(sys.argv) > 1:
        # Log file provided
        log_file = sys.argv[1]
        try:
            with open(log_file, 'r') as f:
                log_content = f.read()
            print(f"Analyzing logs from: {log_file}\n")
        except FileNotFoundError:
            print(f"File not found: {log_file}")
            sys.exit(1)
    else:
        # Use sample logs for demo
        print("No log file provided — using sample failure log\n")
        log_content = """
Error: Error acquiring the state lock

Error message: ConditionalCheckFailedException: The conditional request failed
Lock Info:
  ID:        82a34f1c-4d56-9012-abcd-ef1234567890
  Path:      terraform.tfstate
  Operation: OperationTypeApply
  Who:       runner@github-actions
  Version:   1.8.3
  Created:   2024-01-15 10:23:45
  Info:      

Terraform acquires a state lock to protect the state from being written
by multiple users at the same time. Please resolve the issue above and try
again. For most commands, you can disable locking with the -lock=false flag,
but this is not recommended.
"""

    print("Analyzing pipeline failure...\n")
    analysis = analyze_failure(log_content)
    
    print("=" * 60)
    print(analysis)
    print("=" * 60)
    
    # Save analysis
    output_file = "failure_analysis.md"
    with open(output_file, 'w') as f:
        f.write(analysis)
    print(f"\nAnalysis saved to {output_file}")


if __name__ == "__main__":
    main()