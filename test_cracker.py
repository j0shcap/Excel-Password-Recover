"""Regression tests for issue #1: Cracker.decrypt must accept only the real
password and reject every wrong guess (e.g. `lbanks`, `123wsx`)."""

import io

import msoffcrypto
import openpyxl
import pytest

from cracker import Cracker

CORRECT_PASSWORD = "correcthorse"
# Wrong guesses, including the two false positives reported in issue #1.
WRONG_PASSWORDS = ["lbanks", "123wsx", "password", "", "correcthors", "Correcthorse"]


@pytest.fixture
def encrypted_xlsx(tmp_path):
    """Create a password-protected .xlsx encrypted with CORRECT_PASSWORD."""
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet["A1"] = "top secret"

    plain = io.BytesIO()
    workbook.save(plain)
    plain.seek(0)

    encrypted = io.BytesIO()
    office_file = msoffcrypto.OfficeFile(plain)
    office_file.load_key(password=CORRECT_PASSWORD)
    office_file.encrypt(CORRECT_PASSWORD, encrypted)

    path = tmp_path / "protected.xlsx"
    path.write_bytes(encrypted.getvalue())
    return str(path)


def make_cracker(filename):
    """Build a Cracker without running the crack loop in __init__."""
    cracker = Cracker.__new__(Cracker)
    cracker._Cracker__filename = filename
    return cracker


def test_correct_password_is_accepted(encrypted_xlsx):
    cracker = make_cracker(encrypted_xlsx)
    assert cracker.decrypt(CORRECT_PASSWORD) is True


@pytest.mark.parametrize("wrong_password", WRONG_PASSWORDS)
def test_wrong_passwords_are_rejected(encrypted_xlsx, wrong_password):
    cracker = make_cracker(encrypted_xlsx)
    assert cracker.decrypt(wrong_password) is False
