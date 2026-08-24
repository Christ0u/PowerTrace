"""Provides a measurement logging system for binary data storage on SD card."""
import time
import os
import ubinascii

from src.classes.SDCardCustom import SDCardCustom
from src.classes.RingBuffer import RingBuffer
from src.config.config import MEASUREMENT_LOGGER_BUFFER_SIZE, SDCARD_ROOT_PATH, MEASUREMENT_LOGGER_LOGS_DIRECTORY, RECORD_FORMAT


class MeasurementLogger:
    """Provides a measurement logging system for binary data storage on SD card."""

    def __init__(
            self,
            sdcard: SDCardCustom,
            file_path: str | None = None,
            buffer_size: int = MEASUREMENT_LOGGER_BUFFER_SIZE):
        """
        Initialize the measurement logger with SD card interface and buffer configuration.

        :param sdcard: SDCardCustom instance for file operations.
        :param file_path: path to the measurement log file, or None to set later.
        :param buffer_size: maximum number of records to buffer before flushing to disk.
        :return:
        """
        self.__sdcard = sdcard
        self.__file_path = file_path
        self.__buffer = RingBuffer(
            capacity=buffer_size,
            record_format=RECORD_FORMAT)
        self.__is_started = False
        self.__file = None

    def set_file_path(self, file_path: str) -> None:
        """
        Set the file path for measurement logging.

        :param file_path: path to the measurement log file.
        :return:
        """
        self.__file_path = file_path

    def get_file_path(self) -> str | None:
        """
        Return the current measurement file path.

        :return: file path string, or None if not set.
        """
        return self.__file_path

    @staticmethod
    def __generate_id(n_bytes: int = 16) -> str:
        """
        Generate a random hexadecimal identifier.

        :param n_bytes: number of random bytes to generate.
        :return: hexadecimal string representation of the random bytes.
        """
        return ubinascii.hexlify(os.urandom(n_bytes)).decode()

    @staticmethod
    def generate_file_path() -> str:
        """
        Generate a unique file path for a new measurement log file.

        :return: full file path including timestamp and random identifier.
        """
        return (f"{SDCARD_ROOT_PATH}"
                f"{MEASUREMENT_LOGGER_LOGS_DIRECTORY}"
                f"/measurements_"
                f"{time.ticks_ms()}_"
                f"{MeasurementLogger.__generate_id()}"
                f".bin")

    @staticmethod
    def __get_directory_path(file_path: str) -> str:
        """
        Extract the directory path from a given file path.

        :param file_path: full file path to parse.
        :return: directory path, or SD card root if no directory component.
        """
        parts = file_path.split("/")

        if len(parts) <= 2:
            return SDCARD_ROOT_PATH

        return "/".join(parts[:-1])

    def start(self, truncate: bool = True) -> None:
        """
        Start the measurement logger by opening the log file for writing.

        :param truncate: if True, overwrite existing file; if False, append to it.
        :return:
        """
        if self.__is_started:
            raise Exception("Measurement logger is already started")

        if self.__file_path is None:
            raise Exception("No measurement file path defined.")

        directory_path = self.__get_directory_path(self.__file_path)
        self.__sdcard.create_directory(directory_path)

        if truncate:
            mode = "wb"
        else:
            mode = "ab"

        self.__file = open(self.__file_path, mode)

        self.__buffer.clear()

        self.__is_started = True

    def log(self,
            timestamp: int,
            bus_voltage: float | int,
            current: float | int) -> None:
        """
        Log a single measurement record to the buffer.

        :param timestamp: timestamp of the measurement.
        :param bus_voltage: bus voltage value.
        :param current: current value.
        :return:
        """
        if not self.__is_started:
            raise Exception("Measurement logger has not been started")

        if not self.__buffer.push(
                int(timestamp),
                float(bus_voltage),
                float(current)):
            self.flush()

            if not self.__buffer.push(
                    int(timestamp),
                    float(bus_voltage),
                    float(current)):
                raise Exception("Unable to push record after buffer flush")

    def flush(self) -> None:
        """
        Flush all buffered records to the SD card file.

        :return:
        """
        if not self.__is_started:
            raise Exception("Measurement logger has not been started")

        if self.__file is None:
            raise Exception("No measurement file is open")

        while not self.__buffer.is_empty():
            chunk = self.__buffer.pop_bytes()

            if chunk is not None:
                self.__file.write(chunk)

        self.__file.flush()

    def stop(self) -> None:
        """
        Stop the measurement logger and close the log file.

        :return:
        """
        if not self.__is_started:
            return

        try:
            self.flush()
        finally:
            if self.__file is not None:
                self.__file.close()
                self.__file = None

            self.__is_started = False
