# Feature 5 — Infra Chatbot
# Ask your infrastructure questions in plain English
# Reads Terraform state or Azure CLI output and answers

import os
import sys
import json
import subprocess

def get_infrastructure_info() -> str:
    """Get current infrastructure info from Azure CLI or Terraform."""
    
    infra_info = ""
    
    # Try Azure CLI first
    try:
        result = subprocess.run(
            ["az.cmd", "resource", "list", "--output", "json"],
            capture_output=True, text=True, timeout=30
        )
        if result.returncode == 0:
            resources = json.loads(result.stdout)
            if resources:
                infra_info += f"Azure Resources ({len(resources)} total):\n"
                for r in resources:
                    infra_info += f"- {r.get('name')} ({r.get('type')}) in {r.get('location')}\n"
            else:
                infra_info = "No Azure resources currently deployed."
        else:
            infra_info = "Could not query Azure — not logged in or no resources."
    except Exception as e:
        infra_info = f"Azure CLI not available: {e}"
    
    # Try reading Terraform state if exists
    if os.path.exists("terraform.tfstate"):
        try:
            with open("terraform.tfstate", 'r') as f:
                state = json.load(f)
            resources = state.get("resources", [])
            if resources:
                infra_info += f"\nTerraform State ({len(resources)} resources):\n"
                for r in resources:
                    infra_info += f"- {r.get('name')} ({r.get('type')})\n"
        except Exception as e:
            infra_info += f"\nCould not read Terraform state: {e}"
    
    return infra_info if infra_info else "No infrastructure information available."


def ask_infra_question(question: str, infra_info: str) -> str:
    """Answer infrastructure question using Claude API."""
    
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    
    if api_key and api_key.startswith("sk-ant-"):
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=api_key)
            prompt = (
                "You are a DevOps engineer assistant with access to infrastructure data.\n"
                "Answer this question based on the infrastructure info provided.\n"
                "Be specific and concise. If you can't answer from the data, say so.\n\n"
                f"Infrastructure info:\n{infra_info}\n\n"
                f"Question: {question}"
            )
            message = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )
            return message.content[0].text
        except Exception as e:
            print(f"API call failed ({e}), using mock response\n")
            return get_mock_answer(question, infra_info)
    else:
        return get_mock_answer(question, infra_info)


def get_mock_answer(question: str, infra_info: str) -> str:
    """Mock answers for testing without API credits."""
    
    q = question.lower()
    
    if any(w in q for w in ["what", "list", "show", "running", "deployed"]):
        if "No Azure resources" in infra_info or "NetworkWatcher" in infra_info:
            return ("Currently only NetworkWatcher is running in your Azure subscription. "
                    "No application infrastructure is deployed. "
                    "Run 'terraform apply' in the azure-infrastructure-terraform project to deploy resources.")
        return f"Based on your infrastructure:\n{infra_info}"
    
    elif any(w in q for w in ["cost", "expensive", "price", "billing", "spend"]):
        return ("To check costs:\n"
                "1. Go to Azure Portal → Cost Management\n"
                "2. Run: az consumption usage list --output table\n"
                "3. AKS clusters are the most expensive — ~$5-10/hour\n"
                "4. Use 'terraform destroy' when not needed to save costs")
    
    elif any(w in q for w in ["tag", "tags", "missing"]):
        return ("To check for missing tags:\n"
                "1. Run: az resource list --query \"[?tags==null]\" --output table\n"
                "2. Resources without tags: check your Terraform variables.tf\n"
                "3. Add tags map to all resources: environment, owner, project, managed-by")
    
    elif any(w in q for w in ["health", "status", "healthy", "up", "down"]):
        return ("To check infrastructure health:\n"
                "1. Azure Portal → Resource Groups → check each resource\n"
                "2. Run: az resource list --output table\n"
                "3. For AKS: kubectl get nodes\n"
                "4. Check Azure Monitor for any active alerts")
    
    elif any(w in q for w in ["scale", "resize", "nodes", "capacity"]):
        return ("To scale your AKS cluster:\n"
                "1. Via Terraform: update aks_node_count in variables.tf, run terraform apply\n"
                "2. Via CLI: az aks scale --resource-group <rg> --name <aks> --node-count <n>\n"
                "3. Autoscaler handles this automatically if enabled (min:1 max:5 in our config)")
    
    elif any(w in q for w in ["secret", "vault", "key", "password", "credential"]):
        return ("For secrets management:\n"
                "1. All secrets stored in Azure Key Vault: kv-azinfra-dev\n"
                "2. Add secret: az keyvault secret set --vault-name kv-azinfra-dev --name mysecret --value myvalue\n"
                "3. Get secret: az keyvault secret show --vault-name kv-azinfra-dev --name mysecret\n"
                "4. AKS accesses secrets via managed identity — no passwords needed")
    
    else:
        return (f"I received your question: '{question}'\n\n"
                f"Current infrastructure info:\n{infra_info}\n\n"
                "For a live AI answer, add Claude API credits at console.anthropic.com\n"
                "Common questions I can answer:\n"
                "- What resources are running?\n"
                "- Which resources are missing tags?\n"
                "- How do I scale my cluster?\n"
                "- How do I check costs?\n"
                "- How do I manage secrets?")


def main():
    print("=" * 60)
    print("Infra Chatbot — Ask your infrastructure anything")
    print("=" * 60)
    print("Fetching infrastructure info...\n")
    
    infra_info = get_infrastructure_info()
    
    print(f"Infrastructure summary:\n{infra_info}\n")
    print("=" * 60)
    
    # Interactive mode or single question
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
        print(f"Question: {question}\n")
        answer = ask_infra_question(question, infra_info)
        print(f"Answer:\n{answer}")
    else:
        # Interactive chat loop
        print("Type your questions below. Type 'exit' to quit.\n")
        while True:
            try:
                question = input("You: ").strip()
                if question.lower() in ["exit", "quit", "q"]:
                    print("Goodbye!")
                    break
                if not question:
                    continue
                answer = ask_infra_question(question, infra_info)
                print(f"\nBot: {answer}\n")
                print("-" * 40)
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break


if __name__ == "__main__":
    main()