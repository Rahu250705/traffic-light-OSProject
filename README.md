# Traffic Light Controller using OS Concepts 🚦

## 📘 Overview
This project simulates a **four-way traffic signal system** using key **Operating System concepts** such as:
- **Multithreading**
- **Synchronization (Locks)**
- **Scheduling (Round-Robin)**

It demonstrates how threads (representing each traffic signal) work together without conflicts, ensuring that only one direction is green at a time — similar to how an OS schedules processes efficiently.

---

## ⚙️ Technologies Used
- **Python 3**
- **Tkinter** (for GUI visualization)
- **Threading module** (for concurrency)

---

## 🧩 Files Included
| File Name | Description |
|------------|-------------|
| `traffic_simulation.py` | Basic simulation showing signal sequence |
| `traffic_threads.py` | Uses threads to simulate concurrent signals |
| `traffic_gui.py` | Final graphical version (Tkinter-based GUI) |
| `README.md` | Project documentation (this file) |

---

## ▶️ How to Run
1. Make sure **Python 3** is installed on your system.
2. Open the project folder in Command Prompt.
3. Run the GUI version with:
   ```bash
   python traffic_gui.py
   ```
4. You’ll see a window with traffic lights changing automatically — each controlled by its own thread.

---

## 💡 Operating System Concepts Used
- **Processes and Threads:** Each light runs as an independent thread.
- **Synchronization (Lock):** Prevents multiple lights from turning green simultaneously.
- **Scheduling:** Implements a round-robin approach for time-based switching.
- **Concurrency Control:** Demonstrates how an OS handles multiple processes efficiently.

---

## 👥 Team Members
- Ayushi Maniar-23BIT189
- Jainee Goyani-23BIT174
- Rahul Kumar-23BIT176


---

### 🏁 Project Status
**Completed and ready for submission**  
Developed as part of the Operating Systems coursework.
