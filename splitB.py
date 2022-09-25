import requests, time, sys, json
from datetime import datetime
from validateOptions import trenitaliaStations as stations
from trenitaliaProcessData import processData

f = open('splitA.json','r')
content = json.loads(f.read())
originId = content['originId']
destinationId = content['destinationId']
depDate = content['depDate']
depTime = content['depTime']
retDate = content['retDate']
retTime = content['retTime']
passengers = content['passengers']
[adults, seniors, youngs] = list(map(int, passengers))
depDateObject = datetime.strptime(depDate, '%d-%m-%y')
retDateObject = datetime.strptime(retDate, '%d-%m-%y')
depTimeString = f"{depDateObject.strftime('%Y-%m-%d')}T{depTime}:00:00.000+02:00"
retTimeString = f"{retDateObject.strftime('%Y-%m-%d')}T{retTime}:00:00.000+02:00"
cartId = content['cartId']
cookies = content['cookies']
goingoutId = content['goingoutId']
f.close()

payload = {
    "cartId": cartId,
    "departureLocationId": destinationId,
    "arrivalLocationId": originId,
    "departureTime": depTimeString,
    "returnDepartureTime": retTimeString,
    "forwardSolutionId": goingoutId,
    "adults": adults+seniors+youngs,
    "children": 0,
    "criteria": {
        "frecceOnly": True,
        "regionalOnly": False,
        "noChanges": True,
        "order": "DEPARTURE_DATE",
        "offset": 0,
        "limit": 10
    },
    "advancedSearchRequest": {"bestFare": False}
}

url = "https://www.lefrecce.it/Channels.Website.BFF.WEB/website/ticket/solutions"
response = requests.request("POST", url, json=payload, cookies=cookies)

data = response.json()
[processedData, done] = processData(data, retDateObject.strftime('%d/%m'), [adults, seniors, youngs])
for line in processedData:
    print(line)

with open('trenR.txt', 'w') as f:
    f.write(response.text)