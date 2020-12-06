from multiprocessing import Process, Queue
from keras.models import model_from_json
from sklearn.preprocessing import LabelEncoder
from .get_plate import load_model, preprocess_image, get_plate, draw_box, sort_contours, predict_from_model
import numpy as np



class FrameWorker(Process):
    def __init__(self, task_queue: Queue, result_queue: Queue):
        self.task_queue = task_queue
        self.result_queue = result_queue
        super.__init__()

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
        print("[INFO]{} Model loaded successfully...".format(self.name))

        labels = LabelEncoder()
        labels.classes_ = np.load('models/license_character_classes.npy')
        print("[INFO]{} Labels loaded successfully...".format(self.name))

        frame_idx, frame = self.task_queue.get()
        while frame:
            LpImg, cor = get_plate(test_image)
