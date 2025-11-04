import threading
import time

intersection_lock = threading.Lock()

def traffic_light(direction, green_time):
    while True:
        with intersection_lock:
            print(f"{direction} light is GREEN")
            time.sleep(green_time)
            print(f"{direction} light is YELLOW")
            time.sleep(1)
            print(f"{direction} light is RED")
        time.sleep(0.5)

def main():
    green_time = 3
    directions = ["North", "East", "South", "West"]
    threads = []

    for d in directions:
        t = threading.Thread(target=traffic_light, args=(d, green_time), daemon=True)
        threads.append(t)
        t.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nSimulation stopped by user.")

if __name__ == "__main__":
    main()
