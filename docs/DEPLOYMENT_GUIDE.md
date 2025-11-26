# Deployment & Setup Guide

This guide covers the necessary steps to configure, test, and deploy the `agentic-parallelism` applications.

## 1. API Keys & Environment Configuration

The application requires several API keys to function. These should be set in your `.env` file for local development and as GitHub Secrets for CI/CD.

### Required Keys
| Variable | Description | Provider |
|----------|-------------|----------|
| `OPENAI_API_KEY` | Required for the LLM agent logic. | [OpenAI Platform](https://platform.openai.com/api-keys) |
| `TAVILY_API_KEY` | Required for the "Recent Company News" tool. | [Tavily](https://tavily.com/) |
| `SENTRY_DSN` | Required for error tracking. | [Sentry](https://sentry.io/) |

### Optional Keys
| Variable | Description | Provider |
|----------|-------------|----------|
| `LANGCHAIN_API_KEY` | For tracing agent execution. | [LangSmith](https://smith.langchain.com/) |
| `ANTHROPIC_API_KEY` | If switching LLM provider to Anthropic. | [Anthropic](https://console.anthropic.com/) |

### Local Setup
1. Copy the example file:
   ```bash
   cp apps/parallel_tool_use/.env.example apps/parallel_tool_use/.env
   ```
2. Edit `.env` and paste your actual keys.

---

## 2. Running Local Tests

Tests are already defined in the `apps/parallel_tool_use/tests/` directory. You do **not** need to create a new tests directory.

### Unit Tests
Run these to verify logic without needing real API keys (external calls are mocked).
```bash
# Run all unit tests
pytest apps/parallel_tool_use/tests/test_unit.py -v
```

### End-to-End (E2E) Tests
Run these to verify the full flow with **real** API calls (requires `.env` to be set up).
```bash
# Run e2e tests
pytest apps/parallel_tool_use/tests/test_e2e.py -v
```

---

## 3. Azure Container Registry (ACR) Setup Checklist

You need an Azure Container Registry to store your Docker images.

### Create Registry (via Azure CLI)

# 1. Login to Azure
az login

# 2. Create a Resource Group (if you haven't already)
az group create --name agentic-parallelism-rg --location westus

# 2.1. Check if the resource group exists
az group exists --name agentic-parallelism-rg

# 2.2. Choose the subscription
az account set --subscription <SUBSCRIPTION_ID>

# 2.3. Register the Container Registry provider (required once per subscription)
az provider register --namespace Microsoft.ContainerRegistry

# 2.4. Verify registration
az provider show --namespace Microsoft.ContainerRegistry --query "registrationState" -o tsv   # should be "Registered"

# 2.5. Create the ACR
az acr create \
  --resource-group agentic-parallelism-rg \
  --name agenticparallelismacr \
  --sku Basic \
  --admin-enabled true

# 2.6. Test login
az acr login --name agenticparallelismacr

### Get Credentials
# Get the login server name (e.g., agenticparallelismacr.azurecr.io)
az acr show --name agenticparallelismacr --query loginServer --output tsv

# Get the username and password
az acr credential show --name agenticparallelismacr

---

## 4. GitHub Secrets for CI/CD

To enable the automated deployment pipelines (`.github/workflows/`), you must set the following secrets in your GitHub Repository settings (**Settings** > **Secrets and variables** > **Actions**).

### Azure Credentials
Generate a service principal for GitHub Actions:
```bash
# Replace <SUBSCRIPTION_ID> with your Azure Subscription ID
# Replace <RESOURCE_GROUP> with your Resource Group name (e.g., agentic-parallelism-rg)
az ad sp create-for-rbac --name "github-actions-agentic" \
                         --role contributor \
                         --scopes /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/<RESOURCE_GROUP> \
                         --json-auth
```
Copy the entire JSON output and save it as the secret `AZURE_CREDENTIALS`.

### Save the ACR JSON as a GitHub secret

1. **Export the ACR details**  
   ```bash
   az acr show --name agenticparallelismacr --output json > acr-info.json
   cat acr-info.json   # verify the JSON

### Other Required Secrets

| Secret Name | Value |
|-------------|-------|
| `AZURE_CREDENTIALS` | The JSON output from the command above. |
| `AZURE_REGISTRY` | Your ACR login server (e.g., `agenticparallelismacr.azurecr.io`). |
| `AZURE_CLIENT_ID` | The `username` from `az acr credential show`. |
| `AZURE_CLIENT_SECRET` | The `password` from `az acr credential show`. |
| `AZURE_RESOURCE_GROUP` | Your resource group name (e.g., `agentic-parallelism-rg`). |
| `OPENAI_API_KEY` | Your OpenAI API Key. |
| `TAVILY_API_KEY` | Your Tavily API Key. |
| `SENTRY_DSN` | Your Sentry DSN. |

#### Adding the secrets to GitHub

1. Open your repository on GitHub → **Settings** → **Secrets & variables** → **Actions**.
2. Click **New repository secret** for each entry above.
   - **Name**: use the exact secret name (e.g., `AZURE_REGISTRY`).
   - **Value**: paste the corresponding value:
     - `AZURE_REGISTRY`: run `az acr show --name agenticparallelismacr --query loginServer -o tsv`.
     - `AZURE_CLIENT_ID` and `AZURE_CLIENT_SECRET`: run `az acr credential show --name agenticparallelismacr` and copy the `username` and `password` fields.
     - `AZURE_RESOURCE_GROUP`: `agentic-parallelism-rg`.
     - `OPENAI_API_KEY`, `TAVILY_API_KEY`, `SENTRY_DSN`: copy from your provider dashboards.
3. Save each secret. They will be available to all workflow runs via `${{ secrets.<NAME> }}`.

**Do not** commit any of these values to the repository.
