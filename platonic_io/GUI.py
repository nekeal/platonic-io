import os
import subprocess
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import Toplevel, filedialog, messagebox
from tkinter.ttk import Progressbar

import imageio
from PIL import Image, ImageTk

from platonic_io.recognition_engine import Master


class GUI:
    """
    Is responsible for opening and handling
    graphical interface of an application
    """

    def __init__(self, thread=4):
        self.root = tk.Tk()
        self.progress = Progressbar(self.root, orient="horizontal")
        self.buttons_frame = tk.Frame(self.root, bg="grey")
        self.labelframe = tk.LabelFrame(
            self.root, bg="grey", height=35, width=130, padx=10
        )
        self.label = tk.Label(self.labelframe)
        self.top = None
        self.topSettings = None
        self.report = "../"
        self.video_location = "../"
        self.uploaded_file = ""
        self.video = None
        self.video_name = "processed_video.mp4"
        self.report_name = "processed_report.txt"
        self.progress_percent = 0
        self.thread = thread
        self.video_path = Path(self.video_location).joinpath(self.video_name)
        self.report_path = Path(self.report).joinpath(self.report_name)

    def run(self):
        self.root.geometry("1200x900")
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

        currently_loaded_file_label = tk.Label(
            self.buttons_frame,
            text="Loaded file",
            width=32,
            bg="grey",
            font="Verdana 10 bold",
        )
        currently_loaded_file_label.grid(row=8, column=0, pady=0, padx=0)

        currently_loaded_file = tk.Label(
            self.buttons_frame,
            text="None",
            wraplength=200,
            width=40,
            bg="grey",
            font="Verdana 9 bold",
        )
        currently_loaded_file.grid(row=10, column=0, pady=10, padx=10)

        start_algorithm_button = tk.Button(
            self.buttons_frame,
            text="start algorithm",
            command=lambda: self.start_algorithm(
                currently_loaded_file,
                currently_loaded_file_label,
                upload_file_button,
                start_algorithm_button,
                play_uploaded_video_button,
                inside_player,
                menu_button,
            ),
            width=32,
            state="disabled",
        )
        start_algorithm_button.grid(row=2, column=0, pady=10, padx=10)

        play_uploaded_video_button = tk.Button(
            self.buttons_frame,
            text="outside player",
            command=self.play_uploaded_video,
            width=32,
            state="disabled",
        )
        play_uploaded_video_button.grid(row=4, column=0, pady=10, padx=10)

        inside_player = tk.Button(
            self.buttons_frame,
            text="inbuild player",
            command=self.inside_player,
            width=32,
            state="disabled",
        )
        inside_player.grid(row=6, column=0, pady=10, padx=10)

        upload_file_button = tk.Button(
            self.buttons_frame,
            text="upload a video",
            command=lambda: self.upload_video(
                start_algorithm_button,
                play_uploaded_video_button,
                inside_player,
                currently_loaded_file,
            ),
            width=32,
        )
        upload_file_button.grid(row=0, column=0, pady=10, padx=10)

        self.labelframe.grid(row=0, column=1, pady=10)
        self.label.config(bg="grey71", height=40, width=130)
        self.label.pack_propagate(0)  # type: ignore
        self.label.grid(row=0, column=1, sticky="NESW")

        menu_button = tk.Button(
            self.root, text="settings", width=32, command=self.settings_window
        )
        menu_button.grid(row=1, column=2)

        self.root.mainloop()

    def refresh_paths(self):

        self.video_path = Path(self.video_location).joinpath(self.video_name)
        self.report_path = Path(self.report).joinpath(self.report_name)

    def play_it(self, label):

        for image in self.video.iter_data():  # type: ignore
            frame_image = ImageTk.PhotoImage(
                Image.fromarray(image), height=400, width=800
            )
            self.label.config(image=frame_image, width=920, height=600)
            self.label.image = frame_image  # type: ignore

    def upload_video(self, process, outside, inbuilt, loaded):
        self.uploaded_file = filedialog.askopenfilename()
        if self.uploaded_file.endswith((".mp4", ".mkv")):
            self.video = imageio.get_reader(self.uploaded_file)
            process["state"] = "normal"
            outside["state"] = "normal"
            inbuilt["state"] = "normal"
            loaded["text"] = self.uploaded_file
        else:
            messagebox.showerror(
                "Bad format", "Wrong data format chosen! Select mp4 or mkv file"
            )
            self.uploaded_file = ""

    def start_algorithm(
        self, label, loaded, upload, process, outside, inbuilt, settings
    ):
        self.progress.grid(row=1, column=1, sticky="EW", pady=10, padx=10)
        master = Master(
            self.uploaded_file,
            str(self.video_path),
            self.thread,
        )
        master.start()
        upload["state"] = "disabled"
        process["state"] = "disabled"
        outside["state"] = "disabled"
        inbuilt["state"] = "disabled"
        settings["state"] = "disabled"
        time.sleep(15)
        self.progress_percent = master.get_progress()
        self.refresh_progress(master)
        self.report_path.write_text(str(master.get_log()))
        self.progress["value"] = 100
        self.refresh_paths()
        self.uploaded_file = str(self.video_path)
        self.video = imageio.get_reader(self.uploaded_file)
        upload["state"] = "normal"
        process["state"] = "normal"
        outside["state"] = "normal"
        inbuilt["state"] = "normal"
        settings["state"] = "normal"
        label["text"] = str(self.video_path)
        loaded["text"] = "Processed file"

    def refresh_progress(self, master):
        while master.is_alive():
            self.progress["value"] = self.progress_percent
            self.root.update_idletasks()
            self.progress_percent = master.get_progress()
            time.sleep(1)

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
            messagebox.showerror(
                "No video uploaded", "No video uploaded! Upload one to play it"
            )

    def inside_player(self):
        thread = threading.Thread(target=self.play_it, args=(self.label,))
        thread.daemon = 1  # type: ignore
        thread.start()

    def choose_raport_location(self, label):
        self.report = filedialog.askdirectory(parent=self.top)
        self.refresh_paths()
        label["text"] = "processed report location: " + str(self.report_path)

    def choose_video_location(self, label):
        self.video_location = filedialog.askdirectory(parent=self.top)
        self.refresh_paths()
        label["text"] = "processed video location: " + str(self.video_path)

    def exit_settings(self, top, video_location, report):
        if video_location.get() != "":
            self.video_name = video_location.get() + ".mp4"
        if report.get() != "":
            self.report_name = report.get() + ".txt"
        self.refresh_paths()
        self.topSettings.destroy()  # type: ignore

    def settings_window(self):
        self.topSettings = Toplevel()
        self.topSettings.resizable(0, 0)
        self.topSettings.title("settings")
        self.topSettings.geometry("500x510")
        self.topSettings.config(bg="grey")

        where_is_video = tk.Label(
            self.topSettings,
            text="processed video location: " + str(self.video_path),
            width=90,
            bg="grey",
            wraplength=200,
            pady=15,
            font="Verdana 10 bold",
        )

        where_is_video.place(x=-100, y=355)

        where_is_report = tk.Label(
            self.topSettings,
            text="processed report location: " + str(self.report_path),
            width=90,
            bg="grey",
            wraplength=200,
            pady=15,
            font="Verdana 10 bold",
        )

        where_is_report.place(x=-100, y=260)

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
            command=lambda: self.choose_raport_location(where_is_report),
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
        where_report_input.insert(0, self.report_name[: len(self.report_name) - 4])
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
            command=lambda: self.choose_video_location(where_is_video),
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
        where_video_input.insert(0, self.video_name[: len(self.video_name) - 4])
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
        exit_button.place(x=15, y=455, relwidth=0.95, relheight=0.08)

        how_many_threads = tk.Label(
            self.topSettings,
            text="active threads: " + str(self.thread),
            width=20,
            bg="grey",
            pady=20,
            font="Verdana 10 bold",
        )
        how_many_threads.place(x=180, y=220)


if __name__ == "__main__":
    gui = GUI()
    gui.run()
