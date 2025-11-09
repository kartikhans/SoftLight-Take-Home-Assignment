import os
import re

from playwright.sync_api import sync_playwright, Page, Locator

class StateDetector:
    def __init__(self):
        pass

    def _get_interactive_elements(self, page: Page) -> list[Locator]:
        """
        Helper function to get all interactive elements in a stable, queryable order.
        """

        elements = page.locator(
            "a, button, input, textarea, [role='button'], [role='link'], [role='textbox'], [role='checkbox']"
        ).all()

        visible_elements = []
        seen_text = set()
        for el in elements:
            try:
                if not el.is_visible():
                    continue

                text = (
                        el.text_content() or
                        el.get_attribute("aria-label") or
                        el.get_attribute("placeholder") or
                        el.get_attribute("title")
                )

                if not text:
                    # *** FIX: Use evaluate to get the tag name ***
                    tag = el.evaluate("element => element.tagName.toLowerCase()")
                    if tag == "input":
                        text = el.get_attribute("value") or "input" # Fallback
                    else:
                        continue # Skip elements with no clear identifier

                text = re.sub(r'\s+', ' ', text).strip()

                if text in seen_text and text != "input":
                    continue
                seen_text.add(text)

                visible_elements.append(el)
            except Exception:
                continue
        return visible_elements

    def get_simplified_dom_string(self, page: Page) -> str:
        """
        Gets the simplified DOM string to send to the LLM.
        """
        elements = self._get_interactive_elements(page)
        interactive_strings = []

        for i, el in enumerate(elements):
            agent_id = i + 1 # 1-based indexing for the LLM

            try:
                # *** FIX: Use evaluate to get the tag name ***
                tag = el.evaluate("element => element.tagName.toLowerCase()")

                text = (
                        el.text_content() or
                        el.get_attribute("aria-label") or
                        el.get_attribute("placeholder") or
                        el.get_attribute("title") or
                        (el.get_attribute("value") if tag == "input" else "") # Use tag variable
                )
                text = re.sub(r'\s+', ' ', text).strip()

                interactive_strings.append(
                    f"<element id='{agent_id}' type='{tag}'>{text}</element>"
                )
            except Exception:
                continue # Element may have gone stale

        return "\n".join(interactive_strings)

    def get_element_by_agent_id(self, page: Page, element_id: str) -> Locator | None:
        """
        Finds the Nth element on the page, where N = element_id.
        This re-runs the query, making it robust to re-renders.
        """
        try:
            target_index = int(element_id) - 1
        except ValueError:
            print(f"Error: Invalid element_id '{element_id}'")
            return None

        elements = self._get_interactive_elements(page)

        if 0 <= target_index < len(elements):
            return elements[target_index]
        else:
            print(f"Error: Element with ID {element_id} not found.")
            return None

    def click_element(self, page: Page, element_id: str):
        """
        Finds the element by its ID (index) and clicks it.
        """
        element = self.get_element_by_agent_id(page, element_id)
        if element:
            # Use a more robust click, force=True can help
            element.click(timeout=5000)
        else:
            raise Exception(f"Failed to find element {element_id} to click.")

    def type_in_element(self, page: Page, element_id: str, text: str):
        """
        Finds the element by its ID (index) and types in it.
        """
        element = self.get_element_by_agent_id(page, element_id)
        if element:
            element.fill(text, timeout=5000)
        else:
            raise Exception(f"Failed to find element {element_id} to type in.")

    def press_key(self, page: Page, key: str):
        """
        Presses a key on the keyboard.
        """
        page.keyboard.press(key)

    def capture_screenshot(self, page: Page, path: str):
        """
        Takes a screenshot of the current page state.
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        page.screenshot(path=path, full_page=True)
        print(f"[Browser]: Captured screenshot {path}")