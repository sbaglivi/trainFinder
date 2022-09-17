import requests, sys, re
from datetime import datetime
from italo import *

url = "https://biglietti.italotreno.it/Booking_Acquisto_SelezioneTreno_A.aspx"
promoCodes = [
    {'code': 'VALIGIA', 'expires': '19-09-22 18', 'validAfter': '24-09-22'}
]

stazioni = {
    'milanoCentrale' : 'MC_',
    'firenze' : 'SMN'
}


def validateOptions(args):
    if (len(args) < 4):
        print(f"Expected 4 arguments (origin: string, destination: string, dataPartenza: dd-mm-yy, passengers A(dults)S(eniors)Y(oungs)). \
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
    passengerPattern = re.compile("\d{3}")
    if not passengerPattern.match(args[3]):
        print(f"{args[3]} is not a valid format for passengers: accepted is ASY in digits e.g. 100")
        sys.exit()
             

validateOptions(sys.argv[1:])

# User input
origin = stazioni[sys.argv[1]]
destination = stazioni[sys.argv[2]]
ticketDate = sys.argv[3]
adults = sys.argv[4][0]
senior = sys.argv[4][1]
young = sys.argv[4][2]

"""
adults = 1
senior = 0
young = 0
origin = stazioni['milanoCentrale']
destination = stazioni['firenze']
ticketDate = '25-09-22'
"""

def getPromoCode():
    promoCode = ''
    curDateObject = datetime.now()
    for code in promoCodes:
        expireDateObject = datetime.strptime(code['expires'], '%d-%m-%y %H')
        if expireDateObject > curDateObject:
            if datetime.strptime(code['validAfter'], '%d-%m-%y') < ticketDateObject:
                promoCode = code['code']
        else:
            print('code has expired')
    return promoCode

# Computed data 
day = ticketDate[:2]
ticketDateObject = datetime.strptime(ticketDate,'%d-%m-%y')
yearMonth = ticketDateObject.strftime('%Y-%m')
promoCode = getPromoCode()

#print(origin, destination, day, yearMonth, adults, senior, young, promoCode)

payload = f"__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=%2FwEPDwUBMGQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgQF3gFSZXN0eWxpbmdNYXN0ZXJIZWFkZXJJbXByZXNhUmVzdHlsaW5nQm9va2luZ1NlbGV6aW9uZVRyZW5vQVZpZXckTWFzdGVySGVhZGVyR2xvYmFsTWVudUltcHJlc2FSZXN0eWxpbmdCb29raW5nU2VsZXppb25lVHJlbm9BVmlldyRNYXN0ZXJIZWFkZXJHbG9iYWxNZW51QWdlbnRMb2dpbkltcHJlc2FSZXN0eWxpbmdCb29raW5nU2VsZXppb25lVHJlbm9BVmlldyRDaGVja0JveFJlbWVtYmVyTWUFwwFNYXN0ZXJIZWFkZXJSZXN0eWxpbmdCb29raW5nU2VsZXppb25lVHJlbm9BVmlldyRNYXN0ZXJIZWFkZXJHbG9iYWxNZW51UmVzdHlsaW5nQm9va2luZ1NlbGV6aW9uZVRyZW5vQVZpZXckTWFzdGVySGVhZGVyR2xvYmFsTWVudU1lbWJlckxvZ2luUmVzdHlsaW5nQm9va2luZ1NlbGV6aW9uZVRyZW5vQVZpZXckQ2hlY2tCb3hSZW1haW5Mb2dnZWQFwQFNYXN0ZXJIZWFkZXJSZXN0eWxpbmdCb29raW5nU2VsZXppb25lVHJlbm9BVmlldyRNYXN0ZXJIZWFkZXJHbG9iYWxNZW51UmVzdHlsaW5nQm9va2luZ1NlbGV6aW9uZVRyZW5vQVZpZXckTWFzdGVySGVhZGVyR2xvYmFsTWVudU1lbWJlckxvZ2luUmVzdHlsaW5nQm9va2luZ1NlbGV6aW9uZVRyZW5vQVZpZXckQ2hlY2tCb3hSZW1lbWJlck1lBcABTWFzdGVySGVhZGVyUmVzdHlsaW5nQm9va2luZ1NlbGV6aW9uZVRyZW5vQVZpZXckTWFzdGVySGVhZGVyR2xvYmFsTWVudVJlc3R5bGluZ0Jvb2tpbmdTZWxlemlvbmVUcmVub0FWaWV3JE1hc3RlckhlYWRlckdsb2JhbE1lbnVBZ2VudExvZ2luUmVzdHlsaW5nQm9va2luZ1NlbGV6aW9uZVRyZW5vQVZpZXckQ2hlY2tCb3hSZW1lbWJlck1lDr6cBD4zY3%2Fi565gwK%2BqNwmzH7c%3D&pageToken=&MasterHeaderRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuMemberLoginRestylingBookingSelezioneTrenoAView%24TextBoxUserID=&MasterHeaderRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuMemberLoginRestylingBookingSelezioneTrenoAView%24PasswordFieldPassword=&MasterHeaderRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuMemberLoginRestylingBookingSelezioneTrenoAView%24HiddenSocialLoginRequested=&MasterHeaderRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuMemberLoginRestylingBookingSelezioneTrenoAView%24TextBoxUserIDSocial=&MasterHeaderRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuMemberLoginRestylingBookingSelezioneTrenoAView%24TextBoxPasswordSocial=&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24ButtonChangeSearchInBookingFlow=&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24HIDDENBSJ=true&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListSearchBy=columnView&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListFareTypes=ST&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24RadioButtonMarketStructure=OneWay&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24TextBoxMarketOrigin1={origin}&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24TextBoxMarketDestination1={destination}&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListMarketDay1={day}&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListMarketMonth1={yearMonth}&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownDepartureTimeHoursBegin_1=0&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownDepartureTimeHoursEnd_1=24&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListMarketDay2={day}&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListMarketMonth2={yearMonth}&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownDepartureTimeHoursBegin_2=0&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownDepartureTimeHoursEnd_2=24&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListPassengerType_ADT={adults}&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListPassengerType_CHD=0&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListPassengerType_SNR={senior}&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListPassengerType_YNG={young}&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24PetTextBox=0&promocode={promoCode}&BookingGrigliaTreniRestylingBookingSelezioneTrenoAView%24AvailabilitySearchInputRestylingBookingSelezioneTrenoAView%24InfantTextBox=0&BookingGrigliaTreniRestylingBookingSelezioneTrenoAView%24AvailabilitySearchInputRestylingBookingSelezioneTrenoAView%24PetTextBox=0&BookingGrigliaTreniRestylingBookingSelezioneTrenoAView%24AvailabilitySearchInputRestylingBookingSelezioneTrenoAView%24DropDownListFareTypes=ST&BookingGrigliaTreniRestylingBookingSelezioneTrenoAView%24AvailabilitySearchInputRestylingBookingSelezioneTrenoAView%24DropDownListSearchBy=&BookingGrigliaTreniRestylingBookingSelezioneTrenoAView%24AvailabilitySearchInputRestylingBookingSelezioneTrenoAView%24RadioButtonMarketStructure=OneWay&BookingGrigliaTreniRestylingBookingSelezioneTrenoAView%24PromoCodeRestylingBookingSelezioneTrenoAView%24TextBoxPromoCode=&BookingGrigliaTreniRestylingBookingSelezioneTrenoAView%24AvailabilitySearchInputRestylingBookingSelezioneTrenoAView%24HiddenDateToSearch=&BookingGrigliaTreniRestylingBookingSelezioneTrenoAView%24AvailabilitySearchInputRestylingBookingSelezioneTrenoAView%24HiddenCurrentMarketIndexForChangeDatetoSearch=1&BookingGrigliaTreniRestylingBookingSelezioneTrenoAView%24HiddenFieldBloccaPrezzo=&ShareBookingControlRestylingBookingSelezioneTrenoAView%24HiddenFieldSellKeys=&ShareBookingControlRestylingBookingSelezioneTrenoAView%24HiddenFieldFarePrice=&ShareBookingControlRestylingBookingSelezioneTrenoAView%24TextBoxReceiverEmail=&ShareBookingControlRestylingBookingSelezioneTrenoAView%24TextBoxSenderName=&ShareBookingControlRestylingBookingSelezioneTrenoAView%24TextBoxSenderEmail=&ShareBookingControlRestylingBookingSelezioneTrenoAView%24TextBoxMessage="
headers = {
    "cookie": "RECENT_SEARCHES=RECENT_SEARCHES_0%3DMC_%7CSMN; _abck=F3CFA9C4AE97D7F3017E897F994C0441~-1~YAAQHBTfrUrAo0qDAQAAwqjZTAg3p8QYmI8X3%2FX2WqYlin5U2lmGSELaCtfs5KcEZYhWNT7ZDW2qUArBNrhlTyOIxjjr%2BqH9%2FgzLPy8KRIpCoCGVy7rVGKuSJgacWiIZoECTS080Se%2FbltsEC0GY5hMTI1aOeqNcLi1jxYtrH%2Fi1O3PulBfg6ndx%2BfN3nKATfi8jaeSkhBL9a%2BonqTSYw6BtSI3xLtvQHkVCPmA9ctf6KE7b56LUBiEUZ07AihSnRj6GsO9EBo%2BSxBpJeBMSG8amPrmOzXeKMtDmptDOoeil%2BNPnNh1whnjC%2FwF0AoX3akKr%2FnMHu%2FUkKzFBlUTDfXrWMspV4%2FOGjQwPnaZP053LIKk%2FY1w8aMAo3mFNIBQ%3D~-1~-1~-1",
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://biglietti.italotreno.it",
    "Connection": "keep-alive",
    "Referer": "https://biglietti.italotreno.it/Booking_Acquisto_SelezioneTreno_A.aspx",
    "Cookie": "_abck=F3CFA9C4AE97D7F3017E897F994C0441~0~YAAQERTfrRrb/UODAQAAtawbRwixWjACROvGIymkUnI+rz0PiHltMcYQ4lQhDvQVWlc+9RMPQE8VIxi69rlAHiGORo32fh2yyxCenh0SPkWDYZWWSTEqE649DoiDm2bSoZVWZHePjuUpMpI7/R/NypfROFtd7XzvgIbZyoTg1BM2gC4xfxgmV18Ku3AYuuoWjJpb/9/ve8iPmmV2cNgpLSxuKUMQYFnpBlrE0xTsRuTrXP2Ynjb3v9FILyMt+uq9kPfNS5mGKdqButjsk7GvBPWGi/P7MZAK8g0iACltLsujTjFtyEI5RpksDC/fj3pCRXE6RnNw94c6DQWM9JT3cIE8YCgWw3ANlV0aAMown2KNFjkNzJg5ho051btLSB4p90HP+qYNkv5xEdQvk5jw+rvX4/VAczW7~-1~-1~-1; apay-session-set=IU0S6ZhkNw03AwWuw7P3AhcJ%2BfMcYSjmoYnw14%2FPaUIrLIN5Hd3vkvB3pFeXgw0%3D; RECENT_SEARCHES=RECENT_SEARCHES_0=MC_|SMN; AcceptCookie=True; dtCookie=v_4_srv_5_sn_E53A4081AE77686CAC8DE0CF52CEA0D7_perc_100000_ol_0_mul_1_app-3Aea7c4b59f27d43eb_0_app-3Aabf0a1c42afd340d_0; AKA_A2=A; bm_sz=5EDF780951DFB3B1A7AE0B3CC31940D9~YAAQNvwUArzeM0CDAQAAcKkaRxE4lPiAi1um+naIXLcsH/RQLxDxyyP2xPLjsdKu5vB8IrZxgV+Vc7VrwrX+JloOJLE5awh1E1N6Bw1VXYFngsxpixOWYVp6yt+KvjFBaQvkf6et0qB2dbza1Bn15K5UrhR0SNQwfQx6FEwQ+07k3YLfLKez4A6Mc8hLDgpCQt9w/kFPePU2p1r3tK294POIiw54Wa41uSpMYanOZM1Hm8RQuxY0wtC51ULT6hrhTXbE/1s2yb29/Yy7KJ/DWUksZFzN9E97/opzsP2Htn04Bzm4p+U=~4338500~3420993; Culture=en-US; ak_bmsc=B55242B2608B8CD36114AD6F0E873706~000000000000000000000000000000~YAAQNvwUAn3fM0CDAQAAmcAaRxEEn4x6YPZxARhR5kNqYwIToEsbVbtGECAoZzGi0LaX81O/ExO53zzZuHvbTJrZjs1aia9UAIpfRUw6QRyB2aHglMT8Xf2+KDA5hM348T8APEZf+H580d7iWJoSQ5SyTGmeTV4ZoyMK5RgQ8reztKOVOZZ78UXVkbSHYReAwdblJzzxpS9KUuIHPBBLekRDF7krSBcpH99gSYahBV4oUdlhn0OvPn4O+7WsBd+USJs6iwlu0fvg+eV8vCUOO6wNW20MJ9grbLYNKQ5KgKcTuL/m7wNwlWrvqzx7tHHS6wbnGsw9l1bx0djIM7hRWctp7i/9Ynkf7+mDagUBcXEN5ocpYha5AJdckLyxA6kjxbi6NkP0Z+ocWAI=; bm_mi=37AC3963305CD60D46757A01EE577306~YAAQNvwUAonlM0CDAQAAN3obRxGO78UIw9CIpbNfPhjxutB3wXMPtYO6+o9/wHvSn73LpC7fprHuO8bX+vsRzR8WW/0N4lJKbdHyaBk8fMVG8upFCYFd1tFCvV1jJHLjfI/Pd1KmMrKXm+RZ6wIVTcnJlGsHm+sm5UBuxX54OQxaH0ecW5i85lBEO8Wq8ejoMjxIqWxwqGTnatQ5luVI+RC5vGSbDgPQxLGZLuxQ1XXKhUmjOoxUfD//VKEeSSKICkwQZhX4WGpJbzulNmzqkbgcXP59MLYTlJ4JQarU1OnExc0KJXEngyk6k33Wf1wRZV4=~1; bm_sv=A2066F8088E6E70DC6770B03D38D071A~YAAQERTfrR/c/UODAQAAm7QbRxEYpmjML96Hh1hOr0JaKZzelVcKL/s6uCKjbnou7QvxvdWE+yKMqI6joOxbUA2dUVXBTcKlP2CYnM1v9li+zznNAeiQQZkBivvTwtQU6cr6gegzXVaQD3W0DCrBVYUhetRBw1GaSeZz3ugUdmxXZyuZu/p34y/KC18J2zg2XKq68NFzZZALJ5oAzhgguDEhBE7OkHJJji5Fe0H+tYRyLKLQ7cw/A7+qY5bscNqk7JMk~1; ASP.NET_SessionId=fha3gq555vhmpv55euulnz45; skysales=!08PcKv6UaMadtjYBPRVOtlB1GpUQJXA6HFb2Vov3yrYt38lcFOnjP4DSHidYboxVhXZFOyleGXtrQBU=; rxVisitor=166334534165467H1296LCO86EK23A8FJQM0HLBERA738; dtPC=5$145341650_200h1vCODLUIPDDNRWRHKMOTVKAOPHDMKSACWO-0e0; rxvt=1663347141656|1663345341656",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1"
}

response = requests.request("POST", url, data=payload, headers=headers)

with open('temp.html', 'w') as f:
    f.write(response.text)

data = getDataFromHtml(response.text, ticketDateObject.strftime('%d/%m'))

print(json.dumps(data))


#with open('italoResponse.html', 'w') as f:
#    f.write(response.text)
