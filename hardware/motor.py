# hardware/motor.py

class Motor:
    def __init__(self, gpio, in1, in2, pwm_pin, frequency):
        self.gpio = gpio
        self.in1 = in1
        self.in2 = in2

        self.gpio.setup_output(in1)
        self.gpio.setup_output(in2)
        self.gpio.setup_output(pwm_pin)

        self.pwm = self.gpio.pwm(pwm_pin, frequency)
        self.pwm.start(0)

    def set_speed(self, speed):
        self.gpio.write(self.in1, True)
        self.gpio.write(self.in2, False)
        self.pwm.ChangeDutyCycle(speed)

    def reverse(self, speed):
        self.gpio.write(self.in1, False)
        self.gpio.write(self.in2, True)
        self.pwm.ChangeDutyCycle(speed)

    def stop(self):
        self.gpio.write(self.in1, False)
        self.gpio.write(self.in2, False)
        self.pwm.ChangeDutyCycle(0)
