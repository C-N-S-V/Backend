import smbus
from flask import Flask, request
import time
from datetime import datetime
import mpu9250_1  # Your MPU9250 module import

app = Flask(__name__)

@app.route('/data', methods=['POST'])
def data():
    # I2C 설정
    i2c_bus = smbus.SMBus(1)  # SDA1과 SCL1 핀, 따라서 버스 1
    mpu9250_3 = mpu9250_1.MPU9250(i2c_bus, 0x68)  # IMU 통신 주소
    mpu9250_2 = mpu9250_1.MPU9250(i2c_bus, 0x69)

    try:
        t_prev = datetime.now().timestamp()

    
        ax1 = mpu9250_3.read_accel()
        ax2 = mpu9250_2.read_accel()

   
        print(f"Sensor 1: ax={ax1}")
        print(f"Sensor 2: ax={ax2}")
        
        if abs(ax2-ax1)/1000 > 0.5:
            return "1"
        else:
            return "0"
 

    except KeyboardInterrupt:
        pass
    finally:
        i2c_bus.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
