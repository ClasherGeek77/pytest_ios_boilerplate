import logging

from appium.webdriver.common.appiumby import AppiumBy
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

logger = logging.getLogger("page")

XPATH = AppiumBy.XPATH

PASTE_BUTTON = "//XCUIElementTypeButton[@name='Paste']"


# what every page can do, xpaths only, nothing xcuitest specific beyond
# the paste fallback below, so the shape fits any app whose screen the
# accessibility tree exposes
class BasePage:
    def __init__(self, driver, timeout):
        self.driver = driver
        self.timeout = timeout
        self.wait = WebDriverWait(driver, timeout)

    def click(self, xpath):
        logger.info(f"clicking {xpath}")
        self.wait.until(EC.element_to_be_clickable((XPATH, xpath))).click()

    def send_text(self, xpath, value):
        logger.info(f"typing into {xpath}")
        field = self.wait.until(EC.presence_of_element_located((XPATH, xpath)))
        field.send_keys(value)
        if field.get_attribute("value") == value:
            return
        # xcuitest accepts send_keys on this app's flutter fields but the
        # value never lands (no UIAccessibilitySetValue behind them), so
        # paste it the way a person long-presses
        self._paste_into(field, value)

    # touch and hold opens the edit menu, paste fills from the clipboard,
    # and the menu closing is the proof the paste took
    def _paste_into(self, field, value):
        logger.info(f"pasting into the field instead: {value!r}")
        rect = field.rect
        self.driver.execute_script(
            "mobile: touchAndHold",
            {
                "x": rect["x"] + rect["width"] // 2,
                "y": rect["y"] + rect["height"] // 2,
                "duration": 1.3,
            },
        )
        paste = WebDriverWait(self.driver, self.timeout).until(
            EC.presence_of_element_located((XPATH, PASTE_BUTTON)),
            message="paste menu did not open",
        )
        self.driver.set_clipboard(value.encode("utf-8"))
        paste.click()
        WebDriverWait(self.driver, self.timeout).until(
            EC.invisibility_of_element_located((XPATH, PASTE_BUTTON)),
            message=f"paste menu did not close after pasting {value!r}",
        )

    # xcuitest sometimes reports a button clickable yet the tap does not
    # land, so a click that must change the screen retries until the new
    # screen shows, bounded by tries
    def click_until_shown(self, click_xpath, shows_xpath, tries=3, seconds=5):
        for attempt in range(tries):
            logger.info(f"clicking for state change, try {attempt + 1}: {click_xpath}")
            self.click(click_xpath)
            if self.is_shown(shows_xpath, seconds=seconds):
                return self
        raise AssertionError(
            f"{shows_xpath} never appeared after clicking {click_xpath} {tries} times"
        )

    # a wait: this thing is on screen or the test fails on TimeoutException
    def wait_shown(self, xpath):
        logger.info(f"waiting for {xpath}")
        self.wait.until(EC.presence_of_element_located((XPATH, xpath)))

    # a probe, not a wait: is this thing on screen right now, True or False
    def is_shown(self, xpath, seconds=10):
        logger.info(f"checking shown: {xpath}")
        try:
            WebDriverWait(self.driver, seconds).until(
                EC.presence_of_element_located((XPATH, xpath))
            )
            return True
        except TimeoutException:
            return False
