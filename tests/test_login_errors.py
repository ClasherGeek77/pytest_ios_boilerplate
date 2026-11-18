import pytest


def test_opening_login_shows_the_form(signed_out, assertion):
    login = signed_out.open_login()

    assertion.assert_true(actual_result=login.is_displayed(), label="login form shown")


# the data-driven pattern from the reference repo: every refusal in one
# table, expectations referenced as attribute names, ids keep the report
# readable; the state reset in conftest closes the login screen between rows
@pytest.mark.parametrize(
    ("username_attr", "password_attr", "error_attr"),
    [
        (None, None, "error_username_required"),
        ("standard_user", None, "error_password_required"),
        ("standard_user", "wrong_password", "error_no_match"),
        ("unknown_user", "password", "error_no_match"),
        ("locked_out_user", "password", "error_locked_out"),
    ],
    ids=["no-username", "no-password", "no-match", "unknown-user", "locked-out"],
)
def test_refused_logins_show_their_own_error(
    signed_out, testdata, assertion, username_attr, password_attr, error_attr
):
    username = getattr(testdata, username_attr) if username_attr else None
    password = getattr(testdata, password_attr) if password_attr else None

    login = signed_out.open_login()
    login.enter(username=username, password=password)
    login.sign_in()

    assertion.assert_true(
        actual_result=login.error_shown(getattr(testdata, error_attr)),
        label=f"error shown: {error_attr}",
    )


def test_a_refused_login_stays_on_the_login_screen(signed_out, testdata, assertion):
    login = signed_out.open_login()

    login.enter(username=testdata.locked_out_user, password=testdata.password)
    login.sign_in()
    login.error_shown(testdata.error_locked_out)

    assertion.assert_true(actual_result=login.is_still_here(), label="still on login")
