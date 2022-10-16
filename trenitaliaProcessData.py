import pandas as pd

def minValidPrice(*values):
    validValues = list(filter(lambda x: x != -1,values))
    if not len(validValues):
        raise Exception("Not enough tickets on train")
    return min(validValues)

def calculateMinPrice(row, passengers):
    [adults, seniors, youngs] = passengers
    totPass = adults+seniors+youngs
    try:
        if row['adult'] == -1:
            raise Exception("Not enough tickets on train")
        if (minValidPrice(row['adult'], row['senior'], row['young']) == row['adult']):
            return row['adult']
        minPrice = adults/totPass * row['adult'] + seniors/totPass * minValidPrice(row['senior'], row['adult']) + youngs/totPass * minValidPrice(row['young'], row['adult'])
        return minPrice
    except Exception as e:
        return '/' 

def findSolutionPrices(row, passengers):
    priorityOrder = ['STANDARD', 'STANDARD AREA SILENZIO', 'PREMIUM', 'BUSINESS', 'BUSINESS AREA SILENZIO', 'EXECUTIVE'] 
    pricesFound = {
            'young': -1,
            'senior' : -1,
            'adult' : -1
            }
    allPricesFound = lambda prices: prices['young'] != -1 and prices['senior'] != -1 and prices['adult'] != -1

    while (len(priorityOrder) > 0 and not allPricesFound(pricesFound)):
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
    row['minPrice'] = calculateMinPrice(row, passengers)
    return row

# searchedDate needs to be '%d/%m'
def processData(jsonData, searchedDate, passengers):
    df = pd.json_normalize(jsonData['solutions'])
    solutions = df[df['solution.status'] == "SALEABLE"][['solution.id','solution.departureTime','solution.arrivalTime','solution.duration','solution.origin','solution.destination','grids']]

    solutions.rename(columns={'solution.id':'id', 'solution.duration':'duration', 'solution.departureTime': 'departureTime', 'solution.arrivalTime': 'arrivalTime'}, inplace=True)
    solutions[['departureTime', 'arrivalTime']] = solutions[['departureTime', 'arrivalTime']].apply(pd.to_datetime)
    solutions[['departureDate','departureTime']] = solutions.departureTime.dt.strftime('%d/%m %H:%M').str.split(expand=True)
    solutions['arrivalTime'] = solutions.arrivalTime.dt.strftime('%H:%M')
    solutions['duration'] = solutions.duration.apply(lambda s: s.replace('h ',':').replace('min',''))
    solutions = solutions.apply(lambda col: findSolutionPrices(col, passengers), axis=1)
    solutions['company'] = 'trenitalia';

    sameDaySolutions = solutions[solutions['departureDate'] == searchedDate]
    sameDaySolutions = sameDaySolutions[sameDaySolutions['minPrice'] != '/'];

    solutionsDictionary = sameDaySolutions[['id', 'departureDate', 'departureTime', 'arrivalTime', 'duration', 'young', 'senior', 'adult','company', 'minPrice']].to_dict('records')
    foundNextDaySolutions = solutions.shape[0] > sameDaySolutions.shape[0]
    return [solutionsDictionary, foundNextDaySolutions]
