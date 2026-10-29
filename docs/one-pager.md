# One-pager: GTA VI Market & Sentiment Study

Status: v1.0 · Owner: Rex · Last updated: 29 Oct 2026

## Problem

GTA VI has been in the news for four years. Every announcement, trailer, leak and delay has been followed by a move in Take-Two's share price and a jump in how many people search for, watch and talk about the game.

Most of what's written about this is anecdotal: "stock drops after delay". I haven't found anything public that lines up the whole timeline and measures each event the same way. That's what this project does. It puts game news, public attention and stock prices side by side, and measures how big each effect was, or whether there was one at all.

## Why now

The game launches on 19 Nov 2026. YouTube view counts, Twitch viewers and Reddit activity only exist in the moment, and there's no public archive to pull them from later. If I don't collect them during the run-up and launch week, I can't get them back.

## Audience

The main readers are recruiters and hiring managers for data and analytics roles. They'll look at whether the work is technically sound and clearly explained.

Gamers and people in data or finance are the second group. I expect them to poke holes in it, which is fine, and probably useful.

## What readers should come away with

- How trailers, delays, leaks and the launch line up with stock moves and public attention.
- Which effects show up in the data and which don't. For example, I'd be surprised if one game is visible in Sony's stock, and saying so is a valid result.
- Enough of the method and sources to check the work themselves.

## Goals

1. A public website with an interactive dashboard and a written analysis.
2. A project that shows I can build the whole thing: data pipeline, warehouse, statistics and a sentiment model.
3. Research that is factually correct and that anyone can reproduce.

## Non-goals

- Trading or investment advice.
- Sales forecasting.
- Live analysis. Data is collected every day, but analysis happens in batches.
- Claims about the world economy. I'm only looking at listed companies and public attention data. That's narrower than "the impact of GTA VI", but it's something I can actually back up.
- Spoilers.
- Causal claims. Results are reported as associations.

## Scope

In scope: Take-Two (TTWO), Sony (SONY and 6758.T), the S&P 500 and Nasdaq-100 as benchmarks, Google Trends, YouTube, Reddit, Twitch from preload onward, and sales figures that publishers report.

Out of scope for now, maybe a v2: Microsoft/Xbox, retailers, other publishers, hardware sales.

## Success metrics

Research quality matters most:

- Every event in the timeline has at least one primary source (Rockstar, Take-Two or Sony) or two reputable secondary ones, and the links live in `events.csv`.
- Every number on the site traces back to code and data. One command rebuilds the results from raw data.
- Each statistical result comes with an effect size, a confidence interval and the method used. There's a limitations section.
- The sentiment model is checked against at least 200 posts I've labelled by hand. I'll report the F1 score whatever it is. My target is 0.65 or better.
- Two people, one technical and one who knows finance or gaming, review the write-up before it goes public. I keep a log of what they corrected.

Delivery:

- All collectors run unattended before 11 Nov 2026, and at least 95% of scheduled runs succeed through 31 Dec 2026.
- v1.0 of the site is public by 11 Feb 2027.

I'm not setting a target for views or shares. I'll keep an eye on them, but the point is getting it right, not going viral.

## Constraints

I work on this on Wednesdays and Thursdays, roughly 12 to 16 hours a week. Everything that collects data has to run on its own the rest of the week.

I'll stay on free tiers unless paying for something clearly helps. Any spend gets its own ADR.

The data side is limited by each API's terms and rate limits, and by the spoiler policy.

## Timeline

One milestone per working week, with M0 as kickoff. The full plan is in [backlog.md](backlog.md).

| Milestone | Week of | Focus |
|---|---|---|
| M0 | 28 Oct | Kickoff: docs, access, repo, backlog |
| W1–W2 | 4 Nov – 12 Nov | All collectors live before preload |
| W3–W4 | 18 Nov – 26 Nov | dbt warehouse, launch monitoring |
| W5–W7 | 2 Dec – 17 Dec | Event study, hand-labelling, launch decay |
| Break | 23 Dec – 1 Jan | Collectors keep running |
| W8–W11 | 6 Jan – 28 Jan | Sentiment model, dashboard, Airflow |
| W12–W13 | 3 Feb – 11 Feb | Write-up, review, v1.0 |

## Top risks

| Risk | Mitigation |
|---|---|
| Collectors aren't live before preload | A stopgap YouTube snapshot script runs from day one |
| Reddit API access is denied or slow | Fall back to public JSON endpoints and archive datasets; RQ4 can lean on YouTube and Trends |
| Too few events for strong statistics | Report effect sizes and non-parametric tests, not only p-values |
| Earnings calls land on some event days | Flag those events and run the analysis with and without them |
| Wrong facts in the timeline | Every event needs a citation; two reviewers before publishing |

## Decisions

These were open questions in v0.1.

1. Scope is narrowed to listed companies and attention data, not the wider economy.
2. The dashboard tool will be chosen in the design doc (DOC-2). Power BI's public sharing needs a work or school account, so it might not fit.
3. The repo is public.
4. No reach target. Views and shares are tracked informally.
5. The two reviewers are to be named by W11. They're needed in W12.
