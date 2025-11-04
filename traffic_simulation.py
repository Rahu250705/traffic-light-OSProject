import time

def traffic_light(direction, green_time):
    print(f"{direction} light is GREEN")
    time.sleep(green_time)
    print(f"{direction} light is YELLOW")
    time.sleep(1)
    print(f"{direction} light is RED")
    time.sleep(1)

def main():
    while True:
        traffic_light("North", 3)
        traffic_light("East", 3)
        traffic_light("South", 3)
        traffic_light("West", 3)

if __name__ == "__main__":
    main()
