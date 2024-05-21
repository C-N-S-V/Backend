import smbus
import mpu9250  # Your MPU9250 code import
from datetime import datetime
from flask import Flask, request
import time

app = Flask(__name__)

@app.route('/data', methods=['POST'])
def data():
    # I2C setup
    i2c_bus = smbus.SMBus(1)  # SDA1 and SCL1 pins, so bus 1
    mpu9250_1_ = mpu9250.MPU9250(i2c_bus, 0x68)  # IMU communication address
    mpu9250_2_ = mpu9250.MPU9250(i2c_bus, 0x69)

    # Initialize calibration and angle variables
    GyX_1_Sum = GyY_1_Sum = GyZ_1_Sum = 0
    GyX_1_Off = GyY_1_Off = GyZ_1_Off = 0.0
    GyX_2_Sum = GyY_2_Sum = GyZ_2_Sum = 0
    GyX_2_Off = GyY_2_Off = GyZ_2_Off = 0.0
    nSample = 1024  # Calibration sample count
    AngleX = AngleY = AngleZ = 0.0
    AngleX_2 = AngleY_2 = AngleZ_2 = 0.0  # Accumulated angles

    try:
        while True:
            t_prev = datetime.now().timestamp()
            time.sleep(15)  # Delay for 15 seconds

            GyX_1_, GyY_1_, GyZ_1_ = mpu9250_1_.read_gyro()
            GyX_2_, GyY_2_, GyZ_2_ = mpu9250_2_.read_gyro()  # Read all three axes

            # Gyroscope calibration process
            if nSample > 0:
                GyX_1_Sum += GyX_1_
                GyY_1_Sum += GyY_1_
                GyZ_1_Sum += GyZ_1_
                GyX_2_Sum += GyX_2_
                GyY_2_Sum += GyY_2_
                GyZ_2_Sum += GyZ_2_
                nSample -= 1
                if nSample == 0:
                    GyX_1_Off = GyX_1_Sum / 1024
                    GyY_1_Off = GyY_1_Sum / 1024
                    GyZ_1_Off = GyZ_1_Sum / 1024
                    GyX_2_Off = GyX_2_Sum / 1024
                    GyY_2_Off = GyY_2_Sum / 1024
                    GyZ_2_Off = GyZ_2_Sum / 1024

            # Correct for offset
            GyX_1_D = GyX_1_ - GyX_1_Off
            GyY_1_D = GyY_1_ - GyY_1_Off
            GyZ_1_D = GyZ_1_ - GyZ_1_Off
            GyX_2_D = GyX_2_ - GyX_2_Off
            GyY_2_D = GyY_2_ - GyY_2_Off
            GyZ_2_D = GyZ_2_ - GyZ_2_Off

            # Time tracking
            t_now = datetime.now().timestamp()
            dt = t_now - t_prev
            t_prev = t_now

            # Accumulate angles
            AngleX += GyX_1_D * dt
            AngleY += GyY_1_D * dt
            AngleZ += GyZ_1_D * dt
            AngleX_2 += GyX_2_D * dt
            AngleY_2 += GyY_2_D * dt
            AngleZ_2 += GyZ_2_D * dt

            # Calculate averages and check condition
            AvgX = (AngleX + AngleX_2) / 2
            AvgY = (AngleY + AngleY_2) / 2
            AvgZ = (AngleZ + AngleZ_2) / 2
            total_average = abs(AvgX) + abs(AvgY) + abs(AvgZ)

            if total_average > 3:
                return "1"
            else:
                return "0"  # You can customize this return message based on your requirement

    except KeyboardInterrupt:
        pass
    finally:
        i2c_bus.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
