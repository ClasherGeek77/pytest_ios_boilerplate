from lib.app.base_page import BasePage
from lib.app.pages.login_page import LoginPage


# xcuitest exposes every widget's a11y name in @name, this app uses its
# ValueKey labels as those names
class HomeLocators:
    login_button = "//XCUIElementTypeButton[@name='Login']"
    logout_button = "//XCUIElementTypeButton[@name='Logout']"
    # the signed-in label is a widget whose a11y name IS the username
    user_label = "//*[@name='{user}']"
    counter_text = "//*[@name='You have pushed the button this many times:']"


# the counter page, the app's root; login state only changes the app bar
class HomePage(BasePage):
    def wait_here(self):
        if not self.is_shown(HomeLocators.login_button, seconds=3):
            self.wait_shown(HomeLocators.logout_button)
        return self

    def is_logged_in(self):
        return self.is_shown(HomeLocators.logout_button)

    def is_signed_out(self):
        return self.is_shown(HomeLocators.login_button)

    def user_shown(self, user):
        return self.is_shown(HomeLocators.user_label.format(user=user))

    def counter_shown(self):
        return self.is_shown(HomeLocators.counter_text)

    def open_login(self):
        self.click(HomeLocators.login_button)
        login = LoginPage(self.driver, self.timeout)
        login.wait_here()
        return login

    def logout(self):
        # retry: a logout tap that does not land would hang the next waits
        return self.click_until_shown(
            HomeLocators.logout_button, HomeLocators.login_button
        )
