import requests, time, sys, json
from datetime import datetime
from validateOptions import trenitaliaStations as stations
from trenitaliaProcessData import processData

depDate = '25-09-22'
depTime = '09'
retDate = '25-09-22'
retTime = '17'
depDateObject = datetime.strptime(depDate,'%d-%m-%y')
retDateObject = datetime.strptime(retDate,'%d-%m-%y')
depTimeString = f"{depDateObject.strftime('%Y-%m-%d')}T{depTime}:00:00.000+02:00"
retTimeString = f"{retDateObject.strftime('%Y-%m-%d')}T{retTime}:00:00.000+02:00"
trainDateObject = depDateObject
passengers = '200'
[adults, seniors, youngs] = list(map(int, passengers))

args = sys.argv[1:]
[origin, destination] = args
totalPassengers = 2
originId = stations[origin]
destinationId = stations[destination]

url = "https://www.lefrecce.it/Channels.Website.BFF.WEB/website/ticket/solutions"

payload = {
    "departureLocationId": originId,
    "arrivalLocationId": destinationId,
    "departureTime": depTimeString,
    "returnDepartureTime": retTimeString,
    "adults": adults+seniors+youngs,
    "children": 0,
    "criteria": {
        "frecceOnly": True,
        "regionalOnly": False,
        "noChanges": True,
        "order": "DEPARTURE_DATE",
        "offset": 0,
        "limit": 10
    },
    "advancedSearchRequest": {"bestFare": False}
}
currentTimestamp = int(time.time())
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0",
    "Accept": "application/json, application/pdf, text/calendar",
    "Accept-Language": "en-GB",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.lefrecce.it/Channels.Website.WEB/",
    "Content-Type": "application/json",
    "X-Requested-With": "Fetch",
    "X-CSRF-Token": "j5IXMP7te5qXgAC0f1/OWxspP5SeGJzO9jOENy50FY25UmyZ0y8f5fueM7Mkseu1rI8ujkXJWxMBb3z2PzEv/Q==",
    "Channel": "41",
    "CallerTimestamp": str(currentTimestamp),
    "Origin": "https://www.lefrecce.it",
    "Connection": "keep-alive",
    #"Cookie": "ak_bmsc=D0669D5289E95E09ABE72F85841B5FFE~000000000000000000000000000000~YAAQLRTfrRNthDqDAQAAWOM0VhF3hrSxrWyNNeIWLPLKtPBcDR41Jw6/odOObaf4VTQnZnzY9tBIGFRDOo2esArmheJ6gh6CDdbIplxz4S1v26PjQsAI1L/SyG9zX3qRu6IMMRTOQXObbHltMHmifZqZk6lZLLpGdK1CZZCd/KoqnWudwGqtlpekXLZ6Uk2RB0Yj+BlGrjYBN4slnF/j81rAXk1OkPROgLYg+b11uZ5w0MWETXj2uscOVrI4ttB5cCTmnD3vcV6n8+JIE/AVYlZNeudJuxQZwNcMguKZQwpbHv7c0Oem1JQ0Zut11lYiuNAJep7MPBmB6kqTu7C4MGrSoFjBMdOfaRb1pJeQf2B+AdHk78Mn7MKrL57n8b/IjiwA7VcCHPs/; bm_sv=FE88010ADFD1FF13E84E3658ECAF3754~YAAQIxTfrRi4RRqDAQAAnJdTVhF0VlBdk8bPi33JC4GtQaT9YwSt63sLathg4qwJGzFszB7AMI3HXCoA531eDaqBtU7r0NOo095lhI/9Ft4H7dDDZvLQyTVyJ942V81bvwDJp4tnYue9ywLlnAEBUo6V6yaY8/Ih5t4fSJqhjl1wkZZFwcQGqOLBwOEIWrsGUbGpotOgBJtu+mDCd5vIUerXP2XocMS2b3817eCF4HMcIU4WvWMQEmaUtTG51VqnMDE=~1; bm_mi=9895D04A03648BEB751E007DB152C14C~YAAQIxTfrWm0RRqDAQAArm5TVhHGayEDRRdNVutcYZcVzU0VJyGfXVaQet2V8ALcgAGbJH/OAG9wTxSaAkDaU0CeiodehXSZA4Kk4/A1XfU2zpg0le9UTdz6xyfQAplRj2odvQVs2r8pkz77b5449o+IjY1kI7FRGf7fZGnNc7csmWndwMOUq211h48fBb6amcg2ZPAj6gIlArmc7Ny7km+9cSQuCvVOvAnT5AVUx/NIr4S2acXe2lWqZiG58n1jpkv3cHk2d8cnNK3S3SP7rBdubTYaFrSWGcEffgPs3x37xaLWWtyESsxKHQi5rN3h+lzzyLsPWtBGS17Dbe1Uos+EGz4=~1; WSESSIONID=0000UPY2uWVGTawNB9mcNfYRVRC:PRODWEB416B; CSRFToken=aab5ee9f-c118-401c-9f6a-4b0d573000f3; b2b.apm.cookie=desktop",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-origin",
    "TE": "trailers"
}

with open ('trenarlog.txt', 'w') as log:
    # response = session.post(url, json=payload, headers=headers)
    response = requests.request("POST", url, json=payload, headers=headers)
    log.write(str(response.request.headers))
    log.write('\n\n')
    log.write(str(response.request._cookies))
    log.write('\n\n')
    log.write(str(response.headers))
    log.write('\n\n')
    log.write(str(response.cookies))
    log.write('\n\n')

    with open('trenA.txt', 'w') as f:
        f.write(response.text)

    data = response.json()
    [optionsList, _] = processData(data, depDateObject.strftime('%d/%m'), [adults, seniors, youngs])
    for i in range(len(optionsList)):
        print(f"{i} - {optionsList[i]}")
    choice = int(input('Type the index of desired choice\n'))


    print(f'You selected option: {optionsList[choice]}')
    with open('splitA.json', 'w') as f:
        parameters = {'originId': originId, 'destinationId': destinationId, 'depDate': depDate, 'depTime': depTime, 'passengers': passengers, 'retDate': retDate, 'retTime': retTime, 'goingoutId': optionsList[choice]['id'], 'cartId': data['cartId'], 'cookies': response.cookies.get_dict()}
        f.write(json.dumps(parameters))