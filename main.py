import os
import time
from machine import I2C, Pin, SPI, SoftSPI

from src.libs.ina228 import INA228
from src.classes.SDCardCustom import SDCardCustom


def main():
    # i2c = I2C(id=1, scl=Pin(6), sda=Pin(5), freq=400_000)
    #
    # sensor = INA228(i2c=i2c, shunt_ohms=0.100, max_expected_current=1)
    # sensor.configure()
    # # print(f"shunt_ohms = {sensor._shunt_ohms}")
    #
    # while True:
    #     voltage = sensor.get_vbus_voltage()
    #     shunt_voltage = sensor.get_shunt_voltage()
    #     current = sensor.get_current()
    #     power = sensor.get_power()
    #     charge = sensor.get_charge()
    #     energy = sensor.get_energy()
    #
    #     print("---------------------------------")
    #
    #     print(f"Voltage         : {voltage} V")
    #     print(f"Shunt Voltage   : {shunt_voltage} V")
    #     print(f"Courant         : {current} A")
    #     print(f"Power           : {power} W")
    #     print(f"Charge          : {charge} C / {charge / 3600} Ah")
    #     print(f"Energy          : {energy} J / {energy / 3600} Wh")
    #
    #     time.sleep_ms(500)

    sdcard: SDCardCustom = SDCardCustom()

    print(SDCardCustom.path_exists("/sd"))
    print(SDCardCustom.list_files("/sd"))

    # with open("/sd/test1.txt", "a") as f:
    #     f.write("test\n")
    # test = os.stat("/sd/test1.txt")
    # print(f"test : {test.st_mode}")
    # with open("/sd/test2.txt", "a") as f:
    #     f.write("test2\n")
    #
    # with open("/sd/test1.txt", "r") as f:
    #     print(f.read())
    # with open("/sd/test2.txt", "r") as f:
    #     print(f.read())

    # print(os.listdir("/sd"))


if __name__ == "__main__":
    main()
