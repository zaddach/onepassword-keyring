import shutil
import subprocess
import sys

from keyring import backend
from jaraco.classes import properties
from keyring.errors import PasswordDeleteError

PRIORITY = 10


def cli_exec(command: str):
    result = subprocess.run(command.split(" "), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.stdout, result.stderr


def _user_is_authenticated():
    command = "op whoami"
    stdout, stderr = cli_exec(command)
    if stderr:
        return False
    return True


def sign_in():
    command = "op signin"
    stdout, stderr = cli_exec(command)
    if stderr:
        raise RuntimeError("Failed to sign in to 1Password: " + stderr)
    return True


def _auth():
    if not _user_is_authenticated():
        sign_in()


def _item_exists(service, username):
    command = f"op item get {service} --fields username"
    stdout, stderr = cli_exec(command)
    if stderr:
        raise RuntimeError("Error checking if item exists: " + stderr)
    else:
        return stdout == username


def _onepassword_cli_installed():
    return bool(shutil.which("op"))


class OnePasswordBackend(backend.KeyringBackend):

    @properties.classproperty
    @classmethod
    def priority(cls):
        if not _onepassword_cli_installed():
            raise RuntimeError(
                "Requires onepassword cli: https://developer.1password.com/docs/cli/get-started/"
            )

        return PRIORITY

    def get_password(self, service, username):
        _auth()
        command = f"op item get {service} --fields username,password"
        stdout, stderr = cli_exec(command)
        if stderr:
            raise RuntimeError("Failed to get password: " + stderr)
        else:
            username, password = stdout.strip().split(",")
            if username != username:
                password = None
            return password.strip()

    def set_password(self, service, username, password):
        _auth()
        if _item_exists(service, username):
            command = f"op item edit {service} username={username} password={password}"
            stdout, stderr = cli_exec(command)
        else:
            command = f"op item create title={service} username={username} password={password} --category=login"
            stdout, stderr = cli_exec(command)
        if stderr:
            raise RuntimeError("Failed to set password: " + stderr)

    def delete_password(self, service, username):
        _auth()
        if _item_exists(service, username):
            command = f"op delete item {service}"
            stdout, stderr = cli_exec(command)
            if stderr:
                raise RuntimeError("Failed to delete password: " + stderr)
        else:
            e = sys.exc_info()[0]
            raise PasswordDeleteError(e)

    def get_otp(self, service, username):
        _auth()
        command = f"op item get {service} --otp"
        stdout, stderr = cli_exec(command)
        if stderr:
            raise RuntimeError("Failed to get otp: " + stderr)
        else:
            return stdout.strip()

    def get_item(self, service):
        _auth()
        command = f"op get item {service}"
        stdout, stderr = cli_exec(command)
        if stderr:
            raise RuntimeError("Failed to get item: " + stderr)
        return stdout.strip()
