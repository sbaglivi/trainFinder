from validateOptions import trenitaliaValidateOptions as validateOptions, stations
from trenitaliaRequest import findTrains
from trenitaliaProcessData import processData

from datetime import datetime
import sys, json

args = sys.argv[1:]
if(not validateOptions(args)):
    sys.exit()

[origin, destination, depDate, depTime, passengers] = args
[originId, destinationId] = [stations[origin], stations[destination]]
depDateObject = datetime.strptime(depDate, "%d-%m-%y")
[adults, seniors, youngs] = list(map(int, passengers))

response = findTrains(originId, destinationId, depDateObject.strftime("%Y-%m-%d"), depTime+":00", adults+seniors+youngs)
rawTrainsData = response.json()
trainsData = processData(rawTrainsData, depDateObject.strftime('%d/%m'), [adults,seniors,youngs])

print(json.dumps(trainsData))