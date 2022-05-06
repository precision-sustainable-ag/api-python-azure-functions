import os
import json


def set_variables():
    with open(r'C:\Users\mspinega\Documents\repos\azure-functions\CorrectionsAPI\local.settings.json') as lfile:
        localSettings = json.load(lfile)

    for i in localSettings['Values']:
        os.environ[i] = localSettings['Values'][i]
