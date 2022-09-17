from time import time
import requests


url = "https://www.lefrecce.it/Channels.Website.BFF.WEB/website/ticket/solutions"

stazioni = {
    "torinoPortaSusa" : 830000222,
    "torinoPortaNuova" : 830000219,
    "milanoGaribaldi" : 830001645,
    "milanoCentrale" :  830001700,
    "milanoRogoredo" : 830001820,
    "reggioEmilia" : 830005254,
    "bologna" : 830005043,
    "firenze" : 830006421,
    "romaTermini" : 830008409,
    "romaTiburtina" : 830008217,
    "napoliCentrale" : 830009218,
    "napoliAfragola" : 830009988,
    "salerno" :  830009818,
    "valloDellaLucania" : 830011709
}

dataPartenza = "2022-09-23"
oraPartenza = "16:00"


def findTrains(origin, destination, departureDate, departureTime): 
    # time is hh:mm, date is yyyy-mm-dd. I have hardcoded timezone, I have no clue when it will change

    departureTimestamp = f"{departureDate}T{departureTime}:00.000+02:00"
    currentTimestamp = int(time())

    payload = {
        "departureLocationId": origin,
        "arrivalLocationId": destination,
        "departureTime": departureTimestamp,
        "adults": 1,
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

    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0",
        "Accept": "application/json, application/pdf, text/calendar",
        "Accept-Language": "en-GB",
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": "https://www.lefrecce.it/Channels.Website.WEB/",
        "Content-Type": "application/json",
        "X-Requested-With": "Fetch",
        "X-CSRF-Token": "wxLJjYWjE4XkXGQBcdKDTdZ9A3JnXEM8YbHSUbKvTJ+jBA81c4xiTEjl0xKgEb0CrI8ujkXJWxMBb3z2PzEv/Q==",
        "Channel": "41",
        "CallerTimestamp": str(currentTimestamp),
        "Origin": "https://www.lefrecce.it",
        "Connection": "keep-alive",
        "Cookie": "WSESSIONID=0000lRSUFYeJ0NozrKtJYXi_1UY:PRODWEB137A; CSRFToken=bed8e85c-68a0-4bf1-80e6-dffd2d7844b0; b2b.apm.cookie=desktop; ak_bmsc=547A725EBC438316872DEB8BA3D09EB4~000000000000000000000000000000~YAAQLRTfrVt9RTCDAQAAomvtNhH+u2FalOhxS27vWQS3e8sHAcbjln/Dzu6syDhBRRtwcnJqXDDGzOx+2d1jgi5LGbEaSMv8T+35N67xoNxlGRrkbgr9SEQ+t+MB0AEeLfvf5q08sFT6T+0JLX0dPFzK4ZGRBYHZGYcoB2xzwPdcuSiXW9ER7lmbyMxOaul/NG4FqFTQ5AGkIcYxHpom/qvDZQRuHOFF+dLvhxMkoSMZtJUYZ5BASPqEMK3U/dW9YyTOJiv/rEoh32abeCsgvYWquL46dBPlSQrWdYxWAyE4HcMVG1KVu39gRCNBuOApPN2JUDLGnoXjoH2HhR2sshCjiqObtn3m9+FC1Mjnc8bQh5jTb3DvWfeFXx92AXkL9rU7uZjDDQLJ; bm_sv=6D1B3884D612F3E45817F4A5CA93209F~YAAQMhTfrXxe4gKDAQAA7XD/NhEUKnylC5x2fNqEvcx/eTrumMtR9viaY6hnozL1iFU+JzV3DkSHlLTNT0u4vxfIyRQstB5gXjITkoaGJrF5viWH5psMJAltgiK33yO0cOuKLQivm+ql5vDCYxSK1//XWW2fs79EHvELYEwyJpZsn6BHMQEUyDIhdK5Tu5L5DklV0T3qsiDVGQnNh1ldGvrdezEUONERybqt3hpefUSutHz8KAL3/h71BC2T/MdT2Zo=~1; bm_mi=7A1283CABB5FC78FBD3160B0676F84BF~YAAQMhTfrSdV4gKDAQAAajr/NhFwjvBHKJ5YULa4TXlmftRWJb4US+HDjlu0xtmbWohxo8vg2/y19VBU9j1VoxUukDw+/biCN1Bk+fIHkQGSrPv+1pllHMrsWsZEVGoXgTZQyV3qDv4wGZ6GlMeSQA8gOLugmILLhXFkLWU3cpxZF/fPIcUEinzqzdv4br6RFra/W6RWB9vYeacPdF3oI1heUhJSs0DV5LySdyAyi4dTTkE4u7M5jYNSmfnAQnMGFvXfe0zI86aOXX9loeGMJUi/S2wbe3bcsVf9yywczTXE7OZ0EskshpSuy/6Mn+Q2e4HjHVFzwrFuiq7jagAxlHeCS9w=~1",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-origin",
        "TE": "trailers"
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    return response

#response = findTrains(stazioni['milanoCentrale'], stazioni['firenze'], dataPartenza, oraPartenza)
#print(response.text)
