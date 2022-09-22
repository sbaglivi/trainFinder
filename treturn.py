from datetime import datetime
import json, sys, requests
from trenitaliaProcessData import processData
from trenitaliaRequest import findReturnTrains
from validateOptions import trenitaliaStations as stations, trenitaliaValidateRoundtrip as validateOptions


args = sys.argv[1:]
if not validateOptions(args[:7])
    sys.exit()

[origin, destination, depDate, depTime, passengers, retDate, retTime, goingoutId, cartId, cookies] = args
[adults, seniors, youngs] = list(map(int, passengers))
[originId, destinationId] = [stations[origin], stations[destination]]
totalPassengers = adults+seniors+youngs
depDateObject = datetime.strptime(depDate, '%d-%m-%y')
retDateObject = datetime.strptime(retDate, '%d-%m-%y')

cookies = json.loads(cookies)
departureTimeString = f"{depDateObject.strftime('%Y-%m-%d')}T{depTime}:00:00.000+02:00"
returnTimeString = f"{retDateObject.strftime('%Y-%m-%d')}T{retTime}:00:00.000+02:00"

offset = 0
allData = []

while not done:
    response = findReturnTrains(originId, destinationId, departureTimeString, returnTimeString, totalPassengers, goingoutId, offset, cookies, cartId)
    rawTrainsData = response.json()
    [trainsData, done] = processData(rawTrainsData, retDateObject.strftime('%d/%m'), [adults,seniors,youngs])
    allData += trainsData
    offset += 10
    cookies = response.cookies

print(json.dumps(allData))