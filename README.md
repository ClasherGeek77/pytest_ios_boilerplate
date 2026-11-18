# pytest_ios_boilerplate

## what it is

a starter project for iOS app tests with Python, pytest and Appium 2 (XCUITest driver), running on the Xcode iOS simulator. it ships with 10 working tests against a small Flutter demo app (login errors, login, logout, home screen), so you can run a real mobile suite and then copy the structure for your own app.

- the app under test is downloaded for you by `./fetch_app.sh` (no Flutter, no compiling): https://github.com/ClasherGeek77/mobile_app_mock/releases/tag/v1.0.0
- locators are plain xpaths on `@name` (the accessibility name), kept in `Locators` classes inside the page files
- one Appium session per run, an automatic reset before every test
- the session fixtures start what is missing: the Appium server and the simulator

source: https://github.com/ClasherGeek77/pytest_ios_boilerplate

## when to use it

use it when you want to learn or start an iOS suite in Python with a clean layout (fixtures, page objects, constants, reports). it is macOS only: the iOS simulator exists only inside Xcode.

not for:

- Android (or any non-Mac machine): use https://github.com/ClasherGeek77/pytest_android_boilerplate (same tests, same layout)
- the same tests in Katalon Studio: use https://github.com/ClasherGeek77/katalon_ios_boilerplate
- browser tests: https://github.com/ClasherGeek77/pytest_web_boilerplate; api tests: https://github.com/ClasherGeek77/pytest_api_boilerplate
- real devices, parallel sessions, docker, ci: left out on purpose

## what you need

| thing | version | where |
|---|---|---|
| macOS with Xcode | Xcode 12.4 with its iOS 14.4 simulator runtime was used (the last Xcode for macOS 10.15). a newer Xcode needs a newer xcuitest driver: not verified here | App Store / https://developer.apple.com/xcode/ |
| Python | 3.11 (the line in `.python-version`, 3.11.14; `first_setup.sh` refuses other lines) | https://www.python.org/downloads/ |
| Node.js | 18 or newer (Appium 2.11.5 declares `^14.17 || ^16.13 || >=18` and npm 8+; Node 22 was used) | https://nodejs.org/ |
| Appium | 2.11.5 | `npm install -g appium@2.11.5` |
| Appium driver | xcuitest 5.6.0 | `appium driver install xcuitest@5.6.0` |
| a simulator | named `iPhoneSE14`, iPhone SE (2nd generation), iOS 14.4 | see "pick or create the simulator" |
| git, bash, curl, unzip | any | macOS |

why xcuitest 5.6.0: newer xcuitest drivers build a newer WebDriverAgent that failed with `xcodebuild` code 65 on Xcode 12.4, 5.6.0 is the version that built and ran. the app is an x86_64 simulator build, so it targets an Intel Mac; Apple silicon is not verified. python packages (Appium-Python-Client 3.1.1, selenium 4.52.0, pytest 7.4.4, pytest-html, requests, black, bandit, pylint) are pinned in `requirements.pip`.

### install Appium 2 and the driver

```bash
npm install -g appium@2.11.5
appium driver install xcuitest@5.6.0
appium driver list --installed
```

you should see `xcuitest@5.6.0 [installed (npm)]`. check the server: `appium --version` prints `2.11.5`. make sure Xcode is the active developer directory:

```bash
xcode-select -p        # /Applications/Xcode.app/Contents/Developer
xcodebuild -version
```

the first Appium session builds WebDriverAgent with `xcodebuild`, which takes a while and needs Xcode's license accepted (`sudo xcodebuild -license accept`).

### pick or create the simulator

the suite boots the simulator named in `SIM_NAME` (default `iPhoneSE14`) when none is booted, and runs on whichever simulator is already booted. list what you have:

```bash
xcrun simctl list runtimes
xcrun simctl list devices
```

to create the one the suite names (iPhone SE 2nd generation on the iOS 14.4 runtime):

```bash
xcrun simctl create iPhoneSE14 "iPhone SE (2nd generation)" com.apple.CoreSimulator.SimRuntime.iOS-14-4
```

it prints the new device UDID. to use a different simulator or iOS version, set `SIM_NAME` and `SIM_PLATFORM_VERSION` in `test.env` (the version must match the runtime of that simulator, e.g. `17.5`), after checking `xcrun simctl list runtimes` for the real runtime id. other versions than 14.4 were not run here.

## quick start

```bash
git clone https://github.com/ClasherGeek77/pytest_ios_boilerplate.git
cd pytest_ios_boilerplate
./first_setup.sh
```

