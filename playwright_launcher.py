# Justin Maxwell

# PLAYWRIGHT LAUNCHER
    # Function that opens the Chrome browser, goes to FirstIgnite, uploads the disclosure (in a for loop), and calls the function to create the sell sheet pdf

# IMPORTS
from playwright.sync_api import sync_playwright
import platform
import asyncio

def setup_windows_event_loop():
    """Setup Windows-specific event loop policy to avoid asyncio issues."""
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Function that opens the Chrome browser, goes to FirstIgnite, uploads the disclosure (in a for loop), and calls the function to create the sell sheet pdf
def run(p):
    # Setup Windows event loop if needed
    setup_windows_event_loop()
    
    if platform.system() == "Windows":
        # Windows-specific configuration to avoid asyncio issues
        browser = p.chromium.launch(
            headless=False,  # Keep visible for manual login
            args=[
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-software-rasterizer",
                "--disable-web-security",
                "--disable-features=VizDisplayCompositor"
            ]
        )
    else:
        # Mac/Linux standard configuration
        browser = p.chromium.launch(
            headless=False,  # Keep visible for manual login
            args=["--disable-blink-features=AutomationControlled"]
        )
    context = browser.new_context()
    page = context.new_page()
    return browser, context, page
