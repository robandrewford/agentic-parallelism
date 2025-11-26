This isa **GitHub repo template** strategy that bakes in a **single-dev CI/CD pipeline** plus the surrounding tooling (Linear, Azure Container Apps, Sentry, VS Code AI workflows, etc.) so you I clone → tweak → ship every new side-project.

**Work Management**
- Linear
    - Lightweight, insanely fast, great for solo devs.
    - Linear AI helps draft issue descriptions, break down tasks, summarize comment threads.

**Source control & CI/CD**
- **GitHub Pro** for repos. 
- **GitHub Actions** for CI/CD:
    - On every push or PR: run linting and unit tests.
    - On merge to main: build Docker image, push to ECR, deploy to ECS.

**Deployment & environments**
- **Azure Container Apps**:
    - One small service for **staging**.
    - One slightly larger service for **production**.
- Local dev with Docker Compose where possible.

You don’t need four environments. A realistic setup is:
- Local dev.
- One non‑prod environment (staging/preview).
- Production.

**Testing**
- Unit tests for core logic.
- A **small but critical** E2E suite:
    - Sign‑up / login.
    - The flows that touch money or important data.
- Use **VS Code** to:
    - Generate tests for new code.
    - Propose tests when you fix bugs (“write a test that reproduces this issue”).

**Observability**
- **Sentry** for error tracking (free or low tier).
- A basic uptime check with a GitHub Action that pings a health endpoint.

**AI layers**
- **VS Code** as your main AI dev environment:
    - Code generation, refactoring, test generation.
- A small script that:
    - When you label a Sentry issue “needs‑test”, pulls the stack trace and recent diff.
    - Feeds that into an LLM to propose tests.
    - Opens a PR with those tests for you to review.