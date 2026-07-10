import os
from machine import SoftSPI, Pin
from src.libs.sdcard import SDCard

from src.config.config import SPI_BAUDRATE
from src.config.pins import PIN_SDCARD_SCK, PIN_SDCARD_MISO, PIN_SDCARD_MOSI, PIN_SDCARD_CS


class SDCardCustom:
    def __init__(
            self,
            baudrate: int = SPI_BAUDRATE,
            pin_sdcard_sck: int = PIN_SDCARD_SCK,
            pin_sdcard_miso: int = PIN_SDCARD_MISO,
            pin_sdcard_mosi: int = PIN_SDCARD_MOSI,
            pin_sdcard_cs: int = PIN_SDCARD_CS):

        spi_interface: SoftSPI = SoftSPI(
            baudrate=baudrate,
            sck=Pin(pin_sdcard_sck),
            miso=Pin(pin_sdcard_miso),
            mosi=Pin(pin_sdcard_mosi)
        )
        chip_select: Pin = Pin(pin_sdcard_cs, Pin.OUT)

        self.__sdcard_interface: SDCard = SDCard(spi_interface, chip_select)

        self.__mount()

    def __mount(self) -> None:
        try:
            os.umount("/sd")
        except OSError:
            pass

        os.mount(self.__sdcard_interface, "/sd", readonly=False)

    @staticmethod
    def path_exists(path: str) -> bool:
        try:
            os.stat(path)
            return True
        except OSError:
            return False
        except Exception:
            raise Exception(f"Unexpected error while checking path: {path}")

    @staticmethod
    def list_files(path: str) -> list:
        if not SDCardCustom.path_exists(path):
            return []

        try:
            return os.listdir(path)
        except Exception:
            raise Exception(
                f"Unexpected error while listing files in path: {path}")

