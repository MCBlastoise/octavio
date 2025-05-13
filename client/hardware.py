import gpiozero

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

    def deactivate_light(self):
        self.red_led.off()
        self.green_led.off()

    @property
    def button_pressed(self):
        return self.button.is_pressed
