import os
import time

from src.classes.SDCardCustom import SDCardCustom
from src.classes.INA228Custom import INA228Custom
from src.classes.MeasurementLogger import MeasurementLogger


def main():
    # ina228 = INA228Custom()
    # sdcard: SDCardCustom = SDCardCustom()
    #
    # while True:
    #     measurements = ina228.get_measurements()
    #
    #     print("---------------------------------")
    #     print(f"Voltage         : {measurements.bus_voltage} V")
    #     print(f"Shunt Voltage   : {measurements.shunt_voltage} V")
    #     print(f"Courant         : {measurements.current} A")
    #     print(f"Power           : {measurements.power} W")
    #     print(
    #         f"Charge          : {measurements.charge} C / {measurements.charge / 3600} Ah")
    #     print(
    #         f"Energy          : {measurements.energy} J / {measurements.energy / 3600} Wh")
    #
    #     time.sleep_ms(500)

    sdcard = SDCardCustom()
    logger = MeasurementLogger(sdcard, "/sd/test_log.txt", buffer_size=3)

    logger.start(truncate=True)
    logger.log("10,0.12,0.45")
    logger.log("20,0.15,0.51")
    logger.log("30,0.18,0.63")
    logger.log("40,0.20,0.70")
    logger.log("50,0.24,0.82")

    logger.stop()

    print(sdcard.read_file("/sd/test_log.txt"))


if __name__ == "__main__":
    main()
