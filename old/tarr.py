from datetime import datetime
import json, sys, requests
from trenitaliaProcessData import processData
from validateOptions import trenitaliaStations as stations


args = sys.argv[1:]
[origin, destination, depDate, depTime, retDate, retTime, passengers, goingoutId, cartId, cookies] = args
[adults, seniors, youngs] = list(map(int, passengers))
[originId, destinationId] = [stations[origin], stations[destination]]
totalPassengers = adults+seniors+youngs
depDateObject = datetime.strptime(depDate, '%d-%m-%y')
retDateObject = datetime.strptime(retDate, '%d-%m-%y')

cookies = json.loads(cookies)
departureTimeString = f"{depDateObject.strftime('%Y-%m-%d')}T{depTime}:00:00.000+02:00"
returnTimeString = f"{retDateObject.strftime('%Y-%m-%d')}T{retTime}:00:00.000+02:00"
offset = 0

def findPartialData(origin, destination, departureTimeString, returnTimeString, passengerNumber, goingoutId, offset, cookies, cartId): 
    url = "https://www.lefrecce.it/Channels.Website.BFF.WEB/website/ticket/solutions"

    offset = 0

    payload = {
        "cartId": cartId,
        "departureLocationId": origin,
        "arrivalLocationId": destination,
        "departureTime": departureTimeString,
        "returnDepartureTime": returnTimeString,
        "forwardSolutionId": goingoutId,
        "adults": passengerNumber,
        "children": 0,
        "criteria": {
            "frecceOnly": True,
            "regionalOnly": False,
            "noChanges": True,
            "order": "DEPARTURE_DATE",
            "offset": offset,
            "limit": 10
        },
        "advancedSearchRequest": {"bestFare": False}
    }

    response = requests.request("POST", url=url, json=payload, cookies=cookies)

    returnRawData = response.json()

    with open('trenR.txt', 'w') as f:
        f.write(response.text)
        
    return processData(returnRawData, retDateObject.strftime('%d/%m'), [adults,seniors,youngs]) + [response.cookies]

allData = []
[trainsData, done, cookies] = findPartialData(originId, destinationId, departureTimeString, returnTimeString, totalPassengers, goingoutId, offset, cookies, cartId) 
while not done:
    allData += trainsData
    offset += 10
    [trainsData, done, cookies] = findPartialData(originId, destinationId, departureTimeString, returnTimeString, totalPassengers, goingoutId, offset, cookies, cartId) 
allData += trainsData
print(json.dumps(allData))