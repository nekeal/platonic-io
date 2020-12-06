from multiprocessing import Process, Queue
from threading import Thread
from time import sleep

import cv2
import numpy as np
from keras.models import model_from_json
from sklearn.preprocessing import LabelEncoder

from .get_plate import get_plate, load_model, predict_from_model, sort_contours


class FrameWorker(Process):
    def __init__(self, task_queue: Queue, result_queue: Queue):
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):

        # Load Models
        # Load model architecture, weight and labels
        json_file = open("models/MobileNets_character_recognition.json", "r")
        loaded_model_json = json_file.read()
        json_file.close()
        model = model_from_json(loaded_model_json)
        model.load_weights("models/License_character_recognition_weight.h5")
        wpod_net_path = "models/wpod-net.json"
        wpod_net = load_model(wpod_net_path)
        print("[INFO]{} Model loaded successfully...".format(self.name))

        labels = LabelEncoder()
        labels.classes_ = np.load("models/license_character_classes.npy")
        print("[INFO]{} Labels loaded successfully...".format(self.name))

        while True:
            frame_idx, frame = self.task_queue.get()
            print("{} processing frame {}".format(self.name, frame_idx))
            if frame is None:
                break
            LpImg, cor = get_plate(frame, wpod_net)

            if LpImg and (len(LpImg)):  # check if there is at least one license image
                print("Detect {} plate(s), process {}".format(len(LpImg), self.name))
                # Scales, calculates absolute values, and converts the result to 8-bit.
                plate_image = cv2.convertScaleAbs(LpImg[0], alpha=(255.0))
                # convert to grayscale and blur the image
                gray = cv2.cvtColor(plate_image, cv2.COLOR_BGR2GRAY)
                blur = cv2.GaussianBlur(gray, (7, 7), 0)

                # Applied inversed thresh_binary
                binary = cv2.threshold(
                    blur, 180, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
                )[1]
                # Applied dilation
                kernel3 = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
                thre_mor = cv2.morphologyEx(binary, cv2.MORPH_DILATE, kernel3)

                # creat a copy version "test_roi" of plat_image to draw bounding box
                test_roi = plate_image.copy()
                # contours
                cont, _ = cv2.findContours(
                    thre_mor, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE
                )
                crop_characters = []

                # define standard width and height of character
                digit_w, digit_h = 30, 60

                for c in sort_contours(cont):
                    (x, y, w, h) = cv2.boundingRect(c)
                    ratio = h / w
                    if 1 <= ratio <= 3.5:  # Only select contour with defined ratio
                        if (
                            h / plate_image.shape[0] >= 0.3
                        ):  # Select contour which has the height
                            # larger than 50% of the plate
                            # Draw bounding box arroung digit number
                            cv2.rectangle(
                                test_roi, (x, y), (x + w, y + h), (0, 255, 0), 2
                            )

                            # Sperate number and gibe prediction
                            curr_num = thre_mor[y : y + h, x : x + w]
                            curr_num = cv2.resize(curr_num, dsize=(digit_w, digit_h))
                            _, curr_num = cv2.threshold(
                                curr_num, 220, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU
                            )
                            crop_characters.append(curr_num)

                print("{} Detect {} letters...".format(self.name, len(crop_characters)))
                final_string = ""
                for i, character in enumerate(crop_characters):
                    title = np.array2string(
                        predict_from_model(character, model, labels)
                    )
                    final_string += title.strip("'[]")
                print("{} Achieved result: ".format(self.name), final_string)

                self.result_queue.put((frame_idx, [final_string, frame]))
            else:
                # no plate detected
                self.result_queue.put((frame_idx, ["", frame]))


class Master(Thread):
    def __init__(self, input_path, output_path, worker_count=1):
        super().__init__()
        self.input_path = input_path
        self.output_path = output_path
        self.worker_count = worker_count

    def run(self):
        movie = cv2.VideoCapture(self.input_path)
        size = (
            int(movie.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(movie.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )
        fps = movie.get(cv2.CAP_PROP_FPS)
        sink = cv2.VideoWriter(
            self.output_path,
            cv2.CAP_ANY,
            cv2.VideoWriter_fourcc(*"MJPG"),
            fps,
            size,
            params=None,
        )

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
                while tasks.qsize() >= 2 * self.worker_count:
                    sleep(0.01)
                tasks.put((frame_idx, frame))
                frame_idx += 1
            else:
                no_more_frames = True

            # Flush frames to dst file
            if not results.empty():
                tmp_res = []
                print("FLUSHING FRAMES len(results)={}".format(results.qsize()))
                for _ in range(results.qsize()):
                    tmp_res.append(results.get())
                tmp_res.sort()
                for res in tmp_res:
                    if res[0] - last_saved_idx != 1:
                        # there is no next frame processed yet
                        for fallback_res in tmp_res:
                            results.put(fallback_res)
                        print(
                            "FLUSHING FRAMES BREAKING!! len(results)={}".format(
                                results.qsize()
                            )
                        )
                        break
                    sink.write(res[1][1])
                    print("==========WROTE {} frame".format(res[0]))
                    last_saved_idx = res[0]
                    tmp_res.remove(res)

            if no_more_frames and tasks.qsize() == 0 and results.qsize() == 0:
                movie.release()
                sink.release()
                for w in workers:
                    w.kill()
