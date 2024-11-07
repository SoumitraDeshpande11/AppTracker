import psutil
import time
import tkinter as tk
from tkinter import ttk
from collections import defaultdict
import threading
import subprocess


class AppTracker:
    def __init__(self):
        self.app_times = defaultdict(float)  
        self.current_app = None 
        self.running = True  

    def get_active_app(self):
        
        try:
           
            script = 'tell application "System Events" to get name of first application process whose frontmost is true'
            active_app = subprocess.check_output(['osascript', '-e', script]).strip().decode()
            return active_app
        except Exception as e:
            print("Error getting active application:", e)
            return None

    def track_apps(self):
        last_time = time.time()
        while self.running:
            active_app = self.get_active_app()
            current_time = time.time()

           
            if active_app and active_app != self.current_app:
                if self.current_app:
                    time_spent = current_time - last_time
                    self.app_times[self.current_app] += time_spent
                    last_time = current_time
                self.current_app = active_app

            time.sleep(1)  

    def stop_tracking(self):
        self.running = False


class AppTrackerUI:
    def __init__(self, tracker):
        self.tracker = tracker
        self.root = tk.Tk()
        self.root.title("App Usage Tracker")

        
        self.current_app_label = ttk.Label(self.root, text="Current App: None", font=("Arial", 14))
        self.current_app_label.pack(pady=10)

        
        self.usage_tree = ttk.Treeview(self.root, columns=("App Name", "Time Spent"), show='headings')
        self.usage_tree.heading("App Name", text="App Name")
        self.usage_tree.heading("Time Spent", text="Time Spent (seconds)")
        self.usage_tree.pack(pady=20)

        self.quit_button = ttk.Button(self.root, text="Quit", command=self.quit)
        self.quit_button.pack(pady=10)

        
        self.update_ui_thread = threading.Thread(target=self.update_ui, daemon=True)
        self.update_ui_thread.start()

    def update_ui(self):
        while self.tracker.running:
            current_app = self.tracker.get_active_app() or "None"
            self.current_app_label.config(text=f"Current App: {current_app}")
            self.update_usage_tree()
            time.sleep(2)

    def update_usage_tree(self):
        
        for i in self.usage_tree.get_children():
            self.usage_tree.delete(i)

       
        for app, time_spent in self.tracker.app_times.items():
            self.usage_tree.insert("", "end", values=(app, f"{time_spent:.2f}"))

    def quit(self):
        self.tracker.stop_tracking()
        self.root.destroy()


if __name__ == "__main__":
    tracker = AppTracker()
    tracker_thread = threading.Thread(target=tracker.track_apps, daemon=True)
    tracker_thread.start()
    AppTrackerUI(tracker)
    tk.mainloop()
