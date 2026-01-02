import RPi.GPIO as GPIO
import time

class Motor:
    def __init__(self, in1=24, in2=23, en=26):
        self.IN1 = in1
        self.IN2 = in2
        self.EN = en

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.IN1, GPIO.OUT)
        GPIO.setup(self.IN2, GPIO.OUT)
        GPIO.setup(self.EN, GPIO.OUT)

        self.stop()

    def dispense_one_bill(self, duration=2):
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.HIGH)
        GPIO.output(self.EN, GPIO.HIGH)

        time.sleep(duration)
        self.stop()
        time.sleep(0.5)  # small gap between bills

    def dispense_amount(self, amount):
        runs = int(amount / 500)
        print(f"[MOTOR] Dispensing {runs} bills")

        for i in range(runs):
            print(f"[MOTOR] Bill {i + 1}")
            self.dispense_one_bill()

    def stop(self):
        GPIO.output(self.EN, GPIO.LOW)
        GPIO.output(self.IN1, GPIO.LOW)
        GPIO.output(self.IN2, GPIO.LOW)

    def cleanup(self):
        GPIO.cleanup()
