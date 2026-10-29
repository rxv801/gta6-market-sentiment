# Product Backlog

Source of truth for GitHub Issues and the Projects board. Each story becomes one issue assigned to a milestone. Epics are labels (`epic:*`) and a field on the board, not issues.

Sizes (in working hours): **S** ≈ 1h · **M** ≈ 2–4h · **L** ≈ a full session (6–8h)
Priority: **P0** blocks a deadline · **P1** needed for v1.0 · **P2** nice to have

## Milestones

One milestone per working week (Wednesday + Thursday, about 12h). Due date is the Thursday. Holidays 23 Dec – 1 Jan are off; collectors keep running.

| Milestone | Due | Notes |
|---|---|---|
| M0 – Kickoff | 2026-10-29 | 28–29 Oct |
| W1 – Core capture | 2026-11-05 | 4–5 Nov |
| W2 – Capture complete | 2026-11-12 | 11–12 Nov · preload 12 Nov · collectors frozen at end of week |
| W3 – dbt start | 2026-11-19 | 18–19 Nov · launch 19 Nov |
| W4 – Marts | 2026-11-26 | 25–26 Nov |
| W5 – Event study I | 2026-12-03 | 2–3 Dec |
| W6 – Event study II | 2026-12-10 | 9–10 Dec |
| W7 – Labelling + launch decay | 2026-12-17 | 16–17 Dec |
| W8 – Sentiment model | 2027-01-07 | 6–7 Jan |
| W9 – Dashboard I | 2027-01-14 | 13–14 Jan |
| W10 – Dashboard II | 2027-01-21 | 20–21 Jan |
| W11 – Platform + method | 2027-01-28 | 27–28 Jan |
| W12 – Write-up | 2027-02-04 | 3–4 Feb · send to reviewers |
| W13 – Release | 2027-02-11 | 10–11 Feb · v1.0 tag |

Target v1.0: 11 Feb 2027.

## Epics

| Key | Epic |
|---|---|
| DOC | Docs & Research Design |
| GOV | Governance & Security |
| OPS | DevOps & Platform |
| ING | Ingestion |
| RES | Research Data (events, sources) |
| WH | Warehouse (dbt) |
| AN | Analysis (event study) |
| ML | Sentiment Model |
| BI | Dashboard & Website |

## Stories

### M0 – Kickoff (due 2026-10-29)

28–29 Oct

| ID | Story | Size | Pri | Acceptance criteria |
|---|---|---|---|---|
| DOC-1 | One-pager v1.0 | S | P0 | Open questions resolved; status set to v1.0 |
| DOC-2 | Design doc + ADR-001 stack, ADR-002 hosting, ADR-003 spoiler policy | M | P0 | Architecture diagram, data flow, alternatives considered; dashboard tool decided |
| GOV-1 | Data governance doc | S | P0 | API terms summarised per source; PII handling (hashed usernames); secrets plan; DB roles defined |
| OPS-1 | Provision accounts and API keys | S | P0 | YouTube, Twitch, Supabase working; Reddit applied; keys in password manager and GitHub secrets |
| OPS-2 | Repo scaffold and tooling | M | P0 | Folder layout, uv, ruff, pytest, pre-commit, .env.example, README skeleton |
| OPS-3 | CI and branch protection | S | P0 | Lint + tests run on every PR; `main` requires a PR and green CI |
| OPS-4 | Project board and backlog | S | P1 | Board with views; every M1 story created with acceptance criteria |
| ING-0 | Stopgap YouTube snapshot (spike) | S | P0 | Snapshots saved daily from 28 Oct until ING-2 replaces it |

### W1 – Core capture (due 2026-11-05)

4–5 Nov

