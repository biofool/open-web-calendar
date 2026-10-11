# Executive Summary — Open Web Calendar

Open Web Calendar is a small web service that turns existing calendar
feeds (ICS files and CalDAV calendars) into a web calendar you can embed
in any website.

## What it does for somatic studios and movement fields

- **Publish class schedules without a new system.** If the studio keeps
  its schedule in Nextcloud, Google Calendar, Outlook, or any tool that
  exports ICS/CalDAV, this service renders that feed as a readable web
  calendar. No data re-entry.
- **One page, many sources.** It merges several feeds into one view. A
  studio can combine class schedules, workshop calendars, and room
  bookings into a single display.
- **Embeds in the existing site.** The calendar renders inside an
  iframe. It works with plain HTML pages, WordPress, or any CMS that
  accepts an embed snippet.
- **Respects visitor privacy.** Self-hosting keeps schedule traffic off
  third-party tracking services. The server fetches the feeds; visitors
  only talk to your server.
- **Handles the details calendars need.** Recurring events, time zones,
  multiple languages, mobile layouts, month/week/day/agenda views, and
  links from events to maps or sign-up pages.
- **Keeps source URLs private when needed.** Feed URLs can be encrypted
  so private calendar links (e.g. a members-only schedule) are not
  exposed in the embed code.

## Cost and control

The project is GPL-licensed open source. A hosted public instance exists
at https://open-web-calendar.hosted.quelltext.eu/. A studio can also run
its own instance with Docker or on common PaaS providers. Self-hosting
works behind a firewall and without Internet access for the viewer.