`first_setup.sh` builds `.venv`, installs `requirements.pip` and runs `./fetch_app.sh`, which downloads `ted_mobile_app_test-v1.0.0-ios-simulator.zip` into `apps/` (git-ignored), checks it against the release `SHA256SUMS.txt` and unzips `apps/Runner.app` (bundle id `net.ted.flutterApp`). you should see `ok  ted_mobile_app_test-v1.0.0-ios-simulator.zip`, `app ready in apps/`, then `Setup done, next run ./run_test.sh`. `APP_VERSION=<tag> ./fetch_app.sh` picks another release tag.

check what exists without a simulator:

```bash
.venv/bin/python -m pytest --collect-only -q
```

you should see `10 tests collected` (login errors 7, session 3).

then run one test (this boots the simulator if none is booted, and builds WebDriverAgent on the first run):

```bash
./run_test.sh tests/test_login_errors.py::test_opening_login_shows_the_form
```

you should see the log lines `starting the appium server` (if none answers), `booting the iPhoneSE14 simulator` (if none is booted), `installing .../apps/Runner.app` (first time), then `1 passed`. the HTML report is `reports/report_<timestamp>_<test path>.html`. the whole suite:

```bash
./run_test.sh
```

ends in `10 passed`; it is slow (about 18 minutes was measured on an older Intel Mac, one session on the simulator). the simulator is left running afterwards, close it with `xcrun simctl shutdown all`. these runs were not repeated while writing this README (collection was).

## run one test, or a few

`run_test.sh` takes any pytest argument; an argument replaces the default `TEST_PATH="tests/"` at the top of the script. the variants:

```bash
./run_test.sh tests/test_login_errors.py                                        # one file
./run_test.sh tests/test_login_errors.py::test_opening_login_shows_the_form     # one test
./run_test.sh "tests/test_login_errors.py::test_refused_logins_show_their_own_error[locked-out]"   # one row of a table test
./run_test.sh tests/ -k locked                                                  # names containing "locked"
./run_test.sh tests/ -x                                                         # stop at the first failure
```

edit `TEST_PATH` or `REPORT_NAME` (for example `smoke.html`) at the top of `run_test.sh` to change the defaults. `./checks.sh` runs bandit, black and pylint.

## settings

plain `KEY=value` lines in `test.env`, loaded by `run_test.sh`; the tests read them through `lib/constants.py`.

| key | default | meaning |
|---|---|---|
| `SERVER_URL` | `http://127.0.0.1:4723` | the Appium server. if nothing answers on `/status` the session starts `appium` on that port (with `DEVELOPER_DIR` set to `/Applications/Xcode.app/Contents/Developer` unless you set it) and stops it after the run |
| `SIM_NAME` | `iPhoneSE14` | the simulator to boot when none is booted |
| `SIM_PLATFORM_VERSION` | `14.4` | iOS version passed to Appium, must match the simulator |
| `IOS_APP` | `apps/Runner.app` | the app bundle; installed on the booted simulator when the bundle id is missing there |
| `BUNDLE_ID` | `net.ted.flutterApp` | the app under test |
| `UI_TIMEOUT` | `40` in `test.env` (20 if unset) | seconds a normal wait accepts; the simulator is slow, 20 was flaky |
| `NEW_COMMAND_TIMEOUT` | `300` | Appium session idle timeout |
| `APPIUM_BIN` | `appium` from PATH, else `~/.local/bin/appium` | path of the Appium executable |

## why there is no accessibility enabler here

on Android, Flutter draws its whole screen in one view and the widget tree only becomes visible to Appium when an accessibility service is running, so the Android twin installs a small helper app (`a11y-enabler.apk`, from the same mobile_app_mock release) first. on iOS the Flutter debug build publishes its semantics to the accessibility tree under XCUITest by itself, so nothing like that is needed and `fetch_app.sh` only downloads the app. details of the Android helper: https://github.com/ClasherGeek77/pytest_android_boilerplate

three quirks of this Flutter app on XCUITest, each handled inside `lib/`, never visible in a test:

1. typing: the nodes accept no `setValue` and `send_keys` silently does nothing, so `BasePage.send_text` checks the value afterwards and, when it did not land, touches and holds the field, sets the clipboard and taps `Paste` (needs `appium:allowInsecure=["clipboard"]`, set in `conftest.py`). a native app's fields take the direct `send_keys` path.
2. dropped taps: XCUITest sometimes reports a button clickable while the tap does not land, so app-bar transitions use `click_until_shown` with three bounded tries.
3. the password field is a plain `XCUIElementTypeTextField` here, so fields are found by `@name` (the accessibility label), not by element type.

## how to read the code

```
conftest.py                    fixtures: appium_server, simulator, driver, home_page, login_page, signed_out (autouse), testdata, assertion, logger
lib/constants.py               environment_data (from test.env) and constant_data (the app's own error sentences, users, password)
lib/assertion.py               the only place with a bare `assert`; every check is logged
lib/app/base_page.py           BasePage: click, send_text (+ paste fallback), click_until_shown, wait_shown, is_shown; xpaths only
lib/app/pages/home_page.py     HomePage and its Locators (Login / Logout buttons, user label, counter)
lib/app/pages/login_page.py    LoginPage and LoginLocators (fields, Sign In, Back, error line)
tests/test_login_errors.py     form shown, refused logins as one table, still on the login screen
tests/test_session.py          login shows the user, logout, counter page is home
apps/                          downloaded app (git-ignored)
```

