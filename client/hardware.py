import gpiozero
import signal
import sys

class OctavioHardware:
    def __init__(self, red_pin=17, green_pin=27, button_pin=18):
        self.red_pin = red_pin
        self.green_pin = green_pin
        self.button_pin = button_pin

        self.red_led = gpiozero.LED(red_pin)
        self.green_led = gpiozero.LED(green_pin)
        self.button = gpiozero.Button(button_pin)

    def shine_red(self):
        self.green_led.off()
        self.red_led.on()

    def shine_green(self):
        self.red_led.off()
        self.green_led.on()

    def shine_yellow(self):
        self.green_led.on()
        self.red_led.on()

    def deactivate_light(self):
        self.red_led.off()
        self.green_led.off()

    @property
    def button_pressed(self):
        return self.button.is_pressed

def test_hardware_repl():
    hardware = OctavioHardware()
    def on_shutdown():
        hardware.deactivate_light()
        sys.exit(0)
    signal.signal(signal.SIGTERM, lambda signum, frame: on_shutdown())
    signal.signal(signal.SIGINT, lambda signum, frame: on_shutdown())

    print('Engaging hardware testing REPL')

    test_instructions = "\nOptions are:\n" \
    "\t'd' for lights-off\n" \
    "\t'g' for green\n" \
    "\t'r' for red\n" \
    "\t'y' for yellow\n" \
    "\t'b' to show if button is pressed\n" \
    "\t'exit' or 'quit' to quit\n\n"

    while True:
        command = input(test_instructions)
        match command.strip().lower():
            case 'exit' | 'quit':
                print('Exiting hardware testing REPL')
                break
            case 'd':
                hardware.deactivate_light()
            case 'g':
                hardware.shine_green()
            case 'r':
                hardware.shine_red()
            case 'y':
                hardware.shine_yellow()
            case 'b':
                b = hardware.button_pressed
                text = 'Button is pressed' if b else 'Button is not pressed'
                print(text)
            case _:
                print('Not a valid command to test')

if __name__ == '__main__':
    ...

    test_hardware_repl()
