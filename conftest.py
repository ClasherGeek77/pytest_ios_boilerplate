import json
import logging
import os
import shutil
import subprocess  # nosec B404
import time

import pytest
import requests
from appium import webdriver
from appium.options.ios import XCUITestOptions

from lib.app.pages.home_page import HomePage
from lib.app.pages.login_page import LoginLocators
from lib.assertion import Assertion
from lib.constants import constant_data, environment_data

logger = logging.getLogger(__name__)

# absolute path, so bandit never sees a partial executable in a subprocess
XCRUN = shutil.which("xcrun") or "/usr/bin/xcrun"

# toolchain binaries live outside the usual PATH on this machine
EXTRA_PATH = os.pathsep.join(
    [os.path.dirname(environment_data["appium_bin"]), "/usr/local/bin"]
)


def appium_is_up():
    try:
        answer = requests.get(environment_data["server_url"] + "/status", timeout=3)
        return answer.json()["value"]["ready"]
    except (requests.RequestException, ValueError, KeyError):
        return False


# normally the appium server of this machine runs already, when it does not
# the session starts it itself (with the env the ios driver needs) and
# stops it again after the run
# pylint: disable-next=consider-using-with
@pytest.fixture(scope="session")
def appium_server():
    if appium_is_up():
        logger.info(f"appium server is answering on {environment_data['server_url']}")
        yield
        return
    server_env = dict(os.environ)
    server_env["PATH"] = EXTRA_PATH + os.pathsep + server_env.get("PATH", "")
    server_env["DEVELOPER_DIR"] = os.environ.get(
        "DEVELOPER_DIR", "/Applications/Xcode.app/Contents/Developer"
    )
    port = environment_data["server_url"].rsplit(":", 1)[-1]
    logger.info(f"starting the appium server on port {port}")
    process = subprocess.Popen(  # pylint: disable=consider-using-with  # nosec B603
        [environment_data["appium_bin"], "--port", port],
        env=server_env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )
    deadline = time.time() + 30
    while time.time() < deadline and not appium_is_up():
        time.sleep(1)
    if not appium_is_up():
        process.terminate()
        raise RuntimeError("the appium server did not answer within 30 seconds")
    yield
    process.terminate()
    process.wait(timeout=10)


def simctl_json(*args):
    # pylint: disable-next=consider-using-with
    out = subprocess.run(  # nosec B603 - fixed arguments, local device tooling
        [XCRUN, "simctl", *args, "-j"],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    return json.loads(out.stdout) if out.returncode == 0 else {}


def booted_udid():
    data = simctl_json("list", "devices", "booted")
    for devices in data.get("devices", {}).values():
        for device in devices:
            if device.get("state") == "Booted":
                return device["udid"]
    return None


# the simulator: reuse the booted iPhoneSE14, boot it when it is dark and
# leave it up afterwards, same policy as the android emulator fixture
# (cold boots stay opt-in; only one heavy device should run at a time)
@pytest.fixture(scope="session")
def simulator(appium_server):  # pylint: disable=unused-argument
    udid = booted_udid()
    if udid is None:
        name = environment_data["sim_name"]
        logger.info(f"booting the {name} simulator")
        subprocess.run(  # nosec B603 - fixed arguments, local tooling
            [XCRUN, "simctl", "boot", name],
            capture_output=True,
            text=True,
            timeout=60,
            check=False,
        )
        deadline = time.time() + 120
        while time.time() < deadline and booted_udid() is None:
            time.sleep(2)
        udid = booted_udid()
        if udid is None:
            raise RuntimeError("the simulator did not boot within 120 seconds")
    # the runner.app is normally installed already, this installs it when not
    check = subprocess.run(  # nosec B603 - fixed arguments, local tooling
        [
            XCRUN,
            "simctl",
            "get_app_container",
            "booted",
            environment_data["bundle_id"],
        ],
        capture_output=True,
        text=True,
        timeout=30,
        check=False,
    )
    if check.returncode != 0:
        app = environment_data["ios_app"]
        if not os.path.isdir(app):
            raise RuntimeError(
                f"{environment_data['bundle_id']} is not installed and {app} is "
                "missing, run ./fetch_app.sh to download it"
            )
        logger.info(f"installing {app}")
        subprocess.run(  # nosec B603 - fixed arguments, local tooling
            [XCRUN, "simctl", "install", "booted", app],
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
    return udid


def caps(udid):
    options = XCUITestOptions()
    options.load_capabilities(
        {
            "platformName": "iOS",
            "appium:automationName": "XCUITest",
            "appium:udid": udid,
            "appium:deviceName": environment_data["sim_name"],
            "appium:platformVersion": environment_data["sim_platform_version"],
            "appium:simulatorOnly": True,
            "appium:app": environment_data["ios_app"],
            "appium:forceAppLaunch": True,
            "appium:newCommandTimeout": environment_data["new_command_timeout"],
            # typing falls back to clipboard paste on this app
            "appium:allowInsecure": ["clipboard"],
        }
    )
    return options


# one appium session per run, independence comes from the state reset,
# the same decision as the android project (see README)
@pytest.fixture(scope="session")
def driver(simulator):
    client = webdriver.Remote(environment_data["server_url"], options=caps(simulator))
    yield client
    client.quit()


@pytest.fixture(scope="session")
def home_page(driver):
    return HomePage(driver, environment_data["ui_timeout"])


@pytest.fixture(scope="session")
def login_page(driver):
    from lib.app.pages.login_page import LoginPage

    return LoginPage(driver, environment_data["ui_timeout"])


# runs before every test: the app is on the home page and signed out, so
# no test depends on what the test before it left open
@pytest.fixture(autouse=True)
def signed_out(home_page, login_page):
    if login_page.is_shown(LoginLocators.sign_in_button, seconds=2):
        logger.info("reset, closing a login screen left open by the last test")
        login_page.leave()
    home_page.wait_here()
    if home_page.is_logged_in():
        logger.info("reset, logging out before the test")
        home_page.logout()
    return home_page


class TestData:
    def __init__(self):
        self.password = constant_data["password"]
        self.standard_user = constant_data["standard_user"]
        self.locked_out_user = constant_data["locked_out_user"]
        self.wrong_password = constant_data["wrong_password"]
        self.unknown_user = constant_data["unknown_user"]
        self.error_username_required = constant_data["error_username_required"]
        self.error_password_required = constant_data["error_password_required"]
        self.error_locked_out = constant_data["error_locked_out"]
        self.error_no_match = constant_data["error_no_match"]


@pytest.fixture
def testdata():
    return TestData()


@pytest.fixture
def assertion():
    return Assertion()


@pytest.fixture(name="logger")
def step_logger():
    return logging.getLogger("test")
