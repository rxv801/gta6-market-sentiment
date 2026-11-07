# M0 Kickoff (Sprint 0)

Goal: set up the project the way a professional team would before writing feature code.
Exit: S1 can start with no setup work left.

Hard external constraint: collectors must be live before GTA VI preload (12 Nov 2026) and launch (19 Nov 2026).

| # | Step | Owner hat | Artifact | Est | Status |
|---|------|-----------|----------|-----|--------|
| 1 | Problem definition | PM | `docs/one-pager.md` | 1.5h | [x] v1.0 |
| 2 | Alignment / review | Stakeholders | Open questions resolved in one-pager | incl. | [x] |
| 3 | Technical design | Tech lead | `docs/design.md` + ADR-001..003 | 2h | [ ] |
| 4 | Legal / security / data review | Governance | `docs/data-governance.md` | 45m | [ ] |
| 5 | Access & provisioning | Platform | API keys, Supabase, DB roles, GitHub secrets | 1h | [ ] |
| 6 | Repo & engineering baseline | Engineer | Scaffold PR, CI green on `main` | 2h | [ ] |
| 7 | Backlog & planning | PM + team | GitHub Projects board, S1 groomed | 1.5h | [x] |
| 8 | Working agreement | Team | `docs/working-agreement.md` | 30m | dropped (solo project) |
| 9 | Kickoff | Everyone | 10-min recorded walkthrough | 30m | postponed → DOC-8 (M5) |
| 10 | Sprint 0 review | Everyone | `docs/sprints/s0-review.md` + retro | 30m | [ ] |

Order: 1 → 2 → 3 → 4 before code. Step 5 starts today in parallel (approvals are slow).

Stopgap: until M1 ships, a throwaway `spike/` script snapshots YouTube view counts daily so no data is lost.
