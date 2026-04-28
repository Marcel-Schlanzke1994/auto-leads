# SUBAGENTS – Projektkatalog (Auto-Leads)

_Stand: 2026-04-28_

## Überblick

- Integrierte Subagents aus `awesome-codex-subagents`: **136**.
- Zusätzliche projektbezogene Alias-Subagents: **8** (`planner`, `orchestrator`, `database-architect`, `test-engineer`, `ci-cd-specialist`, `documentation-writer`, `performance-optimizer`, `scraper-extractor`).
- Gesamt in `.codex/agents/`: **144**.

## Empfohlene Kern-Agenten für dieses Projekt

- `planner` – empfohlen für Kern-Workflows im Auto-Lead-System.
- `orchestrator` – empfohlen für Kern-Workflows im Auto-Lead-System.
- `backend-developer` – empfohlen für Kern-Workflows im Auto-Lead-System.
- `fullstack-developer` – empfohlen für Kern-Workflows im Auto-Lead-System.
- `frontend-developer` – empfohlen für Kern-Workflows im Auto-Lead-System.
- `api-designer` – empfohlen für Kern-Workflows im Auto-Lead-System.
- `database-architect` – empfohlen für Kern-Workflows im Auto-Lead-System.
- `reviewer` – empfohlen für Kern-Workflows im Auto-Lead-System.
- `security-auditor` – empfohlen für Kern-Workflows im Auto-Lead-System.
- `test-engineer` – empfohlen für Kern-Workflows im Auto-Lead-System.
- `devops-engineer` – empfohlen für Kern-Workflows im Auto-Lead-System.
- `ci-cd-specialist` – empfohlen für Kern-Workflows im Auto-Lead-System.
- `documentation-writer` – empfohlen für Kern-Workflows im Auto-Lead-System.
- `seo-specialist` – empfohlen für Kern-Workflows im Auto-Lead-System.
- `data-engineer` – empfohlen für Kern-Workflows im Auto-Lead-System.
- `scraper-extractor` – empfohlen für Kern-Workflows im Auto-Lead-System.
- `performance-optimizer` – empfohlen für Kern-Workflows im Auto-Lead-System.

## Sicherheitslevel

- **hoch**: `sandbox_mode = "read-only"` (Analyse/Audit/Review).
- **mittel**: `sandbox_mode = "workspace-write"` (kontrollierte Schreibrechte im Repo).
- **niedrig**: agentenspezifisch nur bei riskanten Instruktionen; derzeit keine `danger-full-access`-Agenten übernommen.

## Vollständige Liste der übernommenen Subagents

