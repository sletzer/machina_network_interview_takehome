import errno
import os
import json
from typing import Tuple
from zlib import crc32

class Preamble:
    def __init__(self, fileName: str):
        self.fileName = fileName
        self.size = 0
        self.cksum = 0

    def generatePreamble(self) -> Tuple[bool, str]:
        success = True
        try:
            self.size= os.stat(self.fileName).st_size
        except:
            self.size = 0
            success = False
        with open(self.fileName, "rb") as inputFile:
            self.cksum = crc32(inputFile.read())
        try:
            jsonStr = json.dumps({"size": str(self.size), "cksum": str(self.cksum)})
        except:
            jsonStr = "Failed to convert to JSON"
            success = False
        return (success, jsonStr)

    def __str__(self):
        success, jsonStr = self.generatePreamble()
        if not success:
            return "Failed to generate preamble... with " + jsonStr
        return jsonStr