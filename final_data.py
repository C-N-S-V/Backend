import smbus
import mpu9250  # MPU9250 모듈 import
from datetime import datetime
from flask import Flask, request
import time

app = Flask(__name__)


def calibrate_sensor(mpu, samples=1024):
    x_sum = y_sum = z_sum = 0
    for _ in range(samples):
        gx, gy, gz = mpu.read_gyro()
        x_sum += gx
        y_sum += gy
        z_sum += gz
        time.sleep(0.01)

    return x_sum / samples, y_sum / samples, z_sum / samples


@app.route('/data', methods=['POST'])
def data():
    # I2C setup
    i2c_bus = smbus.SMBus(1)  # SDA1 and SCL1 pins, so bus 1
    mpu9250_1 = mpu9250.MPU9250(i2c_bus, 0x68)
    mpu9250_2 = mpu9250.MPU9250(i2c_bus, 0x69)

    GyX_1_Off, GyY_1_Off, GyZ_1_Off = calibrate_sensor(mpu9250_1)
    GyX_2_Off, GyY_2_Off, GyZ_2_Off = calibrate_sensor(mpu9250_2)

    AngleX = AngleY = AngleZ = 0.0
    AngleX_2 = AngleY_2 = AngleZ_2 = 0.0

    try:
        while True:
            t_prev = datetime.now().timestamp()
            time.sleep(1)

            GyX_1, GyY_1, GyZ_1 = mpu9250_1.read_gyro()
            GyX_2, GyY_2, GyZ_2 = mpu9250_2.read_gyro()

            GyX_1 -= GyX_1_Off
            GyY_1 -= GyY_1_Off
            GyZ_1 -= GyZ_1_Off
            GyX_2 -= GyX_2_Off
            GyY_2 -= GyY_2_Off
            GyZ_2 -= GyZ_2_Off

            t_now = datetime.now().timestamp()
            dt = t_now - t_prev
            t_prev = t_now

            AngleX += GyX_1 * dt
            AngleX_2 += GyX_2 * dt

            AvgX = abs((AngleX - AngleX_2) / 2)

            print(AvgX)

            if AvgX / 1000 > 0.5:
                return "1"
            else:
                return "0"

    except KeyboardInterrupt:
        pass
    finally:
        i2c_bus.close()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
0 comments on commit 749dec9
