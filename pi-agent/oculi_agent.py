import os
import io
import sys
import argparse
import time
from datetime import datetime

import cv2
import numpy as np
import pytesseract as ocr
from PIL import Image
import boto3
import pyttsx3
import pyaudio
import wave

from oculi_gpio import GPIOThread

# TEXT_ON_BOOT = "Oi. Estou pronto"
AUDIO_ON_BOOT = "./audio/on_boot.wav"

speak_engine = pyttsx3.init(driverName='espeak')
speak_engine.setProperty('voice', 'pt+m7')
rate = speak_engine.getProperty('rate')
speak_engine.setProperty('rate', rate - 50)

def say(text):
    speak_engine.say(text)
    speak_engine.runAndWait()

def play(audio_file):
    chunk = 1024

    f = wave.open(audio_file,"rb")
    p = pyaudio.PyAudio()
    stream = p.open(format = p.get_format_from_width(f.getsampwidth()),
                channels = f.getnchannels(),
                rate = f.getframerate(),
                output = True)
    data = f.readframes(chunk)

    while data:
        stream.write(data)
        data = f.readframes(chunk)

    stream.stop_stream()
    stream.close()

    p.terminate()

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


def agent_loop(gpio=None, show_images=False):

    mirror = False

    cam = cv2.VideoCapture(0)
    client = boto3.client('rekognition')

    predict_ocr = False
    predict_faces = False

    while True:
        ret_val, img = cam.read()
        if mirror:
            img = cv2.flip(img, 1)

        img_np = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_pil = Image.fromarray(img_np)

        if predict_ocr:
            stream = io.BytesIO()
            img_pil.save(stream, format="JPEG")
            image_binary = stream.getvalue()
            do_ocr(client, image_binary)
            predict_ocr = False

        if predict_faces:
            stream = io.BytesIO()
            img_pil.save(stream, format="JPEG")
            image_binary = stream.getvalue()
            do_faces(client, image_binary)
            predict_faces = False


        if show_images:
            cv2.imshow('my webcam', img)

        if gpio is not None and gpio.is_ocr_button_pressed():
            predict_ocr = True
        k = cv2.waitKey(1)
        if k == 97: #a
            predict_ocr = True
        if k == 115: #s
            print('s')
            predict_faces = True
        if k == 27:
            break  # esc to quit
    cv2.destroyAllWindows()

def do_ocr(client, image_binary):
    response = client.detect_text(
        Image={'Bytes': image_binary}
    )

    detections = response['TextDetections']
    for t in detections:
        if t['Type'] != 'LINE':
            continue
        # if t['Confidence'] < 60:
            # continue
        say(t['DetectedText'])
        print(t['DetectedText'], end=" ")
        print()

def build_face_description(face):
    gender = 'pessoa'

    if face.get('Gender') and face['Gender']['Confidence'] > 80:
        if face['Gender']['Value'] == 'Male': gender = "homem"
        if face['Gender']['Value'] == 'Female': gender = "Mulher"
    age_mean = int(0.5 * (face['AgeRange']['High'] + face['AgeRange']['Low']))

    face['Emotions'] = [x for x in face['Emotions'] if x['Confidence'] > 60]

    max_emotion = ''
    if face['Emotions']:
        max_emotion = max(face['Emotions'], key=lambda e: e['Confidence'])['Type']
    print(max_emotion)

    emotion = ""

    if max_emotion == 'HAPPY': emotion = "feliz"
    if max_emotion == 'SAD': emotion = "triste"
    if max_emotion == 'ANGRY': emotion = "nervoso" if gender == "homem" else "nervosa"
    if max_emotion == 'CONFUSED': emotion = "confuso" if gender == "homem" else "nervosa"
    if max_emotion == 'DISGUSTED': emotion = "estar com nojo"
    if max_emotion == 'SUPRISED': emotion = "supreso" if gender == "homem" else "surpresa"
    if max_emotion == 'CALM': emotion = "calmo" if gender == "homem" else "calma"
    if max_emotion == 'FEAR': emotion = "com medo"

    pronoun = 'ele' if gender == 'homem' else 'ela'
    description = f'{gender.capitalize()}. Aproximadamente {int(age_mean)} anos.'
    if emotion:
        description += f'Parece estar {emotion}'
    return description.split('.')

def do_faces(client, image_binary):
    response = client.detect_faces(
        Image={'Bytes': image_binary},
        Attributes= ['ALL']
    )

    persons_detected = response['FaceDetails']
    for p in persons_detected:
        if p['Confidence'] < 80:
            continue
        desc = build_face_description(p)
        print(desc)
        for s in desc:
            say(s)
        time.sleep(1)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Oculi Agent')
    parser.add_argument('--gpio', dest='gpio', action='store_const',
                        const=True, default=False,
                        help='run with GPIO support (default = False)')

    args = parser.parse_args()
    gpio_t1 = None
    if args.gpio:
        gpio_t1 = GPIOThread()
        gpio_t1.start()


    # say(TEXT_ON_BOOT)
    play(AUDIO_ON_BOOT)

    agent_loop(gpio_t1, gpio_t1 is None)
