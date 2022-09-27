from validateOptions import trenitaliaValidateRoundtrip as validateOptions, trenitaliaStations as stations
from trenitaliaRequest import findOutgoingTrains
from trenitaliaProcessData import processData

from datetime import datetime
import sys, json
from requests import cookies as cookieFunctions

try:
    args = sys.argv[1:]
    if(not validateOptions(args)):
        sys.exit()

    [origin, destination, depDate, depTime, passengers, retDate, retTime] = args
    [originId, destinationId] = [stations[origin], stations[destination]]
    depDateObject = datetime.strptime(depDate, "%d-%m-%y")
    retDateObject = datetime.strptime(retDate, "%d-%m-%y")
    [adults, seniors, youngs] = list(map(int, passengers))
    totalPassengers = adults+seniors+youngs
    departureTimeString = f"{depDateObject.strftime('%Y-%m-%d')}T{depTime+':00'}:00.000+02:00"
    returnTimeString = f"{retDateObject.strftime('%Y-%m-%d')}T{retTime+':00'}:00.000+02:00"

    allData = []
    done = False
    offset = 0
    cookies = {}
    cartId = ''

    while not done:
        response = findOutgoingTrains(originId, destinationId, departureTimeString, returnTimeString, totalPassengers, offset, cookies, cartId)
        rawTrainsData = response.json()
        cookies = cookieFunctions.merge_cookies(response.cookies, cookies)
        if not cartId:
            cartId = rawTrainsData['cartId']
        [trainsData, done] = processData(rawTrainsData, depDateObject.strftime('%d/%m'), [adults,seniors,youngs])
        offset += 10
        allData += trainsData

    print(json.dumps({'error': '', 'results': allData, 'cookies': cookies.get_dict(), 'cartId': cartId}))
except Exception as e:
    print(json.dumps({'error': repr(e)+' while running toutgoing.py', 'results': []}))