| ID | Story | Size | Pri | Acceptance criteria |
|---|---|---|---|---|
| ING-1 | Bronze schema and shared loader | M | P0 | Raw tables store payload JSON, source, run_id, loaded_at; insert-only collector role |
| ING-2 | YouTube collector | M | P0 | Daily views, likes, comments for tracked videos; video list in config |
| ING-3 | Twitch poller | M | P0 | Viewers + stream count for GTA VI category every 30 min; live by 5 Nov for baseline |
| ING-5 | Stock prices backfill + daily | S | P0 | TTWO, SONY, 6758.T, ^GSPC, ^NDX from 2021; daily append idempotent |
| ING-7 | Schedule collectors on GitHub Actions | M | P0 | All collectors on cron; secrets from GitHub; manual re-run possible |
| OPS-5 | Failure alerts | S | P0 | Failed run or empty payload sends a notification |

### W2 – Capture complete (due 2026-11-12)

11–12 Nov · preload 12 Nov · collectors frozen at end of week

| ID | Story | Size | Pri | Acceptance criteria |
|---|---|---|---|---|
| RES-1 | events.csv with citations | M | P0 | Every event has date, announce time (ET), market status, type, confounded flag, source URLs |
| ING-4 | Reddit collector with spoiler filter | M | P1 | Daily posts + comment counts from 3 subreddits; spoiler-flagged and blocklisted posts dropped at ingestion; usernames hashed |
| ING-6 | Google Trends backfill + loader | M | P1 | Daily series from 2021 via overlapping windows, rescaled; method documented |
| OPS-6 | Daily health check | S | P1 | Row counts per source per day; flags gaps |
| OPS-7 | Weekly bronze backup | S | P1 | Dump to storage outside Supabase (free tier has no backups) |

### W3 – dbt start (due 2026-11-19)

18–19 Nov · launch 19 Nov

| ID | Story | Size | Pri | Acceptance criteria |
|---|---|---|---|---|
| RES-2 | Verify unconfirmed facts | S | P1 | May 2024 earnings date, pre-order and preload dates, Sony partnership claim each confirmed or removed |
| WH-1 | dbt project setup | S | P1 | Profiles for dev/prod; sources declared with freshness checks |
| WH-3 | Seeds: events, sales_reported | S | P1 | Loaded with accepted_values test on event_type |
| WH-2 | Staging models (6 sources) | L | P1 | Typed, deduplicated, renamed per dbt style guide; one model per source table |
| ING-8 | Launch-window monitoring | S | P0 | Collector health checked every session 12 Nov–3 Dec; incidents written up |

### W4 – Marts (due 2026-11-26)

25–26 Nov

| ID | Story | Size | Pri | Acceptance criteria |
|---|---|---|---|---|
| WH-4 | Dimensions: dim_date, dim_ticker, dim_events | M | P1 | Unique + not_null on keys; trading-day mapping for events |
| WH-5 | int_returns_daily + fct_stock_daily | M | P1 | Returns from adjusted close; matches a hand check on 3 dates |
| WH-6 | fct_interest_daily | M | P1 | Trends, YouTube, Reddit, Twitch on one daily grain |
| WH-7 | dbt tests and hosted docs | M | P1 | Relationship tests facts→dims; lineage graph public |

### W5 – Event study I (due 2026-12-03)

2–3 Dec

| ID | Story | Size | Pri | Acceptance criteria |
|---|---|---|---|---|
| AN-1 | Market model parameters | M | P1 | Alpha/beta per event, 120-day window ending 10 days before, excluding other event windows |
| AN-2 | Abnormal returns and CAR | M | P1 | CAR for [−1,+1], [0,+3], [−5,+5]; clustered May 2025 events handled |
| OPS-8 | CI runs dbt build on test target | M | P2 | PRs touching dbt/ run build + tests |

### W6 – Event study II (due 2026-12-10)

9–10 Dec

| ID | Story | Size | Pri | Acceptance criteria |
|---|---|---|---|---|
| AN-3 | Significance tests | M | P1 | t-test, sign test, bootstrap CI; effect sizes reported |
| AN-4 | Abnormal volume | S | P2 | Same windows as AN-2 |
| AN-5 | Sony analysis (RQ3) | S | P1 | SONY and 6758.T with time-zone shift; null result reported if null |
| AN-6 | Attention pre/post windows (RQ4) | M | P1 | Mean pre vs post per event per series |
| ML-1 | Labelling guide + sample | M | P1 | Guide covers sarcasm, hype slang, delay anger; 200 stratified samples drawn |

