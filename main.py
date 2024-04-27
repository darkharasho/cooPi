import time
import schedule
import logging
from datetime import datetime
from lib import config
from lib.pca9685 import PCA9685

OPEN_TIME = "06:00:00"
CLOSE_TIME = "21:00:00"

logging.basicConfig(filename='output.log', level=logging.INFO,
                    format='%(asctime)s:%(levelname)s:%(message)s')


def door_control(status: str):
    pwm = PCA9685()
    pwm.setPWMFreq(50)  # for servo

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{current_time} - Door control activated")
    logging.info(f"{current_time} - Door control activated")

    pwm.setServoPulse(config.DC_MOTOR_PWM1, 15000)  # for TB6612 set speed

    if status == 'open':
        pwm.setServoPulse(config.DC_MOTOR_INA1, 19999)  # set INA1 L
        pwm.setServoPulse(config.DC_MOTOR_INA2, 0)  # set INA2 H
        print("M1 open")
        logging.info("M1 open")
        time.sleep(8)
        pwm.setServoPulse(config.DC_MOTOR_PWM1, 0)
    elif status == 'close':
        pwm.setServoPulse(config.DC_MOTOR_INA1, 0)  # set INA1 H
        pwm.setServoPulse(config.DC_MOTOR_INA2, 19999)  # set INA2 L
        print("M1 close")
        logging.info("M1 close")
        time.sleep(8)
        pwm.setServoPulse(config.DC_MOTOR_PWM1, 0)  # for TB6612 set speed to 0, stop
    else:
        print("Invalid status")
        logging.warn("Invalid status")


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

    print("Automated Coop Door Schedule Running")
    print(f"Opens at: {OPEN_TIME}")
    print(f"Closes at: {CLOSE_TIME}")

    logging.info("Automated Coop Door Schedule Running")
    logging.info(f"Opens at: {OPEN_TIME}")
    logging.info(f"Closes at: {CLOSE_TIME}")

    schedule.every().day.at(OPEN_TIME).do(lambda: door_control("open"))
    schedule.every().day.at(CLOSE_TIME).do(lambda: door_control("close"))

    health_check_timer = 10

    try:
        while True:
            if (int(datetime.now().strftime("%M")) % health_check_timer == 0 &
                    0 == int(datetime.now().strftime("%S"))):
                logging.info(f"Health check")
            schedule.run_pending()
            time.sleep(1)

    except KeyboardInterrupt:
        print("Keyboard interrupt detected. Exiting...")
        logging.warning("Keyboard interrupt detected")
