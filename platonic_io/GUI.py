import tkinter as tk, threading
from tkinter import filedialog, Toplevel
from tkinter.ttk import *
import os
#from PIL import Image, ImageTk
import imageio

from functools import partial
from PIL import ImageTk, Image

uploaded_file = ''
video = ''

def play_it(label):

    for image in video.iter_data():
        frame_image = ImageTk.PhotoImage(Image.fromarray(image), height = 400, width = 800)
        label.config(image=frame_image, width = 920, height = 600)
        label.image = frame_image

def upload_video():
    file = filedialog.askopenfilename()
    global uploaded_file
    uploaded_file = file
    if uploaded_file.endswith(('.mp4', '.mkv')):
        print(uploaded_file)
        global video
        video = imageio.get_reader(uploaded_file)
    else:
        warning_window('Bad format', 'Wrong data format chosen! Select mp4 or mkv file')
        uploaded_file = ''

def start_algorithm():
    progress.grid(row = 1, column = 1, sticky = "EW", pady = 10)
    download_report_button.config(state = 'normal')
    download_video_button.config(state = 'normal')

def play_uploaded_video():
    if uploaded_file != '':
        os.startfile(uploaded_file)
    else:
        warning_window('No video uploaded', 'No video uploaded! Upload one to play it')

def inside_player():
    thread = threading.Thread(target = play_it, args = (label,))
    thread.daemon = 1
    thread.start()

def download_report():
    print('download report')

def download_video():
    print('download video')

def warning_window(warning_title, warning_message):
    top = Toplevel()
    top.resizable(0, 0)
    top.title(warning_title)
    top.geometry('450x150')
    top.config(bg='grey')
    warning_label = tk.Label(top, text = warning_message, bg = 'grey', pady = 40, font = "Verdana 10 bold")
    warning_label.pack(anchor = 'center')
    exit_button = tk.Button(top, text = 'exit', command = top.destroy, width = 400, height = 35,
            bg = 'grey71')
    exit_button.pack(padx = 10, pady = 7)

def choose_raport_location():
    file = filedialog.askdirectory()
    global report
    report = file
    settings_window()

def choose_video_location():
    file = filedialog.askdirectory()
    global video
    video = file
    settings_window()

def exit_settings(top, video, report):
    global video_name
    global raport_name
    video_name = video.get()
    raport_name = report.get()
    top.destroy()

def settings_window():
    top = Toplevel()
    top.resizable(0, 0)
    top.title('settings')
    top.geometry('450x300')
    top.config(bg = 'grey')
    report_label = tk.Label(top, text = 'Where to store report:', bg = 'grey', 
            pady = 25, font = "Verdana 10 bold")
    report_label.grid(row = 1, column = 0)
    report_button = tk.Button(top, width = 35, text = 'Choose directory', command = choose_raport_location)
    report_button.grid(row = 1, column = 1, padx = 10, pady = 5)
    where_report_label = tk.Label(top, text = 'Report name:', bg = 'grey', pady = 15,
            font="Verdana 10 bold")
    where_report_label.grid(row = 3, column = 0)
    where_report_input = tk.Entry(top, width = 35)
    where_report_input.grid(row = 3, column = 1, padx = 10)
    video_label = tk.Label(top, text = 'Where to store video:', bg = 'grey',
            pady = 20, font = "Verdana 10 bold")
    video_label.grid(row = 2, column = 0)
    video_input = tk.Button(top, width = 35, text = 'Choose directory',
            command = choose_video_location)
    video_input.grid(row = 2, column = 1, padx = 10, pady = 5)
    where_video_label = tk.Label(top, text = 'Video name:', bg = 'grey',
            pady = 15, font = "Verdana 10 bold")
    where_video_label.grid(row = 4, column = 0)
    where_video_input = tk.Entry(top, width = 35)
    where_video_input.grid(row = 4, column = 1, padx = 10)
    exit_button = tk.Button(top, text = 'exit', 
            command = lambda:exit_settings(top, where_video_input, where_report_input),
            width = 400, height = 35, bg = 'grey71')
    exit_button.place(x = 100, y =  250, relwidth = 0.6, relheight = 0.1)


root = tk.Tk()

root.geometry('1400x1000')
root.resizable(0, 0)
root.title('Platonic')
root.config(bg='grey')
root.grid_rowconfigure(0, weight = 1)
root.grid_columnconfigure(0, weight = 1)
root.grid_rowconfigure(1, weight = 4)
root.grid_columnconfigure(1, weight = 4)

progress = Progressbar(root, orient = "horizontal")
progress.grid_forget()

buttons_frame = tk.Frame(root, bg = 'grey')
buttons_frame.pack_propagate(0)
buttons_frame.config(width = 25, height = 40)
buttons_frame.grid(row = 0, column = 2, sticky = "NESW", pady = 10)

upload_file_button = tk.Button(buttons_frame, text = 'upload a video',
        command = upload_video, width = 32)
upload_file_button.grid(row = 0, column = 0, pady = 10, padx = 10)


start_algorithm_button = tk.Button(buttons_frame, text = 'start it', 
        command = start_algorithm, width = 32)
start_algorithm_button.grid(row = 2, column = 0, pady = 10, padx = 10)

play_uploaded_video_button = tk.Button(buttons_frame, text = 'play video', command = play_uploaded_video,
        width = 32)
play_uploaded_video_button.grid(row = 4, column = 0, pady = 10, padx = 10)

download_report_button = tk.Button(buttons_frame, text = 'download report',
        state = 'disabled', command = download_report, width = 32)
download_report_button.grid(row = 6, column = 0, pady = 10, padx = 10)

download_video_button = tk.Button(buttons_frame, text = 'download video', 
        state = 'disabled', command = download_video, width = 32)
download_video_button.grid(row = 8, column = 0, pady = 10, padx = 10)

inside_player = tk.Button(buttons_frame, text = "player", command = inside_player, width = 32)
inside_player.grid(row = 10, column = 0, pady = 10, padx = 10)

labelframe = tk.LabelFrame(root, bg='grey', height = 35, width = 130)
labelframe.grid(row = 0, column = 1, pady = 10)
label = tk.Label(labelframe)
label.config(bg='grey71', height = 40, width = 130)
label.pack_propagate(0)
label.grid(row = 0, column = 1, sticky = "NESW")

plates_frame = tk.Frame(root, bg = 'grey')
plates_frame.grid(row = 0, column = 0, sticky = "NEW", pady = 10, padx = 10)
list_of_plates = tk.Label(plates_frame, text = 'List of recognized plates', bg = 'grey',
        font = "Verdana 10 bold")
list_of_plates.pack(pady = 10)
recognized_plates = tk.Listbox(plates_frame, bg = 'grey')
recognized_plates.config(width = 25, height = 15)
recognized_plates.pack_propagate(0)
recognized_plates.pack()

menu_button = tk.Button(root, text = 'settings', width = 32, command = settings_window)
menu_button.grid(row = 1, column = 2)

for x in range (50):
    recognized_plates.insert('end', str(x))


root.mainloop()
