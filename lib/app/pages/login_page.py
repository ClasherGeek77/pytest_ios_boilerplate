from lib.app.base_page import BasePage


class LoginLocators:
    # this flutter version maps the password field to a plain TextField
    # too, so the a11y name is what separates them, not the type
    username_field = "//XCUIElementTypeTextField[@name='Username']"
    # an xpath, not a secret
    password_field = "//XCUIElementTypeTextField[@name='Password']"  # nosec B105
    sign_in_button = "//XCUIElementTypeButton[@name='Sign In']"
    back_button = "//XCUIElementTypeButton[@name='Back']"
    # the error line is a node whose a11y name is the app's own sentence
    error = '//*[@name="{message}"]'


class LoginPage(BasePage):
    def wait_here(self):
        self.wait_shown(LoginLocators.username_field)
        return self

    def enter(self, username=None, password=None):
        if username is not None:
            self.send_text(LoginLocators.username_field, username)
        if password is not None:
            self.send_text(LoginLocators.password_field, password)
        return self

    def sign_in(self):
        self.click(LoginLocators.sign_in_button)
        return self

    def error_shown(self, message):
        return self.is_shown(LoginLocators.error.format(message=message))

    def is_still_here(self):
        return self.is_shown(LoginLocators.sign_in_button, seconds=3)

    def is_displayed(self):
        return self.is_shown(LoginLocators.username_field) and self.is_shown(
            LoginLocators.password_field
        )

    # the back arrow pops this screen without touching the session,
    # with the same click-retry because a dropped back tap hangs everything
    def leave(self):
        from lib.app.pages.home_page import HomePage, HomeLocators

        home = HomePage(self.driver, self.timeout)
        self.click_until_shown(LoginLocators.back_button, HomeLocators.login_button)
        return home
