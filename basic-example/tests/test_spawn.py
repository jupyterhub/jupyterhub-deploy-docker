from os import getenv
import requests
import pytest
import time
from uuid import uuid4


TIMEOUT = 120


@pytest.fixture(scope="session")
def api_request():
    def _api_request(method, path, **kwargs):
        hub_url = getenv("HUB_URL", "http://localhost:8000").rstrip("/")
        m = getattr(requests, method)
        url = f"{hub_url}{path}"
        r = m(url, headers={"Authorization": "token test-token-123"}, **kwargs)
        r.raise_for_status()
        return r

    return _api_request


def wait_for_hub(api_request):
    # Wait for the hub to be ready
    now = time.time()
    try:
        api_request("get", "/hub/api")
    except requests.exceptions.RequestException:
        if time.time() - now > TIMEOUT:
            raise TimeoutError(f"Hub did not start in {TIMEOUT} seconds")
        time.sleep(5)


def test_create_user_and_server(api_request):
    wait_for_hub(api_request)

    # Create a new user
    username = str(uuid4())
    api_request("post", "/hub/api/users", json={"usernames": [username]})

    # Start a server for the user
    api_request("post", f"/hub/api/users/{username}/server")

    # Wait for the server
    ready = False
    now = time.time()
    while not ready:
        wait_r = api_request("get", f"/hub/api/users/{username}").json()
        if wait_r["servers"][""]["ready"]:
            ready = True
            break
        if time.time() - now > TIMEOUT:
            raise TimeoutError(f"Singleuser server did not start in {TIMEOUT} seconds")
        time.sleep(5)

    # Call the jupyter-server API
    server_r = api_request("get", f"/user/{username}/api").json()
    assert "version" in server_r
    contents_r = api_request("get", f"/user/{username}/api/contents").json()
    assert "content" in contents_r
