import unittest
import azure.functions as func
from requests.structures import CaseInsensitiveDict
import os
import json

from UpdateCrownTable import main  # import the method we want to test
from SharedFunctions.set_environment_variables import set_variables
# Note how the class name starts with Test

URL = "crowndb/{}"

PROTOCOL_ENROLLMENT_BODY = {
    "values": {
        "sensor_data": 1,
        "bulk_density": 0,
        "corn_disease": None,
        "farm_history": 1,
        "soil_texture": 1,
        "gps_locations": 0,
        "soil_nitrogen": 0,
        "yield_monitor": None,
        "decomp_biomass": -999,
        "cash_crop_yield": 1,
        "in_field_biomass": -999,
        "weed_visual_rating": None,
        "weed_quadrat_photos_beta": 1
    },
    "conditions": {
        "code": "QUU",
    }
}

BAD_PROTOCOL_ENROLLMENT_BODY = {
    "values": {
        "sensor_data": 1,
        "bulk_density": 0,
        "corn_disease": None,
        "farm_history": 1,
        "soil_texture": 1,
        "gps_locations": 0,
        "soil_nitrogen": 0,
        "yield_monitor": None,
        "decomp_biomass": -999,
        "cash_crop_yield": 1,
        "in_field_biomass": -999,
        "weed_visual_rating": None,
        "weed_quadrat_photos_beta": 1
    },
    "conditions": {
        "code": "XYZ",
    }
}

SITE_INFORMATION_BODY = {
    "values": {
        "protocols_enrolled": "1",
        'producer_id': '2022DV567'
    },
    "conditions": {
        "code": "QUU",
    }
}

FARM_HISTORY_BODY = {
    "values": {
        "cc_planting_date": "2016-10-30",
        "cc_termination_date": "2016-10-29"
    },
    "conditions": {
        "code": "QUU",
    }
}

DECOMP_BIOMASS_DRY_BODY = {
    "values": {
        "recovery_date": "2016-10-30",
    },
    "conditions": {
        "code": "QUU",
        "subplot": "1",
        "subsample": "A",
        "time": "0",
    }
}

BAD_DECOMP_BIOMASS_DRY_BODY = {
    "values": {
        "recovery_date": "2016-10-30",
    },
    "conditions": {
        "code": "QUU",
        "subplot": "1",
        "time": "0",
    }
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
    def test_good_response_protocol_enrollment(self):
        request = func.HttpRequest(
            method='POST',
            url=URL.format("protocol_enrollment"),
            route_params={"table": "protocol_enrollment"},
            body=json.dumps(PROTOCOL_ENROLLMENT_BODY).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())

        print(json_response)

        assert response.status_code == 201
        assert json_response.get("status") == "success"
        assert "QUU" in json_response.get("details")

    def test_good_response_site_information(self):
        request = func.HttpRequest(
            method='POST',
            url=URL.format("site_information"),
            route_params={"table": "site_information"},
            body=json.dumps(SITE_INFORMATION_BODY).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())

        print(json_response)

        assert response.status_code == 201
        assert json_response.get("status") == "success"
        assert "QUU" in json_response.get("details")

    def test_good_response_farm_history(self):
        request = func.HttpRequest(
            method='POST',
            url=URL.format("farm_history"),
            route_params={"table": "farm_history"},
            body=json.dumps(FARM_HISTORY_BODY).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())

        print(json_response)

        assert response.status_code == 201
        assert json_response.get("status") == "success"
        assert "QUU" in json_response.get("details")

    def test_good_response_decomp_biomass_dry(self):
        request = func.HttpRequest(
            method='POST',
            url=URL.format("decomp_biomass_dry"),
            route_params={"table": "decomp_biomass_dry"},
            body=json.dumps(DECOMP_BIOMASS_DRY_BODY).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())

        print(json_response)

        assert response.status_code == 201
        assert json_response.get("status") == "success"
        assert "QUU" in json_response.get("details")

    def test_invalid_table(self):
        request = func.HttpRequest(
            method='POST',
            url=URL.format("decomp_biomass_ash"),
            route_params={"table": "decomp_biomass_ash"},
            body=json.dumps(DECOMP_BIOMASS_DRY_BODY).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())

        print(json_response)

        assert response.status_code == 400
        assert "missing minimum identifiers for table" in json_response["details"]

    def test_missing_minimum_identifiers(self):
        request = func.HttpRequest(
            method='POST',
            url=URL.format("decomp_biomass_dry"),
            route_params={"table": "decomp_biomass_dry"},
            body=json.dumps(BAD_DECOMP_BIOMASS_DRY_BODY).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())

        print(json_response)

        assert response.status_code == 400
        assert "missing minimum identifiers for table" in json_response["details"]

    def test_invalid_code(self):
        request = func.HttpRequest(
            method='POST',
            url=URL,
            route_params={"table": "protocol_enrollment"},
            body=json.dumps(BAD_PROTOCOL_ENROLLMENT_BODY).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 400
        assert "failed to update" in json_response["details"]

    def test_no_query_params(self):
        request = func.HttpRequest(
            method='POST',
            url=URL,
            body=json.dumps(PROTOCOL_ENROLLMENT_BODY).encode(),
            headers=HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 400
        assert "missing query params" in json_response["details"]

    def test_no_token(self):
        request = func.HttpRequest(
            method='POST',
            url=URL,
            body=json.dumps(PROTOCOL_ENROLLMENT_BODY).encode(),
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 401
        assert "token missing" in json_response["details"]

    def test_expired_token(self):
        request = func.HttpRequest(
            method='POST',
            route_params={'code': 'QUU'},
            url=URL,
            body=json.dumps(PROTOCOL_ENROLLMENT_BODY).encode(),
            headers=EXPIRED_HEADERS
        )

        response = main(request)
        json_response = json.loads(response.get_body())
        print(json_response)

        assert response.status_code == 401
        assert "token_expired" in str(json_response["details"])
