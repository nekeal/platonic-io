import cv2
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import gridspec

from .tutek_local_utils import detect_lp
from os.path import splitext, basename
from keras.models import model_from_json
import glob
import time
from sklearn.preprocessing import LabelEncoder


def load_model(path):
    try:
        path = splitext(path)[0]
        with open('%s.json' % path, 'r') as json_file:
            model_json = json_file.read()
        model = model_from_json(model_json, custom_objects={})
        model.load_weights('%s.h5' % path)
        print("Loading model successfully...")
        return model
    except Exception as e:
        print(e)


def preprocess_image(image, resize=False):
    img = image
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = img / 255
    if resize:
        img = cv2.resize(img, (224, 224))
    return img


def get_plate(image_path, wpod_net, Dmax=608, Dmin=256):
    vehicle = preprocess_image(image_path)
    ratio = float(max(vehicle.shape[:2])) / min(vehicle.shape[:2])
    side = int(ratio * Dmin)
    bound_dim = min(side, Dmax)
    _, LpImg, _, cor = detect_lp(wpod_net, vehicle, bound_dim, lp_threshold=0.5)
    return LpImg, cor


def draw_box(image_path, cor, thickness=3):
    pts = []
    x_coordinates = cor[0][0]
    y_coordinates = cor[0][1]
    # store the top-left, top-right, bottom-left, bottom-right
    # of the plate license respectively
    for i in range(4):
        pts.append([int(x_coordinates[i]), int(y_coordinates[i])])

    pts = np.array(pts, np.int32)
    pts = pts.reshape((-1, 1, 2))
    vehicle_image = preprocess_image(image_path)

    cv2.polylines(vehicle_image, [pts], True, (0, 255, 0), thickness)
    return vehicle_image


def sort_contours(cnts, reverse=False):
    i = 0
    boundingBoxes = [cv2.boundingRect(c) for c in cnts]
    (cnts, boundingBoxes) = zip(*sorted(zip(cnts, boundingBoxes),
                                        key=lambda b: b[1][i], reverse=reverse))
    return cnts

# pre-processing input images and pedict with model
def predict_from_model(image,model,labels):
    image = cv2.resize(image,(80,80))
    image = np.stack((image,)*3, axis=-1)
    prediction = labels.inverse_transform([np.argmax(model.predict(image[np.newaxis,:]))])
    return prediction
