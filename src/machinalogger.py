import logging
from logging.handlers import RotatingFileHandler

def createMachinaLogger(filePath: str, modName: str = __name__) -> logging.Logger:
    #create logger based on module name parameter
    logger = logging.getLogger(modName)

    #create a rotating log file that gets to up to 1gb, 3 times
    oneGig = 1024**3
    fh = RotatingFileHandler(filename = filePath, mode = "w", maxBytes = oneGig, backupCount = 3)
    
    #add format
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    #set level for each logging piece
    logger.setLevel(logging.DEBUG)
    fh.setLevel(logging.DEBUG)

    #finally, add the file handler to logger
    logger.addHandler(fh)

    return logger