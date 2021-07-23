from gpiozero import Button, LED
from signal import pause, sigSIGUSR1
button = Button(17)
led = LED(4)

def switch():
    if led.is_lit:
        led.off()
    else:
        led.on()

def press():
     print("PRESSED")

button.when_pressed = switch

pause()
