# Revised Architecture: Aligned with SOLO Automation

## 🎯 Key Changes Based on SOLO_AUTOMATION.md

### Architecture Decisions - Updated Recommendations

| Decision | Original | **REVISED (SOLO-aligned)** | Rationale |
|----------|----------|---------------------------|-----------|
| **Deployment Target** | Kubernetes | **Azure Container Apps** | Matches your existing SOLO infrastructure |
| **CI/CD** | Generic GitHub Actions | **GitHub Actions → Azure Container Apps** | Leverage existing pipeline patterns |
| **Observability** | Prometheus/Grafana | **Sentry + Health Checks** | Aligns with your Sentry setup |
| **Environments** | Dev/Staging/Prod | **Local → Staging → Production** | Matches your 3-env philosophy |
| **Testing** | Generic pytest | **Unit tests + Critical E2E** | Follow your testing strategy |
| **Work Management** | Not specified | **Linear integration** | Track refactoring in Linear |

---

## 🏗️ Revised Architecture

### Updated Directory Structure

```
agentic-parallelism/
├── apps/                          # 14 standalone apps
│   ├── 01_parallel_tool_use/
│   │   ├── app.py                # FastAPI application
│   │   ├── config.py
│   │   ├── Dockerfile
│   │   ├── requirements.txt
│   │   ├── .env.example         # ✨ NEW: Environment template
│   │   ├── tests/
│   │   │   ├── test_unit.py     # Unit tests
│   │   │   └── test_e2e.py      # ✨ NEW: E2E tests for critical paths
│   │   └── README.md
│   └── ... (all 14)
│
├── shared/                        # Shared modules
│   ├── llm/
│   ├── tools/
│   ├── agents/
│   ├── observability/
│   │   ├── sentry.py           # ✨ NEW: Sentry integration
│   │   └── health.py           # ✨ NEW: Health check utilities
│   └── config/
│
├── .github/
│   └── workflows/
│       ├── ci.yml               # ✨ REVISED: Lint + unit tests on push/PR
│       ├── cd-staging.yml       # ✨ NEW: Deploy to Azure staging on main
│       ├── cd-production.yml    # ✨ NEW: Deploy to Azure prod on tag
│       ├── health-check.yml     # ✨ NEW: Uptime monitoring
│       └── sentry-test-gen.yml  # ✨ NEW: Auto-generate tests from Sentry issues
│
├── infrastructure/               # ✨ REVISED: Azure instead of K8s
│   ├── azure/
│   │   ├── container-apps/
│   │   │   ├── staging/
│   │   │   │   └── app-01.yaml  # Azure Container App manifest
│   │   │   └── production/
│   │   │       └── app-01.yaml
│   │   └── setup.sh            # Azure Container Apps setup script
│   ├── docker-compose.yml       # Local development
│   └── scripts/
│       ├── deploy-staging.sh
│       └── deploy-production.sh
│
├── .linear/                      # ✨ NEW: Linear issue templates
│   └── templates/
│       ├── refactoring-task.md
│       └── bug-report.md
│
├── sentry.properties             # ✨ NEW: Sentry configuration
└── .vscode/                      # ✨ NEW: VS Code AI workflows
    └── tasks.json               # Tasks for AI-assisted development
```

---

## 🔄 Revised CI/CD Pipeline

### GitHub Actions → Azure Container Apps

#### 1. **CI Pipeline** (on push/PR)

```yaml
# .github/workflows/ci.yml
name: CI - Lint and Test

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  lint-and-test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        app: [01_parallel_tool_use, 02_parallel_hypothesis, ...] # All 14

    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r apps/${{ matrix.app }}/requirements.txt
          pip install pytest pytest-cov ruff
      
      - name: Lint with ruff
        run: |
          ruff check apps/${{ matrix.app }}
      
      - name: Run unit tests
        run: |
          pytest apps/${{ matrix.app }}/tests/test_unit.py --cov
      
      - name: Upload coverage to Codecov (optional)
        uses: codecov/codecov-action@v3
        if: matrix.app == '01_parallel_tool_use'  # Only for pilot app
```

