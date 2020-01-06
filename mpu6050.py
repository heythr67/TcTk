"""This program handles the communication over I2C
between a Raspberry Pi and a MPU-6050 Gyroscope / Accelerometer combo.
Made by: MrTijn/Tijndagamer
Released under the MIT License
Copyright (c) 2015, 2016, 2017 MrTijn/Tijndagamer
"""
import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import math
import statistics
import smbus
import time
from tca9548a import I2C_SW
fig= plt.figure()
ax = fig.add_subplot(1,1,1)
xs = []
ys = []

class mpu6050:

    # Global Variables
    GRAVITIY_MS2 = 9.80665
    address = None
    bus = None

    # Scale Modifiers
    ACCEL_SCALE_MODIFIER_2G = 16384.0
    ACCEL_SCALE_MODIFIER_4G = 8192.0
    ACCEL_SCALE_MODIFIER_8G = 4096.0
    ACCEL_SCALE_MODIFIER_16G = 2048.0

    GYRO_SCALE_MODIFIER_250DEG = 131.0
    GYRO_SCALE_MODIFIER_500DEG = 65.5
    GYRO_SCALE_MODIFIER_1000DEG = 32.8
    GYRO_SCALE_MODIFIER_2000DEG = 16.4

    # Pre-defined ranges
    ACCEL_RANGE_2G = 0x00
    ACCEL_RANGE_4G = 0x08
    ACCEL_RANGE_8G = 0x10
    ACCEL_RANGE_16G = 0x18

    GYRO_RANGE_250DEG = 0x00
    GYRO_RANGE_500DEG = 0x08
    GYRO_RANGE_1000DEG = 0x10
    GYRO_RANGE_2000DEG = 0x18

    # MPU-6050 Registers
    PWR_MGMT_1 = 0x6B
    PWR_MGMT_2 = 0x6C

    ACCEL_XOUT0 = 0x3B
    ACCEL_YOUT0 = 0x3D
    ACCEL_ZOUT0 = 0x3F

    TEMP_OUT0 = 0x41

    GYRO_XOUT0 = 0x43
    GYRO_YOUT0 = 0x45
    GYRO_ZOUT0 = 0x47

    ACCEL_CONFIG = 0x1C
    GYRO_CONFIG = 0x1B

    offset= {} 
    CAL_D =  50
    GX_TH = 50 
    GY_TH = 50 
    GZ_TH = 50  
    ACC_TH =10

    def __init__(self, address, bus=1):
        self.address = address
        #self.bus_n = bus
        self.bus = bus
        print('bus number',' ',bus) 
        #self.i2csw= I2C_SW(bus, 0x70, 1)
        #self.i2csw.chn(self.bus_n-1)
        #if self.bus_n == 8 : 
            #self.i2csw2 = I2C_SW(bus,0x70,1)
            #self.i2csw2.chn(0)
            
        self.bus = smbus.SMBus(bus)
        
        # Wake up the MPU-6050 since it starts in sleep mode
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0x00)

    # I2C communication methods

    def read_i2c_word(self, register):
        """Read two i2c registers and combine them.

        register -- the first register to read from.
        Returns the combined read results.
        """
        
        #self.i2csw.chn(self.bus_n-1)
        
        #if self.bus_n == 8 :
             #self.i2csw2.chn(0)
        # Read the data from the registers
        high = self.bus.read_byte_data(self.address, register)
        low = self.bus.read_byte_data(self.address, register + 1)

        value = (high << 8) + low

        if (value >= 0x8000):
            return -((65535 - value) + 1)
        else:
            return value

    # MPU-6050 Methods

    def get_temp(self):
        """Reads the temperature from the onboard temperature sensor of the MPU-6050.

        Returns the temperature in degrees Celcius.
        """
        #self.i2csw.chn(self.bus_n-1)
        #if self.bus_n == 8 : 
             #self.i2csw2.chn(0)  
        raw_temp = self.read_i2c_word(self.TEMP_OUT0)

        # Get the actual temperature using the formule given in the
        # MPU-6050 Register Map and Descriptions revision 4.2, page 30
        actual_temp = (raw_temp / 340.0) + 36.53

        return actual_temp

    def set_accel_range(self, accel_range):
        """Sets the range of the accelerometer to range.

        accel_range -- the range to set the accelerometer to. Using a
        pre-defined range is advised.
        """
        # First change it to 0x00 to make sure we write the correct value later
        #self.i2csw.chn(self.bus_n-1) 
        #if self.bus_n == 8 : 
                #self.i2csw2.chn(0)
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, 0x00)

        # Write the new range to the ACCEL_CONFIG register
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, accel_range)

    def read_accel_range(self, raw = False):
        """Reads the range the accelerometer is set to.

        If raw is True, it will return the raw value from the ACCEL_CONFIG
        register
        If raw is False, it will return an integer: -1, 2, 4, 8 or 16. When it
        returns -1 something went wrong.
        """
        #self.i2csw.chn(self.bus_n-1)
        #if self.bus_n == 8 :
             #self.i2csw2.chn(0)
        raw_data = self.bus.read_byte_data(self.address, self.ACCEL_CONFIG)

        if raw is True:
            return raw_data
        elif raw is False:
            if raw_data == self.ACCEL_RANGE_2G:
                return 2
            elif raw_data == self.ACCEL_RANGE_4G:
                return 4
            elif raw_data == self.ACCEL_RANGE_8G:
                return 8
            elif raw_data == self.ACCEL_RANGE_16G:
                return 16
            else:
                return -1

    def get_accel_data(self, g = False):
        """Gets and returns the X, Y and Z values from the accelerometer.

        If g is True, it will return the data in g
        If g is False, it will return the data in m/s^2
        Returns a dictionary with the measurement results.
        """
        #self.i2csw.chn(self.bus_n-1)
        #if self.bus_n == 8 :
              #self.i2csw2.chn(0) 
        x = self.read_i2c_word(self.ACCEL_XOUT0)
        y = self.read_i2c_word(self.ACCEL_YOUT0)
        z = self.read_i2c_word(self.ACCEL_ZOUT0)

        accel_scale_modifier = None
        accel_range = self.read_accel_range(True)

        if accel_range == self.ACCEL_RANGE_2G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_2G
        elif accel_range == self.ACCEL_RANGE_4G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_4G
        elif accel_range == self.ACCEL_RANGE_8G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_8G
        elif accel_range == self.ACCEL_RANGE_16G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_16G
        else:
            print("Unkown range - accel_scale_modifier set to self.ACCEL_SCALE_MODIFIER_2G")
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_2G

        x = x / accel_scale_modifier
        y = y / accel_scale_modifier
        z = z / accel_scale_modifier

        if g is True:
            return {'x': x, 'y': y, 'z': z}
        elif g is False:
            x = x * self.GRAVITIY_MS2
            y = y * self.GRAVITIY_MS2
            z = z * self.GRAVITIY_MS2
            return {'x': x, 'y': y, 'z': z}

    def set_gyro_range(self, gyro_range):
        """Sets the range of the gyroscope to range.

        gyro_range -- the range to set the gyroscope to. Using a pre-defined
        range is advised.
        """
        # First change it to 0x00 to make sure we write the correct value later
        #self.i2csw.chn(self.bus_n-1) 
        #if self.bus_n == 8 :
             #self.i2csw2.chn(0)
        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, 0x00)

        # Write the new range to the ACCEL_CONFIG register
        self.bus.write_byte_data(self.address, self.GYRO_CONFIG, gyro_range)

    def read_gyro_range(self, raw = False):
        """Reads the range the gyroscope is set to.

        If raw is True, it will return the raw value from the GYRO_CONFIG
        register.
        If raw is False, it will return 250, 500, 1000, 2000 or -1. If the
        returned value is equal to -1 something went wrong.
        """
        #self.i2csw.chn(self.bus_n-1)
        #if self.bus_n == 8 :
             #self.i2csw2.chn(0)
        raw_data = self.bus.read_byte_data(self.address, self.GYRO_CONFIG)

        if raw is True:
            return raw_data
        elif raw is False:
            if raw_data == self.GYRO_RANGE_250DEG:
                return 250
            elif raw_data == self.GYRO_RANGE_500DEG:
                return 500
            elif raw_data == self.GYRO_RANGE_1000DEG:
                return 1000
            elif raw_data == self.GYRO_RANGE_2000DEG:
                return 2000
            else:
                return -1

    def get_gyro_data(self):
        """Gets and returns the X, Y and Z values from the gyroscope.

        Returns the read values in a dictionary.
        """
        #self.i2csw.chn(self.bus_n-1)
        #if self.bus_n == 8 :
             #self.i2csw2.chn(0) 
        x = self.read_i2c_word(self.GYRO_XOUT0)
        y = self.read_i2c_word(self.GYRO_YOUT0)
        z = self.read_i2c_word(self.GYRO_ZOUT0)

        gyro_scale_modifier = None
        gyro_range = self.read_gyro_range(True)

        if gyro_range == self.GYRO_RANGE_250DEG:
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_250DEG
        elif gyro_range == self.GYRO_RANGE_500DEG:
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_500DEG
        elif gyro_range == self.GYRO_RANGE_1000DEG:
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_1000DEG
        elif gyro_range == self.GYRO_RANGE_2000DEG:
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_2000DEG
        else:
            print("Unkown range - gyro_scale_modifier set to self.GYRO_SCALE_MODIFIER_250DEG")
            gyro_scale_modifier = self.GYRO_SCALE_MODIFIER_250DEG

        x = x / gyro_scale_modifier
        y = y / gyro_scale_modifier
        z = z / gyro_scale_modifier

        return {'x': x, 'y': y, 'z': z}

    def get_all_data(self):
        """Reads and returns all the available data."""
        temp = self.get_temp()
        accel = self.get_accel_data()
        gyro = self.get_gyro_data()

        return [accel, gyro, temp]

    def calculate_offset(self,ac_th, gx_th , gy_th, gz_th):
        ax = []
        gx = []
        ay = []
        az = []
        gy = []
        gz = [] 
        self.ACC_TH = ac_th 
        self.GX_TH  = gx_th
        self.GY_TH  = gy_th
        self.GZ_TH  = gz_th 
 
        for i in range(0,self.CAL_D):
               accel_data = self.get_accel_data()
               gyro_data = self.get_gyro_data()

               ax.append(accel_data['x'])
               ay.append(accel_data['y'])
               az.append(accel_data['z'])

               gx.append(gyro_data['x'])
               gy.append(gyro_data['y'])
               gz.append(gyro_data['z'])

               time.sleep(0.2)
        
               #print("Calberating.... "+  str(self.bus_n))
               
               print("Calberating.... ")
        return {'a':math.sqrt(statistics.mean(ax)*statistics.mean(ax)+statistics.mean(ay)*statistics.mean(ay)+statistics.mean(az)*statistics.mean(az)), 'gx':statistics.mean(gx), 'gy':statistics.mean(gy), 'gz':statistics.mean(gz)}


    def detect(self):

        accel_data= self.t_accel_data()
        gyro_data = self.t_gyro_data() 
        accel_dump_data = self.get_accel_data() 
        
        #print("DETECTING BUS ")  
        #print("DETECTING BUS ",self.bus_n)  
        #print("self.offset",self.offset)
        #print("accel_data", accel_data)
        #print("gyro_data", gyro_data) 
        return_data = [] 
        if((accel_data-self.offset['a'] > self.ACC_TH) | (abs(gyro_data['x']-self.offset['gx']) > self.GX_TH) | (abs(gyro_data['y'] - self.offset['gy']) > self.GY_TH) |(abs(gyro_data['z']-self.offset['gz']) > self.GZ_TH)): 
               return_data = [1,accel_dump_data['x'],accel_dump_data['y'],accel_dump_data['z'],gyro_data['x'],gyro_data['y'],gyro_data['z']]
               return return_data 
        return [-1] 

    def t_accel_data(self):
        accel_data = self.get_accel_data()
        x= math.sqrt(accel_data['x']*accel_data['x']+accel_data['y']*accel_data['y']+accel_data['z']*accel_data['z'])
   
        return x

    def t_gyro_data(self):
        return self.get_gyro_data()

def animate(self):
   global xs,ys 
   global ax
   x = t_gyro_data() 
   #x= t_accel_data()
   xs.append(dt.datetime.now())
   ys.append(x['x'])

   xs = xs[-20:]
   ys = ys[-20:] 
   ax.clear()
   ax.plot(xs,ys)

   plt.xticks(rotation=45,ha='right')
   plt.subplots_adjust(bottom=0.30)
   plt.title('time')
   plt.ylabel('Acclerattor data')

#if __name__ == "__main__":
#    mpu = mpu6050(0x68,8)
#    time.sleep(2)  
#    print(mpu.get_temp())
#    mpu.offset= mpu.calculate_offset(10,5,5,5)
     
#    while True :
   	#ani=animation.FuncAnimation(fig,animate,interval=200)
        #plt.show()
        #if(mpu.detect()):
        #  print ("detect ..... " + str(mpu.bus_n)) 
