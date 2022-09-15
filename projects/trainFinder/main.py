import pandas as pd
import sys, re, json
from trenitaliaRequest import *
from datetime import datetime

def validateOptions(args):
    if (len(args) < 4):
        print(f"Expected 4 arguments (origin: string, destination: string, dataPartenza: dd-mm-yy oraPartenza: hh). \
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
             

validateOptions(sys.argv[1:])
result = {
        'success' : True,
        'message' : f"Searching trains from {sys.argv[1]} to {sys.argv[2]} departing on {sys.argv[3]} after {sys.argv[4]}"
}
print(json.dumps(result))
sys.exit()
print(f"Searching trains from {sys.argv[1]} to {sys.argv[2]} departing on {sys.argv[3]} after {sys.argv[4]}")
adjustedDate = datetime.strptime(sys.argv[3], "%d-%m-%y").strftime("%Y-%m-%d")
print(adjustedDate)


dataPartenza = "2022-09-23"
oraPartenza = "16:00"

response = findTrains(stazioni['milanoCentrale'], stazioni['firenze'], dataPartenza, oraPartenza)
json_data = response.json()
#json_data = pd.read_json('data.json')


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
    return row
def processData(jsonData):
    df = pd.json_normalize(jsonData['solutions'])
    solutions = df[df['solution.status'] == "SALEABLE"][['solution.id','solution.departureTime','solution.arrivalTime','solution.duration','solution.origin','solution.destination','grids']]
    solutionWithPrices = solutions.apply(findPrices, axis=1);
    print(solutionWithPrices[['solution.departureTime','solution.arrivalTime','solution.duration','young','senior','adult']])
    return solutionWithPrices


processData(json_data)
