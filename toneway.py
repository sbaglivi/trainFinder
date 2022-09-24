from validateOptions import trenitaliaValidateOptions as validateOptions, trenitaliaStations as stations
from trenitaliaRequest import findOnewayTrains
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

allData = []
done = False
offset = 0
while not done:
    response = findOnewayTrains(originId, destinationId, depDateObject.strftime("%Y-%m-%d"), depTime+":00", adults+seniors+youngs, offset)
    rawTrainsData = response.json()
    [trainsData, done] = processData(rawTrainsData, depDateObject.strftime('%d/%m'), [adults,seniors,youngs])
    offset += 10
    allData += trainsData

print(json.dumps(allData))