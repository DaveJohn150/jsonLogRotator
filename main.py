import json
from json-formatter import flatten, unflatten_list

def addLogs(logs, logType):
    try:
        logFile = CONFIG[logType]['logPath'] + logType + "Log.json"
        data = {"list":[]}
        if os.path.exists(logFile): 
            stats = os.stat(logFile)
            if stats.st_size > CONFIG["logMaxSize"]:
                logging.debug("Log file " + logFile + "exceeds maximum size")
                raise json.JSONDecodeError("Log file too large", "", 0) #file big, rotate
            with open(logFile, "r") as f:
                fileLogs = json.load(f) #formatted as dict with a single list of dicts
            data = unflatten_list(fileLogs)
    except json.JSONDecodeError as e: #fires if file is empty without formatting
        if e.msg != "Log file too large":
            logging.error("Error reading " + logFile + ", rotating")
        rotateLogs(logFile) #moves log to an archive in case formatting error 
    except Exception as e:
        logging.error(e)

    for log in logs:
        # str({"num":1}) in str({"list":[{"num":1}, {"num":2}]})
        if str(log) not in str(data):
            data["list"].append(log)
    data = flatten(data)
    with open(logFile, "w") as f:
        json.dump(data, f)
    
        
def rotateLogs(file):
    logging.info("Rotating log files")
    r = list(range(0, CONFIG["logNumBackups"] + 1))
    r.reverse()
    for i in r:
        if os.path.exists(file + '.' + str(i)):
            if i == CONFIG["logNumBackups"]:
                logging.debug("Deleting oldest log file")
                os.remove(file + '.' + str(i))
            else:
                logging.debug("Renaming file " + file + '.' + str(i) + " to " + file + '.' + str(i + 1))
                os.rename(file + '.' + str(i), file + '.' + str(i + 1))
        elif i == 0:
            logging.debug("Renaming file " + file + " to " + file + ".1")
            os.rename(file, file + '.1')
