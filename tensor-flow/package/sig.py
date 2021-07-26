from gpiozero import LED, Button
from signal import pause
from threading import Thread, Event

led = LED(4)
button = Button(17)

# Event Signal
button_press = Event()

# Decorator to implement function start and stop via button
def button_interrupt(func):

	func_thread = Thread(target=func, name="function")
	func_thread.start()

	def switch():
		if led.is_lit:
			button_press.clear()
			led.off()
		else:
			button_press.set()
			led.on()

	def wrapper():
		try:
			button.when_pressed = switch
			pause()
		except KeyboardInterrupt:
			func_thread.join()
			print("Exitting")

	return wrapper
