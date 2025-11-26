# Makefile for agentic-parallelism deployment workflow

# -------------------------------------------------
# Environment setup
# -------------------------------------------------
env-setup:
	cp apps/parallel_tool_use/.env.example apps/parallel_tool_use/.env

# Install Python dependencies (including sentry-sdk)
install-deps:
	pip install -r apps/parallel_tool_use/requirements.txt

# -------------------------------------------------
# Testing
# -------------------------------------------------
test-unit:
	pytest apps/parallel_tool_use/tests/test_unit.py -v

test-e2e:
	pytest apps/parallel_tool_use/tests/test_e2e.py -v

# -------------------------------------------------
# Azure CLI helpers
# -------------------------------------------------
azure-login:
	az login

azure-rg-create:
	az group create --name agentic-parallelism-rg --location westus

azure-rg-exists:
	az group exists --name agentic-parallelism-rg

azure-set-subscription:
	az account set --subscription <SUBSCRIPTION_ID>

azure-register-provider:
	az provider register --namespace Microsoft.ContainerRegistry

azure-verify-provider:
	az provider show --namespace Microsoft.ContainerRegistry --query "registrationState" -o tsv

# -------------------------------------------------
# Azure Container Registry (ACR)
# -------------------------------------------------
acr-create:
	az acr create \
	  --resource-group agentic-parallelism-rg \
	  --name agenticparallelismacr \
	  --sku Basic \
	  --admin-enabled true

acr-login:
	az acr login --name agenticparallelismacr

acr-login-server:
	az acr show --name agenticparallelismacr --query loginServer --output tsv

acr-credentials:
	az acr credential show --name agenticparallelismacr

# -------------------------------------------------
# Service Principal for GitHub Actions
# -------------------------------------------------
sp-create:
	@echo "Creating Service Principal..."
	@echo "NOTE: Replace <SUBSCRIPTION_ID> with your actual subscription ID in the command below if running manually."
	az ad sp create-for-rbac \
	  --name "github-actions-agentic" \
	  --role contributor \
	  --scopes /subscriptions/$(shell az account show --query id -o tsv)/resourceGroups/agentic-parallelism-rg \
	  --sdk-auth \
	  --output json

# -------------------------------------------------
# Export ACR JSON
# -------------------------------------------------
export-acr-json:
	az acr show --name agenticparallelismacr --output json > acr-info.json

view-acr-json:
	cat acr-info.json

# -------------------------------------------------
# Workflow Monitor (Background Process)
# -------------------------------------------------
monitor-start:
	@if [ -f monitor.pid ]; then \
		echo "Monitor is already running (PID: $$(cat monitor.pid))"; \
	else \
		nohup python3 scripts/monitor_workflows.py > monitor.log 2>&1 & echo $$! > monitor.pid; \
		echo "Monitor started in background (PID: $$(cat monitor.pid))"; \
		echo "Logs are being written to monitor.log"; \
	fi

monitor-stop:
	@if [ -f monitor.pid ]; then \
		kill $$(cat monitor.pid) && rm monitor.pid; \
		echo "Monitor stopped"; \
	else \
		echo "Monitor is not running"; \
	fi

monitor-status:
	@if [ -f monitor.pid ]; then \
		echo "Monitor is running (PID: $$(cat monitor.pid))"; \
		echo "--- Recent Logs ---"; \
		tail -n 5 monitor.log; \
	else \
		echo "Monitor is not running"; \
	fi

monitor-restart: monitor-stop monitor-start

.PHONY: env-setup install-deps test-unit test-e2e azure-login azure-rg-create azure-rg-exists azure-set-subscription azure-register-provider azure-verify-provider acr-create acr-login acr-login-server acr-credentials sp-create export-acr-json view-acr-json monitor-start monitor-stop monitor-status monitor-restart
