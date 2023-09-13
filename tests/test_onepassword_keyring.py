import subprocess

import pytest
from keyring.errors import PasswordDeleteError

from onepassword_keyring import OnePasswordBackend, _onepassword_cli_installed, _user_is_authenticated, _item_exists, \
    sign_in, cli_exec


def mock_auth(mocker):
    mocker.patch('onepassword_keyring._auth', return_value=True)


def mock_item_exists(mocker, exists=True):
    mocker.patch('onepassword_keyring._item_exists', return_value=exists)


def mock_cli_exec(mocker, stdout="", stderr=""):
    mocker.patch('onepassword_keyring.cli_exec', return_value=(stdout, stderr))


def test_cli_exec(mocker):
    mocker.patch('subprocess.run', return_value=subprocess.CompletedProcess(args=[], returncode=0, stdout='output', stderr=''))
    stdout, stderr = cli_exec("some_command")
    assert stdout == 'output'
    assert stderr == ''


@pytest.mark.parametrize("path, expected", [(None, False), ("yay", True)])
def test_onepassword_cli_installed(mocker, path, expected):
    mocker.patch("shutil.which", return_value=path)
    assert _onepassword_cli_installed() == expected


def test_onepassword_not_installed(mocker):
    mocker.patch('shutil.which', return_value=None)
    with pytest.raises(RuntimeError):
        OnePasswordBackend.priority()


def test_user_not_authenticated(mocker):
    mock_cli_exec(mocker, stdout="", stderr="Not authenticated")
    assert not _user_is_authenticated()


def test_sign_in_successful(mocker):
    mock_cli_exec(mocker, stdout='Signed in successfully', stderr='')
    assert sign_in() is True


def test_sign_in_failed(mocker):
    mock_cli_exec(mocker, stdout='', stderr='Failed to sign in')
    with pytest.raises(RuntimeError):
        sign_in()


def test_item_exists(mocker):
    mock_cli_exec(mocker, stdout="user123", stderr="")
    assert _item_exists("some_service", "user123")


def test_item_not_exists(mocker):
    mock_cli_exec(mocker, stdout="user321", stderr="")
    assert not _item_exists("some_service", "user123")


def test_get_password(mocker):
    mock_auth(mocker)
    mock_item_exists(mocker)
    mock_cli_exec(mocker, stdout="user123,password123")

    backend = OnePasswordBackend()
    password = backend.get_password("some_service", "user123")

    assert password == "password123"


def test_get_password_error(mocker):
    mock_auth(mocker)
    mock_item_exists(mocker)
    mock_cli_exec(mocker, stdout="", stderr="Some error")

    backend = OnePasswordBackend()
    with pytest.raises(RuntimeError):
        backend.get_password("some_service", "user123")


def test_set_password(mocker):
    mock_auth(mocker)
    mock_item_exists(mocker, exists=False)
    mock_cli_exec(mocker)

    backend = OnePasswordBackend()
    backend.set_password("some_service", "user123", "password123")


def test_set_password_item_exists(mocker):
    mock_auth(mocker)
    mock_item_exists(mocker, exists=True)
    mock_cli_exec(mocker)

    backend = OnePasswordBackend()
    backend.set_password("some_service", "user123", "new_password123")


def test_delete_password(mocker):
    mock_auth(mocker)
    mock_item_exists(mocker)
    mock_cli_exec(mocker)

    backend = OnePasswordBackend()
    backend.delete_password("some_service", "user123")


def test_delete_password_item_not_exists(mocker):
    mock_auth(mocker)
    mock_item_exists(mocker, exists=False)
    mock_cli_exec(mocker)

    backend = OnePasswordBackend()
    with pytest.raises(PasswordDeleteError):
        backend.delete_password("some_service", "user123")


def test_get_otp(mocker):
    mock_auth(mocker)
    mock_item_exists(mocker)
    mock_cli_exec(mocker, stdout="otp_123")

    backend = OnePasswordBackend()
    otp = backend.get_otp("some_service", "user123")

    assert otp == "otp_123"


def test_get_item(mocker):
    mock_auth(mocker)
    mock_item_exists(mocker)
    mock_cli_exec(mocker, stdout="item_info")

    backend = OnePasswordBackend()
    item = backend.get_item("some_service")

    assert item == "item_info"
