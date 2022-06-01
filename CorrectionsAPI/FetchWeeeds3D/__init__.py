import json
import logging
from mimetypes import init
import traceback
import os

import azure.functions as func
from azure.storage.blob import BlobServiceClient

from SharedFunctions import global_vars, initializer

# github issues class to handle actions on github issues


class FetchWeeds3D:
    # constructor sets the user variable
    def __init__(self, req):
        initial_state = initializer.initialize(
            route_params=None, body_params=["codes"], req=req)

        self.body_params_obj = initial_state["body_params_obj"]
        self.token = initial_state["token"]
        self.token_missing = initial_state["token"] == None
        self.authenticated = initial_state["authenticated"]
        self.auth_response = initial_state["auth_response"]
        self.invalid_params = initial_state["body_params_obj"] is None

    def fetch_videos(self):
        blob_service_client = BlobServiceClient(
            account_url="https://weedsmedia2.blob.core.windows.net", credential=os.environ["WEEDS3D_SAS_TOKEN"])

        file_list = []

        try:
            weeds3d = blob_service_client.get_container_client("weeds3d")
            for blob in weeds3d.list_blobs(name_starts_with="PSA-OnFarm"):
                for code in self.body_params_obj["codes"]:
                    if code in blob.name:
                        split_file = blob.name.split("_")

                        file_list.append(
                            {
                                "file_name": blob.name,
                                # "affiliation": split_file[1],
                                "code": split_file[3],
                                "timing_number": split_file[2].split("-")[1],
                                "treatment": split_file[5][0:-1],
                                "subplot": split_file[5][-1],
                                "crop": split_file[4],
                                "video_number": split_file[6].split("-")[1],
                                "master_ref": split_file[7],
                                "file_size": blob.size,
                                "last_modified": blob.last_modified.strftime("%m/%d/%Y, %H:%M:%S"),
                            }
                        )

            file_list.sort(key=lambda x: x["code"])
            if len(file_list) > 0:
                return func.HttpResponse(json.dumps({"status": "success", "files": file_list}), headers=global_vars.HEADER, status_code=201)
            else:
                return func.HttpResponse(json.dumps({"status": "error", "details": "no files with codes {}".format(self.body_params_obj["codes"])}), headers=global_vars.HEADER, status_code=400)
        except Exception:
            logging.exception(traceback.format_exc())
            print(traceback.format_exc())
            return func.HttpResponse(json.dumps({"status": "error", "details": traceback.format_exc()}), headers=global_vars.HEADER, status_code=200)


def main(req: func.HttpRequest) -> func.HttpResponse:
    # log that the function is called
    logging.info('Python HTTP trigger function processed a request.')

    # in a try catch because if the payload is not json it causes exception
    try:
        # instantiate FetchWeeds3D class
        weeds_fetcher = FetchWeeds3D(req)

        # authenticate user based on token
        if any([not weeds_fetcher.authenticated, weeds_fetcher.invalid_params, weeds_fetcher.token_missing]):
            return initializer.get_response(weeds_fetcher.authenticated, weeds_fetcher.auth_response,
                                            weeds_fetcher.invalid_params, weeds_fetcher.token_missing, False)
        else:
            return weeds_fetcher.fetch_videos()

    except Exception as error:
        logging.info("program encountered exception: " +
                     traceback.format_exc())
        logging.exception(error)
        return func.HttpResponse(
            json.dumps({"status": "error", "details": traceback.format_exc()}),
            status_code=500,
            headers=global_vars.HEADER
        )