### W7 – Labelling + launch decay (due 2026-12-17)

16–17 Dec

| ID | Story | Size | Pri | Acceptance criteria |
|---|---|---|---|---|
| ML-2 | Hand-label 200 samples | L | P1 | Labelled before seeing model output |
| AN-7 | Launch decay curve (RQ5) | M | P1 | Twitch/YouTube/Trends peak and half-life after 19 Nov |

### W8 – Sentiment model (due 2027-01-07)

6–7 Jan

| ID | Story | Size | Pri | Acceptance criteria |
|---|---|---|---|---|
| ML-3 | Model evaluation | M | P1 | RoBERTa on MPS vs VADER baseline; accuracy, macro F1, confusion matrix |
| ML-4 | Score corpus + sentiment marts | M | P1 | int_sentiment_scored_daily, fct_sentiment_daily; aggregates only |
| BI-1 | Site skeleton and deploy | M | P1 | Public URL; builds from gold marts |

### W9 – Dashboard I (due 2027-01-14)

13–14 Jan

| ID | Story | Size | Pri | Acceptance criteria |
|---|---|---|---|---|
| BI-2 | Page: timeline overview | M | P1 | TTWO price with event markers |
| BI-3 | Page: event study | M | P1 | CAR by event and window, coloured by type, with CIs |
| BI-4 | Page: sentiment vs market | M | P1 | Sentiment and abnormal return on aligned axes |

### W10 – Dashboard II (due 2027-01-21)

20–21 Jan

| ID | Story | Size | Pri | Acceptance criteria |
|---|---|---|---|---|
| BI-5 | Page: PlayStation lens | S | P2 | SONY abnormal returns, PS5 Pro interest |
| BI-6 | Page: launch tracker | M | P1 | Twitch/YouTube/Trends since 19 Nov |
| OPS-10 | One-command rebuild | M | P1 | `make all` rebuilds marts and results from bronze |
| BI-7 | Custom domain | S | P2 | Only if ADR approves the spend |

### W11 – Platform + method (due 2027-01-28)

27–28 Jan

| ID | Story | Size | Pri | Acceptance criteria |
|---|---|---|---|---|
| OPS-9 | Airflow DAG for batch transforms | L | P2 | Runs dbt build + scoring locally in Docker; ADR on why capture stays on Actions |
| DOC-4 | Methodology doc | M | P1 | Event study, sentiment, data sources, limitations |

### W12 – Write-up (due 2027-02-04)

3–4 Feb · send to reviewers

| ID | Story | Size | Pri | Acceptance criteria |
|---|---|---|---|---|
| DOC-5 | Findings write-up | L | P1 | Every figure cited to a model or notebook |
| DOC-6 | Data dictionary | S | P1 | Generated from dbt docs |
| DOC-7 | README polish | S | P1 | Screenshots, architecture diagram, how to run |

### W13 – Release (due 2027-02-11)

10–11 Feb · v1.0 tag

| ID | Story | Size | Pri | Acceptance criteria |
|---|---|---|---|---|
| RES-3 | External review | M | P1 | Two reviewers; corrections log in docs/ |
| DOC-8 | Demo / kickoff video | S | P2 | 5–10 min walkthrough |
| DOC-9 | Launch post | S | P2 | LinkedIn post linking site and repo |
| DOC-10 | Project retro + resume update | S | P1 | Retro doc; resume lists only what shipped |

## Board setup (GitHub Projects)

- **Fields:** Status (Backlog, Ready, In progress, Review, Done), Priority, Size, Epic, Iteration (2 weeks = 4 sessions)
- **Views:**
  - Board, grouped by Status, filtered to the current iteration
  - Table of everything, grouped by Milestone
  - Roadmap by milestone due dates
- **Epics:** single-select field on the board plus `epic:*` labels
- **Automation:** new issue → Backlog; PR merged → Done