| Agent | Kurzbeschreibung | Empfohlene Nutzung | Sicherheitslevel | Auto-Lead-Relevanz |
|---|---|---|---|---|
| `accessibility-tester` | Use when a task needs an accessibility audit of UI changes, interaction flows, or component behavior. | Analyse/Review | hoch (`read-only`) | hoch |
| `ad-security-reviewer` | Use when a task needs Active Directory security review across identity boundaries, delegation, GPO exposure, or directory hardening. | Analyse/Review | hoch (`read-only`) | hoch |
| `agent-installer` | Use when a task needs help selecting, copying, or organizing custom agent files from this repository into Codex agent directories. | Analyse/Review | hoch (`read-only`) | mittel |
| `agent-organizer` | Use when the parent agent needs help choosing subagents and dividing a larger task into clean delegated threads. | Analyse/Review | hoch (`read-only`) | mittel |
| `ai-engineer` | Use when a task needs implementation or debugging of model-backed application features, agent flows, or evaluation hooks. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `angular-architect` | Use when a task needs Angular-specific help for component architecture, dependency injection, routing, signals, or enterprise application structure. | Implementierung/Refactor | mittel (`workspace-write`) | hoch |
| `api-designer` | Use when a task needs API contract design, evolution planning, or compatibility review before implementation starts. | Analyse/Review | hoch (`read-only`) | hoch |
| `api-documenter` | Use when a task needs consumer-facing API documentation generated from the real implementation, schema, and examples. | Implementierung/Refactor | mittel (`workspace-write`) | hoch |
| `architect-reviewer` | Use when a task needs architectural review for coupling, system boundaries, long-term maintainability, or design coherence. | Analyse/Review | hoch (`read-only`) | hoch |
| `azure-infra-engineer` | Use when a task needs Azure-specific infrastructure review or implementation across resources, networking, identity, or automation. | Analyse/Review | hoch (`read-only`) | mittel |
| `backend-developer` | Use when a task needs scoped backend implementation or backend bug fixes after the owning path is known. | Implementierung/Refactor | mittel (`workspace-write`) | hoch |
| `blockchain-developer` | Use when a task needs blockchain or Web3 implementation and review across smart-contract integration, wallet flows, or transaction lifecycle handling. | Implementierung/Refactor | mittel (`workspace-write`) | niedrig |
| `browser-debugger` | Use when a task needs browser-based reproduction, UI evidence gathering, or client-side debugging through a browser MCP server. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `build-engineer` | Use when a task needs build-graph debugging, bundling fixes, compiler pipeline work, or CI build stabilization. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `business-analyst` | Use when a task needs requirements clarified, scope normalized, or acceptance criteria extracted from messy inputs before engineering work starts. | Analyse/Review | hoch (`read-only`) | mittel |
| `chaos-engineer` | Use when a task needs resilience analysis for dependency failure, degraded modes, recovery behavior, or controlled fault-injection planning. | Analyse/Review | hoch (`read-only`) | mittel |
| `ci-cd-specialist` | Use for CI/CD pipeline hardening, quality gates, and safe deployment workflow design. | Implementierung/Refactor | mittel (`workspace-write`) | hoch |
| `cli-developer` | Use when a task needs a command-line interface feature, UX review, argument parsing change, or shell-facing workflow improvement. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `cloud-architect` | Use when a task needs cloud architecture review across compute, storage, networking, reliability, or multi-service design. | Analyse/Review | hoch (`read-only`) | hoch |
| `code-mapper` | Use when the parent agent needs a high-confidence map of code paths, ownership boundaries, and execution flow before changes are made. | Analyse/Review | hoch (`read-only`) | mittel |
| `code-reviewer` | Use when a task needs a broader code-health review covering maintainability, design clarity, and risky implementation choices in addition to correctness. | Analyse/Review | hoch (`read-only`) | hoch |
| `competitive-analyst` | Use when a task needs a grounded comparison of tools, products, libraries, or implementation options. | Analyse/Review | hoch (`read-only`) | mittel |
| `compliance-auditor` | Use when a task needs compliance-oriented review of controls, auditability, policy alignment, or evidence gaps in a regulated workflow. | Analyse/Review | hoch (`read-only`) | hoch |
| `content-marketer` | Use when a task needs product-adjacent content strategy or messaging that still has to stay grounded in real technical capabilities. | Analyse/Review | hoch (`read-only`) | mittel |
| `context-manager` | Use when a task needs a compact project context summary that other subagents can rely on before deeper work begins. | Analyse/Review | hoch (`read-only`) | mittel |
| `cpp-pro` | Use when a task needs C++ work involving performance-sensitive code, memory ownership, concurrency, or systems-level integration. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `csharp-developer` | Use when a task needs C# or .NET application work involving services, APIs, async flows, or application architecture. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `customer-success-manager` | Use when a task needs support-pattern synthesis, adoption risk analysis, or customer-facing operational guidance from engineering context. | Analyse/Review | hoch (`read-only`) | mittel |
| `data-analyst` | Use when a task needs data interpretation, metric breakdown, trend explanation, or decision support from existing analytics outputs. | Analyse/Review | hoch (`read-only`) | mittel |
| `data-engineer` | Use when a task needs ETL, ingestion, transformation, warehouse, or data-pipeline implementation and debugging. | Implementierung/Refactor | mittel (`workspace-write`) | hoch |
| `data-researcher` | Use when a task needs source gathering and synthesis around datasets, metrics, data pipelines, or evidence-backed quantitative questions. | Analyse/Review | hoch (`read-only`) | hoch |
| `data-scientist` | Use when a task needs statistical reasoning, experiment interpretation, feature analysis, or model-oriented data exploration. | Analyse/Review | hoch (`read-only`) | mittel |
| `database-administrator` | Use when a task needs operational database administration review for availability, backups, recovery, permissions, or runtime health. | Analyse/Review | hoch (`read-only`) | hoch |
| `database-architect` | Use for schema design, migration strategy, indexing, and query/runtime data modeling decisions. | Analyse/Review | hoch (`read-only`) | hoch |
| `database-optimizer` | Use when a task needs database performance analysis for query plans, schema design, indexing, or data access patterns. | Analyse/Review | hoch (`read-only`) | hoch |
| `debugger` | Use when a task needs deep bug isolation across code paths, stack traces, runtime behavior, or failing tests. | Analyse/Review | hoch (`read-only`) | mittel |
| `dependency-manager` | Use when a task needs dependency upgrades, package graph analysis, version-policy cleanup, or third-party library risk assessment. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `deployment-engineer` | Use when a task needs deployment workflow changes, release strategy updates, or rollout and rollback safety analysis. | Implementierung/Refactor | mittel (`workspace-write`) | hoch |
| `devops-engineer` | Use when a task needs CI, deployment pipeline, release automation, or environment configuration work. | Implementierung/Refactor | mittel (`workspace-write`) | hoch |
| `devops-incident-responder` | Use when a task needs rapid operational triage across CI, deployments, infrastructure automation, and service delivery failures. | Analyse/Review | hoch (`read-only`) | hoch |
| `django-developer` | Use when a task needs Django-specific work across models, views, forms, ORM behavior, or admin and middleware flows. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `docker-expert` | Use when a task needs Dockerfile review, image optimization, multi-stage build fixes, or container runtime debugging. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `docs-researcher` | Use when a task needs documentation-backed verification of APIs, version-specific behavior, or framework options. | Analyse/Review | hoch (`read-only`) | hoch |
| `documentation-engineer` | Use when a task needs technical documentation that must stay faithful to current code, tooling, and operator workflows. | Implementierung/Refactor | mittel (`workspace-write`) | hoch |
| `documentation-writer` | Use for architecture, operations, and developer documentation updates tied to code and workflow changes. | Implementierung/Refactor | mittel (`workspace-write`) | hoch |
| `dotnet-core-expert` | Use when a task needs modern .NET and ASP.NET Core expertise for APIs, hosting, middleware, or cross-platform application behavior. | Implementierung/Refactor | mittel (`workspace-write`) | niedrig |
| `dotnet-framework-4.8-expert` | Use when a task needs .NET Framework 4.8 expertise for legacy enterprise applications, compatibility constraints, or Windows-bound integrations. | Implementierung/Refactor | mittel (`workspace-write`) | niedrig |
| `dx-optimizer` | Use when a task needs developer-experience improvements in setup time, local workflows, feedback loops, or day-to-day tooling friction. | Analyse/Review | hoch (`read-only`) | mittel |
| `electron-pro` | Use when a task needs Electron-specific implementation or debugging across main/renderer/preload boundaries, packaging, and desktop runtime behavior. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `elixir-expert` | Use when a task needs Elixir and OTP expertise for processes, supervision, fault tolerance, or Phoenix application behavior. | Implementierung/Refactor | mittel (`workspace-write`) | niedrig |
| `embedded-systems` | Use when a task needs embedded or hardware-adjacent work involving device constraints, firmware boundaries, timing, or low-level integration. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `erlang-expert` | Use when a task needs Erlang/OTP and rebar3 expertise for BEAM processes, testing, releases, upgrades, or distributed runtime behavior. | Implementierung/Refactor | mittel (`workspace-write`) | niedrig |
| `error-coordinator` | Use when multiple errors or symptoms need to be grouped, prioritized, and assigned to the right debugging or review agents. | Analyse/Review | hoch (`read-only`) | hoch |
| `error-detective` | Use when a task needs log, exception, or stack-trace analysis to identify the most probable failure source quickly. | Analyse/Review | hoch (`read-only`) | mittel |
| `fintech-engineer` | Use when a task needs financial systems engineering across ledgers, reconciliation, transfers, settlement, or compliance-sensitive transactional flows. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `flutter-expert` | Use when a task needs Flutter expertise for widget behavior, state management, rendering issues, or mobile cross-platform implementation. | Implementierung/Refactor | mittel (`workspace-write`) | niedrig |
| `frontend-developer` | Use when a task needs scoped frontend implementation or UI bug fixes with production-level behavior and quality. | Implementierung/Refactor | mittel (`workspace-write`) | hoch |
| `fullstack-developer` | Use when one bounded feature or bug spans frontend and backend and a single worker should own the entire path. | Implementierung/Refactor | mittel (`workspace-write`) | hoch |
| `game-developer` | Use when a task needs game-specific implementation or debugging involving gameplay systems, rendering loops, asset flow, or player-state behavior. | Implementierung/Refactor | mittel (`workspace-write`) | niedrig |
| `git-workflow-manager` | Use when a task needs help with branching strategy, merge flow, release branching, or repository collaboration conventions. | Analyse/Review | hoch (`read-only`) | hoch |
| `golang-pro` | Use when a task needs Go expertise for concurrency, service implementation, interfaces, tooling, or performance-sensitive backend paths. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `graphql-architect` | Use when a task needs GraphQL schema evolution, resolver architecture, federation design, or distributed graph performance/security review. | Analyse/Review | hoch (`read-only`) | hoch |
| `incident-responder` | Use when a task needs broad production incident triage, containment planning, or evidence-driven root cause analysis. | Analyse/Review | hoch (`read-only`) | mittel |
| `iot-engineer` | Use when a task needs IoT system work involving devices, telemetry, edge communication, or cloud-device coordination. | Implementierung/Refactor | mittel (`workspace-write`) | niedrig |
| `it-ops-orchestrator` | Use when a task needs coordinated operational planning across infrastructure, incident response, identity, endpoint, and admin workflows. | Analyse/Review | hoch (`read-only`) | hoch |
| `java-architect` | Use when a task needs Java application or service architecture help across framework boundaries, JVM behavior, or large codebase structure. | Implementierung/Refactor | mittel (`workspace-write`) | hoch |
| `javascript-pro` | Use when a task needs JavaScript-focused work for runtime behavior, browser or Node execution, or application-level code that is not TypeScript-led. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `knowledge-synthesizer` | Use when multiple agents have returned findings and the parent agent needs a distilled, non-redundant synthesis. | Analyse/Review | hoch (`read-only`) | mittel |
| `kotlin-specialist` | Use when a task needs Kotlin expertise for JVM applications, Android code, coroutines, or modern strongly typed service logic. | Implementierung/Refactor | mittel (`workspace-write`) | niedrig |
| `kubernetes-specialist` | Use when a task needs Kubernetes manifest review, rollout safety analysis, or cluster workload debugging. | Analyse/Review | hoch (`read-only`) | mittel |
| `laravel-specialist` | Use when a task needs Laravel-specific work across routing, Eloquent, queues, validation, or application structure. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `legacy-modernizer` | Use when a task needs a modernization path for older code, frameworks, or architecture without losing behavioral safety. | Analyse/Review | hoch (`read-only`) | mittel |
| `legal-advisor` | Use when a task needs legal-risk spotting in product or engineering behavior, especially around terms, data handling, or externally visible commitments. | Analyse/Review | hoch (`read-only`) | mittel |
| `llm-architect` | Use when a task needs architecture review for prompts, tool use, retrieval, evaluation, or multi-step LLM workflows. | Analyse/Review | hoch (`read-only`) | hoch |
| `m365-admin` | Use when a task needs Microsoft 365 administration help across Exchange Online, Teams, SharePoint, identity, or tenant-level automation. | Analyse/Review | hoch (`read-only`) | niedrig |
| `machine-learning-engineer` | Use when a task needs ML system implementation work across training pipelines, feature flow, model serving, or inference integration. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `market-researcher` | Use when a task needs market landscape, positioning, or demand-side research tied to a technical product or category. | Analyse/Review | hoch (`read-only`) | hoch |
| `mcp-developer` | Use when a task needs work on MCP servers, MCP clients, tool wiring, or protocol-aware integrations. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `microservices-architect` | Use when a task needs service-boundary design, inter-service contract review, or distributed-system architecture decisions. | Analyse/Review | hoch (`read-only`) | hoch |
| `ml-engineer` | Use when a task needs practical machine learning implementation across feature engineering, inference wiring, and model-backed application logic. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `mlops-engineer` | Use when a task needs model deployment, registry, pipeline, monitoring, or environment orchestration for machine learning systems. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `mobile-app-developer` | Use when a task needs app-level mobile product work across screens, state, API integration, and release-sensitive mobile behavior. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `mobile-developer` | Use when a task needs mobile implementation or debugging across app lifecycle, API integration, and device/platform-specific UX constraints. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `multi-agent-coordinator` | Use when a task needs a concrete multi-agent plan with clear role separation, dependencies, and result integration. | Analyse/Review | hoch (`read-only`) | hoch |
| `network-engineer` | Use when a task needs network-path analysis, service connectivity debugging, load-balancer review, or infrastructure network design input. | Analyse/Review | hoch (`read-only`) | mittel |
| `nextjs-developer` | Use when a task needs Next.js-specific work across routing, rendering modes, server actions, data fetching, or deployment-sensitive frontend behavior. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `nlp-engineer` | Use when a task needs NLP-specific implementation or analysis involving text processing, embeddings, ranking, or language-model-adjacent pipelines. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `orchestrator` | Use for multi-agent delegation strategy, conflict-free sequencing, and integration checkpoints. | Analyse/Review | hoch (`read-only`) | hoch |
| `payment-integration` | Use when a task needs payment-flow review or implementation for checkout, idempotency, webhooks, retries, or settlement state handling. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `penetration-tester` | Use when a task needs adversarial review of an application path for exploitability, abuse cases, or practical attack surface analysis. | Analyse/Review | hoch (`read-only`) | hoch |
| `performance-engineer` | Use when a task needs performance investigation for slow requests, hot paths, rendering regressions, or scalability bottlenecks. | Analyse/Review | hoch (`read-only`) | hoch |
| `performance-monitor` | Use when a task needs ongoing performance-signal interpretation across build, runtime, or operational metrics before deeper optimization starts. | Analyse/Review | hoch (`read-only`) | hoch |
| `performance-optimizer` | Use for profiling-guided performance improvements and bottleneck mitigation across app, data, and pipelines. | Analyse/Review | hoch (`read-only`) | hoch |
| `php-pro` | Use when a task needs PHP expertise for application logic, framework integration, runtime debugging, or server-side code evolution. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `planner` | Use for feature planning, milestone definition, dependency mapping, and ExecPlan updates before implementation. | Analyse/Review | hoch (`read-only`) | hoch |
| `platform-engineer` | Use when a task needs internal platform, golden-path, or self-service infrastructure design for developers. | Analyse/Review | hoch (`read-only`) | mittel |
| `postgres-pro` | Use when a task needs PostgreSQL-specific expertise for schema design, performance behavior, locking, or operational database features. | Analyse/Review | hoch (`read-only`) | mittel |
| `powershell-5.1-expert` | Use when a task needs Windows PowerShell 5.1 expertise for legacy automation, full .NET Framework interop, or Windows administration scripts. | Implementierung/Refactor | mittel (`workspace-write`) | niedrig |
| `powershell-7-expert` | Use when a task needs modern PowerShell 7 expertise for cross-platform automation, scripting, or .NET-based operational tooling. | Implementierung/Refactor | mittel (`workspace-write`) | niedrig |
| `powershell-module-architect` | Use when a task needs PowerShell module structure, command design, packaging, or profile architecture work. | Implementierung/Refactor | mittel (`workspace-write`) | niedrig |
| `powershell-security-hardening` | Use when a task needs PowerShell-focused hardening across script safety, admin automation, execution controls, or Windows security posture. | Analyse/Review | hoch (`read-only`) | niedrig |
| `powershell-ui-architect` | Use when a task needs PowerShell-based UI work for terminals, forms, WPF, or admin-oriented interactive tooling. | Implementierung/Refactor | mittel (`workspace-write`) | niedrig |
| `product-manager` | Use when a task needs product framing, prioritization, or feature-shaping based on engineering reality and user impact. | Analyse/Review | hoch (`read-only`) | mittel |
| `project-manager` | Use when a task needs dependency mapping, milestone planning, sequencing, or delivery-risk coordination across multiple workstreams. | Analyse/Review | hoch (`read-only`) | mittel |
| `prompt-engineer` | Use when a task needs prompt revision, instruction design, eval-oriented prompt comparison, or prompt-output contract tightening. | Analyse/Review | hoch (`read-only`) | mittel |
| `python-pro` | Use when a task needs a Python-focused subagent for runtime behavior, packaging, typing, testing, or framework-adjacent implementation. | Implementierung/Refactor | mittel (`workspace-write`) | hoch |
| `qa-expert` | Use when a task needs test strategy, acceptance coverage planning, or risk-based QA guidance for a feature or release. | Analyse/Review | hoch (`read-only`) | hoch |
| `quant-analyst` | Use when a task needs quantitative analysis of models, strategies, simulations, or numeric decision logic. | Analyse/Review | hoch (`read-only`) | mittel |
| `rails-expert` | Use when a task needs Ruby on Rails expertise for models, controllers, jobs, callbacks, or convention-driven application changes. | Implementierung/Refactor | mittel (`workspace-write`) | niedrig |
| `react-specialist` | Use when a task needs a React-focused agent for component behavior, state flow, rendering bugs, or modern React patterns. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `refactoring-specialist` | Use when a task needs a low-risk structural refactor that preserves behavior while improving readability, modularity, or maintainability. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `research-analyst` | Use when a task needs a structured investigation of a technical topic, implementation approach, or design question. | Analyse/Review | hoch (`read-only`) | hoch |
| `reviewer` | Use when a task needs PR-style review focused on correctness, security, behavior regressions, and missing tests. | Analyse/Review | hoch (`read-only`) | hoch |
| `risk-manager` | Use when a task needs explicit risk analysis for product, operational, financial, or architectural decisions. | Analyse/Review | hoch (`read-only`) | mittel |
| `rust-engineer` | Use when a task needs Rust expertise for ownership-heavy systems code, async runtime behavior, or performance-sensitive implementation. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `sales-engineer` | Use when a task needs technically accurate solution positioning, customer-question handling, or implementation tradeoff explanation for pre-sales contexts. | Analyse/Review | hoch (`read-only`) | mittel |
| `scraper-extractor` | Use for web extraction, crawler logic, and structured lead data parsing with robots/ToS compliance. | Implementierung/Refactor | mittel (`workspace-write`) | hoch |
| `scrum-master` | Use when a task needs process facilitation, iteration planning, or workflow friction analysis for an engineering team. | Analyse/Review | hoch (`read-only`) | mittel |
| `search-specialist` | Use when a task needs fast, high-signal searching of the codebase or external sources before deeper analysis begins. | Analyse/Review | hoch (`read-only`) | hoch |
| `security-auditor` | Use when a task needs focused security review of code, auth flows, secrets handling, input validation, or infrastructure configuration. | Analyse/Review | hoch (`read-only`) | hoch |
| `security-engineer` | Use when a task needs infrastructure and platform security engineering across IAM, secrets, network controls, or hardening work. | Analyse/Review | hoch (`read-only`) | hoch |
| `seo-specialist` | Use when a task needs search-focused technical review across crawlability, metadata, rendering, information architecture, or content discoverability. | Analyse/Review | hoch (`read-only`) | hoch |
| `slack-expert` | Use when a task needs Slack platform work involving bots, interactivity, events, workflows, or Slack-specific integration behavior. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `spring-boot-engineer` | Use when a task needs Spring Boot expertise for service behavior, configuration, data access, or enterprise API implementation. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `sql-pro` | Use when a task needs SQL query design, query review, schema-aware debugging, or database migration analysis. | Analyse/Review | hoch (`read-only`) | mittel |
| `sre-engineer` | Use when a task needs reliability engineering work involving SLOs, alerting, error budgets, operational safety, or service resilience. | Analyse/Review | hoch (`read-only`) | hoch |
| `swift-expert` | Use when a task needs Swift expertise for iOS or macOS code, async flows, Apple platform APIs, or strongly typed application logic. | Implementierung/Refactor | mittel (`workspace-write`) | niedrig |
| `task-distributor` | Use when a broad task needs to be broken into concrete sub-tasks with clear boundaries for multiple agents or contributors. | Analyse/Review | hoch (`read-only`) | mittel |
| `technical-writer` | Use when a task needs release notes, migration notes, onboarding material, or developer-facing prose derived from real code changes. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `terraform-engineer` | Use when a task needs Terraform module design, plan review, state-aware change analysis, or IaC refactoring. | Analyse/Review | hoch (`read-only`) | mittel |
| `terragrunt-expert` | Use when a task needs Terragrunt-specific help for module orchestration, environment layering, dependency wiring, or DRY infrastructure structure. | Analyse/Review | hoch (`read-only`) | mittel |
| `test-automator` | Use when a task needs implementation of automated tests, test harness improvements, or targeted regression coverage. | Implementierung/Refactor | mittel (`workspace-write`) | hoch |
| `test-engineer` | Use for test strategy, regression coverage, and executable validation plans across services and routes. | Implementierung/Refactor | mittel (`workspace-write`) | hoch |
| `tooling-engineer` | Use when a task needs internal developer tooling, scripts, automation glue, or workflow support utilities. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `trend-analyst` | Use when a task needs trend synthesis across technology shifts, adoption patterns, or emerging implementation directions. | Analyse/Review | hoch (`read-only`) | mittel |
| `typescript-pro` | Use when a task needs strong TypeScript help for types, interfaces, refactors, or compiler-driven fixes. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `ui-designer` | Use when a task needs concrete UI decisions, interaction design, and implementation-ready design guidance before or during development. | Analyse/Review | hoch (`read-only`) | mittel |
| `ui-fixer` | Use when a UI issue is already reproduced and the parent agent wants the smallest safe patch. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `ux-researcher` | Use when a task needs UI feedback synthesized into actionable product and implementation guidance. | Analyse/Review | hoch (`read-only`) | hoch |
| `vue-expert` | Use when a task needs Vue expertise for component behavior, Composition API patterns, routing, or state and rendering issues. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `websocket-engineer` | Use when a task needs real-time transport and state work across WebSocket lifecycle, message contracts, and reconnect/failure behavior. | Implementierung/Refactor | mittel (`workspace-write`) | mittel |
| `windows-infra-admin` | Use when a task needs Windows infrastructure administration across Active Directory, DNS, DHCP, GPO, or Windows automation. | Analyse/Review | hoch (`read-only`) | mittel |
| `wordpress-master` | Use when a task needs WordPress-specific implementation or debugging across themes, plugins, content architecture, or operational site behavior. | Implementierung/Refactor | mittel (`workspace-write`) | niedrig |
| `workflow-orchestrator` | Use when the parent agent needs an explicit Codex subagent workflow for a complex task with multiple stages. | Analyse/Review | hoch (`read-only`) | hoch |
