import os
import subprocess
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import Toplevel, filedialog
from tkinter.ttk import Progressbar

import imageio
from PIL import Image, ImageTk

from platonic_io.recognition_engine import Master



class GUI:
    def __init__(self, thread=4):
        self.root = tk.Tk()
        self.progress = Progressbar(self.root, orient="horizontal")
        self.buttons_frame = tk.Frame(self.root, bg="grey")
        self.labelframe = tk.LabelFrame(self.root, bg="grey", height=35, width=130)
        self.label = tk.Label(self.labelframe)
        self.top = None
        self.topSettings = None
        self.report = "../"
        self.video_location = "../"
        self.uploaded_file = ""
        self.video = None
        self.video_name = "processed.mp4"
        self.raport_name = "raport.txt"
        self.progress_percent = 0
        self.thread = thread

    def run(self):
        self.root.geometry("1400x1000")
        self.root.resizable(0, 0)
        self.root.title("Platonic")
        self.root.config(bg="grey")
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        self.root.grid_rowconfigure(1, weight=4)
        self.root.grid_columnconfigure(1, weight=4)

        self.progress.grid_forget()

        self.buttons_frame.pack_propagate(0)  # type: ignore
        self.buttons_frame.config(width=25, height=40)
        self.buttons_frame.grid(row=0, column=2, sticky="NESW", pady=10)

        upload_file_button = tk.Button(
            self.buttons_frame,
            text="upload a video",
            command=self.upload_video,
            width=32,
        )
        upload_file_button.grid(row=0, column=0, pady=10, padx=10)

        start_algorithm_button = tk.Button(
            self.buttons_frame,
            text="start algorithm",
            command=self.start_algorithm,
            width=32,
        )
        start_algorithm_button.grid(row=2, column=0, pady=10, padx=10)

        play_uploaded_video_button = tk.Button(
            self.buttons_frame,
            text="outside player",
            command=self.play_uploaded_video,
            width=32,
        )
        play_uploaded_video_button.grid(row=4, column=0, pady=10, padx=10)

        inside_player = tk.Button(
            self.buttons_frame,
            text="inbuild player",
            command=self.inside_player,
            width=32,
        )
        inside_player.grid(row=6, column=0, pady=10, padx=10)

        self.labelframe.grid(row=0, column=1, pady=10)
        self.label.config(bg="grey71", height=40, width=130)
        self.label.pack_propagate(0)  # type: ignore
        self.label.grid(row=0, column=1, sticky="NESW")

        menu_button = tk.Button(
            self.root, text="settings", width=32, command=self.settings_window
        )
        menu_button.grid(row=1, column=2)

        self.root.mainloop()

    def play_it(self, label):

        for image in self.video.iter_data():  # type: ignore
            frame_image = ImageTk.PhotoImage(
                Image.fromarray(image), height=400, width=800
            )
            self.label.config(image=frame_image, width=920, height=600)
            self.label.image = frame_image  # type: ignore

    def upload_video(self):
        self.uploaded_file = filedialog.askopenfilename()
        if self.uploaded_file.endswith((".mp4", ".mkv")):
            self.video = imageio.get_reader(self.uploaded_file)
        else:
            self.warning_window(
                "Bad format", "Wrong data format chosen! Select mp4 or mkv file"
            )
            self.uploaded_file = ""

    def start_algorithm(self):
        self.progress.grid(row=1, column=1, sticky="EW", pady=10)
        master = Master(
            self.uploaded_file,
            os.path.join(self.video_location, self.video_name),
            self.thread,
        )
        master.start()
        time.sleep(15)
        self.progress_percent = master.get_progress()
        self.refresh_progress(master)
        Path(os.path.join(self.report, self.raport_name)).write_text(
            str(master.get_log())
        )

    def refresh_progress(self, master):
        while master.is_alive():
            self.progress["value"] = self.progress_percent
            self.root.update_idletasks()
            self.progress_percent = master.get_progress()

    def play_uploaded_video(self):
        if self.uploaded_file != "" and sys.platform == "win32":
            os.startfile(self.uploaded_file)  # type: ignore
        elif sys.platform == "darwin" and self.uploaded_file != "":
            opener = "open"
            subprocess.call([opener, self.uploaded_file])
        elif self.uploaded_file != "":
            opener = "xdg-open"
            subprocess.call([opener, self.uploaded_file])
        else:
            self.warning_window(
                "No video uploaded", "No video uploaded! Upload one to play it"
            )

    def inside_player(self):
        thread = threading.Thread(target=self.play_it, args=(self.label,))
        thread.daemon = 1  # type: ignore
        thread.start()

    def warning_window(self, warning_title, warning_message):
        self.top = Toplevel()
        self.top.resizable(0, 0)
        self.top.title(warning_title)
        self.top.geometry("450x150")
        self.top.config(bg="grey")
        warning_label = tk.Label(
            self.top, text=warning_message, bg="grey", pady=40, font="Verdana 10 bold"
        )
        warning_label.pack(anchor="center")
        exit_button = tk.Button(
            self.top,
            text="exit",
            command=self.top.destroy,
            width=400,
            height=35,
            bg="grey71",
        )
        exit_button.pack(padx=10, pady=7)

    def choose_raport_location(self):
        self.report = filedialog.askdirectory()

    def choose_video_location(self):
        self.video_location = filedialog.askdirectory()

    def exit_settings(self, top, video_location, report):
        if video_location.get() != "":
            self.video_name = video_location.get()
        if report.get() != "":
            self.raport_name = report.get()
        self.topSettings.destroy()

    def settings_window(self):
        self.topSettings = Toplevel()
        self.topSettings.resizable(0, 0)
        self.topSettings.title("settings")
        self.topSettings.geometry("500x300")
        self.topSettings.config(bg="grey")
        report_label = tk.Label(
            self.topSettings,
            text="Where to store report:",
            bg="grey",
            pady=25,
            font="Verdana 10 bold",
        )
        report_label.grid(row=1, column=0)
        report_button = tk.Button(
            self.topSettings,
            width=35,
            text="Choose directory",
            command=self.choose_raport_location,
        )
        report_button.grid(row=1, column=1, padx=10, pady=5)
        where_report_label = tk.Label(
            self.topSettings,
            text="Report name:",
            bg="grey",
            pady=15,
            font="Verdana 10 bold",
        )
        where_report_label.grid(row=3, column=0)
        where_report_input = tk.Entry(self.topSettings, width=35)
        where_report_input.grid(row=3, column=1, padx=10)
        video_label = tk.Label(
            self.topSettings,
            text="Where to store video:",
            bg="grey",
            pady=20,
            font="Verdana 10 bold",
        )
        video_label.grid(row=2, column=0)
        video_input = tk.Button(
            self.topSettings,
            width=35,
            text="Choose directory",
            command=self.choose_video_location,
        )
        video_input.grid(row=2, column=1, padx=10, pady=5)
        where_video_label = tk.Label(
            self.topSettings,
            text="Video name:",
            bg="grey",
            pady=15,
            font="Verdana 10 bold",
        )
        where_video_label.grid(row=4, column=0)
        where_video_input = tk.Entry(self.topSettings, width=35)
        where_video_input.grid(row=4, column=1, padx=10)
        exit_button = tk.Button(
            self.topSettings,
            text="save",
            command=lambda: self.exit_settings(
                self.topSettings, where_video_input, where_report_input
            ),
            width=400,
            height=35,
            bg="grey71",
        )
        exit_button.place(x=100, y=250, relwidth=0.6, relheight=0.1)


siema = GUI()
siema.run()
