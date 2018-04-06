import tkinter as tk
import tkinter.ttk as ttk
import threading
import datetime

from socket import AF_INET, SOCK_DGRAM
import sys
import socket
import struct, time

class CountingThread(threading.Thread):
    def __init__(self, master):
        super().__init__()
        self.master = master
        self.force_quit = False

    def run(self):
        while True:
            if not self.force_quit:
                self.main_loop()
                time.sleep(0.5)
            elif self.force_quit:
                del self.master.worker
                return
            else:
                continue
        return

    def main_loop(self):
        host = b"pool.ntp.org"
        port = 123
        buf = 1024
        address = (host,port)
        msg = '\x1b' + 47 * '\0'

        # reference time (in seconds since 1900-01-01 00:00:00)
        TIME1970 = 2208988800 # 1970-01-01 00:00:00

        # connect to server
        client = socket.socket( AF_INET, SOCK_DGRAM)
        client.sendto(msg.encode(), address)
        msg, address = client.recvfrom( buf )

        t = struct.unpack( "!12I", msg )[10]
        t -= TIME1970
        self.master.update_time_remaining(time.ctime(t).replace("  "," ").rsplit(" ")[-2])


class Timer(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("The Time")
        self.geometry("400x100")
        self.resizable(False, False)

        style = ttk.Style()
        style.configure("TLabel", foreground="black", background="lightgrey", font=(None, 50), anchor="center")

        self.main_frame = tk.Frame(self, width=500, height=300, bg="lightgrey")

        self.time_var = tk.StringVar(self)
        self.time_var.set("time")
        self.time_display = ttk.Label(self.main_frame, textvar=self.time_var)

        self.main_frame.pack(fill=tk.BOTH, expand=1)

        self.time_display.pack(fill=tk.X, pady=15)

        self.oron = False
        self.protocol("WM_DELETE_WINDOW", self.safe_destroy)
        self.wm_attributes('-topmost', 1)
        self.bind('<Control-f>', self.toggle_or)
        self.start()

    def toggle_or(self, event=None):
        if not self.oron:
            self.overrideredirect(1)
            self.oron = True
        else:
            self.overrideredirect(0)
            self.oron = False

    def setup_worker(self):
        worker = CountingThread(self)
        self.worker = worker

    def start(self):
        if not hasattr(self, "worker"):
            self.setup_worker()
        self.worker.start()

    def update_time_remaining(self, time_string):
        self.time_var.set(time_string)
        self.update_idletasks()

    def safe_destroy(self):
        if hasattr(self, "worker"):
            self.worker.force_quit = True
            self.after(100, self.safe_destroy)
        else:
            self.destroy()

if __name__ == '__main__':
    root = Timer()
    root.mainloop()
