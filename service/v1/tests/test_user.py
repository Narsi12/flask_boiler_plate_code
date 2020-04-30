import json

create_url = "/myservice/v1/user/createuser"
auth_token_url = "/myservice/v1/user/authtoken"
user_details = "/myservice/v1/user/userdetails"


def test_create_user_existing_success(client):
    payload = {"email": "venkateshar.in@mouritech.com", "password": "123456"}
    res = client.post(create_url, json=payload)
    assert res.status_code == 200
    assert json.loads(res.data) == {'message': 'User email already registered'}


def test_create_user_missing_params(client):
    payload = {"email": "venkateshar.in@mouritech.com"}
    res = client.post(create_url, json=payload)
    assert res.status_code == 400
    assert json.loads(res.data) == {'message': "{'password': ['Missing data for required field.']}"}


def test_create_user_empty_params(client):
    payload = {}
    res = client.post(create_url, json=payload)
    assert res.status_code == 400


def test_auth_token_user_success(client):
    auth_token_url = "/myservice/v1/user/authtoken?email={}&password={}".\
        format("venkateshar.in@mouritech.com", "abc@123")
    res = client.get(auth_token_url)
    assert res.status_code == 200


def test_auth_token_user_invalid_params(client):
    auth_token_url = "/myservice/v1/user/authtoken?email={}". \
        format("venkateshar.in@mouritech.com")
    res = client.get(auth_token_url)
    assert res.status_code == 400
    assert json.loads(res.data) == {'message': 'Invalid Credential'}


def test_user_details_success(client):
    auth_token_url = "/myservice/v1/user/authtoken?email={}&password={}". \
        format("venkateshar.in@mouritech.com", "abc@123")
    token_resp = json.loads(client.get(auth_token_url).data)
    auth_token = token_resp["token"]
    headers = {"x-access-tokens": auth_token}
    res = client.get(user_details, headers=headers)
    assert res.status_code == 200


def test_user_details_invalid_token(client):
    auth_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJ1c2VyX2lkIjoyLCJleHAiOjE1ODgxNTU4O" \
                 "Dd9.5-S32oT8HxZyYvmfRG6BCzsb1KfkXyQVGIGeFM64wP8"
    headers = {"x-access-tokens": auth_token}
    res = client.get(user_details, headers=headers)
    assert res.status_code == 200
    assert json.loads(res.data) == {"message":"token is invalid"}


def test_user_details_without_token(client):
    headers = {}
    res = client.get(user_details, headers=headers)
    assert res.status_code == 200
    assert json.loads(res.data) == {"message": "a valid token is missing"}