the fixture chain: `appium_server` -> `simulator` (reuses a booted one, else boots `SIM_NAME`, installs the app if missing, returns the UDID) -> `driver` (one session for the whole run, `forceAppLaunch` restarts the app). `signed_out` runs before every test: it closes a login screen left open (Back) and logs out if logged in, so tests do not depend on each other. a test asks for `signed_out` (it returns the `HomePage`), `testdata` and `assertion`.

locators: every widget's accessibility name is its `@name`. the two fields are told apart by name, not by type:

```python
class LoginLocators:
    username_field = "//XCUIElementTypeTextField[@name='Username']"
    sign_in_button = "//XCUIElementTypeButton[@name='Sign In']"
    error = '//*[@name="{message}"]'
```

## how to add a test

example: after logging in, the app bar shows the user name (this is `test_logging_in_shows_the_user_in_the_app_bar`).

1. value: add anything static to `constant_data` in `lib/constants.py` and expose it in `TestData` in `conftest.py` (copy a line, `self.x = constant_data["x"]`). users, password and the error sentences are already there.
2. locator: add the xpath to the page's `Locators` class in `lib/app/pages/home_page.py` or `login_page.py`, using `@name`.
3. action: add a method on the page class that uses the `BasePage` verbs (`click`, `click_until_shown`, `send_text`, `wait_shown`, `is_shown`) and returns the next page or a boolean. see the existing `HomePage` methods (`is_logged_in`, `user_shown`, `open_login`, `logout`).
4. test: add a function in `tests/test_session.py` (or a new `tests/test_<area>.py`), asking for the fixtures it needs. the existing one:

```python
def test_logging_in_shows_the_user_in_the_app_bar(signed_out, testdata, assertion):
    login = signed_out.open_login()

    login.enter(username=testdata.standard_user, password=testdata.password).sign_in()

    assertion.assert_true(
        actual_result=signed_out.is_logged_in(), label="logged in after sign in"
    )
```

   several refusals of one rule go in one `@pytest.mark.parametrize` table, see `test_refused_logins_show_their_own_error` in `tests/test_login_errors.py`.
5. run just that test, then the checks:

```bash
./run_test.sh tests/test_session.py::test_logging_in_shows_the_user_in_the_app_bar
./checks.sh
```

a new screen means a new file in `lib/app/pages/` (copy `login_page.py`).

## if it breaks

| symptom | cause | fix |
|---|---|---|
| `no python 3.11 found` | `first_setup.sh` needs the Python 3.11 line | install it, or `TEST_PYTHON=/path/to/python3.11 ./first_setup.sh` |
| `checksum mismatch for apps/...` or a failed download | interrupted download, no internet | run `./fetch_app.sh` again (it deleted the bad file) |
| `the appium server did not answer within 30 seconds` | `appium` not found, or Xcode not selected | `appium --version`; set `APPIUM_BIN` in `test.env`; `xcode-select -p` |
| `the simulator did not boot within 120 seconds` | no simulator with that name | `xcrun simctl list devices` must show `SIM_NAME`; create it (see above) |
| `... is not installed and .../apps/Runner.app is missing` | `apps/` is empty | run `./fetch_app.sh` |
| session creation fails with `xcodebuild failed with code 65` | the WebDriverAgent of the installed driver does not build with your Xcode | use the pinned pair (Xcode 12.4 with xcuitest 5.6.0), or try the driver version that matches your Xcode: not verified |
| a wait times out on the first test | slow simulator, WebDriverAgent still starting | raise `UI_TIMEOUT` in `test.env`; re-run |
| a tap seems to do nothing | XCUITest dropped the tap | the lib retries the app-bar buttons; for new buttons use `click_until_shown` |
| text was not typed | `send_keys` is a silent no-op on this app | `send_text` already falls back to paste; check `allowInsecure=["clipboard"]` if you changed the capabilities |

debugging many failures: reproduce one failing interaction as a small standalone snippet, fix it, re-run only that test, and run the whole suite last. never run an Android emulator and the simulator at the same time on a small machine.

## next

- the Android twin: https://github.com/ClasherGeek77/pytest_android_boilerplate
- the app under test and its releases: https://github.com/ClasherGeek77/mobile_app_mock
- the same app in Katalon Studio: https://github.com/ClasherGeek77/katalon_ios_boilerplate
- the same layout for api and web: https://github.com/ClasherGeek77/pytest_api_boilerplate and https://github.com/ClasherGeek77/pytest_web_boilerplate
