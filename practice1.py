import time
from mpu9250_jmdev.registers import *
from mpu9250_jmdev.mpu_9250 import MPU9250

# MPU9250 인스턴스 생성
mpu = MPU9250(
	address_ak = AK8963_ADDRESS,
	address_mpu_master=MPU9050_ADDRESS_68,
	address_mpu_slave=None,
	bus=1,
	gfs=GFS_1000,# 파라미터로 범위 지정
	afs=AFS_8G,
	mfs=AK8963_BIT_16,
	mode=AK8963_MODE_C100HZ)
# MPU9250 설정
mpu.configure()
	
while True:
	# accelerometer, gyrocope, magnetometer 값 읽기
	accel_data = mpu.readAccelerometerMaster()
	gyro_data = mpu.readGyroscopeMaster()
	mag_data = mpu.readMagnetometerMaster()
	# 센서 값 출력
	print("Accelerometer: ", accel_data)
	print("Gyroscope: " , gyro_data)
	print("Magnetometer:", mag_data)
	#1초마다 값 읽음
	time.sleep(1)
