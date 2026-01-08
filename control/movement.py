# control/movement.py

class MovementController:
    def __init__(self, left_motor, right_motor, speed):
        self.left_motor = left_motor
        self.right_motor = right_motor
        self.speed = speed

    def forward(self):
        self.left_motor.set_speed(self.speed)
        self.right_motor.set_speed(self.speed)

    def backward(self):
        self.left_motor.reverse(self.speed)
        self.right_motor.reverse(self.speed)

    def left(self):
        self.left_motor.reverse(self.speed)
        self.right_motor.set_speed(self.speed)

    def right(self):
        self.left_motor.set_speed(self.speed)
        self.right_motor.reverse(self.speed)

    def stop(self):
        self.left_motor.stop()
        self.right_motor.stop()