#### 2. **CD Pipeline - Staging** (on merge to main)

```yaml
# .github/workflows/cd-staging.yml
name: CD - Deploy to Azure Staging

on:
  push:
    branches: [main]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    strategy:
      matrix:
        app: [01_parallel_tool_use]  # Start with pilot, expand later

    steps:
      - uses: actions/checkout@v3
      
      - name: Build Docker image
        run: |
          docker build -t ${{ matrix.app }}:${{ github.sha }} \
            -f apps/${{ matrix.app }}/Dockerfile .
      
      - name: Push to Azure Container Registry
        uses: azure/docker-login@v1
        with:
          login-server: ${{ secrets.AZURE_REGISTRY }}
          username: ${{ secrets.AZURE_CLIENT_ID }}
          password: ${{ secrets.AZURE_CLIENT_SECRET }}
      
      - name: Tag and push
        run: |
          docker tag ${{ matrix.app }}:${{ github.sha }} \
            ${{ secrets.AZURE_REGISTRY }}/${{ matrix.app }}:staging
          docker push ${{ secrets.AZURE_REGISTRY }}/${{ matrix.app }}:staging
      
      - name: Deploy to Azure Container Apps (Staging)
        uses: azure/container-apps-deploy-action@v1
        with:
          resource-group: agentic-parallelism-rg
          container-app-name: ${{ matrix.app }}-staging
          image: ${{ secrets.AZURE_REGISTRY }}/${{ matrix.app }}:staging
          environment-variables: |
            LLM_PROVIDER=openai
            SENTRY_ENVIRONMENT=staging
```

#### 3. **CD Pipeline - Production** (on git tag)

```yaml
# .github/workflows/cd-production.yml
name: CD - Deploy to Azure Production

on:
  push:
    tags:
      - 'v*.*.*'  # Semantic versioning tags

jobs:
  deploy-production:
    runs-on: ubuntu-latest
    environment: production
    # ... similar to staging but with production targets
```

#### 4. **Health Check Monitoring**

```yaml
# .github/workflows/health-check.yml
name: Uptime Health Check

on:
  schedule:
    - cron: '*/15 * * * *'  # Every 15 minutes

jobs:
  health-check:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        app: 
          - name: parallel-tool-use
            url: https://parallel-tool-use.azurecontainerapps.io/health
          # Add all 14 apps

    steps:
      - name: Check health endpoint
        run: |
          response=$(curl -s -o /dev/null -w "%{http_code}" ${{ matrix.app.url }})
          if [ $response != "200" ]; then
            echo "Health check failed for ${{ matrix.app.name }}"
            exit 1
          fi
      
      - name: Notify on failure (Sentry)
        if: failure()
        uses: getsentry/action-release@v1
        with:
          environment: production
          version: ${{ github.sha }}
```

---

## 🐛 Sentry Integration

### Setup in each app

```python
# apps/01_parallel_tool_use/app.py

import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration
from shared.config import load_config

config = load_config()

# Initialize Sentry
if config.sentry_dsn:
    sentry_sdk.init(
        dsn=config.sentry_dsn,
        environment=config.environment,  # staging/production
        traces_sample_rate=0.1,  # 10% for performance monitoring
        integrations=[FastApiIntegration()],
        release=config.version,  # From git tag
    )

# Your FastAPI app
app = FastAPI()

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": config.version,
        "environment": config.environment
    }

# Sentry will auto-capture exceptions
```

### Auto-generate tests from Sentry issues

