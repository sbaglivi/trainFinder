import pandas as pd
import sys, re, json
from trenitaliaRequest import *
from datetime import datetime

def validateOptions(args):
    if (len(args) < 5):
        print(f"Expected 5 arguments (origin: string, destination: string, dataPartenza: dd-mm-yy oraPartenza: hh, passengers: 3 0-9 numbers for Adults/Seniors/Youngs). \
                Received {len(args)}")
        sys.exit()
    if (args[0] not in stazioni.keys() or args[1] not in stazioni.keys()):
        invalid = args[0] if args[0] not in stazioni.keys() else args[1]
        print(f"{invalid} is not a valid name for a train station. Accepted are ${stazioni.keys()}")
        sys.exit()

    def validateDate(date_text):
        try:
            if date_text != datetime.strptime(date_text, "%d-%m-%y").strftime('%d-%m-%y'):
                raise ValueError
            desiredDate = datetime.strptime(date_text, "%d-%m-%y")
            today = datetime.now()
            if today > desiredDate:
                raise ValueError
            return True
        except ValueError:
            return False
    if not validateDate(args[2]):
        print(f"Invalid date. Make sure the format is dd-mm-yy and the date is in the future.")
        sys.exit()
    hourPattern = re.compile("[01][0-9]|2[0-3]")
    if not hourPattern.match(args[3]):
        print(f"{args[3]} is not a valid format for the departure time. Accepted is hh).")
        sys.exit()
    if not re.compile("[1-9][0-9]{2}|[0-9][1-9][0-9]|[0-9]{2}[1-9]").match(args[4]):
        print(f"{args[4]} is not a valid format for passengers. Accepted is \d\d\d with at least 1 != 0.")
        sys.exit()
             

validateOptions(sys.argv[1:])
"""
result = {
        'success' : True,
        'message' : f"Searching trains from {sys.argv[1]} to {sys.argv[2]} departing on {sys.argv[3]} after {sys.argv[4]}"
}
print(json.dumps(result))
sys.exit()
print(f"Searching trains from {sys.argv[1]} to {sys.argv[2]} departing on {sys.argv[3]} after {sys.argv[4]}")
"""
trainDateObject = datetime.strptime(sys.argv[3], "%d-%m-%y")
adjustedDate = trainDateObject.strftime("%Y-%m-%d")

adults = int(sys.argv[5][0])
seniors = int(sys.argv[5][1])
youngs = int(sys.argv[5][2])



dataPartenza = "2022-09-23"
oraPartenza = "16:00"

#response = findTrains(stazioni['milanoCentrale'], stazioni['firenze'], dataPartenza, oraPartenza)
response = findTrains(stazioni[sys.argv[1]], stazioni[sys.argv[2]], adjustedDate, sys.argv[4]+":00")
json_data = response.json()
if 'solutions' not in json_data.keys():
    #print(json.dumps({'error': f'No trains found for search from {sys.argv[1]} to {sys.argv[2]} departing on {sys.argv[3]} after {sys.argv[4]}', 'results':[]}))
    json.dumps([])
    sys.exit()
#json_data = pd.read_json('data.json')

def minValid(*values):
    validValues = list(filter(lambda x: x != -1,values))
    if not len(validValues):
        raise Exception("Not enough tickets on train")
    return min(validValues)

def calculateMinPrice(row):
    try:
        if row['adult'] == -1:
            raise Exception("Not enough tickets on train")
        minPrice = adults * row['adult'] + seniors * minValid(row['senior'], row['adult']) + youngs * minValid(row['young'], row['adult'])
        return minPrice
    except Exception as e:
        return '/' 

def findPrices(row):
    priorityOrder = ['STANDARD', 'STANDARD AREA SILENZIO', 'PREMIUM', 'BUSINESS', 'BUSINESS AREA SILENZIO'] 
    pricesFound = {
            'young': -1,
            'senior' : -1,
            'adult' : -1
            }


    def allPricesFound():
        return pricesFound['young'] != -1 and pricesFound['senior'] != -1 and pricesFound['adult'] != -1

    while (len(priorityOrder) > 0 and not allPricesFound()):
        searchedServiceFound = False
        for service in row['grids'][0]['services']:
            if searchedServiceFound:
                break
            if (service['name'] != priorityOrder[0]):
                continue
            for offer in service['offers']:
                if offer['status'] != 'SALEABLE':
                    continue
                if offer['name'] == 'YOUNG':
                    if (pricesFound['young'] == -1 or offer['price']['amount'] < pricesFound['young']):
                        pricesFound['young'] = offer['price']['amount']
                elif offer['name'] == 'SENIOR':
                    if (pricesFound['senior'] == -1 or offer['price']['amount'] < pricesFound['senior']):
                        pricesFound['senior'] = offer['price']['amount']
                else:
                    if (pricesFound['adult'] == -1 or offer['price']['amount'] < pricesFound['adult']):
                        pricesFound['adult'] = offer['price']['amount']
            searchedServiceFound = True
            break
        priorityOrder.pop(0)

    row['young'] = pricesFound['young']
    row['senior'] = pricesFound['senior']
    row['adult'] = pricesFound['adult']
    row['minPrice'] = calculateMinPrice(row)
    return row

durationPattern = re.compile('(\d+)(?:h )(\d+)(?:min)')
def formatDuration(s):
    return ":".join(durationPattern.search(s).groups())

def processData(jsonData):
    df = pd.json_normalize(jsonData['solutions'])
    solutions = df[df['solution.status'] == "SALEABLE"][['solution.id','solution.departureTime','solution.arrivalTime','solution.duration','solution.origin','solution.destination','grids']]
    solutions['solution.departureTime'] = pd.to_datetime(solutions['solution.departureTime']);
    solutions['solution.arrivalTime'] = pd.to_datetime(solutions['solution.arrivalTime']);
    solutions['departureTime'] = solutions['solution.departureTime'].dt.strftime('%H:%M')
    solutions['arrivalTime'] = solutions['solution.arrivalTime'].dt.strftime('%H:%M')
    solutions['departureDate'] = solutions['solution.departureTime'].dt.strftime('%d/%m')
    #solutions.sameDay = solutions['solution.departureTime'].dt.stftime('%Y-%m-%d') == adjustedDate
    solutions.rename(columns={'solution.id':'id', 'solution.duration':'duration'}, inplace=True)
    solutions['duration'] = solutions['duration'].apply(formatDuration)
    solutionsWithPrices = solutions.apply(findPrices, axis=1)
    solutionsWithPrices['company'] = 'trenitalia';
    sameDaySolutions = solutionsWithPrices[solutionsWithPrices['departureDate'] == trainDateObject.strftime("%d/%m")]
    # return solutionsWithPrices[['id', 'departureDate', 'departureTime', 'arrivalTime', 'duration', 'young', 'senior', 'adult']]
    return sameDaySolutions[['id', 'departureTime', 'arrivalTime', 'duration', 'young', 'senior', 'adult','company', 'minPrice']]


processedData = processData(json_data)
#print(json.dumps({'error': '', 'results': processedData.to_json(orient='records')}))
#print(json.dumps({'error': '', 'results': processedData.to_dict('records')}))
print(json.dumps(processedData.to_dict('records')))
