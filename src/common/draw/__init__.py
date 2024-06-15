import cv2
import numpy as np

from .typing import Image


def imageToBytes(img: Image):
    _, im = cv2.imencode('.png', cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR))

    return im.tobytes()
