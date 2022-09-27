import sys, json
from datetime import datetime
from italoProcessData import getDataFromHtml
from validateOptions import italoStations as stations, italoValidateRoundtrip as validateOptions
from italoRequest import findOutgoingTrains, getPromoCode


try:
    args = sys.argv[1:]
    if not validateOptions(args):
        sys.exit()

    [origin, destination, depDate, depTime, passengers, retDate, retTime] = args
    [adults, seniors, youngs] = list(map(int, passengers))
    [originId, destinationId] = [stations[origin], stations[destination]]
    totalPassengers = adults+seniors+youngs
    depDateObject = datetime.strptime(depDate, '%d-%m-%y')
    retDateObject = datetime.strptime(retDate, '%d-%m-%y')

    depDay = depDate[:2]
    depYearMonth = depDateObject.strftime('%Y-%m')
    retDay = retDate[:2]
    retYearMonth = retDateObject.strftime('%Y-%m')
    promoCode = getPromoCode(depDateObject)

    response = findOutgoingTrains(originId, destinationId, depDay, depYearMonth, retDay, retYearMonth, adults, seniors, youngs, promoCode)

    data = getDataFromHtml(response.text, totalPassengers, depTime)

    print(json.dumps({'error': '', 'results': data, 'cookies': response.cookies.get_dict()}))
except Exception as e:
    print(json.dumps({'error': repr(e)+' while running ioutgoing.py', 'results': []}))
