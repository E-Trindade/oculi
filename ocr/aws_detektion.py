import numpy as np
import cv2
import pytesseract as ocr
from PIL import Image

from datetime import datetime
import time

import os
import io

import boto3

import pyttsx3



def process_image(image):
    image_rgb = image.convert('RGB')
    image_np = np.asarray(image).astype(np.uint8) 
    image_np = np.asarray(image).astype(np.uint8)
    image_np[:, :, 0] = 0 # zerando o canal R (RED)
    image_np[:, :, 1] = 0 # zerando o canal B (BLUE)
    im = cv2.cvtColor(image_np, cv2.COLOR_RGB2GRAY) 
    ret, thresh = cv2.threshold(im, 127, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
    img_bin = Image.fromarray(thresh)
    return img_bin


def show_webcam(mirror=False):
    last_run = 0
    cam = cv2.VideoCapture(0)
    client = boto3.client('rekognition')

    predict = False

    engine = pyttsx3.init(driverName='espeak')
    engine.setProperty('voice', 'pt+m1')

    while True:
        ret_val, img = cam.read()
        if mirror:
            img = cv2.flip(img, 1)

        img_np = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_np)

        if predict:
            stream = io.BytesIO()
            img_pil.save(stream, format="JPEG")
            image_binary = stream.getvalue()

            response = client.detect_text(
                Image={'Bytes':image_binary}
            )
            from pprint import pprint
            # pprint()
            detections = response['TextDetections']
            text = ""
            for t in detections:
                text = t['DetectedText'] + " "
                if t['Type'] != 'LINE':
                    continue
                if t['Confidence'] < 0.7:
                    continue
                engine.say(t['DetectedText'])
                print(t['DetectedText'], end=" ")
                print()
            predict = False
            engine.runAndWait()


        cv2.imshow('my webcam', img)
        # cv2.imshow('processed', np.asarray(img_proc))
        if cv2.waitKey(1) == 97: #a
            predict = True
        if cv2.waitKey(1) == 27:
            break  # esc to quit
    cv2.destroyAllWindows()


def main():
    show_webcam(mirror=False)


if __name__ == '__main__':
    main()
