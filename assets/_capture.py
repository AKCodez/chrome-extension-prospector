"""Capture real flow screenshots via Playwright."""
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT = Path(__file__).parent

URLS = {
    "store-search.png":  ("https://chromewebstore.google.com/search/productivity",                                                 1440, 1100),
    "store-detail.png":  ("https://chromewebstore.google.com/detail/maketime-increase-product/afhokbldaaeggpigpijmomaooflpikji",   1440, 1100),
}


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        for name, (url, w, h) in URLS.items():
            page = browser.new_page(viewport={"width": w, "height": h})
            try:
                page.goto(url, wait_until="networkidle", timeout=45000)
            except Exception as e:
                print(f"[{name}] navigate warning: {e}")
            page.wait_for_timeout(2500)
            out_path = OUT / name
            page.screenshot(path=str(out_path), full_page=False)
            print(f"[{name}] saved -> {out_path}")
            page.close()
        browser.close()


if __name__ == "__main__":
    main()
