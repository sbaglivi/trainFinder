import json, sys

args = sys.argv[1:]

[origin, destination, depDate, depTime, retDate, retTime, passengers, goingoutId, cartId, cookies] = args
[adults, seniors, youngs] = list(map(int, passengers))

cookies = json.loads(cookies)

print(json.dumps(f'searching ret train from {destination} to {origin} on {retDate} at {retTime} for {adults+seniors+youngs} passengers'))