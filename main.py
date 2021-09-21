import requests
import datetime
# import json
import logging
logging.basicConfig(filename='BusBoard.log', filemode='w', level=logging.DEBUG)

APP_ID = 'c3e79790'
APP_KEY = '8f91ea0737e54199559851b2312781be'


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


def getNextFive(departures):
    i = 0
    busList = []
    # loops through every bus number (consisting of several buses behind each other in the timetable)
    # busNumber is name in-specific, the bus number is the top level Key within 'departures'
    for busNumber in departures:
        # print(busNumber)
        # loops through every individual bus of a given number (API only stores 3 at a time I think)
        for departure in departures[busNumber]:
            Buses = {"Number": None, "Destination": None, "ArrivalTime": None, "TimeMinutes": None}
            # this loop just prints out everything within the line 'busNumber'
            # print(departue)

            arrivalTimeMinutes, arrivalTime = timeConversion(departure)

            Buses["Number"] = busNumber
            Buses["Destination"] = departure["direction"]
            Buses["ArrivalTime"] = arrivalTime
            Buses["TimeMinutes"] = arrivalTimeMinutes

            busList.append(Buses)

            # print(f'Bus number {departure["line"]} is arriving at {arrivalTime} on '
            #       f'{departure["expected"]["arrival"]["date"]}, this is {arrivalTimeMinutes} seconds from epoch')

            i += 1

    # print(*busList, sep='\n')

    # sort buses by the earliest to arrive (ArrivalSeconds Key)
    busList.sort(key=lambda y: y["TimeMinutes"])    # y keyword is non specific but does need to access correct key

    busList = busList[0:5]

    for x in range(0, len(busList)):
        del busList[x]["TimeMinutes"]

    return busList


def main():
    now = datetime.datetime.now()
    logging.info(f'Program start at {now.strftime("%Y-%m-%d %H:%M:%S")}')

    try:
        postcode = input('Please enter a valid UK Postcode:')
        p = requests.get(f'https://api.postcodes.io/postcodes?q={postcode}')
        postcodeInfo = p.json()
        coordinates = postcodeInfo["result"]
        lat = coordinates[0]["latitude"]
        lon = coordinates[0]["longitude"]

    except TypeError:
        print('I said a valid UK postcode you dingbat, you get Bath now')
        postcode = 'BA2 1AX'
        p = requests.get(f'https://api.postcodes.io/postcodes?q={postcode}')
        postcodeInfo = p.json()
        coordinates = postcodeInfo["result"]
        lat = coordinates[0]["latitude"]
        lon = coordinates[0]["longitude"]

    s = requests.get(f'http://transportapi.com/v3/uk/places.json?lat={lat}&lon={lon}&type=bus_stop&app_id={APP_ID}'
                     f'&app_key={APP_KEY}')

    response_stops = s.json()
    stops = response_stops["member"]

    print('\nThe nearest bus stops and arrival times near you are:')

    for ii in range(0, 2):

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

        for i in range(0, len(nextFiveBuses)):
            print(f'{nextFiveBuses[i]["Number"] :<4} {nextFiveBuses[i]["Destination"] :<45}'
                  f' {nextFiveBuses[i]["ArrivalTime"] :<5}')


if __name__ == "__main__":
    main()
