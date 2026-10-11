# Technology Underpinnings — Open Web Calendar

A Python/Flask service that fetches ICS and CalDAV calendar feeds and
renders them as an embeddable web calendar. The frontend is DHTMLX
Scheduler inside a Jinja2 template.

## Request flow

`open_web_calendar/app.py` defines the Flask app and all routes. The
central route is `GET /calendar.<ext>`:

- `calendar.html` — renders `templates/calendars/dhtmlx.html`, the
  embeddable calendar page.
- `calendar.json` — returns calendar metadata (names, colors,
  categories) via `convert/calendar.py` (`ConvertToCalendars`).
- `calendar.events.json` — returns events in the DHTMLX Scheduler JSON
  format via `convert/events.py` (`ConvertToEvents`).
- `calendar.ics` — merges all source feeds into one ICS download via
  `convert/ics.py` (`ConvertToICS`, uses the `mergecal` library).
- `calendar.spec` — returns the effective specification as JSON.

Other routes: `/` and `/about.html` (configuration UI),
`/configuration.js` and `/locale_<lang>.js` (generated JS config and
DHTMLX locale strings), `/encrypt`, `/decrypt`, `/new-key` (URL
encryption), and `/caldav/list-calendars` + `/caldav/sign-up` (CalDAV
discovery and event sign-up).

## Specification pipeline

`default_specification.yml` holds every tunable: feed URLs, language,
skin, tabs, controls, timezone, HTML-cleaning flags, menu options.
`get_specification()` in `app.py` merges three layers, lowest to highest
priority:

1. `default_specification.yml`
2. The `OWC_SPECIFICATION` environment variable (YAML/JSON text or a
   file path) plus `app.DEFAULT_SPECIFICATION`
3. Query parameters, and optionally a remote spec file pointed to by
   the `specification_url` parameter

## Calendar sources

`open_web_calendar/calendars/` abstracts feed access:

- `ics.py` (`ICSCalendars`) — fetches ICS URLs, parses with `icalendar`,
  expands recurring events with `recurring-ical-events`, applies
  `x-wr-timezone` compatibility.
- `caldav.py` (`CalDAVCalendars`) — reads calendars over CalDAV using
  the `caldav` client library; also supports adding attendees
  (event sign-up).
- `errors.py` (`InvalidCalendars`) — wraps broken feeds so a bad source
  produces an error entry instead of a failed page.
- `info/` — collects per-calendar metadata (name, description, color,
  CSS classes) for the calendar list.

## Conversion layer

`convert/base.py` defines `ConversionStrategy`: retrieve all calendars
(in a `ThreadPoolExecutor`), then merge them into one output. Each
converter subclasses it (`calendar.py`, `events.py`, `ics.py`).
`convert/events.py` maps icalendar fields to DHTMLX event objects —
times, locations (with OpenStreetMap links via
`icalendar-compatibility`), categories, organizers/attendees, and
per-status styling.

## Security

- `clean_html.py` sanitizes event HTML with `lxml`'s `Cleaner`; the
  `clean_html_*` spec flags control it.
- `encryption.py` uses Fernet (`cryptography`) and bcrypt to encrypt
  feed URLs, keeping private calendar links out of embed code. Keys come
  from `OWC_ENCRYPTION_KEYS`.
- `flask_allowed_hosts` restricts which hostnames the service responds
  to (`ALLOWED_HOSTS`).
- `error.py` converts exceptions to JSON errors with HTTP status codes.

## Frontend

- `templates/calendars/dhtmlx.html` + `static/js/calendar.js` — the
  calendar view, built on DHTMLX Scheduler (vendored in
  `static/js/dhtmlx/` with skins in `static/css/dhtmlx/`).
- `templates/index.html` + `static/js/index.js` — the configuration
  page that builds the iframe snippet.
- `static/js/signup.js` — CalDAV event sign-up UI.

## Internationalization

`translate.py` loads YAML translation files from
`translations/<lang>/<file>.yml` (about 38 languages) and exposes them to
templates. `templates/locale.js` generates DHTMLX locale JS per
language. Translations are managed through Weblate.

## Caching and configuration

`config.py` (`Config` class, `environment` singleton) maps environment
variables to settings: port, debug, `ALLOWED_HOSTS`, and a
`requests-cache` filesystem cache for fetched feeds (size, file size,
expiry, directory).

## Packaging and deployment

- `pyproject.toml` — hatchling build with `hatch-vcs` versioning;
  dependencies pinned in `requirements/base.txt` (compiled with
  pip-compile-multi from `requirements/base.in`).
- `Procfile` / `app.json` — Heroku deployment with gunicorn.
- `Dockerfile` — Alpine image running gunicorn on port 80 via
  `docker/start-service.sh`.
- `vercel.json` — Vercel Python serverless deploy.
- `app.py` (repo root) — compatibility shim exposing `app` and `main`.

## Testing and tooling

- `open_web_calendar/test/` — pytest suite.
- `open_web_calendar/features/` — behave/Gherkin feature files run
  against a real browser via Selenium (`features/steps/browser_steps.py`,
  `tox -e web`).
- `tox.ini` — test matrix (py310–py312, web, docs, reuse, ruff).
- `mkdocs.yml` + `docs/` — documentation site built with MkDocs
  Material; `mkdocs.test.yml` builds a quick English/German-only site.
- `.pre-commit-config.yaml` — ruff lint/format hooks.
- `REUSE.toml` + `LICENSES/` — per-file license compliance (REUSE spec).
