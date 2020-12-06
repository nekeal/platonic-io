#from multiprocessing import Process, Queue
from queue import Queue
from threading import Thread
from time import sleep
import matplotlib.pyplot as plt

import cv2
from keras.models import model_from_json
from sklearn.preprocessing import LabelEncoder
from .get_plate import load_model, preprocess_image, get_plate, draw_box, sort_contours, predict_from_model, get_width_height_ratio
import numpy as np


class FrameWorker(Thread):
    def __init__(self, task_queue: Queue, result_queue: Queue):
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):

        # Load Models
        # Load model architecture, weight and labels
        json_file = open('models/MobileNets_character_recognition.json', 'r')
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)
        model.load_weights("models/License_character_recognition_weight.h5")
        wpod_net_path = "models/wpod-net.json"
        wpod_net = load_model(wpod_net_path)

        labels = LabelEncoder()
        labels.classes_ = np.load('models/license_character_classes.npy')

        while True:
            frame_idx, frame = self.task_queue.get()
            if frame is None:
                break
            LpImg, cor = get_plate(frame,wpod_net)

            if LpImg and (len(LpImg)):  # check if there is at least one license image
                plates_strings = []
                positive_cor = []
                for curr_cor in cor:
                    ratio = get_width_height_ratio(curr_cor)
                    if ratio >= 2 and ratio < 8:
                        positive_cor.append(curr_cor)
                for idx, plate_img in enumerate(LpImg):
                    # Scales, calculates absolute values, and converts the result to 8-bit.
                    plate_image = cv2.convertScaleAbs(plate_img, alpha=(255.0))
                    # convert to grayscale and blur the image
                    gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
                    blur = cv2.GaussianBlur(gray, (7, 7), 0)

                    # Applied inversed thresh_binary
                    binary = cv2.threshold(blur, 180, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
                    ## Applied dilation
                    kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                    thre_mor = cv2.morphologyEx(binary, cv2.MORPH_DILATE, kernel3)

                    # creat a copy version "test_roi" of plat_image to draw bounding box
                    test_roi = plate_image.copy()
                    # contours
                    cont, _ = cv2.findContours(thre_mor, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
                    crop_characters = []

                    # define standard width and height of character
                    digit_w, digit_h = 30, 60

                    for c in sort_contours(cont):
                        (x, y, w, h) = cv2.boundingRect(c)
                        ratio = h / w
                        if 1 <= ratio <= 3.5:  # Only select contour with defined ratio
                            if h / plate_image.shape[0] >= 0.3:  # Select contour which has the height larger than 50% of the plate
                                # Draw bounding box arroung digit number
                                cv2.rectangle(test_roi, (x, y), (x + w, y + h), (0, 255, 0), 2)

                                # Sperate number and gibe prediction
                                curr_num = thre_mor[y:y + h, x:x + w]
                                curr_num = cv2.resize(curr_num, dsize=(digit_w, digit_h))
                                _, curr_num = cv2.threshold(curr_num, 220, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
                                crop_characters.append(curr_num)

                    final_string = ''
                    for i, character in enumerate(crop_characters):
                        title = np.array2string(predict_from_model(character, model, labels))
                        final_string += title.strip("'[]")
                    plates_strings.append(final_string)

                plate_frame = draw_box(frame, positive_cor)
                self.result_queue.put((frame_idx, plates_strings, plate_frame))
            else:
                # no plate detected
                self.result_queue.put((frame_idx, [], frame))


class Master(Thread):
    def __init__(self, input_path, output_path, worker_count=1):
        """

        :param input_path:
        :param output_path:
        :param progress_percentage: passed variable to which an actual progrss state % will be written
        :param worker_count:
        """
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.worker_count = worker_count
        self.progress = 0
        self.log = ""

    def run(self):
        movie = cv2.VideoCapture(self.input_path)
        size = (int(movie.get(cv2.CAP_PROP_FRAME_WIDTH)), int(movie.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        fps = movie.get(cv2.CAP_PROP_FPS)
        frames_in_file = movie.get(cv2.CAP_PROP_FRAME_COUNT)
        sink = cv2.VideoWriter(self.output_path, cv2.CAP_ANY, cv2.VideoWriter_fourcc(*'MJPG'), fps, size, params=None)
        plates_log = []

        tasks = Queue()
        results = Queue()
        workers = []

        for i in range(self.worker_count):
            worker = FrameWorker(tasks, results)
            workers.append(worker)
            worker.start()


        no_more_frames = False
        frame_idx = 0
        last_saved_idx = -1
        while True:
            # Read frames and distribute among workers
            ret, frame = movie.read()
            # no more frames
            if ret:
                while tasks.qsize() >= 4*self.worker_count:
                    sleep(0.01)
                tasks.put((frame_idx, frame))
                frame_idx += 1
            else:
                no_more_frames = True

            #Flush frames to dst file
            if not results.empty():
                tmp_res = []
                for _ in range(results.qsize()):
                    tmp_res.append(results.get())
                tmp_res.sort(key=lambda x: x[0])
                for res in tmp_res:
                    if res[0] - last_saved_idx != 1:
                        # there is no next frame processed yet
                        for fallback_res in tmp_res:
                            if fallback_res[0] > last_saved_idx:
                                results.put(fallback_res)
                        break
                    sink.write(res[2])
                    plates_log.append([res[0], res[1]])
                    print("==========WROTE {} frame".format(res[0]))
                    last_saved_idx = res[0]
                    self.progress = round((last_saved_idx / frames_in_file-1)*100, 1)

            if no_more_frames and tasks.qsize() == 0 and results.qsize() == 0:
                print("Reached end")
                for entry in plates_log:
                    timestamp = (entry[0]/fps)
                    valid_plates = [p for p in entry[1] if 4 <= len(p) < 9]
                    self.log += str(timestamp) + "s: " + str(valid_plates) + "\n"
                movie.release()
                sink.release()
                # for w in workers:
                #     w.kill()
                print(plates_log)
                break


    def get_progress(self):
        return self.progress

    def get_log(self):
        return self.log








