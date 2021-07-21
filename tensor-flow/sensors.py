from gpiozero import LED, Button
from time import sleep
from signal import pause

led = LED(4)
button = Button(17)

def signal():

    def switch():
        if led.is_lit:
            led.off()
        else:
            led.on()

    while True:
        try:
            button.when_pressed = switch
        except KeyboardInterrupt:
            break
    print("\nQuitting")
    
if __name__ == "__main__":
    signal()
