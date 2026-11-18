import os
import shutil

# dynamic, changes between runs or environments
environment_data = {
    "server_url": os.environ.get("SERVER_URL", "http://127.0.0.1:4723"),
    "sim_name": os.environ.get("SIM_NAME", "iPhoneSE14"),
    "sim_platform_version": os.environ.get("SIM_PLATFORM_VERSION", "14.4"),
    "ios_app": os.path.abspath(
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            os.environ.get("IOS_APP", "apps/Runner.app"),
        )
    ),
    "bundle_id": os.environ.get("BUNDLE_ID", "net.ted.flutterApp"),
    "ui_timeout": int(os.environ.get("UI_TIMEOUT", "20")),
    "new_command_timeout": int(os.environ.get("NEW_COMMAND_TIMEOUT", "300")),
    "appium_bin": os.environ.get(
        "APPIUM_BIN",
        shutil.which("appium") or os.path.expanduser("~/.local/bin/appium"),
    ),
}

# static, never changes between runs or environments
constant_data = {
    "error_username_required": "Epic sadface: Username is required",
    "error_password_required": "Epic sadface: Password is required",
    "error_locked_out": "Epic sadface: Sorry, this user has been locked out.",
    "error_no_match": (
        "Epic sadface: Username and password do not match any user in this service"
    ),
    "password": "secret_sauce",
    "standard_user": "standard_user",
    "locked_out_user": "locked_out_user",
    "wrong_password": "not_the_real_password",
    "unknown_user": "nobody_at_all",
}
