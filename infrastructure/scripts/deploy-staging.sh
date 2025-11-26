#!/bin/bash
# Deploy applications to Azure Container Apps - Staging Environment

set -e

echo "🚀 Deploying to Azure Container Apps (Staging)..."

# Load environment variables
if [ -f .env.staging ]; then
    export $(cat .env.staging | grep -v '^#' | xargs)
else
    echo "⚠️  .env.staging file not found. Using environment variables."
fi

# Check required variables
required_vars=("AZURE_RESOURCE_GROUP" "ACR_NAME" "SUBSCRIPTION_ID")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var is not set"
        exit 1
    fi
done

# Login to Azure (if not already logged in)
echo "🔐 Checking Azure login status..."
az account show > /dev/null 2>&1 || az login

# Set subscription
echo "📋 Setting subscription to $SUBSCRIPTION_ID..."
az account set --subscription "$SUBSCRIPTION_ID"

# Deploy App 01
echo "📦 Deploying App 01 (Parallel Tool Use) to staging..."
az containerapp update \
    --name parallel-tool-use-staging \
    --resource-group "$AZURE_RESOURCE_GROUP" \
    --image "${ACR_NAME}.azurecr.io/01_parallel_tool_use:staging-latest" \
    --set-env-vars \
        ENVIRONMENT=staging \
        LLM_PROVIDER=openai \
        SENTRY_ENVIRONMENT=staging

# Add more apps as they are refactored
# echo "📦 Deploying App 02 (Parallel Hypothesis) to staging..."
# az containerapp update \
#     --name parallel-hypothesis-staging \
#     --resource-group "$AZURE_RESOURCE_GROUP" \
#     --image "${ACR_NAME}.azurecr.io/02_parallel_hypothesis:staging-latest" \
#     ...

echo "✅ Deployment to staging complete!"
echo "🔍 Verifying deployments..."

# Verify App 01
APP_URL=$(az containerapp show \
    --name parallel-tool-use-staging \
    --resource-group "$AZURE_RESOURCE_GROUP" \
    --query properties.configuration.ingress.fqdn -o tsv)

echo "🌐 App 01 URL: https://${APP_URL}"
echo "🏥 Checking health endpoint..."

if curl -f "https://${APP_URL}/health"; then
    echo "✅ App 01 is healthy!"
else
    echo "❌ App 01 health check failed!"
    exit 1
fi

echo ""
echo "🎉 All deployments verified successfully!"
