import errno
import os
import json
from typing import Tuple
from zlib import crc32

class Preamble:
    """
    Preamble is a utility class that describes just enough metadata
    to ensure that the file being xferred from server to client is 
    not corrupted post-download (per requirement in spec).

    It's __str__ special function will generate a json output that can
    be a serialized output sent to the client before the actual file is sent
    """
    def __init__(self, fileName: str):
        self.fileName = fileName
        self.size = 0
        self.cksum = 0
    
    @classmethod
    def from_json(cls, jsonStr: str):
        jsonMap = json.loads(jsonStr)
        toRet = cls("")
        toRet.cksum = int(jsonMap['cksum'])
        toRet.size = int(jsonMap['size'])
        return toRet

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

    def __eq__(self, other):
        if self.cksum == other.cksum and self.size == other.size:
            return True
        else:
            return False