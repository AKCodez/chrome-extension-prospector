#!/usr/bin/env python3
"""End-to-end Chrome Web Store prospect builder.

Usage: python prospect.py <niche> [--threshold N] [--limit N] [--out PATH]

Reads APIFY_API_TOKEN from env. Outputs prospects.json with merged
data: name, url, users, rating, reviews, email, offer_low, offer_high, score.
"""
import argparse
import concurrent.futures
import json
import os
import re
import sys
from pathlib import Path

import requests

APIFY_BASE = "https://api.apify.com/v2/acts"
DISCOVERY_ACTOR = "tugelbay~chrome-web-store-intelligence"
ENRICH_ACTOR = "fatihtahta~chrome-webstore-extensions-scraper"

FREE_EMAIL_DOMAINS = {
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com",
    "protonmail.com", "icloud.com", "aol.com", "live.com", "msn.com",
}

BIG_CO_DOMAINS = {
    "google.com", "microsoft.com", "atlassian.com", "salesforce.com",
    "adobe.com", "grammarly.com", "honey.com", "loom.com", "toggl.com",
    "notion.so", "asana.com", "monday.com", "clickup.com", "hubspot.com",
    "zoom.us", "slack.com", "dropbox.com", "evernote.com",
}


def parse_users(value) -> int:
    if not value:
        return 0
    return int(re.sub(r"[^\d]", "", str(value)) or 0)


def lowball_offer(users: int) -> tuple[int, int]:
    if users >= 1_000_000: return 25_000, 100_000
    if users >= 500_000:   return 15_000, 50_000
    if users >= 100_000:   return 5_000, 20_000
    if users >= 50_000:    return 2_500, 8_000
    if users >= 10_000:    return 500, 2_500
    return 0, 0


def _to_float(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _to_int(v):
    f = _to_float(v)
    return int(f) if f is not None else None


def solo_dev_score(email, rating, reviews) -> int:
    if not email:
        return 0
    score = 1
    domain = email.split("@")[-1].lower()
    if domain in BIG_CO_DOMAINS:
        return -5
    if domain in FREE_EMAIL_DOMAINS:
        score += 2
    r = _to_float(rating)
    if r is not None and r >= 4.5:
        score += 1
    n = _to_int(reviews)
    if n is not None and n < 500:
        score += 1
    return score


def run_actor(actor_id: str, payload: dict, token: str, timeout: int = 300) -> list:
    url = f"{APIFY_BASE}/{actor_id}/run-sync-get-dataset-items"
    params = {"token": token, "timeout": timeout}
    resp = requests.post(url, params=params, json=payload, timeout=timeout + 30)
    if resp.status_code >= 400:
        raise RuntimeError(f"Apify {actor_id} failed: {resp.status_code} {resp.text[:300]}")
    return resp.json()


DISCOVERY_MAX_PER_KEYWORD = 25


def discover(niche: str, limit: int, token: str) -> list:
    return run_actor(
        DISCOVERY_ACTOR,
        {
            "searchKeywords": [niche],
            "maxSearchResultsPerKeyword": min(limit, DISCOVERY_MAX_PER_KEYWORD),
        },
        token,
    )


def enrich(niche: str, limit: int, token: str) -> list:
    return run_actor(
        ENRICH_ACTOR,
        {"queries": [niche], "limit": limit},
        token,
    )


def merge(disc: list, enr: list, threshold: int) -> list:
    enr_by_id = {d.get("id"): d for d in enr}
    rows = []
    for d in disc:
        ext_id = d.get("extensionId")
        users = parse_users(d.get("users"))
        if users < threshold:
            continue
        e = enr_by_id.get(ext_id, {})
        email = e.get("developerEmail")
        rating = _to_float(d.get("rating") or e.get("rating"))
        reviews = _to_int(d.get("ratingsCount") or e.get("ratingCount"))
        lo, hi = lowball_offer(users)
        rows.append({
            "id": ext_id,
            "name": d.get("extensionTitle") or e.get("title") or "",
            "url": d.get("extensionUrl") or e.get("url"),
            "users": users,
            "rating": rating,
            "reviews": reviews,
            "category": d.get("category") or "",
            "updated": d.get("updated") or e.get("updated") or "",
            "email": email,
            "developer_website": e.get("developerWebsite") or "",
            "support_url": e.get("supportUrl") or "",
            "privacy_policy": e.get("privacyPolicy") or "",
            "offer_low": lo,
            "offer_high": hi,
            "score": solo_dev_score(email, rating, reviews),
        })
    rows.sort(key=lambda r: (-r["score"], -r["users"]))
    return rows


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("niche")
    ap.add_argument("--threshold", type=int, default=10_000)
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--out", default="prospects.json")
    args = ap.parse_args()

    token = os.environ.get("APIFY_API_TOKEN")
    if not token:
        print("ERROR: APIFY_API_TOKEN environment variable is required.", file=sys.stderr)
        return 2

    print(f"[1/3] Discovery: '{args.niche}' (limit={args.limit})...", file=sys.stderr)
    print(f"[2/3] Enrichment: '{args.niche}' (limit={args.limit})...", file=sys.stderr)
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as ex:
        f_disc = ex.submit(discover, args.niche, args.limit, token)
        f_enr = ex.submit(enrich, args.niche, args.limit, token)
        disc = f_disc.result()
        enr = f_enr.result()

    print(f"  discovery: {len(disc)} results, enrichment: {len(enr)} results", file=sys.stderr)

    print(f"[3/3] Merging, filtering (>={args.threshold:,} users), scoring...", file=sys.stderr)
    rows = merge(disc, enr, args.threshold)

    out_path = Path(args.out)
    out_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")

    qualified_with_email = sum(1 for r in rows if r["email"])
    print(f"\nFound {len(rows)} prospects, {qualified_with_email} with email.", file=sys.stderr)
    print(f"Written to {out_path.resolve()}", file=sys.stderr)

    print(json.dumps({
        "niche": args.niche,
        "total_prospects": len(rows),
        "with_email": qualified_with_email,
        "output_path": str(out_path.resolve()),
        "top_5": rows[:5],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
