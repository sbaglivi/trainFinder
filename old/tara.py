import requests, time, sys, json
from trenitaliaProcessData import processData
from validateOptions import trenitaliaValidateRoundtrip as validateOptions, trenitaliaStations as stations
from trenitaliaProcessData import processData
from datetime import datetime

args = sys.argv[1:]
if(not validateOptions(args)):
    sys.exit()

[origin, destination, depDate, depTime, passengers, retDate, retTime] = args
[originId, destinationId] = [stations[origin], stations[destination]]
depDateObject = datetime.strptime(depDate, "%d-%m-%y")
retDateObject = datetime.strptime(retDate, "%d-%m-%y")
[adults, seniors, youngs] = list(map(int, passengers))


def findRoundTripA(origin, destination, departureDate, departureTime, returnDate, returnTime, passengerNumber): 
    def findPartialData(origin, destination, departureDate, departureTime, returnDate, returnTime, passengerNumber, offset, cookies, cartId): 
        url = "https://www.lefrecce.it/Channels.Website.BFF.WEB/website/ticket/solutions"
        departureTimeString = f"{departureDate}T{departureTime}:00.000+02:00"
        returnTimeString = f"{returnDate}T{returnTime}:00.000+02:00"

        payload = {
            "departureLocationId": origin,
            "arrivalLocationId": destination,
            "departureTime": departureTimeString,
            "returnDepartureTime": returnTimeString,
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
        if (cartId):
            payload['cartId'] = cartId
        currentTimestamp = int(time.time())
        headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0",
            "Accept": "application/json, application/pdf, text/calendar",
            "Accept-Language": "en-GB",
            "Accept-Encoding": "gzip, deflate, br",
            "Referer": "https://www.lefrecce.it/Channels.Website.WEB/",
            "Content-Type": "application/json",
            "X-Requested-With": "Fetch",
            #"X-CSRF-Token": "j5IXMP7te5qXgAC0f1/OWxspP5SeGJzO9jOENy50FY25UmyZ0y8f5fueM7Mkseu1rI8ujkXJWxMBb3z2PzEv/Q==",
            #"Channel": "41",
            "CallerTimestamp": str(currentTimestamp),
            "Origin": "https://www.lefrecce.it",
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-origin",
            "TE": "trailers"
        }
        if cookies:
            response = requests.request("POST", url, json=payload, headers=headers, cookies=cookies)
        else:
            response = requests.request("POST", url, json=payload, headers=headers)

        rawData = response.json()
        trainsData = processData(rawData, depDateObject.strftime("%d/%m"), [adults,seniors,youngs])
        return  trainsData + [response.cookies, rawData['cartId']]
    allData = []
    cookies = ''
    cartId = ''
    offset = 0
    [trainsData, done, cookies, cartId] = findPartialData(origin, destination, departureDate, departureTime, returnDate, returnTime, passengerNumber, offset, cookies, cartId) 
    while not done:
        allData += trainsData
        offset += 10
        [trainsData, done, cookies, cartId] = findPartialData(origin, destination, departureDate, departureTime, returnDate, returnTime, passengerNumber, offset, cookies, cartId) 
    allData += trainsData
    return {'data': allData, 'cartId': cartId, 'cookies': cookies.get_dict()}

data = findRoundTripA(originId, destinationId, depDateObject.strftime("%Y-%m-%d"), depTime+':00', retDateObject.strftime("%Y-%m-%d"), retTime+':00', adults+seniors+youngs)
print(json.dumps(data))