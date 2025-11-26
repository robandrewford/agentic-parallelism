#!/bin/bash
# Deploy applications to Azure Container Apps - Production Environment

set -e

echo "🚀 Deploying to Azure Container Apps (Production)..."
echo "⚠️  WARNING: This will deploy to PRODUCTION!"
read -p "Are you sure you want to continue? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ Deployment cancelled."
    exit 0
fi

# Get version tag
if [ -z "$1" ]; then
    echo "❌ Error: Version tag required"
    echo "Usage: ./deploy-production.sh v1.0.0"
    exit 1
fi

VERSION=$1
echo "📌 Deploying version: $VERSION"

# Load environment variables
if [ -f .env.production ]; then
    export $(cat .env.production | grep -v '^#' | xargs)
else
    echo "⚠️  .env.production file not found. Using environment variables."
fi

# Check required variables
required_vars=("AZURE_RESOURCE_GROUP" "ACR_NAME" "SUBSCRIPTION_ID")
for var in "${required_vars[@]}"; do
    if [ -z "${!var}" ]; then
        echo "❌ Error: $var is not set"
        exit 1
    fi
done

# Login to Azure
echo "🔐 Checking Azure login status..."
az account show > /dev/null 2>&1 || az login

# Set subscription
echo "📋 Setting subscription to $SUBSCRIPTION_ID..."
az account set --subscription "$SUBSCRIPTION_ID"

# Deploy App 01
echo "📦 Deploying App 01 (Parallel Tool Use) to production..."
az containerapp update \
    --name parallel-tool-use-production \
    --resource-group "$AZURE_RESOURCE_GROUP" \
    --image "${ACR_NAME}.azurecr.io/01_parallel_tool_use:${VERSION}" \
    --set-env-vars \
        ENVIRONMENT=production \
        VERSION="$VERSION" \
        LLM_PROVIDER=openai \
        SENTRY_ENVIRONMENT=production

# Add more apps as they are refactored

echo "✅ Deployment to production complete!"
echo "🔍 Verifying deployments..."

# Verify App 01
APP_URL=$(az containerapp show \
    --name parallel-tool-use-production \
    --resource-group "$AZURE_RESOURCE_GROUP" \
    --query properties.configuration.ingress.fqdn -o tsv)

echo "🌐 App 01 URL: https://${APP_URL}"
echo "🏥 Checking health endpoint..."

sleep 30  # Wait for deployment to stabilize

if curl -f "https://${APP_URL}/health"; then
    echo "✅ App 01 is healthy!"
else
    echo "❌ App 01 health check failed!"
    echo "⚠️  Consider rolling back!"
    exit 1
fi

echo ""
echo "🎉 Production deployment verified successfully!"
echo "📝 Don't forget to create a Sentry release for version: $VERSION"
