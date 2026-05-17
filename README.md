# Chrome Extension Prospector

A Claude Code skill that turns a single niche keyword into a full Chrome Web Store acquisition pipeline:

1. **Discover** — finds free extensions in your niche with thousands of users (Apify).
2. **Enrich** — pulls the developer email for every hit (100% coverage in testing).
3. **Score** — flags solo devs (Gmail/free email + small studio) vs big companies (auto-skipped).
4. **Offer** — computes a severely lowballed acquisition anchor — designed to invite counter-offers.
5. **Persist** — writes everything to a fresh Google Sheet, auto-named per niche.
6. **Send** — fires personalized, CAN-SPAM-compliant Gmail outreach.

## Install

```bash
/plugin marketplace add akcodez/chrome-extension-prospector
/plugin install chrome-extension-prospector
```

## Usage

```text
/chrome-extension-prospector productivity
/chrome-extension-prospector "screenshot recorder" --threshold 50000
/chrome-extension-prospector ai-writing --dry-run
```

The niche keyword is the only required argument. The skill will:
- Prompt you for sender identity on first run (saved to `~/.chrome-prospector/config.json`)
- Run two Apify actors in parallel
- Filter by user count (default ≥ 10,000)
- Open a Google Sheet with the qualified prospects
- Send the outreach (or draft it with `--dry-run`)

## Setup

Required:

- **`APIFY_API_TOKEN`** environment variable — sign up at https://apify.com.
- **Gmail MCP** connected via `/mcp` for outreach.
- **Google Sheets** — either the `googlesheets-automation` skill (Rube/Composio) or any Sheets MCP. Falls back to a local CSV.

The skill checks for all of these on first run and tells you what's missing.

## How the lowball formula works

| Users | Anchor Offer |
| --- | --- |
| 10k – 50k | $500 – $2,500 |
| 50k – 100k | $2,500 – $8,000 |
| 100k – 500k | $5,000 – $20,000 |
| 500k – 1M | $15,000 – $50,000 |
| 1M+ | $25,000 – $100,000 |

Market rate for free Chrome extensions is roughly $0.50 – $2 per weekly active user. These numbers are deliberately ~5–10× below market — the strategy is to anchor very low, frame the offer as "side project exit cash," and bank on developers counter-offering with a number that's still well below their actual market value.

## Cost expectations

- Apify discovery + enrichment: **~$7.50 per 1,000 prospects scraped** ($3.50 + $3.99).
- A typical 100-extension scrape → ~10–20 qualified prospects: **under $1**.
- Gmail outreach: free under personal Gmail rate limits.

## Compliance

The included email template is **CAN-SPAM compliant** when you fill in your physical mailing address in the config — accurate sender info, non-deceptive subject, physical address in the footer, and a working opt-out (`Reply STOP`). The skill refuses to send if the address field is empty.

By default, the skill **skips EU developers** (heuristic on website TLD) to stay clear of GDPR consent requirements. Pass `--include-eu` to opt in.

## License

MIT
