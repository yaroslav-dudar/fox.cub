import json
import os

class Config:
    settings = {}
    configpath = "../config/config.json"

    def __init__(self):
        folder = os.path.dirname(os.path.realpath(__file__))
        with open(os.path.join(folder, "..", self.configpath)) as f:
            self.settings = json.load(f)

    def __getitem__(self, key):
        return self.settings[key]
