from machine import I2C, Pin
from src.libs.ina228 import INA228

from src.config.config import I2C_FREQUENCY, INA_228_MAX_EXPECTED_CURRENT, INA_228_SHUNT_RESISTANCE
from src.config.pins import PIN_INA228_SCL, PIN_INA228_SDA


class INA228Custom:
    def __init__(
            self,
            pin_ina228_sda: int = PIN_INA228_SDA,
            pin_ina228_scl: int = PIN_INA228_SCL,
            frequency: int = I2C_FREQUENCY,
            shunt_resistance: float | int = INA_228_SHUNT_RESISTANCE,
            max_expected_current: float | int = INA_228_MAX_EXPECTED_CURRENT):

        i2c = I2C(
            id=1,
            scl=Pin(pin_ina228_scl),
            sda=Pin(pin_ina228_sda),
            freq=frequency)

        self.__ina228_interface = INA228(
            i2c=i2c,
            shunt_ohms=shunt_resistance,
            max_expected_current=max_expected_current)

        self.__ina228_interface.configure()

    def get_bus_voltage(self) -> float | int:
        return self.__ina228_interface.get_vbus_voltage()

    def get_shunt_voltage(self) -> float | int:
        return self.__ina228_interface.get_shunt_voltage()

    def get_current(self) -> float | int:
        return self.__ina228_interface.get_current()

    def get_power(self) -> float | int:
        return self.__ina228_interface.get_power()

    def get_charge(self) -> float | int:
        return self.__ina228_interface.get_charge()

    def get_energy(self) -> float | int:
        return self.__ina228_interface.get_energy()

    def get_internal_temperature(self) -> float | int:
        return self.__ina228_interface.get_temp_voltage()
