from src.classes.SDCardCustom import SDCardCustom
from src.classes.RingBuffer import RingBuffer
from src.config.config import MEASUREMENT_LOGGER_BUFFER_SIZE, MEASUREMENT_LOGGER_DECIMAL_PRECISION, MEASUREMENT_LOGGER_LOGS_DIRECTORY, SDCARD_ROOT_PATH


class MeasurementLogger:
    def __init__(
        self,
        sdcard: SDCardCustom,
        file_path: str = SDCARD_ROOT_PATH +
        MEASUREMENT_LOGGER_LOGS_DIRECTORY +
        "/measurements.csv",
            buffer_size: int = MEASUREMENT_LOGGER_BUFFER_SIZE):

        self.__sdcard = sdcard
        self.__file_path = file_path
        self.__buffer = RingBuffer(buffer_size)
        self.__is_started = False

    @staticmethod
    def __get_directory_path(file_path: str) -> str:
        parts = file_path.split("/")

        if len(parts) <= 2:
            return SDCARD_ROOT_PATH

        return "/".join(parts[:-1])

    @staticmethod
    def __format_float(
            value: float | int,
            decimals: int = MEASUREMENT_LOGGER_DECIMAL_PRECISION) -> str:

        return f"{value:.{decimals}f}"

    @staticmethod
    def __build_csv_line(timestamp: int,
                         bus_voltage: float | int,
                         current: float | int) -> str:

        result = ",".join([
            str(timestamp),
            MeasurementLogger.__format_float(bus_voltage),
            MeasurementLogger.__format_float(current)
        ])

        return result

    def start(self, truncate: bool = True) -> None:

        directory_path = self.__get_directory_path(self.__file_path)
        self.__sdcard.create_directory(directory_path)
        self.__sdcard.create_file(self.__file_path, truncate=truncate)

        if truncate or self.__sdcard.get_file_size(self.__file_path) == 0:
            self.__sdcard.append_line(
                self.__file_path,
                "timestamp_ms, bus_voltage_V, current_A")

        self.__is_started = True

    def log(self,
            timestamp: int,
            bus_voltage: float | int,
            current: float | int) -> None:
        if not self.__is_started:
            raise Exception("Measurement logger has not been started")

        line = self.__build_csv_line(
            timestamp,
            bus_voltage,
            current)

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
