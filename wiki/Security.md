# Security — open-web-calendar

Fork of niccokunzmann/open-web-calendar. 2026-10 audit: `eval()` in dhtmlx locale converter sandboxed (dict-only builtins) — upstream PR https://github.com/niccokunzmann/open-web-calendar/pull/1266 .

## Standing rules
- Never commit secrets (`.env`, `*.key`, `credentials*.json` are gitignored).
- Never read or log secret values — key names and lengths only.
- Security fixes land reviewed-but-uncommitted first, then roll dev → main.
