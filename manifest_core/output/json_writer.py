import json
import os

class JSONWriter:

    @staticmethod
    def write(filepath, data):
        with open(filepath, "w") as f:
            json.dump(data, f, indent=4)
