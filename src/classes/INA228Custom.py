"""Provides an interface to read electrical measurements from the INA228 power monitoring module."""
from machine import I2C, Pin
from src.libs.ina228 import INA228

from src.config.config import I2C_FREQUENCY, INA_228_MAX_EXPECTED_CURRENT, INA_228_SHUNT_RESISTANCE
from src.config.pins import PIN_INA228_SCL, PIN_INA228_SDA


class INA228Custom:
    """Provides an interface to read electrical measurements from the INA228 power monitoring module."""

    def __init__(
            self,
            pin_ina228_sda: int = PIN_INA228_SDA,
            pin_ina228_scl: int = PIN_INA228_SCL,
            frequency: int = I2C_FREQUENCY,
            shunt_resistance: float | int = INA_228_SHUNT_RESISTANCE,
            max_expected_current: float | int = INA_228_MAX_EXPECTED_CURRENT,
            adc_range: int = 0,
            v_bus_conversion_time: int = 0x05,
            v_shunt_conversion_time: int = 0x05,
            avg: int = 0x03,
            current_lsb: float | int | None = None):
        """
        Initialize the INA228 power monitor with I2C configuration and calibration parameters.

        :param pin_ina228_sda: GPIO pin for I2C data line.
        :param pin_ina228_scl: GPIO pin for I2C clock line.
        :param frequency: I2C bus frequency in Hz.
        :param shunt_resistance: shunt resistor value in ohms.
        :param max_expected_current: maximum expected current in amperes.
        :param adc_range: ADC voltage range selection.
        :param v_bus_conversion_time: bus voltage conversion time setting.
        :param v_shunt_conversion_time: shunt voltage conversion time setting.
        :param avg: number of samples to average.
        :param current_lsb: current LSB value for calibration, or None for auto-calculation.
        :return:
        """
        i2c = I2C(
            id=1,
            scl=Pin(pin_ina228_scl),
            sda=Pin(pin_ina228_sda),
            freq=frequency)

        self.__ina228_interface = INA228(
            i2c=i2c,
            shunt_ohms=shunt_resistance,
            max_expected_current=max_expected_current,
            adc_range=adc_range,
            v_bus_conversion_time=v_bus_conversion_time,
            v_shunt_conversion_time=v_shunt_conversion_time,
            avg=avg,
            current_lsb=current_lsb)

        self.__ina228_interface.configure()

    def get_bus_voltage(self) -> float | int:
        """
        Return the measured bus voltage.

        :return: bus voltage in volts.
        """
        return self.__ina228_interface.get_vbus_voltage()

    def get_shunt_voltage(self) -> float | int:
        """
        Return the measured shunt voltage.

        :return: shunt voltage in volts.
        """
        return self.__ina228_interface.get_shunt_voltage()

    def get_current(self) -> float | int:
        """
        Return the measured current.

        :return: current in amperes.
        """
        return self.__ina228_interface.get_current()

    def get_power(self) -> float | int:
        """
        Return the calculated power.

        :return: power in watts.
        """
        return self.__ina228_interface.get_power()

    def get_charge(self) -> float | int:
        """
        Return the accumulated charge.

        :return: charge in coulombs.
        """
        return self.__ina228_interface.get_charge()

    def get_energy(self) -> float | int:
        """
        Return the accumulated energy.

        :return: energy in joules.
        """
        return self.__ina228_interface.get_energy()

    def get_internal_temperature(self) -> float | int:
        """
        Return the internal temperature of the INA228.

        :return: temperature in degrees Celsius.
        """
        return self.__ina228_interface.get_temp_voltage()
