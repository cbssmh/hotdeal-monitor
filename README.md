# Multi Hotdeal Notifier

Python crawler that checks selected Korean hotdeal boards and sends Discord
notifications for newly discovered posts.

The current production runtime is GitHub Actions. The application is designed as
a one-shot job: each scheduled run loads the previous JSON state, checks enabled
sites, sends notifications for unseen posts, and commits the updated state back
to the repository.

## Production Runtime

- Scheduler: GitHub Actions cron
- Entrypoint: `python app.py`
- State: `state/seen_posts.json`
- Notifications: Discord webhook
- Runtime secret: `DISCORD_WEBHOOK_URL`

The workflow is defined in `.github/workflows/hotdeal-check.yml`.

## Supported Sites

Enabled by default:

- Ruliweb
- Eomisae
- PPOMPPU

Implemented but disabled by default:

- FMKorea

FMKorea is kept in the codebase, but `sites.json` disables it because it returns
HTTP 430 from cloud environments often enough to make it unsuitable for the
current GitHub Actions production run.

## GitHub Actions Setup

1. Add the repository secret:

   ```text
   DISCORD_WEBHOOK_URL=<discord webhook url>
   ```

2. Ensure the workflow has permission to commit state updates:

   ```yaml
   permissions:
     contents: write
   ```

3. Enable the scheduled workflow in GitHub Actions.

The workflow can also be started manually with `workflow_dispatch`.

## State Persistence

State is stored in `state/seen_posts.json`.

The file tracks seen post IDs by site:

```json
{
  "version": 1,
  "sites": {
    "ruliweb": {
      "seen_ids": {
        "104305": {
          "title": "...",
          "url": "...",
          "first_seen_at": "2026-05-23T11:59:02+00:00"
        }
      }
    }
  }
}
```

At the end of a run, `app.py` writes the JSON state only if new posts were saved.
The GitHub Actions workflow commits `state/seen_posts.json` only when the file
changed.

## Duplicate Prevention

Duplicate prevention is based on per-site post IDs.

For each enabled site:

1. The crawler returns the latest posts.
2. Posts duplicated within the same crawler result are removed.
3. Existing IDs in `state/seen_posts.json` are skipped.
4. New posts are sent to Discord.
5. A post is saved to state only after its Discord notification succeeds.

This means a Discord failure does not mark the post as seen. The same post may be
retried on a later run, which is preferred over silently dropping notifications.

## First Run Behavior

When a site has no existing `seen_ids` state, the run is treated as initialization.
Current posts are saved without sending Discord notifications.

This prevents the first production run, or the first run after enabling a new
site, from sending a backlog of old posts.

## Failure Handling

Each site is handled independently. If one crawler fails, the error is logged and
the next enabled site is still checked.

Discord send failures are handled per post. A failed notification does not stop
the whole run and does not update state for that post.

## Local Development

Create a virtual environment and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

For local runs, provide `DISCORD_WEBHOOK_URL` through the environment or a local
`.env` file:

```text
DISCORD_WEBHOOK_URL=<discord webhook url>
```

Run one check:

```bash
python app.py
```

## Project Structure

```text
.
├── .github/workflows/hotdeal-check.yml
├── app.py
├── config.py
├── notifier.py
├── state_store.py
├── sites.json
├── state/
│   └── seen_posts.json
└── crawlers/
    ├── eomisae.py
    ├── fmkorea.py
    ├── ppomppu.py
    └── ruliweb.py
```

## Legacy / Migration Notes

This project previously ran on an Oracle VM with systemd and APScheduler.
Production has been migrated to GitHub Actions scheduled execution.

The following files are legacy components from the previous runtime:

- `run.py`
- `scheduler.py`
- `db.py`

They are not part of the current production GitHub Actions path. The current
state store is JSON, not SQLite.

## Operational Notes

- Keep `state/seen_posts.json` committed.
- Do not enable FMKorea in production unless HTTP 430 behavior has been
  revalidated in GitHub Actions.
- The workflow commits state updates using the GitHub Actions bot.
- The workflow is triggered by `schedule` and `workflow_dispatch`, so state
  commits do not create a workflow loop.

