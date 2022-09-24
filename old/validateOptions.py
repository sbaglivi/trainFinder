import re
from datetime import datetime

italoStations = {
    'torinoPortaNuova' : 'TOP',
    'torinaPortaSusa' : 'OUE',
    'milanoCentrale' : 'MC_',
    'milanoRogoredo' : 'RG_',
    'reggioEmilia' : 'AAV',
    'bologna' : 'BC_',
    'firenze' : 'SMN',
    'romaTermini': 'RMT',
    'romaTiburtina' : 'RTB',
    'napoliCentrale' : 'NAC',
    'napoliAfragola' : 'NAF',
    'salerno' : 'SAL',
    'valloDellaLucania' : 'VLH'
}

trenitaliaStations = {
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

def validateOptions(args, stations):
    if (len(args) < 5):
        print(f"Expected 5 arguments (origin: string, destination: string, dataPartenza: dd-mm-yy oraPartenza: hh, \
         passengers: 3 0-9 numbers for Adults/Seniors/Youngs). Received {len(args)}")
        return False

    if (args[0] not in stations.keys() or args[1] not in stations.keys()):
        invalid = args[0] if args[0] not in stations.keys() else args[1]
        print(f"{invalid} is not a valid name for a train station. Accepted are ${stations.keys()}")
        return False

    if not validateDate(args[2]):
        print(f"Invalid date. Make sure the format is dd-mm-yy and the date is in the future.")
        return False

    hourPattern = re.compile("[01][0-9]|2[0-3]")
    if not hourPattern.match(args[3]):
        print(f"{args[3]} is not a valid format for the departure time. Accepted is hh).")
        return False

    if not re.compile("[1-9][0-9]{2}|[0-9][1-9][0-9]|[0-9]{2}[1-9]").match(args[4]):
        print(f"{args[4]} is not a valid format for passengers. Accepted is \d\d\d with at least 1 != 0.")
        return False
    return True

def trenitaliaValidateOptions(args):
    return validateOptions(args, trenitaliaStations)

def italoValidateOptions(args):
    return validateOptions(args, italoStations)

def validateMoreOptions(args):
    if len(args) != 2:
        print('Expected 2 more options for return: date and time')
        return False
    if not validateDate(args[0]):
        print(f"Invalid date. Make sure the format is dd-mm-yy and the date is in the future.")
        return False

    hourPattern = re.compile("[01][0-9]|2[0-3]")
    if not hourPattern.match(args[1]):
        print(f"{args[1]} is not a valid format for the departure time. Accepted is hh).")
        return False
    return True
def trenitaliaValidateRoundtrip(args):
    return validateOptions(args[:5], trenitaliaStations) and validateMoreOptions(args[5:])
def italoValidateRoundtrip(args):
    return validateOptions(args[:5], italoStations) and validateMoreOptions(args[5:])
