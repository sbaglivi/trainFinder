from bs4 import BeautifulSoup
from math import floor
import re

def compareDepartureTime(train, searchedTime):
    departureTime = int(train['departureTime'].replace(':', ''))
    return departureTime >= int(searchedTime+'00')

def getDataFromHtml(html, passengers, searchedTime): # passenger is just a number
    pricePattern = re.compile('\d+[\.|,]?\d+')
    allTrains = []
    soup = BeautifulSoup(html, 'html.parser')
    trainDivs = soup.find_all(class_='item-treno')
    for trainDiv in trainDivs:
        trainData = {}
        trainData['id'] = trainDiv['data-train-number']
        times = trainDiv.find(class_='layout__item').find('p').text
        [trainData['departureTime'],trainData['arrivalTime']] = times.split(' > ')
        trainData['duration'] = trainDiv['data-train-duration']

        pricing_rows = trainDiv.find_all(class_='row-tariffa')[1:]
        minPrice = -1
        minPriceInputValue = ''
        #prices = []
        for row in pricing_rows:
            pricing_cols = row.find_all(class_='col-tariffa')[1:]
            for col in pricing_cols:
                try:
                    price = col.find("label").text
                    inputVal = col.find("input").get('value')
                    numPrice = float(pricePattern.search(price).group().replace(',','.')) 
                    if numPrice <  minPrice or minPrice == -1:
                        minPrice = numPrice
                        minPriceInputValue = inputVal
                except AttributeError:
                    price  = 'sold out'
                #prices.append(price)

        trainData['minIndividualPrice'] = minPrice
        trainData['inputValue'] = minPriceInputValue
        trainData['minPrice'] = round(minPrice*passengers,2)
        trainData['company'] = 'italo'
        #trainData['prices'] = prices
        if minPrice != -1:
            allTrains.append(trainData)
    afterDesiredTime = list(filter(lambda train: compareDepartureTime(train, searchedTime), allTrains))
    return afterDesiredTime
