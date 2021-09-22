from api_keys import *
import requests
import datetime
import logging
logging.basicConfig(filename='BusBoard.log', filemode='w', level=logging.DEBUG)


def getPostcode(postcode):
    print('Thanks, querying...')
    lat, lon = postcode2LatLon(postcode)
    return lat, lon


def postcode2LatLon(postcode):
    postcodeInfo = postcodeRequest(postcode)

    if postcodeInfo['result'] is None:
        print('I said a valid UK postcode you dingbat, you get Bath now')
        postcode = 'BA2 1AX'
        postcodeInfo = postcodeRequest(postcode)

    lat = postcodeInfo["result"][0]["latitude"]
    lon = postcodeInfo["result"][0]["longitude"]

    return lat, lon


def postcodeRequest(postcode):
    p = requests.get(f'https://api.postcodes.io/postcodes?q={postcode}')
    postcodeInfo = p.json()
    return postcodeInfo


def getBusStops(lat, lon):
    s = requests.get(f'http://transportapi.com/v3/uk/places.json?lat={lat}&lon={lon}&type=bus_stop&app_id={APP_ID}'
                     f'&app_key={APP_KEY}')

    response_stops = s.json()
    stops = response_stops["member"]
    return stops


def getBusTimes(stops, ii):
    Atcocode = stops[ii]["atcocode"]
    Distance = int(stops[ii]["distance"])
    name = stops[ii]["name"]

    nextFiveBuses = []
    nextFiveBuses.append({"Name": name, "Distance": Distance, "TimeMinutes": 0})

    r = requests.get(f'http://transportapi.com/v3/uk/bus/stop/{Atcocode}/live.json?app_id={APP_ID}'
                     f'&app_key={APP_KEY}')
    response = r.json()
    departures = response["departures"]
    nextFiveBuses = getNextFive(departures, nextFiveBuses)

    # nextFiveBuses.append({"Name": name, "Distance": Distance})

    return nextFiveBuses


def getNextFive(departures, busList):
    # returns a list of dictionaries which contain information on the next five buses expected to arrive at the given
    # bus stop
    i = 0
    # busList = []
    # loops through every bus number (consisting of several buses behind each other in the timetable)
    # busNumber is name in-specific, the bus number is the top level Key within 'departures'
    for busNumber in departures:
        # loops through every individual bus of a given number (API only stores 3 at a time I think)
        for departure in departures[busNumber]:
            arrivalTimeMinutes, arrivalTime = timeConversion(departure)
            Buses = {"Number": busNumber, "Destination": departure["direction"], "ArrivalTime": arrivalTime,
                     "TimeMinutes": arrivalTimeMinutes}
            busList.append(Buses)
            i += 1

    # sort buses by the earliest to arrive (ArrivalSeconds Key)
    busList.sort(key=lambda y: y["TimeMinutes"])    # y keyword is non specific but does need to access correct key
    busList = busList[0:5]

    # delete un-needed dictionary entries
    for x in range(0, len(busList)):
        del busList[x]["TimeMinutes"]

    return busList


def HMFunction(listName, key):
    Hour = int(listName[key][0:2])
    Minute = int(listName[key][3:5])
    return Hour, Minute


def YMDFunction(listName, key):
    Year = int(listName[key][0:4])
    Month = int(listName[key][5:7])
    Day = int(listName[key][8:10])
    return Year, Month, Day


def timeConversion(departure):

    expectedArrival = departure["expected"]["arrival"]

    try:
        Hour, Minute = HMFunction(expectedArrival, "time")
    except TypeError:
        Hour, Minute = HMFunction(departure, "aimed_departure_time")
        logging.warning('no "expected" field,  "aimed_departure_time" used instead')

    try:
        Year, Month, Day = YMDFunction(expectedArrival, "date")
    except TypeError:
        Year, Month, Day = YMDFunction(departure, "date")
        logging.warning('no "expected" field,  "date" used instead')

    arrivalTimeMinutes = int((datetime.datetime(Year, Month, Day, Hour, Minute)
                              - datetime.datetime(1970, 1, 1, 0, 0)).total_seconds()) // 60

    # correct date format for display
    if Minute < 10:
        Minute = f'0{Minute}'
    if Hour < 10:
        Hour = f'0{Hour}'
    arrivalTime = f'{str(Hour)}:{str(Minute)}'

    return arrivalTimeMinutes, arrivalTime


def displayBusTimes(nextFiveBuses):
    print(f'\n{nextFiveBuses[0]["Name"]} ({nextFiveBuses[0]["Distance"]}m)')
    for i in range(1, len(nextFiveBuses)):
        print(f'{nextFiveBuses[i]["Number"] :<4} {nextFiveBuses[i]["Destination"] :<45}'
              f' {nextFiveBuses[i]["ArrivalTime"] :<5}')


def listBusTimes(nextFiveBuses):
    listFiveBuses = []
    listFiveBuses.append(f'\n{nextFiveBuses[0]["Name"]} ({nextFiveBuses[0]["Distance"]}m)')
    for i in range(1, len(nextFiveBuses)):
        listFiveBuses.append(f'{nextFiveBuses[i]["Number"] :<4} {nextFiveBuses[i]["Destination"] :<45}'
                             f' {nextFiveBuses[i]["ArrivalTime"] :<5}')

    return listFiveBuses

def newlistBusTimes(nextFiveBuses):
    listFiveBuses = []
    listFiveBuses.append(f'\n{nextFiveBuses[0]["Name"]} ({nextFiveBuses[0]["Distance"]}m)')
    for i in range(1, len(nextFiveBuses)):
        listFiveBuses.append([f'{nextFiveBuses[i]["Number"] :<4}'], [f'{nextFiveBuses[i]["Destination"] :<45}'],
                             [f' {nextFiveBuses[i]["ArrivalTime"] :<5}'])

    return listFiveBuses


def main(postcode):

    lat, lon = getPostcode(postcode)
    stops = getBusStops(lat, lon)

    print('\nThe nearest bus stops and arrival times near you are:')
    noBusStops = 2
    BusTimes = []
    NewBusTimes = []

    for i in range(0, noBusStops):
        nextFiveBuses = getBusTimes(stops, i)
        # displayBusTimes(nextFiveBuses)
        listBusTimes1 = listBusTimes(nextFiveBuses)     # convert list of dictionaries into list of lists
        # listBusTimes2 = newlistBusTimes(nextFiveBuses)
        # print(listBusTimes2)
        BusTimes.append(listBusTimes1)

    print(*BusTimes, sep='\n')

    return BusTimes


# if __name__ == "__main__":
#     postcode = 'OX49 5NU'
#     main(postcode)
