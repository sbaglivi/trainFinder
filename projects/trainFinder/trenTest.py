from trenitaliaProcessData import processData
import json

with open('testdata.txt','r') as f:
    rawData = json.load(f)
    trainData = processData(rawData, '10/11', [1,1,1])
    for line in trainData:
        print(line)