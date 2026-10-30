---
name: wind-portal-conventions
description: Project rules and decisions for the wind forecast evaluation portal (FastAPI + pandas backend, React frontend, Elexon FUELHH/WINDFOR data). Use when writing or changing any code, tests or docs in this repo.
---

# Wind forecast portal: conventions

Source of truth for the plan: `docs/Wind Forecast Evaluation Portal Project Guide.md`, `docs/Wind Forecast Portal Phased To-Do List.md`, `docs/Wind Forecast Portal Research Notes.md`, `docs/Wind Forecast Portal Data Flow.md`. Read the relevant one before starting a phase.

## Stack and commands (run from `backend/`)
- Python 3.12 with uv. `uv add <pkg>`, `uv run pytest`, `uv run ruff check . && uv run ruff format .`, `uv run mypy app`, `uv run uvicorn app.main:app --reload`.
- Refresh data: `uv run python -m app.services.ingest --refresh`.
- Print the full analysis: `uv run python -m app.services.report [--cutoff 09:00]`.
- Analysis code: `app/services/selection.py` (parse_cutoff, expected_hours, cutoff_for_targets, select_forecasts, hourly_actuals, build_scored -> (scored, Coverage)) and `app/services/metrics.py` (summarise, percentile, by_hour_of_day/by_day/by_horizon/by_generation_level, recommendation_text). Reuse these from routes; do not reimplement.
- API: shared query validation lives in `app/routes/params.py` (`date_range`, `cutoff_param` dependencies, 422 with a clear `detail`). Analysis routes in `app/routes/analysis.py` (`/api/v1/series`, `/api/v1/metrics`); schemas in `app/models/analysis.py`. The error histogram (500 MW bins) is computed in the backend.
- Buffer recommendation = P90 rounded UP to a whole MW (`metrics.buffer_mw`).
- Frontend (`frontend/`): Next.js 16 App Router + TypeScript, shadcn/ui (Tailwind 4, `npx shadcn@latest add <component>`), TanStack React Query, ECharts (canvas; import only the parts needed in `components/charts/echart.tsx`). Commands: `npm run dev|lint|typecheck|format|build`. API base URL from `NEXT_PUBLIC_API_BASE_URL` (see `.env.example`). Next 16 differs from older versions: read `frontend/node_modules/next/dist/docs/` before using unfamiliar Next APIs.
- Dashboard pieces: `components/dashboard.tsx` (assembles everything), `kpi-cards.tsx` (tooltips explain each metric), `cutoff-select.tsx` (shadcn Select, half-hour steps), `date-range-picker.tsx` (shadcn Calendar + Popover), `query-state.tsx` (loading/error+retry/empty), charts in `components/charts/` with shared `colors.ts` (actual blue, forecast orange, error purple). Hooks in `hooks/use-analysis.ts` use `keepPreviousData`.
- Always use shadcn components for UI (add with `npx shadcn@latest add <name>`, answer "n" to overwrite prompts). Verify UI changes in a real browser (playwright-core with system Chrome, screenshots in the session scratchpad).
- Frontend layout: `src/lib/api/` (typed client + response types, keep in sync with `backend/app/models/`), `src/hooks/` (React Query hooks), `src/components/` (UI, charts wrapped so pages never touch echarts directly). No statistics in the browser.

## Architecture rules
- Routes (`app/routes/`) validate input and return typed responses. No analysis logic.
- Logic (`app/services/`) is pure functions: no web, file or network code in `selection.py` and `metrics.py`.
- Schemas in `app/models/`. Config constants in `app/config.py`.
- No database. App reads `backend/data/actuals.parquet` and `forecasts.parquet` at start-up and never calls Elexon at request time.

## Domain decisions (do not change without asking)
- Only Elexon FUELHH (actual) and WINDFOR (forecast), national GB wind, delivery window 2 Jan to 1 Feb 2026.
- All timestamps UTC. The cutoff is interpreted in UK time and converted to UTC properly.
- Default cutoff 09:00 on the day before delivery (D-1), user adjustable.
- Selection: for each target hour, take forecasts with `publish_time <= cutoff`, choose the latest. Never use a forecast published after the cutoff (leakage). Skip slots with no forecast and report coverage; never fill silently.
- Alignment: option B. Average the two half-hour actuals inside each forecast hour, score hourly.
- Percentiles use the nearest-rank method (`np.percentile(..., method="inverted_cdf")`). Hour-of-day breakdown is by UTC hour; by-day breakdown is by UK delivery day.
- error = forecast - actual (positive = over-forecast). Metrics: MAE, RMSE, bias, P50/P90/P95 of abs error, WAPE, coverage. Buffer recommendation = P90 abs error.
- Prototype numbers in the research notes are not final. Recompute with tests before quoting.

## Process
- Every logic change comes with tests (leakage, edge cases). Ruff, mypy and pytest must pass before a phase is done.
- After finishing a phase, use the `phase-learning-doc` skill and tick the to-do list.
- Do not commit or push unless the user asks. Commit messages are small and meaningful.
- Anonymity: no company or challenge name in repo name, README or video title. Disclose AI tool use in the README.
- Update this skill when a convention or decision changes.
