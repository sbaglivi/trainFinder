import sys, json
from datetime import datetime
from italoProcessData import getDataFromHtml
from validateOptions import italoStations as stations, italoValidateRoundtrip as validateOptions
from italoRequest import findReturnTrains, getPromoCode


args = sys.argv[1:]
if not validateOptions(args[:7]):
    sys.exit()

[origin, destination, depDate, depTime, passengers, retDate, retTime, inputValue, cookies] = args
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
cookies = json.loads(cookies)

response = findReturnTrains(originId, destinationId, depDay, depYearMonth, retDay, retYearMonth, adults, seniors, youngs, promoCode, cookies)
data = getDataFromHtml(response.text, totalPassengers, retTime)

print(json.dumps(data))