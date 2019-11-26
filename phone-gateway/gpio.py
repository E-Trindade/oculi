import RPi.GPIO as GPIO # Import Raspberry Pi GPIO library
import time
GPIO.setwarnings(False) # Ignore warning for now
GPIO.setmode(GPIO.BOARD) # Use physical pin numbering

GPIO.setup(10, GPIO.IN, pull_up_down=GPIO.PUD_DOWN) # Set pin 10 to be an input pin and set initial value to be pulled low (off)

last_read = 0
while True: # Run forever
    if GPIO.input(10) == GPIO.HIGH:
        if time.time() - last_read < 3:
            # print('skiping')
            continue
        last_read = time.time()
        print("Button was pushed!")
