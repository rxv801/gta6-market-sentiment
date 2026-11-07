# ADR-004: Dashboard tool

Status: Proposed · Date: 2026-10-29

## Context

Goal G1 in the one-pager is a public website with an interactive dashboard. The original plan used Power BI. Two problems came up:

- Publishing a Power BI report to the web needs a work or school Microsoft account and an admin setting. A personal account can't do it.
- Power BI Desktop is Windows only, so on a Mac it needs a Windows VM.

Power BI is still one of the most requested tools in Australian data analyst job ads.

## Options

| Option | Public website | Resume value | Effort | Cost |
|---|---|---|---|---|
| Power BI | No. Screenshots, PDF and a video instead | High for analyst roles | Medium, plus VM setup | Free |
| Streamlit | Yes, on Streamlit Community Cloud | Good for data and ML roles | Low, all Python | Free |
| Evidence.dev | Yes, as a static site | Lower recognition, but pairs well with dbt | Low, SQL and Markdown | Free |
| Streamlit site plus a Power BI version | Yes | Covers both | Highest | Free |

## Proposed decision

Streamlit for the public site, because it's the only option that meets G1 cheaply and keeps the whole project in Python. A Power BI version of the same gold marts can be added in W10 or W11 if there's time.

## To decide

Rex picks an option, and the status changes to Accepted.
