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

    logger = MeasurementLogger(sdcard)

    logger.start(truncate=True)

    test_measurements = []

    for i in range(1000):
        timestamp = (i + 1) * 1000

        bus_voltage = 5.00 + (i % 20) * 0.01
        shunt_voltage = 0.010 + (i % 10) * 0.001
        current = 0.120 + (i % 30) * 0.005
        power = bus_voltage * current
        charge = 0.050 + i * 0.010
        energy = power * ((i + 1) * 0.1)

        test_measurements.append((
            timestamp,
            bus_voltage,
            shunt_voltage,
            current,
            power,
            charge,
            energy
        ))

    start = time.ticks_ms()
    for measurement in test_measurements:
        logger.log(
            measurement[0],
            measurement[1],
            measurement[2],
            measurement[3],
            measurement[4],
            measurement[5],
            measurement[6])
    elapsed = time.ticks_diff(time.ticks_ms(), start)
    print("log() took:", elapsed, "ms")
    logger.stop()

    # content = sdcard.read_file("/sd/logs/measurements.csv")
    # print(content)


if __name__ == "__main__":
    main()
