"""Provides an interface to manage SD card operations on MicroPython."""
import os
from machine import SPI, Pin
from src.libs.sdcard import SDCard

from src.config.config import SPI_BAUDRATE, SPI_ID
from src.config.pins import PIN_SDCARD_SCK, PIN_SDCARD_MISO, PIN_SDCARD_MOSI, PIN_SDCARD_CS


class SDCardCustom:
    """Provides an interface to manage SD card operations on MicroPython."""

    def __init__(
            self,
            spi_id: int = SPI_ID,
            baudrate: int = SPI_BAUDRATE,
            pin_sdcard_sck: int = PIN_SDCARD_SCK,
            pin_sdcard_miso: int = PIN_SDCARD_MISO,
            pin_sdcard_mosi: int = PIN_SDCARD_MOSI,
            pin_sdcard_cs: int = PIN_SDCARD_CS):
        """
        Initialize the SD card interface with SPI configuration and mount the card.

        :param spi_id: SPI bus identifier.
        :param baudrate: SPI communication baudrate.
        :param pin_sdcard_sck: GPIO pin for SPI clock.
        :param pin_sdcard_miso: GPIO pin for SPI MISO.
        :param pin_sdcard_mosi: GPIO pin for SPI MOSI.
        :param pin_sdcard_cs: GPIO pin for chip select.
        :return:
        """
        spi_interface: SPI = SPI(
            spi_id,
            baudrate=baudrate,
            polarity=0,
            phase=0,
            bits=8,
            firstbit=SPI.MSB,
            sck=Pin(pin_sdcard_sck),
            miso=Pin(pin_sdcard_miso),
            mosi=Pin(pin_sdcard_mosi)
        )

        chip_select: Pin = Pin(pin_sdcard_cs, Pin.OUT)
        chip_select.value(1)

        self.__sdcard_interface: SDCard = SDCard(spi_interface, chip_select)

        self.__mount()

    def __mount(self) -> None:
        """
        Mount the SD card at /sd, unmounting first if already mounted.

        :return:
        """
        try:
            os.umount("/sd")
        except OSError:
            pass

        os.mount(self.__sdcard_interface, "/sd", readonly=False)

    @staticmethod
    def path_exists(path: str) -> bool:
        """
        Check if a path exists on the SD card.

        :param path: path to check.
        :return: True if path exists, False otherwise.
        """
        try:
            os.stat(path)
            return True
        except OSError:
            return False
        except Exception:
            raise Exception(f"Unexpected error while checking path: {path}")

    @staticmethod
    def list_files(path: str) -> list:
        """
        List all files and directories in a given path.

        :param path: directory path to list.
        :return: list of file and directory names, or empty list if path does not exist.
        """
        if not SDCardCustom.path_exists(path):
            return []

        try:
            return os.listdir(path)
        except Exception:
            raise Exception(
                f"Unexpected error while listing files in path: {path}")

    @staticmethod
    def create_directory(path: str) -> None:
        """
        Create a new directory if it does not already exist.

        :param path: directory path to create.
        :return:
        """
        if SDCardCustom.path_exists(path):
            return

        try:
            os.mkdir(path)
        except Exception:
            raise Exception(
                f"Unexpected error while creating directory: {path}")

    @staticmethod
    def create_file(path: str, truncate: bool = False) -> None:
        """
        Create a new file, optionally truncating it if it already exists.

        :param path: file path to create.
        :param truncate: if True, truncate existing file; if False, skip if file exists.
        :return:
        """
        if SDCardCustom.path_exists(path) and not truncate:
            return

        try:
            with open(path, "w") as file:
                file.write("")
        except Exception:
            raise Exception(f"Unexpected error while creating file: {path}")

    @staticmethod
    def append_line(path: str, line: str) -> None:
        """
        Append a single line to a file.

        :param path: file path to append to.
        :param line: line content to append.
        :return:
        """
        try:
            with open(path, "a") as file:
                file.write(line + "\n")
        except Exception:
            raise Exception(
                f"Unexpected error while appending line to file: {path}")

    @staticmethod
    def append_lines(path: str, lines: list) -> None:
        """
        Append multiple lines to a file.

        :param path: file path to append to.
        :param lines: list of lines to append.
        :return:
        """
        if not lines:
            return

        try:
            with open(path, "a") as file:
                for line in lines:
                    file.write(str(line) + "\n")
        except Exception:
            raise Exception(
                f"Unexpected error while appending lines to file: {path}")

    @staticmethod
    def read_file(path: str) -> str:
        """
        Read the entire content of a file.

        :param path: file path to read.
        :return: file content as string.
        """
        if not SDCardCustom.path_exists(path):
            raise OSError(f"File does not exist: {path}")

        try:
            with open(path, "r") as file:
                return file.read()
        except Exception:
            raise Exception(f"Unexpected error while reading file: {path}")

    @staticmethod
    def delete_file(path: str) -> None:
        """
        Delete a file if it exists.

        :param path: file path to delete.
        :return:
        """
        if not SDCardCustom.path_exists(path):
            return

        try:
            os.remove(path)
        except Exception:
            raise Exception(f"Unexpected error while deleting file: {path}")

    @staticmethod
    def delete_directory(path: str) -> None:
        """
        Delete a directory if it exists.

        :param path: directory path to delete.
        :return:
        """
        if not SDCardCustom.path_exists(path):
            return

        try:
            os.rmdir(path)
        except Exception:
            raise Exception(
                f"Unexpected error while deleting directory: {path}")

    @staticmethod
    def get_file_size(path: str) -> int:
        """
        Get the size of a file in bytes.

        :param path: file path to check.
        :return: file size in bytes, or 0 if file does not exist.
        """
        if not SDCardCustom.path_exists(path):
            return 0

        try:
            return os.stat(path)[6]
        except Exception:
            raise Exception(
                f"Unexpected error while getting file size: {path}")
