---
name: chrome-extension-prospector
description: "Find free Chrome Web Store extensions in a given niche that have thousands of users, pull their developer emails, compute severely lowballed acquisition offers, write the prospect list to a Google Sheet, and auto-send Gmail outreach. Use when the user wants to identify Chrome extension acquisition targets, build a prospect list, or run cold-outreach acquisition campaigns. The niche keyword is the only required argument."
argument-hint: "<niche> [--threshold N] [--limit N] [--dry-run]"
---

# Chrome Extension Prospector

End-to-end acquisition prospecting for Chrome Web Store extensions.

Given a niche keyword (e.g. `productivity`, `screenshot`, `ai writer`), the skill discovers extensions, enriches with developer emails, filters by user count, computes lowballed acquisition offers, writes everything to a fresh Google Sheet, and auto-sends personalized Gmail outreach.

## Required environment

Before the skill can run, verify these are configured. If anything is missing, stop and tell the user what to set up — do not guess.

1. **`APIFY_API_TOKEN`** environment variable — required for the two Apify actors used for scraping. Sign up at https://apify.com (free tier covers small runs).
2. **Gmail MCP** — connected via `/mcp` so outreach can be sent. Without it, run in `--dry-run` mode (drafts only, no send).
3. **Google Sheets access** — either the `googlesheets-automation` skill (Rube/Composio) or a Sheets MCP. Without it, the skill writes a local CSV instead.
4. **Sender config file** — `~/.chrome-prospector/config.json` with sender identity for CAN-SPAM compliance. If missing, prompt the user once (see Setup below), then save it.

## Setup (first run only)

If `~/.chrome-prospector/config.json` does not exist:

1. Ask the user for these values **once**:
   - Sender name (e.g. "Aria")
   - Sender email (the From: address; must be reachable)
   - Reply-to email (usually same as sender)
   - Company / studio name (appears in footer)
   - **Full physical mailing address** (required by CAN-SPAM — without it, do not send)
2. Write the values to `~/.chrome-prospector/config.json` using the schema in `config.example.json`.
3. Confirm the saved config back to the user.

## Workflow

When invoked with a niche argument, follow this sequence. Always read the niche from `$1` or the user's most recent message. Default threshold is 10,000 users; default limit is 100 per actor.

### Step 1 — Run the prospect pipeline

Run the Python script. It calls both Apify actors in parallel, merges by extension ID, filters by user threshold, scores each prospect for solo-dev signals, and computes a lowballed offer range.

```powershell
python "${SKILL_DIR}\scripts\prospect.py" "<niche>" --threshold 10000 --limit 100 --out "${SKILL_DIR}\prospects.json"
```

The script's stdout is a JSON object with `total_prospects`, `with_email`, `output_path`, and `top_5`. The full prospect list is at the `output_path`. Report the count and top 5 to the user before continuing.

### Step 2 — Show the user the lowball strategy

Print a short table showing the top prospects (name, users, rating, score, offer range, email). The offer ranges are intentionally aggressive ("severely lowball") — the strategy is to anchor low and bank on counter-offers. Do not soften the numbers.

The valuation tiers used:

| Users | Anchor Offer |
| --- | --- |
| 10k – 50k | $500 – $2,500 |
| 50k – 100k | $2,500 – $8,000 |
| 100k – 500k | $5,000 – $20,000 |
| 500k – 1M | $15,000 – $50,000 |
| 1M+ | $25,000 – $100,000 |

Market rate is ~5–10× these numbers. The lowball is an anchor that invites a counter-offer.

### Step 3 — Create the Google Sheet

Create a new Google Sheet named `Chrome Prospects - <niche> - YYYY-MM-DD` (use today's date). Headers, in order:

`Name | URL | Users | Rating | Reviews | Category | Updated | Email | Developer Site | Offer Low | Offer High | Score | Status | Sent At | Reply`

Then add one row per prospect from `prospects.json`, sorted by score then user count (already sorted by the script). Initial `Status` is `pending`; `Sent At` and `Reply` are blank.

Use the `googlesheets-automation` skill or whatever Sheets MCP is wired up. If neither is available, write a CSV to `${SKILL_DIR}\prospects-<niche>-<date>.csv` and tell the user.

### Step 4 — Render and send outreach

For every prospect that has a non-empty `email` field and `score > 0` (skip the big-company flags with score -5):

1. Render `templates/email.md` by substituting:
   - `{{name}}`, `{{users_formatted}}` (e.g. "10,000"), `{{rating}}`, `{{category_short}}`
   - `{{offer_low_formatted}}`, `{{offer_high_formatted}}` (with thousands separators)
   - `{{sender_name}}`, `{{sender_email}}`, `{{company}}`, `{{address}}` from `~/.chrome-prospector/config.json`
2. The first line of the template is `SUBJECT: ...` — extract that as the email subject, send the rest as the body.
3. Send via Gmail MCP to the prospect's `email`. From: `{{sender_email}}`, Reply-To: `{{reply_to}}`.
4. Mark the row in the Sheet as `Status: sent`, `Sent At: <ISO timestamp>`.

**Pacing:** the default is send-all-immediately. If the user passes `--rate-limit N` (or there are more than ~30 prospects), batch into 30/day chunks across business hours to avoid Gmail spam flagging.

**Dry-run mode (`--dry-run`):** do everything except the final send — create the Sheet, render every email body, but write the rendered body to the `Status` column as `draft: <first 60 chars>` instead of sending. Use this for first-time campaigns to sanity-check the template before going live.

### Step 5 — Summarize

After completing, give the user:
- Total prospects found / qualified / emailed
- Total dollar value of all anchor offers combined (sum of `offer_high`)
- Sheet URL
- Any prospects that failed to send (with reason)

## Safety rails

- **CAN-SPAM:** the email template includes the required physical address and opt-out. Never send if `~/.chrome-prospector/config.json` is missing the `address` field.
- **GDPR:** if a prospect's developer website domain ends in `.eu` or a known EU TLD (`.de`, `.fr`, `.it`, `.es`, `.nl`, `.se`, `.pl`, etc.), skip them by default unless the user passes `--include-eu`.
- **Big-company filter:** prospects with `score == -5` (email domain matches a known big-co like toggl.com, grammarly.com) are excluded from the send list automatically. They still appear in the Sheet for reference, marked `Status: skipped (big-co)`.
- **Deduplication:** before sending, check the Sheet for the prospect's email — if it was already contacted in a prior run (any sheet matching `Chrome Prospects - *`), skip and mark `Status: skipped (already-contacted)`. Tell the user the count of dedupes.

## Argument parsing

- `<niche>` — required. Free-text keyword. Examples: `productivity`, `screenshot recorder`, `ai writing`, `seo tools`.
- `--threshold N` — minimum user count. Default 10000.
- `--limit N` — max results per Apify actor (controls cost). Default 100. Cost is ~$0.0075 per result across both actors.
- `--dry-run` — render everything but don't send emails.
- `--include-eu` — opt-in to emailing EU developers (GDPR risk).
- `--rate-limit N` — cap emails sent per day. Default unlimited.

## Cost expectations

- Apify discovery + enrichment: **~$7.50 per 1,000 prospects scraped** ($3.50 + $3.99).
- Gmail send: free under personal Gmail rate limits (~500/day).
- A typical campaign of 100 scraped → ~10–20 qualified prospects: **under $1**.
