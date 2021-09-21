def main():
    now = datetime.datetime.now()
    logging.info(f'Program start at {now.strftime("%Y-%m-%d %H:%M:%S")}')

    Atcocode = str(input(f'Welcome to the Bus Board'
                         f'\nSome examples to get you started;'
                         f'\nSouthGate (Wh) - 0180BAC30592'
                         f'\nEuston Station (Stop E) - 490000077E'
                         f'\nWestgate Buildings (Wd) - 0180BAC30345'
                         f'\nManvers Street (Be) - 0180BAC30601'
                         f'\nManvers Street (Bg) - 0180BAA01347'
                         f'\nPlease input a bus station atcocode to find the next 5 buses departing from that station: '
                         f''))

    # website link for example bus station to get a better idea of the layout
    # http://transportapi.com/v3/uk/bus/stop/0180BAC30592/live.json?app_id=c3e79790&app_key=8f91ea0737e54199559851b2312781be
    r = requests.get(f'http://transportapi.com/v3/uk/bus/stop/{Atcocode}/live.json?app_id={APP_ID}&app_key={APP_KEY}')

    response = r.json()
    departures = response["departures"]
    name = response["name"]
    # display name of station
    print(name)
    # print(departures)

    nextFiveBuses = getNextFive(departures)
    # print(*nextFiveBuses, sep='\n')

    for i in range(0, len(nextFiveBuses)):
        print(f'{nextFiveBuses[i]["Number"] :<4} {nextFiveBuses[i]["Destination"] :<40}'
              f' {nextFiveBuses[i]["ArrivalTime"] :<5}')