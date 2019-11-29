import threading
import time

BUTTON_READ_OCR = 10

class GPIOThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.isDaemon = True
        self.buttons_pushed = {
            'read_ocr': False
        }

        self.last_read_ocr = 0

    def run(self):
        import RPi.GPIO as GPIO
        print('GPIO starting')
        sys.stdout.flush()

        import RPi.GPIO as GPIO
        GPIO.setwarnings(False) # Ignore warning for now
        GPIO.setmode(GPIO.BOARD) # Use physical pin numbering

        GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)
        while True: # Run forever
            if GPIO.input(BUTTON_READ_OCR) == GPIO.HIGH:
                if time.time() - last_read_ocr < 5:
                    continue

                self.last_read_ocr = time.time()
                self.buttons_pushed[BUTTON_READ_OCR] = True
                print("OCR Button was pushed!", flush=True)

    def is_ocr_button_pressed(self):
        pressed = self.buttons_pushed[BUTTON_READ_OCR] == True
        if pressed:
            self.buttons_pushed[BUTTON_READ_OCR] = False
        return pressed
