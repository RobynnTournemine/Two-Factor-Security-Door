import RPi.GPIO as GPIO
import time
channel = 33

GPIO.setmode(GPIO.BOARD)
GPIO.setup(channel, GPIO.OUT)
try:
	while True:
		GPIO.output(channel, False)
		time.sleep(5)
		GPIO.output(channel, True)
		GPIO.cleanup()
except KeyboardInterrupt:
	GPIO.cleanup()