```yaml
# .github/workflows/sentry-test-gen.yml
name: Generate Tests from Sentry Issues

on:
  issues:
    types: [labeled]

jobs:
  generate-test:
    if: contains(github.event.issue.labels.*.name, 'needs-test')
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Extract Sentry stack trace
        id: sentry
        run: |
          # Parse issue body for Sentry URL
          # Fetch stack trace via Sentry API
          # Store in $GITHUB_OUTPUT
      
      - name: Generate test with AI
        uses: openai/chatgpt-action@v1  # Hypothetical action
        with:
          prompt: |
            Based on this stack trace, write a pytest test that reproduces the issue:
            ${{ steps.sentry.outputs.stacktrace }}
          output_file: test_generated.py
      
      - name: Create PR with generated test
        uses: peter-evans/create-pull-request@v5
        with:
          title: "Test for Sentry issue #${{ github.event.issue.number }}"
          body: "Auto-generated test from Sentry issue"
          branch: test/sentry-${{ github.event.issue.number }}
```

---

## ☁️ Azure Container Apps Configuration

### Staging Environment

```yaml
# infrastructure/azure/container-apps/staging/app-01.yaml

properties:
  environmentId: /subscriptions/{sub}/resourceGroups/agentic-parallelism-rg/providers/Microsoft.App/managedEnvironments/staging
  configuration:
    ingress:
      external: true
      targetPort: 8000
      traffic:
        - latestRevision: true
          weight: 100
    secrets:
      - name: openai-api-key
        value: ${OPENAI_API_KEY}
      - name: sentry-dsn
        value: ${SENTRY_DSN}
    registries:
      - server: ${ACR_NAME}.azurecr.io
        username: ${ACR_USERNAME}
        passwordSecretRef: acr-password
  template:
    containers:
      - name: parallel-tool-use
        image: ${ACR_NAME}.azurecr.io/01_parallel_tool_use:staging
        resources:
          cpu: 0.25  # Small for staging
          memory: 0.5Gi
        env:
          - name: LLM_PROVIDER
            value: openai
          - name: OPENAI_API_KEY
            secretRef: openai-api-key
          - name: SENTRY_DSN
            secretRef: sentry-dsn
          - name: ENVIRONMENT
            value: staging
    scale:
      minReplicas: 1
      maxReplicas: 2  # Small scale for staging
```

### Production Environment

```yaml
# infrastructure/azure/container-apps/production/app-01.yaml
# Similar to staging but with:
# - More resources (cpu: 0.5, memory: 1Gi)
# - Higher scale (minReplicas: 2, maxReplicas: 10)
# - Production secrets
```

---

## 🧪 Revised Testing Strategy

### Unit Tests (every push)

```python
# apps/01_parallel_tool_use/tests/test_unit.py

import pytest
from unittest.mock import Mock, patch
from app import create_agent, run_query

def test_agent_creation():
    """Test agent can be created with mock LLM."""
    with patch('shared.llm.LLMFactory.create') as mock_llm:
        agent = create_agent()
        assert agent is not None

def test_query_processing():
    """Test query processing logic."""
    with patch('shared.llm.LLMFactory.create'):
        result = run_query("What is NVDA stock price?")
        assert "result" in result
```

### E2E Tests (critical paths only)

```python
# apps/01_parallel_tool_use/tests/test_e2e.py

import pytest
import requests
import os

@pytest.mark.e2e
def test_health_endpoint():
    """Critical: Health check must work for uptime monitoring."""
    base_url = os.getenv("APP_URL", "http://localhost:8000")
    response = requests.get(f"{base_url}/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

@pytest.mark.e2e
def test_agent_execution_with_real_apis():
    """Critical: Agent can execute with real LLM and tools."""
    # This uses real OpenAI API (run sparingly!)
    base_url = os.getenv("APP_URL", "http://localhost:8000")
    response = requests.post(
        f"{base_url}/run",
        json={"query": "What is NVDA stock price?"}
    )
    assert response.status_code == 200
    assert "result" in response.json()
```

---

## 📋 Linear Integration

### Issue Templates

