import numpy as np
import cv2
import pytesseract as ocr
from PIL import Image

from datetime import datetime

import os

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
	while True:
		ret_val, img = cam.read()
		if mirror:
			img = cv2.flip(img, 1)

		img_np = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
		img_pil = Image.fromarray(img_np)


		img_proc = process_image(img_pil)

		# print(datetime.timestamp(datetime.now()))
		if datetime.timestamp(datetime.now()) - last_run > 3:
			phrase = ocr.image_to_string(img_proc, lang='por')
			if phrase != '': print(phrase)
			last_run = datetime.timestamp(datetime.now())


		# cv2.imshow('my webcam', img)
		cv2.imshow('processed', np.asarray(img_proc))
		if cv2.waitKey(1) == 27:
			break  # esc to quit
	cv2.destroyAllWindows()


def main():
	show_webcam(mirror=False)


if __name__ == '__main__':
	main()
