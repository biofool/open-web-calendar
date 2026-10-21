# SPDX-FileCopyrightText: 2024 Nicco Kunzmann and Open Web Calendar Contributors <https://open-web-calendar.quelltext.eu/>
#
# SPDX-License-Identifier: GPL-2.0-only
"""Handle calendars from ICS links."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

import icalendar
import recurring_ical_events

from open_web_calendar.calendars.base import Calendars
from open_web_calendar.calendars.errors import InvalidCalendars

if TYPE_CHECKING:
    from datetime import datetime

log = logging.getLogger(__name__)

# Upper bound on recurrences one VEVENT may expand to — a hostile RRULE
# (FREQ=SECONDLY over a year, or COUNT=99999999) turns a single request
# into a CPU/memory sink.
_MAX_RRULE_EXPANSIONS = 100_000
_FREQ_PER_DAY = {
    "SECONDLY": 86400.0,
    "MINUTELY": 1440.0,
    "HOURLY": 24.0,
    "DAILY": 1.0,
    "WEEKLY": 1 / 7,
    "MONTHLY": 1 / 30,
    "YEARLY": 1 / 365,
}


def _rrule_value(rrule, key, default):
    v = rrule.get(key)
    if v is None:
        return default
    return v[0] if isinstance(v, list) else v


def _exceeds_recurrence_cap(event: icalendar.Event, query_end) -> bool:
    """Estimate whether an event's RRULE can exceed the expansion cap."""
    rrule = event.get("RRULE")
    if rrule is None:
        return False
    try:
        count = _rrule_value(rrule, "COUNT", None)
        if count is not None:
            return int(count) > _MAX_RRULE_EXPANSIONS
        freq = str(_rrule_value(rrule, "FREQ", "DAILY")).upper()
        interval = max(1, int(_rrule_value(rrule, "INTERVAL", 1)))
        per_day = _FREQ_PER_DAY.get(freq)
        if per_day is None:
            return True  # unknown frequency — refuse to expand unbounded
        dtstart = event.get("DTSTART")
        if dtstart is None or not hasattr(dtstart.dt, "toordinal"):
            return True  # cannot bound the expansion
        until = _rrule_value(rrule, "UNTIL", None)
        until_ord = until.toordinal() if hasattr(until, "toordinal") else None
        # Bounded by UNTIL when present, else by the query window's end.
        span_end_ord = (
            until_ord
            if until_ord is not None
            else (query_end.toordinal() if hasattr(query_end, "toordinal") else None)
        )
        if span_end_ord is None:
            return True
        days = max(0, span_end_ord - dtstart.dt.toordinal())
        return days * per_day / interval > _MAX_RRULE_EXPANSIONS
    except (TypeError, ValueError, AttributeError):
        return True  # unparseable RRULE — refuse rather than burn CPU


class ICSCalendars(Calendars):
    """Wrapper to handle ICS calendars."""

    @classmethod
    def from_text(cls, text: str):
        """Create ICS calendars from the text of a calendar file."""
        result = cls()
        result.add_from_text(text)
        return result

    def __init__(self):
        """Handle ICS calendars in a unified way."""
        self._calendars: list[icalendar.Calendar] = []

    def add_from_text(self, text: str):
        """Add ICS calendars from text."""
        try:
            self._calendars.extend(icalendar.Calendar.from_ical(text, multiple=True))
        except ValueError as e:
            raise InvalidCalendars(
                "The content of this URL is not an ICS calendar."
            ) from e

    def __bool__(self):
        """If we have any content."""
        return bool(self._calendars)

    def get_events_between(
        self, start: datetime, end: datetime
    ) -> list[icalendar.Event]:
        events = []
        for calendar in self._calendars:
            # Drop VEVENTs whose RRULE would expand beyond the cap —
            # expanding them is a CPU/memory DoS per request.
            filtered = icalendar.Calendar()
            for comp in calendar.subcomponents:
                if comp.name == "VEVENT" and _exceeds_recurrence_cap(comp, end):
                    log.warning(
                        "skipping VEVENT with excessive RRULE expansion: %s",
                        comp.get("SUMMARY", "?"),
                    )
                    continue
                filtered.add_component(comp)
            events.extend(
                recurring_ical_events.of(filtered).between(start, end)
            )
        return events

    def get_icalendars(self) -> list[icalendar.Calendar]:
        return self._calendars[:]


__all__ = ["ICSCalendars"]
