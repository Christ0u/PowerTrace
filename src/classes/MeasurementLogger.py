from src.classes.SDCardCustom import SDCardCustom
from src.classes.RingBuffer import RingBuffer
from src.config.config import MEASUREMENT_LOGGER_BUFFER_SIZE


class MeasurementLogger:
    def __init__(
            self,
            sdcard: SDCardCustom,
            file_path: str,
            buffer_size: int = MEASUREMENT_LOGGER_BUFFER_SIZE):

        self.__sdcard = sdcard
        self.__file_path = file_path
        self.__buffer = RingBuffer(buffer_size)
        self.__is_started = False

    def start(self, truncate: bool = True) -> None:
        self.__sdcard.create_file(self.__file_path, truncate=truncate)
        self.__is_started = True

    def log(self, line: str) -> None:
        if not self.__is_started:
            raise Exception("Measurement logger has not been started")

        if not self.__buffer.push(line):
            self.flush()

            if not self.__buffer.push(line):
                raise Exception("Unable to push line after buffer flush")

    def flush(self) -> None:
        if not self.__is_started:
            raise Exception("Measurement logger has not been started")

        lines: list[str] = []

        while not self.__buffer.is_empty():
            line = self.__buffer.pop()

            if line is not None:
                lines.append(line)

        self.__sdcard.append_lines(self.__file_path, lines)

    def stop(self) -> None:
        if not self.__is_started:
            return

        self.flush()
        self.__is_started = False
