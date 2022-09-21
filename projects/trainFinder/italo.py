from validateOptions import italoValidateOptions as validateOptions, italoStations as stations
from italoProcessData import getDataFromHtml
from italoRequest import findTrains

import sys, json
from datetime import datetime

args = sys.argv[1:]
if (not validateOptions(args)):
    sys.exit()

[origin, destination, depDate, depTime, passengers] = args
[originId, destinationId] = [stations[origin], stations[destination]]
depDateObject = datetime.strptime(depDate, "%d-%m-%y")
[adults, seniors, youngs] = list(map(int, passengers))

response = findTrains(originId, destinationId, depDateObject, [adults, seniors, youngs])

trainsData = getDataFromHtml(response.text, adults+seniors+youngs, depTime)

print(json.dumps(trainsData))