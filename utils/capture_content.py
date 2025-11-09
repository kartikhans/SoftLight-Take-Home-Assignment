from playwright.sync_api import sync_playwright, Page, Playwright
import time
from config import Config
import re


class CaptureContent:
    def __init__(self, headless=False):
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.headless = headless
        self.is_running = False

    def start_browser(self):
        """Start the browser session"""
        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless, args=["--start-maximized"]
        )
        self.context = self.browser.new_context(viewport={"width": 1280, "height": 720})
        self.is_running = True
        print("Browser started successfully")

    def close_browser(self):
        """Close the browser session"""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()
        self.is_running = False
        print("Browser closed successfully")

    def navigate_to(self, url):
        """Navigate to a URL"""
        if not self.is_running:
            self.start_browser()

        if self.page is None:
            self.page = self.context.new_page()

        print(f"Navigating to: {url}")
        self.page.goto(url, wait_until="domcontentloaded")
        time.sleep(Config.WAIT_TIME)

    def find_and_click(self, target_description):
        """Find and click an element based on description"""
        if not self.page:
            return False

        # Try different strategies to find the element
        strategies = [
            # Strategy 1: Look for buttons with matching text
            lambda: self.page.query_selector(
                f"button:has-text('{target_description}')"
            ),
            # Strategy 2: Look for links with matching text
            lambda: self.page.query_selector(f"a:has-text('{target_description}')"),
            # Strategy 3: Look for elements with aria-label
            lambda: self.page.query_selector(f"[aria-label*='{target_description}']"),
            # Strategy 4: Look for elements with title attribute
            lambda: self.page.query_selector(f"[title*='{target_description}']"),
            # Strategy 5: Look for elements with data-testid containing keywords
            lambda: self._find_by_testid(target_description),
            # Strategy 6: Look for divs with button role
            lambda: self.page.query_selector(
                f"[role='button']:has-text('{target_description}')"
            ),
        ]

        for strategy in strategies:
            try:
                element = strategy()
                if element and element.is_visible():
                    print(f"Found element: {target_description}")
                    element.click()
                    time.sleep(Config.WAIT_TIME)
                    return True
            except Exception as e:
                continue

        print(f"Could not find element: {target_description}")
        return False

    def _find_by_testid(self, description):
        """Find elements by data-testid based on common patterns"""
        keywords = description.lower().split()
        testid_patterns = [f"[data-testid*='{keyword}']" for keyword in keywords]

        for pattern in testid_patterns:
            element = self.page.query_selector(pattern)
            if element and element.is_visible():
                return element
        return None

    def capture_screenshot(self, full_page=True):
        """Capture screenshot of current page state"""
        if not self.page:
            return None

        try:
            screenshot = self.page.screenshot(type="png", full_page=full_page)
            return screenshot
        except Exception as e:
            print(f"Error capturing screenshot: {e}")
            return None

    def get_current_url(self):
        """Get current page URL"""
        return self.page.url if self.page else None

    def wait_for_load(self, timeout=5000):
        """Wait for page to load"""
        if self.page:
            self.page.wait_for_load_state("networkidle", timeout=timeout)

    def get_simplified_dom(self, page: Page) -> str:
        """
        Gets a simplified representation of the DOM, focusing only on
        interactive elements and assigning them a temporary ID.
        """
        # 1. Find all interactive elements
        # Using a broad selector to catch buttons, links, inputs, and custom elements
        elements = page.locator(
            "a, button, input, textarea, [role='button'], [role='link'], [role='textbox']"
        ).all()

        interactive_elements = []
        element_id_counter = 1
        seen_elements_text = set()

        for el in elements:
            try:
                # 2. Get meaningful text
                text = (
                    el.text_content()
                    or el.get_attribute("aria-label")
                    or el.get_attribute("placeholder")
                    or el.get_attribute("title")
                )

                if not text:
                    # For inputs, the 'value' is also important
                    if el.tag_name() == "input":
                        text = el.get_attribute("value") or "input"
                    else:
                        continue  # Skip elements with no clear identifier

                text = re.sub(r"\s+", " ", text).strip()  # Normalize whitespace

                # 3. Filter out duplicates and invisible elements
                if text in seen_elements_text or not el.is_visible():
                    continue

                seen_elements_text.add(text)

                # 4. Assign a temporary ID for the LLM to use
                agent_id = str(element_id_counter)
                el.set_attribute("data-agent-id", agent_id)
                element_id_counter += 1

                # 5. Create a simple string representation
                tag = el.tag_name()
                interactive_elements.append(
                    f"<element id='{agent_id}' type='{tag}'>{text}</element>"
                )

            except Exception:
                continue  # Element might be stale, just skip it

        return "\n".join(interactive_elements)
