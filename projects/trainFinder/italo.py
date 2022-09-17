from bs4 import BeautifulSoup
from math import floor
import re, json

def departureTimeFromTimestring(string):
    hours = floor(int(string)/60)
    minutes = int(string)%60
    return f'{hours}:{minutes}'
#trainData['departureTime'] = departureTimeFromTimestring(trainDiv['data-train-timestamp'])


def getDataFromHtml(html, dayMonth):
    pricePattern = re.compile('\d+\.?\d+')
    timePattern = re.compile('\d{2}:\d{2}')
    allData = []
    soup = BeautifulSoup(html, 'html.parser')
    trainDivs = soup.find_all(class_='item-treno')
    for trainDiv in trainDivs:
        trainData = {}
        trainData['id'] = trainDiv['data-train-number'] # train number
        trainData['departureDate'] = dayMonth ## temp ??
        times = trainDiv.find(class_='layout__item').find('p').text
        [trainData['departureTime'],trainData['arrivalTime']] = times.split(' > ')
        trainData['duration'] = trainDiv['data-train-duration']
        pricing_rows = trainDiv.find_all(class_='row-tariffa')[1:]
        #prices = []
        minPrice = -1
        for row in pricing_rows:
            pricing_cols = row.find_all(class_='col-tariffa')[1:]
            for col in pricing_cols:
                try:
                    price = col.find("label").text
                    numPrice = float(pricePattern.search(price).group()) 
                    if numPrice <  minPrice or minPrice == -1:
                        minPrice = numPrice
                except AttributeError:
                    price  = 'sold out'
                #prices.append(price)
        trainData['minPrice'] = minPrice
        #trainData['prices'] = prices
        allData.append(trainData)
    return allData
def openFileAndGetDataFromHtml(filePath, dayMonth):
    pricePattern = re.compile('\d+\.?\d+')
    timePattern = re.compile('\d{2}:\d{2}')
    allData = []
    with open(filePath, 'r') as htmlFile:
        soup = BeautifulSoup(htmlFile, 'html.parser')
        trainDivs = soup.find_all(class_='item-treno')
        for trainDiv in trainDivs:
            trainData = {}
            trainData['id'] = trainDiv['data-train-number'] # train number
            trainData['departureDate'] = dayMonth ## temp ??
            times = trainDiv.find(class_='layout__item').find('p').text
            [trainData['departureTime'],trainData['arrivalTime']] = times.split(' > ')
            trainData['duration'] = trainDiv['data-train-duration']
            pricing_rows = trainDiv.find_all(class_='row-tariffa')[1:]
            prices = []
            minPrice = -1
            for row in pricing_rows:
                pricing_cols = row.find_all(class_='col-tariffa')[1:]
                for col in pricing_cols:
                    try:
                        price = col.find("label").text
                        numPrice = float(pricePattern.search(price).group()) 
                        print(numPrice)
                        if numPrice <  minPrice or minPrice == -1:
                            minPrice = numPrice
                    except AttributeError:
                        price  = 'sold out'
                    prices.append(price)
            trainData['minPrice'] = minPrice
            trainData['prices'] = prices
            allData.append(trainData)
    return allData

#data = openFileAndGetDataFromHtml('temp.html', '29/10')
