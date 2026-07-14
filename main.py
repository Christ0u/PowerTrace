import os
import time

from src.classes.SDCardCustom import SDCardCustom
from src.classes.INA228Custom import INA228Custom


def main():
    ina228 = INA228Custom()

    while True:
        measurements = ina228.get_measurements()

        print("---------------------------------")
        print(f"Voltage         : {measurements.bus_voltage} V")
        print(f"Shunt Voltage   : {measurements.shunt_voltage} V")
        print(f"Courant         : {measurements.current} A")
        print(f"Power           : {measurements.power} W")
        print(
            f"Charge          : {measurements.charge} C / {measurements.charge / 3600} Ah")
        print(
            f"Energy          : {measurements.energy} J / {measurements.energy / 3600} Wh")

        time.sleep_ms(500)

    sdcard: SDCardCustom = SDCardCustom()

    print(SDCardCustom.path_exists("/sd"))
    print(SDCardCustom.list_files("/sd"))

    with open("/sd/test1.txt", "a") as f:
        f.write("test\n")
    test = os.stat("/sd/test1.txt")
    print(f"test : {test.st_mode}")
    with open("/sd/test2.txt", "a") as f:
        f.write("test2\n")

    with open("/sd/test1.txt", "r") as f:
        print(f.read())
    with open("/sd/test2.txt", "r") as f:
        print(f.read())

    print(os.listdir("/sd"))


if __name__ == "__main__":
    main()
