from validateOptions import italoValidateOptions as validateOptions, italoStations as stations
from italoProcessData import getDataFromHtml
from italoRequest import findOnewayTrains, getPromoCode

import sys, json
from datetime import datetime

try:
    args = sys.argv[1:]
    if (not validateOptions(args)):
        sys.exit()

    [origin, destination, depDate, depTime, passengers] = args
    [originId, destinationId] = [stations[origin], stations[destination]]
    depDateObject = datetime.strptime(depDate, "%d-%m-%y")
    [adults, seniors, youngs] = list(map(int, passengers))
    promoCode = getPromoCode(depDateObject)
    depDay = depDate[:2]
    depYearMonth = depDateObject.strftime('%Y-%m')

    response = findOnewayTrains(originId, destinationId, depDay, depYearMonth, [adults, seniors, youngs], promoCode)

    trainsData = getDataFromHtml(response.text, adults+seniors+youngs, depTime)

    print(json.dumps({'error': '', 'results': trainsData}))
except Exception as e:
    print(json.dumps({'error': repr(e)+' while running ioneway.py', 'results': []}))
