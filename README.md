<!--
SPDX-FileCopyrightText: 2024 Nicco Kunzmann and Open Web Calendar Contributors <https://open-web-calendar.quelltext.eu/>

SPDX-License-Identifier: CC-BY-SA-4.0
-->

[![Open Web Calendar](https://open-web-calendar.quelltext.eu/assets/img/logo/github-social-preview.svg)][web]

[![](https://badge.fury.io/py/open-web-calendar.svg)](https://pypi.org/project/open-web-calendar/)
[![](https://img.shields.io/pypi/pyversions/open-web-calendar)](https://pypi.org/project/open-web-calendar)
[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/niccokunzmann/open-web-calendar/run-tests.yml?logo=github)](https://github.com/niccokunzmann/open-web-calendar/actions?query=branch%3Amaster)
![](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)

You might want to:
- **[Try&nbsp;it&nbsp;out][web]**
- [Contribute!](https://open-web-calendar.quelltext.eu/contributing/)
- [Set up for development](https://open-web-calendar.quelltext.eu/dev/)
- [Read the documentation][docs]

There are several commercial solutions which allow embedding of calendars into my website.
I only have a link to an ICS file and want to show a nice-looking calendar on my site.
Browser-only calendars usually have the problem that many ICS files can not be
accessed (such as ownCloud/nextCloud in my case).
I also want to be in control over who knows the people who
visit the site and not pass everything to Google.
This is a solution in my case which I share with the world.
You are free to use it or deploy your own, modify or share it.
It works offline and in company networks, too.

Features
- Embedded calendar
- Choice of time zone
- ICS link, best multiple
- month/week as a view
- name, time of event, link?
- showing the time span
- styling of choice (icon, color, font, ...)

## How to use it

The fastest way is the hosted instance: https://open-web-calendar.hosted.quelltext.eu/

The service renders an embeddable HTML calendar from one or more ICS or
CalDAV feed URLs. There are two ways to configure it:

1. **The configuration page** (`/`): fill in feed URLs, language, skin,
   tabs, and styling. The page generates an iframe snippet to paste into
   your site.
2. **URL parameters directly**: every option in
   `open_web_calendar/default_specification.yml` can be passed as a query
   parameter. Example:

   ```
   https://<your-host>/calendar.html?url=https://example.com/schedule.ics&language=en&skin=material
   ```

Embed the result in any web page:

```html
<iframe src="https://<your-host>/calendar.html?url=https://example.com/schedule.ics"
        width="100%" height="600"></iframe>
```

## Run it yourself

### Docker (recommended for self-hosting)

```sh
docker run -d --rm -p 5000:80 --name open-web-calendar niccokunzmann/open-web-calendar
```

Then open http://localhost:5000. Or build from this repo:

```sh
docker build --tag open-web-calendar .
docker run -d -p 5000:80 open-web-calendar
```

### Python

Requires Python 3.9+.

```sh
pip install -r requirements/base.txt
gunicorn -w 4 -b 0.0.0.0:5000 "open_web_calendar.app:app"
```

For development mode (auto-reload, debug):

```sh
pip install -r requirements/dev.in
APP_DEBUG=true python app.py
```

The app also runs as `python -m open_web_calendar` or via the
`open-web-calendar` console script after `pip install .`.

### Deployment notes

- `Procfile` + `app.json`: Heroku-ready (gunicorn, `WORKERS` env var).
- `vercel.json`: deploys to Vercel as a Python serverless app.
- Packages exist for Cloudron and YunoHost. See `docs/host/`.
- The service must be reachable by your visitors. Put it behind HTTPS
  when you embed it in a public site.

### Configuration (environment variables)

| Variable | Default | Purpose |
| --- | --- | --- |
| `PORT` | `5000` | Listen port |
| `WORKERS` | `4` | Gunicorn worker count |
| `APP_DEBUG` | `false` | Debug mode (tracebacks on errors) |
| `ALLOWED_HOSTS` | _(empty = all)_ | Comma-separated hostnames the service answers for |
| `OWC_SPECIFICATION` | `{}` | YAML/JSON overrides merged into every calendar's spec; may be a file path |
| `OWC_ENCRYPTION_KEYS` | _(unset)_ | Comma-separated Fernet keys for encrypting/decrypting feed URLs |
| `CACHE_REQUESTED_URLS_FOR_SECONDS` | `600` | How long fetched feeds stay cached |
| `CACHE_SIZE` | `200` (MB, or `unlimited`) | Max on-disk feed cache |
| `CACHE_FILE_SIZE` | `10` (MB) | Max size of a single cached feed |
| `CACHE_DIRECTORY` | system temp | Cache location |
| `SOURCE_TIMEOUT` | `60` | Timeout (s) for fetching source feeds; `0` = requests default |

## Common commands

| Task | Command |
| --- | --- |
| All tests | `tox` |
| Unit tests (one Python version) | `tox -e py312` or `pytest` |
| Browser tests (Selenium) | `tox -e web` (`-D browser=chrome`, `-D window=375x812`) |
| Lint + format | `tox -e ruff` or `pre-commit run -a` |
| License headers (REUSE) | `tox -e reuse` |
| Build docs | `tox -e docs -- build` (quick: `tox -e docs-quick -- build`) |

## Important caveats

- **Fetch failures appear in the calendar, not at deploy time.** A dead
  or unreachable ICS URL shows up as an error event inside the rendered
  calendar. Check feeds before publishing.
- **Caching delays updates.** Feeds are cached 10 minutes by default.
  Lower `CACHE_REQUESTED_URLS_FOR_SECONDS` for schedules that change
  often; set `0` to disable the cache.
- **The server fetches the URLs it is given.** Restrict what it can
  reach (network policy, `ALLOWED_HOSTS`) before exposing it publicly;
  see `docs/host/docker.md` for a compose example that isolates the
  container.
- **HTML in event descriptions is sanitized** (`clean_html` options in
  `default_specification.yml`). Do not disable the `clean_html_*` flags
  unless you control every feed.
- **Encrypted URLs need a key.** Set `OWC_ENCRYPTION_KEYS` to enable
  `/encrypt` and protected feed URLs. Generate one at the `/new-key`
  endpoint.
- **GPL-2.0 license.** If you modify the code and serve it, the
  `source_code` spec field must point at your modified source.

[web]: https://open-web-calendar.hosted.quelltext.eu/
[docs]: https://open-web-calendar.quelltext.eu/

Changelog
---------

The changelog can be found [here](https://open-web-calendar.quelltext.eu/changelog/).

Funding
-------

[<img alt="Logo NLnet: abstract logo of four people seen from above" src="https://nlnet.nl/logo/banner.svg" height="50px" />](https://nlnet.nl/) [<img alt="Logo NGI Zero: letterlogo shaped like a tag" src="https://nlnet.nl/image/logos/NGI0Core_tag.svg" height="50px" />](https://nlnet.nl/core)

This project was funded twice - in 2024 and 2025 - through the [NGI0 Core Fund](https://nlnet.nl/core), a fund established by [NLnet](https://nlnet.nl/) with financial support from the European Commission's [Next Generation Internet programme](https://ngi.eu/). You might be able to get funded, too!
