# Privacy policy

Last updated: 9 November 2026

This policy covers the GTA VI Market Event Study (https://github.com/rxv801/gta6-market-sentiment), a non-commercial research project run by one independent developer.

## YouTube API Services

This project uses YouTube API Services. By using or reading this project's YouTube-based results, you also agree to be bound by the [YouTube Terms of Service](https://www.youtube.com/t/terms). See also the [Google Privacy Policy](http://www.google.com/policies/privacy).

## What we collect

- **YouTube:** view, like and comment counts for official Rockstar Games videos, read with an API key. If comment sentiment is added, public comment text is stored only so it can be scored, then deleted within 30 days of being fetched. Commenter names and channel IDs are not stored. Comments are never quoted or displayed.
- **Other sources:** daily stock prices. Google Trends search interest and Twitch category totals (total viewers and stream counts only, no usernames or stream titles) are planned but not collected yet.

We don't use YouTube sign-in, and we don't access, collect or store any data from your YouTube or Google account. This project doesn't set cookies or add tracking of its own. The project is hosted on GitHub, and the dashboard will be hosted by a third party, so their own privacy policies and cookies apply on those sites.

## How the data is used

Only to calculate aggregate statistics, such as daily changes and sentiment scores, which will be published as charts in a free public write-up and dashboard. The data is not sold, shared with third parties, or used for advertising.

## Where it is stored

In a private Postgres database hosted by Supabase. It isn't exposed through any public API. Only the project owner's admin login can read it, and the collectors that write to it can only insert rows.

## How long it is kept

- YouTube statistics: up to 30 days, or up to 36 months if YouTube grants permission under Section III.L of its Developer Policies. Collection started on 6 November 2026.
- YouTube comment text: deleted within 30 days of being fetched.
- Aggregate results: for the life of the project.

## Your choices and contact

You can review or revoke access that apps have to your Google account at [Google security settings](https://security.google.com/settings/security/permissions). This project never requests that access.

For questions or deletion requests, open an issue at https://github.com/rxv801/gta6-market-sentiment/issues.
