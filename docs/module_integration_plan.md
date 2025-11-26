# ProductionEquityAI: Frontend & Modules 1–7 Integration Plan

## Goals
- Deliver a ChatGPT-style conversational frontend that orchestrates requests across all analytical modules.
- Integrate Modules 1–7 so data ingestion, valuation, modeling, and deployment share consistent contracts.

## Architectural Overview
1. **Gateway API**
   - Add a FastAPI service layer that exposes unified endpoints for chat, data retrieval, and job orchestration.
   - Introduce versioned REST/GraphQL routes that map user intents (e.g., "value AAPL", "train factor model") to module pipelines.
2. **Task Orchestrator**
   - Use a job queue (e.g., Celery/RQ) to run long jobs (valuation, training) asynchronously.
   - Persist job metadata and results so the frontend can poll or stream updates.
3. **Model Registry & Artifacts**
   - Standardize storage for trained models (Module 5–6) with metadata (dataset hash, parameters, timestamps).
   - Enable model selection in API calls (e.g., `model=latest-dcf`, `model=factor-v2`).
4. **Shared Schemas**
   - Define Pydantic schemas for all module inputs/outputs to guarantee compatibility between services and the UI.

## Frontend (ChatGPT-Style) Build
- **Tech stack**: Next.js/React with TypeScript and Tailwind for fast iteration.
- **Chat Surface**: A message list, input box, streaming responses (Server-Sent Events or WebSockets), and quick actions ("Run valuation", "Update data").
- **Session Memory**: Store conversation context and past results in local storage plus server-side session tokens.
- **API Contracts**:
  - `POST /chat/stream` → streams assistant messages backed by tool-calling to Modules 1–7 via the Gateway API.
  - `GET /entities/{ticker}` → fetches cached fundamentals/prices (Module 1) and derived metrics.
  - `POST /jobs` → submit valuation/training jobs; `GET /jobs/{id}` → status/results for Modules 2–6 workloads.
- **UI Modules**: dedicated panels for fundamentals (Module 1), valuation outputs (Module 2–3), ML forecasts (Module 5–6), and deployment toggles (Module 7).

## Module Integration Path
1. **Module 1 (Ingestion & Preprocessing)**
   - Keep existing pipelines; expose read-only endpoints for cached fundamentals, prices, and rates.
2. **Module 2 (Valuation Engine)**
   - Implement DCF/multiples services that read Module 1 tables; return JSON + chart-ready series.
3. **Module 3 (Comparable Analysis)**
   - Add peer screening and factor comparisons; share factor definitions with Module 2 valuation inputs.
4. **Module 4 (Risk & Scenario Modeling)**
   - Provide Monte Carlo/scenario endpoints that consume Module 1 data and feed sensitivity charts to the UI.
5. **Module 5 (Traditional ML Forecasting)**
   - Add pipelines for feature engineering, model training, and evaluation; register artifacts in the model registry.
6. **Module 6 (Deep Learning / LLM Insights)**
   - Support sequence models and LLM-based summarization of filings; expose inference endpoints.
7. **Module 7 (Deployment & Monitoring)**
   - Wrap inference services with monitoring hooks (latency, drift) and automated rollbacks; ship CLI/infra templates.

## Data Contracts & Validation
- Define canonical dataclasses/Pydantic models for:
  - `FinancialSnapshot`, `PriceSeries`, `TreasuryCurve` (Module 1 outputs)
  - `ValuationRequest/Response`, `ScenarioRequest/Response`
  - `ForecastJob`, `ForecastResult`, `ModelMetadata`
- Enforce schema compatibility tests to prevent breaking changes between modules and the frontend.

## Milestones
1. **Scaffold Gateway API** (FastAPI + queue + SSE/WebSocket support)
2. **Ship Chat UI** (Next.js app + streaming hook + session cache)
3. **Expose Module 1 endpoints** (read-only) and wire to UI data panels
4. **Add valuation/comps APIs** (Modules 2–3) with job orchestration
5. **Integrate forecasting/deep learning** (Modules 5–6) with model registry
6. **Enable deployment/monitoring hooks** (Module 7) and CI/CD templates

## Testing & Observability
- Contract tests for every API schema; snapshot tests for chat rendering.
- Integration tests that simulate a full chat session triggering Modules 1–7.
- Observability: structured logs, OpenTelemetry traces, and frontend performance logging.

## Deliverables
- `frontend/` Next.js codebase with chat UI and module-specific panels.
- `gateway/` service exposing unified APIs, job orchestration, and streaming endpoints.
- CI pipeline running lint/tests for both frontend and backend services.
