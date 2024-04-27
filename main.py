import time
from lib import config
from lib.pca9685 import PCA9685
from celery import Celery

app = Celery('tasks', broker='pyamqp://guest@localhost//')


def open():
    pwm = PCA9685()
    pwm.setPWMFreq(50)  # for servo

    print("open")
    pwm.setServoPulse(config.DC_MOTOR_PWM1, 15000)  # for TB6612 set speed
    # CCW
    pwm.setServoPulse(config.DC_MOTOR_INA1, 19999)  # set INA1 L
    pwm.setServoPulse(config.DC_MOTOR_INA2, 0)  # set INA2 H
    print("M1 rotate")
    time.sleep(8)


def close():
    print("close")

    pwm = PCA9685()
    pwm.setPWMFreq(50)  # for servo

    # CW
    pwm.setServoPulse(config.DC_MOTOR_INA1, 0)  # set INA1 H
    pwm.setServoPulse(config.DC_MOTOR_INA2, 19999)  # set INA2 L
    print("M1 rotate opposite")
    time.sleep(8)
    pwm.setServoPulse(config.DC_MOTOR_PWM1, 0)  # for TB6612 set speed to 0, stop


if __name__ == '__main__':
    """for servo motor:
    the high part of the pulse is T
    T = 0.5ms => 0   degree
    T = 1.0ms => 45  degree
    T = 1.5ms => 90  degree
    T = 2.0ms => 135 degree
    T = 2.5ms => 180 degree

    for 2 channel DC motor driven by TB6612FNG
    IN1   IN2  PWM  STBY  OUT1   OUT2      MODE
    H     H   H/L   H     L      L    short brake
    L     H    H    H     L      H       CCW
    L     H    L    H     L      L    short brake
    H     L    H    H     H      L       CW
    H     L    L    H     L      L    short brake
    L     L    H    H    OFF    OFF      STOP
    H/L   H/L  H/L   L    OFF    OFF    standby
    """
    pwm = PCA9685()
    pwm.setPWMFreq(50)  # for servo

    while True:
        """The following code is applied to
        DC motor control
        """

        open()
        close()
        exit()
