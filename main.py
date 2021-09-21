from api_keys import *
import requests
import datetime
import logging
logging.basicConfig(filename='BusBoard.log', filemode='w', level=logging.DEBUG)


def getPostcode():
    postcode = input('Please enter a valid UK Postcode:')
    print('Thanks, querying...')
    lat, lon = postcode2latlon(postcode)
    return lat, lon


def postcode2latlon(postcode):
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

    r = requests.get(f'http://transportapi.com/v3/uk/bus/stop/{Atcocode}/live.json?app_id={APP_ID}'
                     f'&app_key={APP_KEY}')

    response = r.json()
    departures = response["departures"]
    name = response["name"]
    # display name of station
    print(f'\n{name} ({Distance}m)')

    nextFiveBuses = getNextFive(departures)
    return nextFiveBuses


def getNextFive(departures):
    # returns a list of dictionaries which contain information on the next five buses expected to arrive at the given
    # bus stop
    i = 0
    busList = []
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

    for x in range(0, len(busList)):
        del busList[x]["TimeMinutes"]

    return busList


def timeConversion(departure):

    expectedArrival = departure["expected"]["arrival"]

    try:
        Hour = int(expectedArrival["time"][0:2])
        Minute = int(expectedArrival["time"][3:5])
    except TypeError:
        Hour = int(departure["aimed_departure_time"][0:2])
        Minute = int(departure["aimed_departure_time"][3:5])
        logging.warning('no "expected" field,  "aimed_departure_time" used instead')

    try:
        Year = int(expectedArrival["date"][0:4])
        Month = int(expectedArrival["date"][5:7])
        Day = int(expectedArrival["date"][8:10])
    except TypeError:
        Year = int(departure["date"][0:4])
        Month = int(departure["date"][5:7])
        Day = int(departure["date"][8:10])
        logging.warning('no "expected" field,  "date" used instead')

    arrivalTimeMinutes = int((datetime.datetime(Year, Month, Day, Hour, Minute)
                              - datetime.datetime(1970, 1, 1, 0, 0)).total_seconds()) // 60

    if Minute < 10:
        Minute = f'0{Minute}'

    if Hour < 10:
        Hour = f'0{Hour}'

    arrivalTime = f'{str(Hour)}:{str(Minute)}'

    return arrivalTimeMinutes, arrivalTime


def displayBusTimes(nextFiveBuses):
    for i in range(0, len(nextFiveBuses)):
        print(f'{nextFiveBuses[i]["Number"] :<4} {nextFiveBuses[i]["Destination"] :<45}'
              f' {nextFiveBuses[i]["ArrivalTime"] :<5}')


def main():
    now = datetime.datetime.now()
    logging.info(f'Program start at {now.strftime("%Y-%m-%d %H:%M:%S")}')

    lat, lon = getPostcode()
    stops = getBusStops(lat, lon)

    print('\nThe nearest bus stops and arrival times near you are:')
    for ii in range(0, 2):
        nextFiveBuses = getBusTimes(stops, ii)
        displayBusTimes(nextFiveBuses)


if __name__ == "__main__":
    main()
