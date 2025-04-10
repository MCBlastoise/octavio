import RPi.GPIO as GPIO

class OctavioHardware:
    def __init__(self, red_pin=17, green_pin=27, button_pin=18):
        self.red_pin = red_pin
        self.green_pin = green_pin
        self.button_pin = button_pin

        GPIO.cleanup()
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(red_pin, GPIO.OUT)
        GPIO.setup(green_pin, GPIO.OUT)
        GPIO.setup(button_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)  # Enable internal pull-up
    
    def shine_red(self):
        GPIO.output(self.green_pin, GPIO.LOW)  # Turn off green
        GPIO.output(self.red_pin, GPIO.HIGH)   # Turn on red

    def shine_green(self):
        GPIO.output(self.red_pin, GPIO.LOW)    # Turn off red
        GPIO.output(self.green_pin, GPIO.HIGH) # Turn on green

    def deactivate_light(self):
        GPIO.output(self.green_pin, GPIO.LOW)  # Turn off green
        GPIO.output(self.red_pin, GPIO.LOW)    # Turn off red
    
    @property
    def button_pressed(self):
        return GPIO.input(self.button_pin) == GPIO.LOW