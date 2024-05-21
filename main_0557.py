import smbus
from flask import Flask, request
import time
from datetime import datetime
import mpu9250  # Your MPU9250 module import

app = Flask(__name__)

@app.route('/data', methods=['POST'])
def data():
    # I2C 설정
    i2c_bus = smbus.SMBus(1)  # SDA1과 SCL1 핀, 따라서 버스 1
    mpu9250_1 = mpu9250.MPU9250(i2c_bus, 0x68)  # IMU 통신 주소
    mpu9250_2 = mpu9250.MPU9250(i2c_bus, 0x69)

    try:
        t_prev = datetime.now().timestamp()
        time.sleep(15)  # 15초 지연

        # 가속도 데이터 읽기
        ax1, ay1, az1 = mpu9250_1.read_accel()
        ax2, ay2, az2 = mpu9250_2.read_accel()

        # 여기에 데이터 처리 로직 추가
        print(f"Sensor 1: ax={ax1}, ay={ay1}, az={az1}")
        print(f"Sensor 2: ax={ax2}, ay={ay2}, az={az2}")

        return "Data processed"

    except KeyboardInterrupt:
        pass
    finally:
        i2c_bus.close()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
