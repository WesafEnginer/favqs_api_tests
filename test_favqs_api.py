import pytest
import requests
import random
import string
from faker import Faker
from dotenv import load_dotenv
import os

load_dotenv() 

BASE_URL = "https://favqs.com/api"
API_KEY = os.getenv("FAVQS_API_KEY")

faker = Faker()

def random_login(length=12):
    chars = string.ascii_lowercase + string.digits + "_"
    return ''.join(random.choice(chars) for _ in range(length))


@pytest.fixture(scope="session")
def headers():
    return {
        "Authorization": f'Token token="{API_KEY}"',
        "Content-Type": "application/json"
    }


@pytest.fixture
def created_user(headers):
    user_data = {
        "user": {
            "login": random_login(),
            "email": faker.email(),
            "password": faker.password(length=8),
        }
    }

    resp = requests.post(f"{BASE_URL}/users", json=user_data, headers=headers)
    assert resp.status_code == 200, f"User creation failed: {resp.text}"
    result = resp.json()

    token = result.get("User-Token")
    assert token, "No user token in response"

    return {
        "login": result["login"],
        "email": user_data["user"]["email"],
        "password": user_data["user"]["password"],
        "token": token
    }


def test_user_creation(created_user, headers):
    user_headers = {**headers, "User-Token": created_user["token"]}

    resp = requests.get(f"{BASE_URL}/users/{created_user['login']}", headers=user_headers)
    assert resp.status_code == 200, f"Can't get user data: {resp.text}"

    data = resp.json()
    assert data["login"] == created_user["login"], "Login mismatch"
    assert data["account_details"]["email"] == created_user["email"], "Email mismatch"


def test_user_update(created_user, headers):
    user_headers = {**headers, "User-Token": created_user["token"]}
    new_login = random_login()
    new_email = faker.email()

    update_data = {
        "user": {
            "login": new_login,
            "email": new_email
        }
    }

    resp = requests.put(f"{BASE_URL}/users/{created_user['login']}", json=update_data, headers=user_headers)
    assert resp.status_code == 200, f"Update failed: {resp.text}"

    resp_get = requests.get(f"{BASE_URL}/users/{new_login}", headers=user_headers)
    assert resp_get.status_code == 200, f"Can't get updated user: {resp_get.text}"

    updated = resp_get.json()
    assert updated["login"] == new_login, "Updated login mismatch"
    assert updated["account_details"]["email"] == new_email, "Updated email mismatch"
