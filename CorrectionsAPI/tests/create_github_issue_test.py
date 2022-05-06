import unittest
import azure.functions as func
from requests.structures import CaseInsensitiveDict
import os
import json

from CreateGithubIssue import main  # import the method we want to test
from SharedFunctions.set_environment_variables import set_variables
# Note how the class name starts with Test

URL = "precision-sustainable-ag/repos/data_corrections/issues/mikahpinegar"

BODY = {
    "action": "create",
    "title": "test",
    "assignees": [
        "brianwdavis",
        "saseehav",
        "mikahpinegar"
    ],
    "labels": [
        "producer-information",
        "RHS"
    ],
    "body": "<table>\n            <tbody><tr>\n              <td>producer_id</td>\n              <td>2017GA003</td>\n          </tr><tr>\n              <td>first_name</td>\n              <td>null</td>\n          </tr><tr>\n              <td>last_name</td>\n              <td>Hedrick</td>\n          </tr><tr>\n              <td>email</td>\n              <td>null</td>\n          </tr><tr>\n              <td>phone</td>\n              <td>null</td>\n          </tr><tr>\n              <td>codes</td>\n              <td>RHS</td>\n          </tr><tr>\n              <td>years</td>\n              <td>2017</td>\n          </tr></tbody>\n        </table> <br/> test"
}

# Arrange
set_variables()
token = os.environ["USER_TOKEN"]

HEADERS = CaseInsensitiveDict()
HEADERS["Accept"] = "application/json"
HEADERS["Authorization"] = "Bearer {}".format(token)

invalid_token = os.environ["EXPIRED_USER_TOKEN"]

EXPIRED_HEADERS = CaseInsensitiveDict()
EXPIRED_HEADERS["Accept"] = "application/json"
EXPIRED_HEADERS["Authorization"] = "Bearer {}".format(invalid_token)


class TestCreateGithubIssue(unittest.TestCase):
    def test_good_response(self):
        request = func.HttpRequest(
            method='POST',
            url=URL,
            route_params={'user': 'mikahpinegar'},
            body=json.dumps(BODY).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())

        print(json_response)

        assert response.status_code == 201

    def test_invalid_github_user(self):
        request = func.HttpRequest(
            method='POST',
            url=URL,
            route_params={'user': 'oansddasd'},
            body=json.dumps(BODY).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 400
        assert "invalid github nickname" in json_response["details"]

    def test_no_route_params(self):
        request = func.HttpRequest(
            method='POST',
            url=URL,
            body=json.dumps(BODY).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 400
        assert "missing query params" in json_response["details"]

    def test_no_body_params(self):
        request = func.HttpRequest(
            method='POST',
            body=None,
            url=URL,
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 500

    def test_no_token(self):
        request = func.HttpRequest(
            method='POST',
            url=URL,
            body=json.dumps(BODY).encode(),
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 401
        assert "token missing" in json_response["details"]

    def test_expired_token(self):
        request = func.HttpRequest(
            method='POST',
            route_params={'user': 'mikahpinegar'},
            url=URL,
            body=json.dumps(BODY).encode(),
            headers=EXPIRED_HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 401
        assert "token_expired" in str(json_response["details"])
