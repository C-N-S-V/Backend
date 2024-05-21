import smbus
import mpu9250  # MPU9250 모듈 import
from datetime import datetime
from flask import Flask, request
import time
import math

app = Flask(__name__)

def low_pass_filter(current, previous, alpha=0.5):
    return alpha * current + (1 - alpha) * previous

def calibrate_sensor(mpu, samples=1024):
    ax_sum = ay_sum = az_sum = 0
    for _ in range(samples):
        ax, ay, az = mpu.read_accel()
        ax_sum += ax
        ay_sum += ay
        az_sum += az
        time.sleep(0.01)

    return ax_sum / samples, ay_sum / samples, az_sum / samples

def calculate_angles(ax, ay, az):
    roll = math.atan2(ay, az) * 180 / math.pi
    pitch = math.atan2(-ax, math.sqrt(ay**2 + az**2)) * 180 / math.pi
    return roll, pitch

@app.route('/data', methods=['POST'])
def data():
    i2c_bus = smbus.SMBus(1)
    mpu9250_1 = mpu9250.MPU9250(i2c_bus, 0x68)
    mpu9250_2 = mpu9250.MPU9250(i2c_bus, 0x69)

    Ax_1_Off, Ay_1_Off, Az_1_Off = calibrate_sensor(mpu9250_1)
    Ax_2_Off, Ay_2_Off, Az_2_Off = calibrate_sensor(mpu9250_2)

    # Initialize the previous values for filtering
    prev_Ax1, prev_Ay1, prev_Az1 = 0, 0, 0
    prev_Ax2, prev_Ay2, prev_Az2 = 0, 0, 0

    while True:
        time.sleep(15)

        accel_1 = []
        accel_2 = []

        for _ in range(10):
            Ax_1, Ay_1, Az_1 = mpu9250_1.read_accel()
            Ax_2, Ay_2, Az_2 = mpu9250_2.read_accel()

            # Apply low-pass filter
            Ax_1 = low_pass_filter(Ax_1, prev_Ax1)
            Ay_1 = low_pass_filter(Ay_1, prev_Ay1)
            Az_1 = low_pass_filter(Az_1, prev_Az1)
            Ax_2 = low_pass_filter(Ax_2, prev_Ax2)
            Ay_2 = low_pass_filter(Ay_2, prev_Ay2)
            Az_2 = low_pass_filter(Az_2, prev_Az2)

            # Update previous values
            prev_Ax1, prev_Ay1, prev_Az1 = Ax_1, Ay_1, Az_1
            prev_Ax2, prev_Ay2, prev_Az2 = Ax_2, Ay_2, Az_2

            accel_1.append((Ax_1, Ay_1, Az_1))
            accel_2.append((Ax_2, Ay_2, Az_2))
            time.sleep(0.1)

        # Calculate average and adjust for offset
        Ax_1_avg = sum([a[0] for a in accel_1]) / len(accel_1) - Ax_1_Off
        Ay_1_avg = sum([a[1] for a in accel_1]) / len(accel_1) - Ay_1_Off
        Az_1_avg = sum([a[2] for a in accel_1]) / len(accel_1) - Az_1_Off
        Ax_2_avg = sum([a[0] for a in accel_2]) / len(accel_2) - Ax_2_Off
        Ay_2_avg = sum([a[1] for a in accel_2]) / len(accel_2) - Ay_2_Off
        Az_2_avg = sum([a[2] for a in accel_2]) / len(accel_2) - Az_2_Off

        roll_1, pitch_1 = calculate_angles(Ax_1_avg, Ay_1_avg, Az_1_avg)
        roll_2, pitch_2 = calculate_angles(Ax_2_avg, Ay_2_avg, Az_2_avg)

        avg_roll = (roll_1 + roll_2) / 2
        avg_pitch = (pitch_1 + pitch_2) / 2

        # Check posture thresholds
        if abs(avg_roll) > 3 or abs(avg_pitch) > 3:
            return "1"
        else:
            return "0"

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
