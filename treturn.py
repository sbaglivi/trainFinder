from datetime import datetime
import json, sys, requests
from trenitaliaProcessData import processData
from trenitaliaRequest import findReturnTrains
from validateOptions import trenitaliaStations as stations, trenitaliaValidateRoundtrip as validateOptions


args = sys.argv[1:]
if not validateOptions(args[:7]):
    sys.exit()

[origin, destination, depDate, depTime, passengers, retDate, retTime, goingoutId, cartId, cookies] = args
[adults, seniors, youngs] = list(map(int, passengers))
[originId, destinationId] = [stations[origin], stations[destination]]
totalPassengers = adults+seniors+youngs
depDateObject = datetime.strptime(depDate, '%d-%m-%y')
retDateObject = datetime.strptime(retDate, '%d-%m-%y')

cookies = json.loads(cookies)
depTimeString = f"{depDateObject.strftime('%Y-%m-%d')}T{depTime}:00:00.000+02:00"
retTimeString = f"{retDateObject.strftime('%Y-%m-%d')}T{retTime}:00:00.000+02:00"

f = open('splitA.json','r')
c = open('compare.txt', 'w')
content = json.loads(f.read())
c.write(str(originId == content['originId'])+'\n')
c.write(str(depDate == content['depDate'])+'\n')
c.write(str(depTime == content['depTime'])+'\n')
c.write(str(retDate == content['retDate'])+'\n')
c.write(str(retTime == content['retTime'])+'\n')
c.write(str(passengers == content['passengers'])+'\n')
c.write(str(goingoutId == content['goingoutId'])+'\t'+goingoutId+'\t'+content['goingoutId']+'\n')
c.write('\n\n'+str(cookies))
c.write('\n\n'+str(content['cookies']))
f.close()
c.close()


# -----------
offset = 0
allData = []
done = False

"""
while not done:
    response = findReturnTrains(destinationId, originId, depTimeString, retTimeString, totalPassengers, goingoutId, offset, cookies, cartId)
    rawTrainsData = response.json()
    with open('treturnlog.txt', 'w') as f:
        f.write(response.text)
    [trainsData, done] = processData(rawTrainsData, retDateObject.strftime('%d/%m'), [adults,seniors,youngs])
    allData += trainsData
    offset += 10
"""
payload = {
    "cartId": cartId,
    "departureLocationId": destinationId,
    "arrivalLocationId": originId,
    "departureTime": depTimeString,
    "returnDepartureTime": retTimeString,
    #"forwardSolutionId": "x8dabd0e2-45f5-40bf-9b01-13fb6da2526f",
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
#response = findReturnTrains(destinationId, originId, depTimeString, retTimeString, totalPassengers, goingoutId, offset, cookies, cartId)
rawTrainsData = response.json()
[trainsData, done] = processData(rawTrainsData, retDateObject.strftime('%d/%m'), [adults,seniors,youngs])

print(json.dumps(trainsData))