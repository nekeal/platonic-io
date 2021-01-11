from pathlib import Path
from queue import Queue
from threading import Thread
from time import sleep

import cv2
import numpy as np
from sklearn.preprocessing import LabelEncoder
from tqdm import tqdm

from platonic_io import logger

from .get_plate import draw_box, get_plate, get_width_height_ratio, load_model
from .local_utils import get_model_filepath
from .ocr import LicencePlateOCRReader


class FrameWorker(Thread):
    def __init__(self, task_queue: Queue, result_queue: Queue):
        super().__init__()
        self.task_queue = task_queue
        self.result_queue = result_queue

    def run(self):
        from keras.models import model_from_json  # long running import

        # Load Models
        # Load model architecture, weight and labels
        loaded_model_json = get_model_filepath(
            "MobileNets_character_recognition.json"
        ).read_text()
        model = model_from_json(loaded_model_json)
        model.load_weights(
            str(get_model_filepath("License_character_recognition_weight.h5"))
        )
        wpod_net_path = str(get_model_filepath("wpod-net.json"))
        wpod_net = load_model(wpod_net_path)

        labels = LabelEncoder()
        labels.classes_ = np.load(get_model_filepath("license_character_classes.npy"))

        while True:
            frame_idx, frame = self.task_queue.get()
            if frame is None:
                break
            lp_img, cor = get_plate(frame, wpod_net)

            if lp_img and (len(lp_img)):  # check if there is at least one license image
                plates_strings = []
                positive_cor = []
                for curr_cor in cor:
                    ratio = get_width_height_ratio(curr_cor)
                    if 2 <= ratio < 8:
                        positive_cor.append(curr_cor)
                for idx, plate_img in enumerate(lp_img):
                    #  Scales, calculates absolute values,
                    #  and converts the result to 8-bit.
                    plate_image = cv2.convertScaleAbs(plate_img, alpha=(255.0))

                    reader = LicencePlateOCRReader(plate_image)
                    plates_strings.append(reader.read_text())

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
        :param worker_count:
        """
        super().__init__()
        assert Path(input_path).is_file(), "Source video does not exist"
        self.input_path = input_path
        self.output_path = output_path
        self.worker_count = worker_count
        self.progress = 0
        self.log = ""

    def run(self):
        logger.debug(f"Starting recognition of {self.input_path}")
        movie = cv2.VideoCapture(self.input_path)
        size = (
            int(movie.get(cv2.CAP_PROP_FRAME_WIDTH)),
            int(movie.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        )
        fps = movie.get(cv2.CAP_PROP_FPS)
        frames_in_file = movie.get(cv2.CAP_PROP_FRAME_COUNT)
        sink = cv2.VideoWriter(
            self.output_path,
            cv2.CAP_ANY,
            cv2.VideoWriter_fourcc(*"MJPG"),
            fps,
            size,
            params=None,
        )
        plates_log = []

        tasks: Queue = Queue()
        results: Queue = Queue()
        workers = []

        for i in range(self.worker_count):
            worker = FrameWorker(tasks, results)
            workers.append(worker)
            worker.start()

        no_more_frames = False
        frame_idx = 0
        last_saved_idx = -1
        progress_bar = tqdm(desc="Progress")
        while True:
            # Read frames and distribute among workers
            ret, frame = movie.read()
            # no more frames
            if ret:
                while tasks.qsize() >= 4 * self.worker_count:
                    sleep(0.01)
                tasks.put((frame_idx, frame))
                frame_idx += 1
                progress_bar.update(1)
            else:
                no_more_frames = True

            # Flush frames to dst file
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
                    logger.debug(f"Saved {res[0]} frame")
                    last_saved_idx = res[0]
                    self.progress = round(
                        (last_saved_idx / (frames_in_file - 1)) * 100, 1
                    )

            if no_more_frames and tasks.qsize() == 0 and results.qsize() == 0:
                self.progress = 100
                logger.debug("Reached end")
                for entry in plates_log:
                    timestamp = entry[0] / fps
                    valid_plates = [p for p in entry[1] if 4 <= len(p) < 9]
                    self.log += str(timestamp) + "s: " + str(valid_plates) + "\n"
                movie.release()
                sink.release()
                for w in workers:
                    tasks.put((None, None))
                logger.debug(plates_log)
                break

    def get_progress(self):
        return self.progress

    def get_log(self):
        return self.log
