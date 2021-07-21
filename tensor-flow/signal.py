from gpiozero import LED, Button
from time import sleep

led = LED(4)
button = Button(17)

def light():
	if led.is_lit:
		led.off()
	else:
		led.on()


def switch(func):
	def wrapper():
		while True:
			try:
				button.wait_for_press()
				light()
				func()
				light()
			except KeyboardInterrupt:
				break
				print("\nQuitting")
	return wrapper

