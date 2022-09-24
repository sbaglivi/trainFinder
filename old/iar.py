import requests, sys, json
from datetime import datetime
from italoProcessData import getDataFromHtml
from validateOptions import italoStations as stations


args = sys.argv[1:]

[origin, destination, depDate, depTime, passengers, retDate, retTime] = args
[adults, seniors, youngs] = list(map(int, passengers))
[originId, destinationId] = [stations[origin], stations[destination]]
totalPassengers = adults+seniors+youngs
depDateObject = datetime.strptime(depDate, '%d-%m-%y')
retDateObject = datetime.strptime(retDate, '%d-%m-%y')


depDay = depDate[:2]
depYearMonth = depDateObject.strftime('%Y-%m')
retDay = retDate[:2]
retYearMonth = retDateObject.strftime('%Y-%m')
promoCode = '' # CHANGE ME

# First Request (second attempt)

url = "https://biglietti.italotreno.it/Booking_Acquisto_SelezioneTreno_A.aspx"

payload = f"__EVENTTARGET=&__EVENTARGUMENT=&__VIEWSTATE=%2FwEPDwUBMGQYAQUeX19Db250cm9sc1JlcXVpcmVQb3N0QmFja0tleV9fFgQF3gFSZXN0eWxpbmdNYXN0ZXJIZWFkZXJJbXByZXNhUmVzdHlsaW5nQm9va2luZ1NlbGV6aW9uZVRyZW5vQVZpZXckTWFzdGVySGVhZGVyR2xvYmFsTWVudUltcHJlc2FSZXN0eWxpbmdCb29raW5nU2VsZXppb25lVHJlbm9BVmlldyRNYXN0ZXJIZWFkZXJHbG9iYWxNZW51QWdlbnRMb2dpbkltcHJlc2FSZXN0eWxpbmdCb29raW5nU2VsZXppb25lVHJlbm9BVmlldyRDaGVja0JveFJlbWVtYmVyTWUFwwFNYXN0ZXJIZWFkZXJSZXN0eWxpbmdCb29raW5nU2VsZXppb25lVHJlbm9BVmlldyRNYXN0ZXJIZWFkZXJHbG9iYWxNZW51UmVzdHlsaW5nQm9va2luZ1NlbGV6aW9uZVRyZW5vQVZpZXckTWFzdGVySGVhZGVyR2xvYmFsTWVudU1lbWJlckxvZ2luUmVzdHlsaW5nQm9va2luZ1NlbGV6aW9uZVRyZW5vQVZpZXckQ2hlY2tCb3hSZW1haW5Mb2dnZWQFwQFNYXN0ZXJIZWFkZXJSZXN0eWxpbmdCb29raW5nU2VsZXppb25lVHJlbm9BVmlldyRNYXN0ZXJIZWFkZXJHbG9iYWxNZW51UmVzdHlsaW5nQm9va2luZ1NlbGV6aW9uZVRyZW5vQVZpZXckTWFzdGVySGVhZGVyR2xvYmFsTWVudU1lbWJlckxvZ2luUmVzdHlsaW5nQm9va2luZ1NlbGV6aW9uZVRyZW5vQVZpZXckQ2hlY2tCb3hSZW1lbWJlck1lBcABTWFzdGVySGVhZGVyUmVzdHlsaW5nQm9va2luZ1NlbGV6aW9uZVRyZW5vQVZpZXckTWFzdGVySGVhZGVyR2xvYmFsTWVudVJlc3R5bGluZ0Jvb2tpbmdTZWxlemlvbmVUcmVub0FWaWV3JE1hc3RlckhlYWRlckdsb2JhbE1lbnVBZ2VudExvZ2luUmVzdHlsaW5nQm9va2luZ1NlbGV6aW9uZVRyZW5vQVZpZXckQ2hlY2tCb3hSZW1lbWJlck1lDr6cBD4zY3%2Fi565gwK%2BqNwmzH7c%3D&pageToken=&MasterHeaderRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuMemberLoginRestylingBookingSelezioneTrenoAView%24TextBoxUserID=&MasterHeaderRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuMemberLoginRestylingBookingSelezioneTrenoAView%24PasswordFieldPassword=&MasterHeaderRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuMemberLoginRestylingBookingSelezioneTrenoAView%24HiddenSocialLoginRequested=&MasterHeaderRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuMemberLoginRestylingBookingSelezioneTrenoAView%24TextBoxUserIDSocial=&MasterHeaderRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuRestylingBookingSelezioneTrenoAView%24MasterHeaderGlobalMenuMemberLoginRestylingBookingSelezioneTrenoAView%24TextBoxPasswordSocial=&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24ButtonChangeSearchInBookingFlow=&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24HIDDENBSJ=true&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListSearchBy=columnView&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListFareTypes=ST&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24RadioButtonMarketStructure=RoundTrip&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24TextBoxMarketOrigin1={originId}&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24TextBoxMarketDestination1={destinationId}&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListMarketDay1={depDay}&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListMarketMonth1={depYearMonth}&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownDepartureTimeHoursBegin_1=0&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownDepartureTimeHoursEnd_1=24&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListMarketDay2={retDay}&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListMarketMonth2={retYearMonth}&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownDepartureTimeHoursBegin_2=0&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownDepartureTimeHoursEnd_2=24&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListPassengerType_ADT={adults}&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListPassengerType_CHD=0&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListPassengerType_SNR={seniors}&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24DropDownListPassengerType_YNG={youngs}&ModuloRicercaBookingRicercaRestylingBookingSelezioneTrenoAView%24PetTextBox=0&promocode=&BookingGrigliaTreniRestylingBookingSelezioneTrenoAView%24AvailabilitySearchInputRestylingBookingSelezioneTrenoAView%24InfantTextBox=0&BookingGrigliaTreniRestylingBookingSelezioneTrenoAView%24AvailabilitySearchInputRestylingBookingSelezioneTrenoAView%24PetTextBox=0&BookingGrigliaTreniRestylingBookingSelezioneTrenoAView%24AvailabilitySearchInputRestylingBookingSelezioneTrenoAView%24DropDownListFareTypes=ST&BookingGrigliaTreniRestylingBookingSelezioneTrenoAView%24AvailabilitySearchInputRestylingBookingSelezioneTrenoAView%24DropDownListSearchBy=&BookingGrigliaTreniRestylingBookingSelezioneTrenoAView%24AvailabilitySearchInputRestylingBookingSelezioneTrenoAView%24RadioButtonMarketStructure=RoundTrip&BookingGrigliaTreniRestylingBookingSelezioneTrenoAView%24PromoCodeRestylingBookingSelezioneTrenoAView%24TextBoxPromoCode={promoCode}&BookingGrigliaTreniRestylingBookingSelezioneTrenoAView%24AvailabilitySearchInputRestylingBookingSelezioneTrenoAView%24HiddenDateToSearch=&BookingGrigliaTreniRestylingBookingSelezioneTrenoAView%24AvailabilitySearchInputRestylingBookingSelezioneTrenoAView%24HiddenCurrentMarketIndexForChangeDatetoSearch=1&BookingGrigliaTreniRestylingBookingSelezioneTrenoAView%24HiddenFieldBloccaPrezzo=&ShareBookingControlRestylingBookingSelezioneTrenoAView%24HiddenFieldSellKeys=&ShareBookingControlRestylingBookingSelezioneTrenoAView%24HiddenFieldFarePrice=&ShareBookingControlRestylingBookingSelezioneTrenoAView%24TextBoxReceiverEmail=&ShareBookingControlRestylingBookingSelezioneTrenoAView%24TextBoxSenderName=&ShareBookingControlRestylingBookingSelezioneTrenoAView%24TextBoxSenderEmail=&ShareBookingControlRestylingBookingSelezioneTrenoAView%24TextBoxMessage="
headers = {
    "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:104.0) Gecko/20100101 Firefox/104.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/x-www-form-urlencoded",
    "Origin": "https://biglietti.italotreno.it",
    "Connection": "keep-alive",
    "Referer": "https://biglietti.italotreno.it/Booking_Acquisto_SelezioneTreno_A.aspx",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Fetch-Dest": "document",
    "Sec-Fetch-Mode": "navigate",
    "Sec-Fetch-Site": "same-origin",
    "Sec-Fetch-User": "?1"
}

response = requests.request("POST", url, data=payload, headers=headers)

data = getDataFromHtml(response.text, totalPassengers, depTime)
savedData = {'data': data, 'cookies': response.cookies.get_dict()}
with open('italoA.html', 'w') as f:
    f.write(response.text)
with open('italoA.json', 'w') as f:
    f.write(json.dumps(savedData))

print(json.dumps(savedData))