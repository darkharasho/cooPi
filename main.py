import time
import schedule
import logging
import argparse
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
        print("[OPEN] Start")
        logging.info("[OPEN] Start")
        time.sleep(9)
        pwm.setServoPulse(config.DC_MOTOR_PWM1, 0)
        print("[OPEN] Finished")
        logging.info("[OPEN] Finished")
    elif status == 'close':
        print("[CLOSE] Start")
        logging.info("[CLOSE] Start")
        for i in [3, 4]:
            warning_close(pwm, i)
        print("[CLOSE] Finished")
        logging.info("[CLOSE] Finished")
        # warning_close(pwm)
        # warning_close(pwm, 3)
        #
        pwm.setServoPulse(config.DC_MOTOR_PWM1, 19999)  # for TB6612 set speed

        pwm.setServoPulse(config.DC_MOTOR_INA1, 0)  # set INA1 H
        pwm.setServoPulse(config.DC_MOTOR_INA2, 19999)  # set INA2 L
        print("[CLOSE] Start")
        logging.info("[CLOSE] Start")
        time.sleep(4)
        pwm.setServoPulse(config.DC_MOTOR_PWM1, 0)  # for TB6612 set speed to 0, stop
        print("[CLOSE] Finished")
        logging.info("[CLOSE] Finished")
    else:
        print("Invalid status")
        logging.warn("Invalid status")

def warning_close(pwm, timer=2):
    pwm.setServoPulse(config.DC_MOTOR_PWM1, 15000)
    print("[CLOSE] Warning")
    logging.info("[CLOSE] Warning")
    # Partially close the door to warn
    pwm.setServoPulse(config.DC_MOTOR_INA1, 0)  # set INA1 H
    pwm.setServoPulse(config.DC_MOTOR_INA2, 19999)  # set INA2 L
    time.sleep(timer)

    # Open the door fully
    pwm.setServoPulse(config.DC_MOTOR_INA1, 19999)  # set INA1 H
    pwm.setServoPulse(config.DC_MOTOR_INA2, 0)  # set INA2 L
    time.sleep(2)

    # Stop and wait 5 seconds before fully closing
    pwm.setServoPulse(config.DC_MOTOR_PWM1, 0)  # for TB6612 set speed to 0, stop
    time.sleep(5)


def main():
    parser = argparse.ArgumentParser(description='Automated Chicken Coop Door')
    parser.add_argument('-m', '--mode',
                        choices=['open', 'close', 'auto'],
                        default='auto', help='Choose mode of operation')

    args = parser.parse_args()

    if args.mode == 'open':
        door_control("open")
    elif args.mode == 'close':
        door_control("close")
    elif args.mode == 'auto':
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


if __name__ == '__main__':
    main()
