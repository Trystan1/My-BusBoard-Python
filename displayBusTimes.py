def displayBusTimes(nextFiveBuses):
    print(f'\n{nextFiveBuses[0]["Name"]} ({nextFiveBuses[0]["Distance"]}m)')
    for i in range(1, len(nextFiveBuses)):
        print(f'{nextFiveBuses[i]["Number"] :<4} {nextFiveBuses[i]["Destination"] :<45}'
              f' {nextFiveBuses[i]["ArrivalTime"] :<5}')

# displayBusTimes(nextFiveBuses)