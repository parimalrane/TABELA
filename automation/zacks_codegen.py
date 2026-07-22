import os

from dotenv import load_dotenv
from playwright.sync_api import Playwright, sync_playwright, expect

load_dotenv()

assert os.getenv("ZACKS_USERNAME"), "ZACKS_USERNAME not found"
assert os.getenv("ZACKS_PASSWORD"), "ZACKS_PASSWORD not found"

def run(playwright: Playwright) -> None:
    browser = playwright.chromium.launch(headless=False)
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://www.zacks.com/")
    page.get_by_role("link", name="Sign In").click()
    page.get_by_role("textbox", name="Username or Email Address").click()
    page.get_by_role(
        "textbox",
        name="Username or Email Address"
    ).fill(os.getenv("ZACKS_USERNAME"))

    page.get_by_role(
        "textbox",
        name="Password Password"
    ).fill(os.getenv("ZACKS_PASSWORD"))

    page.get_by_role("button", name="Sign In").click()

    page.wait_for_load_state("networkidle")
    page.get_by_label("main").get_by_role("link", name="Stock Screener").click()
    page.locator("iframe[title=\"Stock Screener \"]").content_frame.get_by_role("tab", name="My Screen").click()
    page.locator("iframe[title=\"Stock Screener \"]").content_frame.get_by_role("link", name="Run").click()
    with page.expect_download() as download_info:
        page.locator("iframe[title=\"Stock Screener \"]").content_frame.locator("a").filter(has_text="CSV").click()
    download = download_info.value
    page.get_by_role("link", name="ETF Screener").click()
    page.locator("iframe[title=\"ETF Screener \"]").content_frame.get_by_role("tab", name="My Screen").click()
    page.locator("iframe[title=\"ETF Screener \"]").content_frame.get_by_role("link", name="Run").click()
    with page.expect_download() as download1_info:
        page.locator("iframe[title=\"ETF Screener \"]").content_frame.locator("a").filter(has_text="CSV").click()
    download1 = download1_info.value
    page.locator("iframe[title=\"ETF Screener \"]").content_frame.locator("body").press("ControlOrMeta+a")
    page.locator("iframe[title=\"ETF Screener \"]").content_frame.locator("body").press("ControlOrMeta+c")
    page.close()

    # ---------------------
    context.close()
    browser.close()


with sync_playwright() as playwright:
    run(playwright)
