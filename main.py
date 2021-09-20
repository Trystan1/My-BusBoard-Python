import requests
import datetime
# import json
import logging
logging.basicConfig(filename='BusBoard.log', filemode='w', level=logging.DEBUG)

APP_ID = 'c3e79790'
APP_KEY = '8f91ea0737e54199559851b2312781be'
# Atcocode = '0180BAC30592'
Atcocode = '490000077E'


def timeConversion(expectedArrival):

    Hour = int(expectedArrival["time"][0:2])
    Minute = int(expectedArrival["time"][3:5])

    Year = int(expectedArrival["date"][0:4])
    Month = int(expectedArrival["date"][5:7])
    Day = int(expectedArrival["date"][8:10])

    departureTimeMinutes = int((datetime.datetime(Year, Month, Day, Hour, Minute)
                                - datetime.datetime(1970, 1, 1, 0, 0)).total_seconds()) // 60

    return departureTimeMinutes


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
            arrivalTime = departure["expected"]["arrival"]["time"]

            expectedArrival = departure["expected"]["arrival"]

            arrivalTimeMinutes = timeConversion(expectedArrival)

            Buses["Number"] = busNumber
            Buses["Destination"] = departure["direction"]
            Buses["ArrivalTime"] = arrivalTime
            Buses["TimeMinutes"] = arrivalTimeMinutes

            busList.append(Buses)

            # print(f'Bus number {departure["line"]} is arriving at {arrivalTime} on '
            #       f'{departure["expected"]["arrival"]["date"]}, this is {arrivalTimeMinutes} seconds from epoch')

            i += 1

    # sort buses by the earliest to arrive (ArrivalSeconds Key)
    busList.sort(key=lambda random_word: Buses["TimeMinutes"])

    for x in range(0, 5):
        del busList[x]["TimeMinutes"]

    return busList[0:5]


def main():
    now = datetime.datetime.now()
    logging.info(f'Program start at {now.strftime("%Y-%m-%d %H:%M:%S")}')

    # website link for example bus station to get a better idea of the layout
    # http://transportapi.com/v3/uk/bus/stop/490000077E/live.json?app_id=c3e79790&app_key=8f91ea0737e54199559851b2312781be
    r = requests.get(f'http://transportapi.com/v3/uk/bus/stop/{Atcocode}/live.json?app_id={APP_ID}&app_key={APP_KEY}')

    response = r.json()
    departures = response["departures"]
    # print(departures)

    nextFiveBuses = getNextFive(departures)
    # print(*nextFiveBuses, sep='\n')

    for i in range(0, 5):
        print(f'{nextFiveBuses[i]["Number"] :<4} {nextFiveBuses[i]["Destination"] :<20}'
              f' {nextFiveBuses[i]["ArrivalTime"] :<5}')


if __name__ == "__main__":
    main()