```markdown
# .linear/templates/refactoring-task.md

## App Refactoring: [App ##]

**Category**: [Core Agents / Multi-Agent / Reliability / RAG]

### Tasks
- [ ] Extract notebook logic to `app.py`
- [ ] Create Dockerfile
- [ ] Write unit tests
- [ ] Write E2E test for critical path
- [ ] Configure Azure Container App
- [ ] Deploy to staging
- [ ] Verify in staging
- [ ] Deploy to production

### Acceptance Criteria
- Unit tests pass in CI
- E2E test passes locally
- Health endpoint returns 200
- Deployed to staging successfully
- No Sentry errors in first 24h
```

### Workflow
1. Linear AI helps break down each app refactoring
2. Track progress per app (14 issues total)
3. Link to PRs automatically
4. Close issues on production deployment

---

## 🎓 Educational Value (Maintained!)

### For Students:
1. **Local Development**: Docker Compose
2. **CI/CD Basics**: GitHub Actions patterns
3. **Cloud Deployment**: Azure Container Apps (simpler than K8s)
4. **Observability**: Sentry integration
5. **Testing**: Unit + E2E strategies

### Progression:
- **Week 1**: Run locally with Docker Compose
- **Week 2**: Understand GitHub Actions CI
- **Week 3**: Deploy to Azure staging
- **Week 4**: Production deployment patterns

**Benefits over K8s**:
- ✅ Simpler than Kubernetes (lower barrier)
- ✅ Matches real-world solo-dev practices
- ✅ Serverless pricing (cheaper for demos)
- ✅ Faster to production

---

## 🚀 Revised Migration Plan

### Phase 1: Pilot (2 weeks)
- **App 01** (Parallel Tool Use)
- Build shared modules
- Set up Azure Container Apps
- Configure GitHub Actions
- Deploy to staging

### Phase 2: Scale (2-3 weeks)
- Apps 02-05 (Core + Multi-Agent patterns)
- Refine templates
- Add Sentry integration
- Production deployments

### Phase 3: Complete (2-3 weeks)
- Apps 06-14 (Reliability + RAG patterns)
- Full CI/CD for all apps
- Health monitoring
- Documentation

### Phase 4: Enhance (1-2 weeks)
- Linear integration
- AI-assisted test generation
- Performance optimization
- Student documentation

---

## 📊 SOLO Alignment Summary

| SOLO Component | Integration | Benefit |
|----------------|-------------|---------|
| **Linear** | Issue templates, AI task breakdown | Track refactoring progress |
| **GitHub Actions** | CI/CD pipelines | Automated testing & deployment |
| **Azure Container Apps** | Staging + production | Matches existing infra |
| **Sentry** | Error tracking + test generation | Production monitoring |
| **VS Code** | AI-assisted development | Speed up refactoring |
| **Docker Compose** | Local development | Consistent local environment |

---

## ✅ Updated Recommendations

1. **Target Azure Container Apps** instead of K8s
   - Lower complexity
   - Matches your SOLO stack
   - Better for solo-dev teaching

2. **Use Sentry from day one**
   - Integrated in shared modules
   - Auto-test generation workflow
   - Production-ready observability

3. **3-environment model**
   - Local (Docker Compose)
   - Staging (Azure Container Apps)
   - Production (Azure Container Apps)

4. **Small but critical E2E suite**
   - Health endpoints (for uptime)
   - Agent execution (core functionality)
   - Nothing else (keep it lean)

5. **Linear for project management**
   - Track refactoring per app
   - Use Linear AI for task breakdown
   - Link to GitHub PRs

---

## 🤔 Final Questions

1. **Azure subscription**: Do you have one set up, or should I include setup instructions?

2. **Sentry account**: Existing one or new project?

3. **Linear workspace**: Should I create issue templates for all 14 apps?

4. **VS Code tasks**: Should I create AI-assisted workflows for common refactoring patterns?

5. **Start date**: When would you like to kick off Phase 1?

---

**This revised architecture fully aligns with your SOLO automation while maintaining educational value. Ready to proceed?** 🚀
