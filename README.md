# Hotdeal Monitor

Python hotdeal monitoring automation service that checks selected Korean
hotdeal boards and sends Discord notifications for newly discovered posts.

The project is intentionally lightweight: it uses direct HTTP requests,
site-specific parsers, a JSON state file, and a Discord webhook. It is positioned
as a small server-friendly notifier rather than a general-purpose crawler
platform.

## Runtime Model

- Entrypoint: `python app.py`
- State: local JSON file at `state/seen_posts.json`
- Notifications: Discord webhook
- Site configuration: `sites.json`
- Duplicate prevention: per-site post ID tracking

`app.py` is a one-shot run. In production, run it from a small server, VM,
cron, or another scheduler that preserves the local `state/` directory between
runs.

## Supported Sites

Enabled by default:

- Ruliweb
- Eomisae
- PPOMPPU

Implemented but disabled by default:

- FMKorea

FMKorea is kept in the codebase, but `sites.json` disables it because it returns
HTTP 430 from cloud environments often enough to make it unsuitable for the
current server-friendly default configuration.

Server-friendly operation may intentionally monitor fewer sources if a site is
unstable from hosted or free-tier networks.

## Configuration

For local or server runs, provide `DISCORD_WEBHOOK_URL` through the environment
or a local `.env` file:

```text
DISCORD_WEBHOOK_URL=<discord webhook url>
```

Site enablement is controlled in `sites.json`:

```json
{
  "name": "fmkorea",
  "enabled": false
}
```

## GitHub Actions

The repository workflow is a safety check for public GitHub release. It installs
dependencies, validates Python files, and validates `sites.json`.

It does not run the crawler, send Discord notifications, or commit runtime
state. Scheduled crawler execution in GitHub Actions can be fragile when state is
stored as a local JSON file, because each runner starts from a fresh checkout
unless state is committed or stored externally.

Committing runtime state from a scheduled workflow is possible, but it is brittle
for a public repository:

- state commits create repository noise
- push conflicts can cause duplicate notifications on later runs
- runtime state becomes public history
- ignored state files and automatic commits work against each other

For this project, persistent local state on a lightweight server is the safer
default operating model.

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
`state/*.json` is ignored by Git because it is runtime data, not source code.

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
└── crawlers/
    ├── eomisae.py
    ├── fmkorea.py
    ├── ppomppu.py
    └── ruliweb.py
```

## Legacy / Migration Notes

This project previously ran on an Oracle VM with systemd and APScheduler.
It has since been simplified into a one-shot monitor that can be scheduled by
the hosting environment.

The following files are legacy components from the previous runtime:

- `run.py`
- `scheduler.py`
- `db.py`

They are not part of the current production GitHub Actions path. The current
state store is JSON, not SQLite.

## Known Limitations

- External site HTML can change without notice and break parsers.
- Free-tier networks and hosted runners may be blocked or rate limited.
- Some sites block scraping from cloud environments; FMKorea is disabled by
  default for this reason.
- Runtime state should not be committed to a public repository.
- GitHub Actions is useful for repository validation, but it is not ideal for
  all crawler workloads that require durable local state.
- This project favors simple failure-aware monitoring over broad site coverage.

## Operational Notes

- Keep `state/seen_posts.json` local to the runtime environment.
- Do not enable FMKorea unless HTTP 430 behavior has been revalidated from the
  target runtime network.
- Prefer disabling fragile crawlers in `sites.json` instead of deleting them.
- Treat crawler failures as expected operational events, not necessarily code
  failures.
