"""
Smart Traffic Management System (GUI)
File: traffic_gui.py

How it works (short):
- Tkinter GUI shows a 4-way intersection with 4 traffic lights and car queues.
- A scheduler thread gives GREEN to one direction at a time (round-robin).
- A lock (intersection_lock) ensures only one direction can be GREEN at once.
- Cars spawn randomly (producer thread). When a light is GREEN, cars pass (consumer behavior).
- GUI updates are scheduled safely via root.after(...) from background threads.

Run: python traffic_gui.py
"""

import threading
import time
import random
import tkinter as tk
from tkinter import ttk

# --------------------------
# Configuration parameters
# --------------------------
GREEN_TIME = 4          # seconds each green lasts (default)
YELLOW_TIME = 1         # seconds for yellow
SPAWN_INTERVAL = 2.0    # seconds between new car spawn checks
PASS_INTERVAL = 0.6     # how quickly cars pass during green (seconds)
MAX_QUEUE_SHOW = 20     # maximum number shown on GUI for compact display

# --------------------------
# Shared structures / lock
# --------------------------
intersection_lock = threading.Lock()
stop_event = threading.Event()  # to signal threads to stop


# --------------------------
# GUI / Visualization Class
# --------------------------
class TrafficGUI:
    def __init__(self, root):
        self.root = root
        root.title("Smart Traffic Management System (OS Project)")
        self.canvas = tk.Canvas(root, width=600, height=600, bg="#222")
        self.canvas.pack()

        # Create labels and controls
        control_frame = ttk.Frame(root)
        control_frame.pack(fill="x", pady=6)

        self.start_btn = ttk.Button(control_frame, text="Start Simulation", command=self.start_sim)
        self.start_btn.pack(side="left", padx=6)
        self.stop_btn = ttk.Button(control_frame, text="Stop Simulation", command=self.stop_sim, state="disabled")
        self.stop_btn.pack(side="left")

        ttk.Label(control_frame, text="Green time (s):").pack(side="left", padx=(12, 2))
        self.green_time_var = tk.IntVar(value=GREEN_TIME)
        self.green_spin = ttk.Spinbox(control_frame, from_=2, to=10, textvariable=self.green_time_var, width=4)
        self.green_spin.pack(side="left")

        ttk.Label(control_frame, text="Spawn interval (s):").pack(side="left", padx=(12, 2))
        self.spawn_var = tk.DoubleVar(value=SPAWN_INTERVAL)
        self.spawn_spin = ttk.Spinbox(control_frame, from_=0.5, to=5.0, increment=0.5, textvariable=self.spawn_var, width=4)
        self.spawn_spin.pack(side="left")

        # Intersection drawing center
        self._draw_intersection()

        # state
        self.lights = {
            "North": {"state": "RED", "rect": None, "label": None},
            "East":  {"state": "RED", "rect": None, "label": None},
            "South": {"state": "RED", "rect": None, "label": None},
            "West":  {"state": "RED", "rect": None, "label": None},
        }
        # queue counts for cars waiting at each direction
        self.queues = {"North": 0, "East": 0, "South": 0, "West": 0}

        # place lights and queue labels
        self._place_lights_and_labels()

        # threads
        self.threads = []
        self.scheduler_thread = None
        self.spawn_thread = None
        self.pass_threads = {}  # per-direction pass worker threads (created when green)

        # status label
        self.status_var = tk.StringVar(value="Ready. Press Start.")
        self.status_label = ttk.Label(root, textvariable=self.status_var)
        self.status_label.pack(fill="x")

    def _draw_intersection(self):
        c = self.canvas
        # Road rectangles
        c.create_rectangle(180, 0, 420, 600, fill="#444", outline="")
        c.create_rectangle(0, 180, 600, 420, fill="#444", outline="")
        # Center box
        c.create_rectangle(240, 240, 360, 360, fill="#111", outline="#666")

    def _place_lights_and_labels(self):
        c = self.canvas
        # North light (top center)
        self.lights["North"]["rect"] = c.create_oval(280, 40, 320, 80, fill="darkred", outline="white", width=2)
        self.lights["North"]["label"] = c.create_text(300, 90, text="North: 0", fill="white")
        # East (right)
        self.lights["East"]["rect"] = c.create_oval(520, 280, 560, 320, fill="darkred", outline="white", width=2)
        self.lights["East"]["label"] = c.create_text(520, 330, text="East: 0", fill="white", anchor="w")
        # South
        self.lights["South"]["rect"] = c.create_oval(280, 520, 320, 560, fill="darkred", outline="white", width=2)
        self.lights["South"]["label"] = c.create_text(300, 520, text="South: 0", fill="white", anchor="n")
        # West
        self.lights["West"]["rect"] = c.create_oval(40, 280, 80, 320, fill="darkred", outline="white", width=2)
        self.lights["West"]["label"] = c.create_text(80, 330, text="West: 0", fill="white", anchor="e")

    def update_light_gui(self, direction, state):
        """Called from threads via root.after to update light color/state."""
        colors = {"GREEN": "green", "YELLOW": "yellow", "RED": "darkred"}
        self.lights[direction]["state"] = state
        rect_id = self.lights[direction]["rect"]
        self.canvas.itemconfig(rect_id, fill=colors.get(state, "darkred"))
        self._update_status_text()

    def _update_status_text(self):
        # update labels showing queue sizes
        for d in ["North", "East", "South", "West"]:
            count = self.queues.get(d, 0)
            lbl_id = self.lights[d]["label"]
            txt = f"{d}: {min(count, MAX_QUEUE_SHOW)}"
            if count > MAX_QUEUE_SHOW:
                txt += "+"
            self.canvas.itemconfig(lbl_id, text=txt)

    def start_sim(self):
        # disable start, enable stop
        self.start_btn.config(state="disabled")
        self.stop_btn.config(state="normal")
        stop_event.clear()
        self.status_var.set("Simulation running...")
        # start threads
        gtime = int(self.green_time_var.get())
        spawn_int = float(self.spawn_var.get())

        self.scheduler_thread = threading.Thread(target=self.scheduler_worker, args=(gtime,), daemon=True)
        self.spawn_thread = threading.Thread(target=self.spawn_worker, args=(spawn_int,), daemon=True)

        self.scheduler_thread.start()
        self.spawn_thread.start()

    def stop_sim(self):
        # signal threads to stop
        stop_event.set()
        self.status_var.set("Stopping... please wait.")
        self.start_btn.config(state="normal")
        self.stop_btn.config(state="disabled")
        # clear lights to RED
        for d in self.lights:
            self.root.after(0, lambda dd=d: self.update_light_gui(dd, "RED"))
        self.status_var.set("Stopped. Press Start to run again.")

    def scheduler_worker(self, green_time):
        """Gives green to directions in round-robin. Uses lock to ensure single green."""
        directions = ["North", "East", "South", "West"]
        i = 0
        while not stop_event.is_set():
            direction = directions[i % 4]
            # try to acquire lock to set green for this direction
            acquired = intersection_lock.acquire(timeout=1.0)
            if not acquired:
                # could not acquire quickly, try next
                i += 1
                continue
            try:
                # Set this direction to GREEN (GUI update via after)
                self.root.after(0, lambda d=direction: self.update_light_gui(d, "GREEN"))
                # Start a passing worker for this direction (cars will pass while green)
                pass_thread = threading.Thread(target=self.pass_cars_worker, args=(direction, green_time), daemon=True)
                pass_thread.start()
                self.pass_threads[direction] = pass_thread

                # Keep green for green_time seconds (with early stop check)
                start_t = time.time()
                while (time.time() - start_t) < green_time and not stop_event.is_set():
                    time.sleep(0.1)
                # Turn YELLOW
                self.root.after(0, lambda d=direction: self.update_light_gui(d, "YELLOW"))
                time.sleep(YELLOW_TIME)
                # After yellow, set RED
                self.root.after(0, lambda d=direction: self.update_light_gui(d, "RED"))
            finally:
                intersection_lock.release()
            i += 1
            # small gap before next direction
            time.sleep(0.2)

    def spawn_worker(self, spawn_interval):
        """Randomly spawn cars into queues."""
        while not stop_event.is_set():
            # randomly pick a direction and add 0-2 cars
            dir_choice = random.choice(["North", "East", "South", "West"])
            added = random.choices([0, 1, 2], weights=[0.4, 0.45, 0.15])[0]
            if added > 0:
                self.queues[dir_choice] += added
                # update GUI (must use after)
                self.root.after(0, self._update_status_text)
            # wait
            # use the GUI-controlled spawn interval (user editable)
            spawn_interval = float(self.spawn_var.get())
            # jitter to feel more natural
            jitter = random.uniform(-0.4, 0.8)
            time.sleep(max(0.2, spawn_interval + jitter))

    def pass_cars_worker(self, direction, green_time):
        """While the direction is green, let cars pass at PASS_INTERVAL rate."""
        start = time.time()
        while (time.time() - start) < green_time and not stop_event.is_set():
            if self.queues.get(direction, 0) > 0:
                # one car passes
                self.queues[direction] -= 1
                # update GUI safely
                self.root.after(0, self._update_status_text)
                # short animation: flash passing text on status
                self.root.after(0, lambda d=direction: self._flash_passing(d))
                # wait to simulate car moving through intersection
                time.sleep(PASS_INTERVAL)
            else:
                # no car waiting; wait a little and check again
                time.sleep(0.25)

    def _flash_passing(self, direction):
        # Temporarily show passing message in status bar
        prev = self.status_var.get()
        self.status_var.set(f"{direction} passing car...")
        # after short delay revert
        self.root.after(500, lambda: self.status_var.set("Simulation running..."))

# --------------------------
# Program entry point
# --------------------------
def main():
    root = tk.Tk()
    app = TrafficGUI(root)

    # Ensure threads stop if window closed
    def on_closing():
        stop_event.set()
        # small delay to allow threads to notice
        time.sleep(0.2)
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_closing)
    root.mainloop()


if __name__ == "__main__":
    main()
