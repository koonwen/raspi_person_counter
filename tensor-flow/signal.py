from gpiozero import LED, Button
from signal import pause

led = LED(4)
button = Button(17)

def light():
	if led.is_lit:
		led.off()
	else:
		led.on()


def switch(func):
	def wrapper(func):
		while True:
			try:
				button.when_pressed = light
				func()
			except KeyboardInterrupt:
				break
				print("\nQuitting")
	return wrapper

led.source = button

pause()