def test_logging_in_shows_the_user_in_the_app_bar(signed_out, testdata, assertion):
    login = signed_out.open_login()

    login.enter(username=testdata.standard_user, password=testdata.password).sign_in()

    assertion.assert_true(
        actual_result=signed_out.is_logged_in(), label="logged in after sign in"
    )
    assertion.assert_true(
        actual_result=signed_out.user_shown(testdata.standard_user),
        label="user label shows the name",
    )


def test_logging_out_returns_to_the_signed_out_app_bar(signed_out, testdata, assertion):
    login = signed_out.open_login()
    login.enter(username=testdata.standard_user, password=testdata.password).sign_in()

    signed_out.logout()

    assertion.assert_true(
        actual_result=signed_out.is_signed_out(), label="signed out app bar"
    )


def test_the_counter_page_is_the_home_page_underneath(signed_out, assertion, logger):
    logger.warning("checking the app root is the counter page")

    signed_out.wait_here()

    assertion.assert_true(
        actual_result=signed_out.counter_shown(), label="counter page shown"
    )
