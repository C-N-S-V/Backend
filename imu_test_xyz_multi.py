import smbus
import mpu9250  # Your MPU9250 module
from datetime import datetime

# I2C setup
i2c_bus = smbus.SMBus(1)  # SDA1 and SCL1 pins, so bus 1

# Initialize two MPU9250 sensors with different addresses
mpu1 = mpu9250.MPU9250(i2c_bus, 0x68)  # First MPU9250 sensor (AD0 connected to GND)
mpu2 = mpu9250.MPU9250(i2c_bus, 0x69)  # Second MPU9250 sensor (AD0 connected to VCC)

# Initialize calibration and angle variables for both sensors
GyXSum1 = GyYSum1 = GyZSum1 = 0
GyXSum2 = GyYSum2 = GyZSum2 = 0
GyXOff1 = GyYOff1 = GyZOff1 = 0.0
GyXOff2 = GyYOff2 = GyZOff2 = 0.0
nSample1 = nSample2 = 1024  # Calibration sample count
t_prev1 = t_prev2 = 0  # Time tracking
AngleX1 = AngleY1 = AngleZ1 = 0.0  # Accumulated angles for first sensor
AngleX2 = AngleY2 = AngleZ2 = 0.0  # Accumulated angles for second sensor

cnt_loop = 0  # Loop count for periodic output

try:
    while True:
        # Read all three axes for each sensor
        GyX1, GyY1, GyZ1 = mpu1.read_gyro()
        GyX2, GyY2, GyZ2 = mpu2.read_gyro()

        # Calibration process for the first sensor
        if nSample1 > 0:
            GyXSum1 += GyX1
            GyYSum1 += GyY1
            GyZSum1 += GyZ1
            nSample1 -= 1
            if nSample1 == 0:
                GyXOff1 = GyXSum1 / 1024
                GyYOff1 = GyYSum1 / 1024
                GyZOff1 = GyZSum1 / 1024
        else:
            # Offset correction for the first sensor
            GyXD1 = GyX1 - GyXOff1
            GyYD1 = GyY1 - GyYOff1
            GyZD1 = GyZ1 - GyZOff1
            GyXR1 = GyXD1 / 131
            GyYR1 = GyYD1 / 131
            GyZR1 = GyZD1 / 131

            # Time tracking and angle calculation for the first sensor
            t_now1 = datetime.now().microsecond
            dt_n1 = t_now1 - t_prev1
            t_prev1 = t_now1
            dt1 = dt_n1 / 1000000

            AngleX1 += GyXR1 * dt1
            AngleY1 += GyYR1 * dt1
            AngleZ1 += GyZR1 * dt1

        # Calibration process for the second sensor
        if nSample2 > 0:
            GyXSum2 += GyX2
            GyYSum2 += GyY2
            GyZSum2 += GyZ2
            nSample2 -= 1
            if nSample2 == 0:
                GyXOff2 = GyXSum2 / 1024
                GyYOff2 = GyYSum2 / 1024
                GyZOff2 = GyZSum2 / 1024
        else:
            # Offset correction for the second sensor
            GyXD2 = GyX2 - GyXOff2
            GyYD2 = GyY2 - GyYOff2
            GyZD2 = GyZ2 - GyZOff2
            GyXR2 = GyXD2 / 131
            GyYR2 = GyYD2 / 131
            GyZR2 = GyZD2 / 131

            # Time tracking and angle calculation for the second sensor
            t_now2 = datetime.now().microsecond
            dt_n2 = t_now2 - t_prev2
            t_prev2 = t_now2
            dt2 = dt_n2 / 1000000

            AngleX2 += GyXR2 * dt2
            AngleY2 += GyYR2 * dt2
            AngleZ2 += GyZR2 * dt2

        cnt_loop += 1

        # Print accumulated angles periodically
        if cnt_loop % 50 == 0:
            print(
                "Sensor 1: AngleX = %.2f, AngleY = %.2f, AngleZ = %.2f" % (AngleX1, AngleY1, AngleZ1)
            )
            print(
                "Sensor 2: AngleX = %.2f, AngleY = %.2f, AngleZ = %.2f" % (AngleX2, AngleY2, AngleZ2)
            )

except KeyboardInterrupt:
    pass

i2c_bus.close()
