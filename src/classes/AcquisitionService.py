"""Provides an asynchronous acquisition service for power measurements."""
import time
import uasyncio as asyncio

from src.classes.INA228Custom import INA228Custom
from src.classes.MeasurementLogger import MeasurementLogger

from src.config.config import MIN_SAMPLE_PERIOD_MS, MAX_SAMPLE_PERIOD_MS


class AcquisitionService:
    """Provides an asynchronous acquisition service for power measurements."""

    STATUS_IDLE = "idle"
    STATUS_RECORDING = "recording"
    STATUS_STOPPING = "stopping"
    STATUS_ERROR = "error"

    def __init__(
            self,
            logger: MeasurementLogger,
            ina228: INA228Custom | None = None,
            sample_period_ms: int = 200):
        """
        Initialize the acquisition service with logger and sampling configuration.

        :param logger: MeasurementLogger instance for data persistence.
        :param ina228: INA228Custom instance for measurements, or None to create later.
        :param sample_period_ms: time between consecutive samples in milliseconds.
        :return:
        """
        self.__ina228 = ina228
        self.__logger = logger
        self.__sample_period_ms = sample_period_ms

        self.__status = self.STATUS_IDLE
        self.__task = None
        self.__stop_requested = False
        self.__last_error = None
        self.__last_start_timestamp_ms = None
        self.__last_stop_timestamp_ms = None
        self.__last_recorded_samples = 0
        self.__duration_ms = None

        self.__ina228_config = {
            "adc_range": 0,
            "v_bus_conversion_time": 5,
            "v_shunt_conversion_time": 5,
            "avg": 3,
            "current_lsb": None,
        }

    def set_sample_period_ms(self, sample_period_ms: int) -> None:
        """
        Set the sampling period within allowed bounds.

        :param sample_period_ms: new sampling period in milliseconds.
        :return:
        """
        if sample_period_ms < MIN_SAMPLE_PERIOD_MS:
            raise ValueError("sample_period_ms is too small")

        if sample_period_ms > MAX_SAMPLE_PERIOD_MS:
            raise ValueError("sample_period_ms is too large")

        self.__sample_period_ms = sample_period_ms

    def __create_ina228(self) -> INA228Custom:
        """
        Create a new INA228Custom instance using the current configuration.

        :return: configured INA228Custom instance.
        """
        return INA228Custom(
            adc_range=self.__ina228_config["adc_range"],
            v_bus_conversion_time=self.__ina228_config["v_bus_conversion_time"],
            v_shunt_conversion_time=self.__ina228_config["v_shunt_conversion_time"],
            avg=self.__ina228_config["avg"],
            current_lsb=self.__ina228_config["current_lsb"],
        )

    def set_ina228_config(self, config: dict) -> None:
        """
        Update the INA228 configuration parameters.

        :param config: dictionary with INA228 configuration values.
        :return:
        """
        if config is None:
            return

        default_config = {
            "adc_range": 0,
            "v_bus_conversion_time": 5,
            "v_shunt_conversion_time": 5,
            "avg": 3,
            "current_lsb": None,
        }

        default_config.update(config)
        self.__ina228_config = default_config

    async def start(
            self,
            duration_ms: int | None = 30_000,
            truncate: bool = True) -> None:
        """
        Start the acquisition task asynchronously.

        :param duration_ms: total acquisition duration in milliseconds, or None for unlimited.
        :param truncate: if True, overwrite existing log file; if False, append to it.
        :return:
        """
        if self.__task is not None and not self.__task.done():
            raise Exception("Acquisition is already running")

        self.__ina228 = self.__create_ina228()

        self.__stop_requested = False
        self.__last_error = None
        self.__last_recorded_samples = 0
        self.__last_start_timestamp_ms = time.ticks_ms()
        self.__last_stop_timestamp_ms = None
        self.__duration_ms = duration_ms
        self.__status = self.STATUS_RECORDING

        file_path = self.__logger.generate_file_path()
        self.__logger.set_file_path(file_path)

        self.__task = asyncio.create_task(
            self.__run(duration_ms=duration_ms, truncate=truncate)
        )

    async def __run(self, duration_ms: int | None, truncate: bool) -> None:
        """
        Run the main acquisition loop with precise timing control.

        :param duration_ms: total acquisition duration in milliseconds, or None for unlimited.
        :param truncate: if True, overwrite existing log file; if False, append to it.
        :return:
        """
        self.__logger.start(truncate=truncate)

        start_time = time.ticks_ms()  # 12
        next_deadline = start_time  # 12

        try:
            while not self.__stop_requested:
                now = time.ticks_ms()  # 12
                remaining = time.ticks_diff(next_deadline, now)

                if remaining > 0:
                    await asyncio.sleep_ms(remaining)
                    continue

                elapsed = time.ticks_diff(next_deadline, start_time)

                if duration_ms is not None and elapsed >= duration_ms:
                    break

                bus_voltage = self.__ina228.get_bus_voltage()
                current = self.__ina228.get_current()

                self.__logger.log(
                    timestamp=elapsed,
                    bus_voltage=bus_voltage,
                    current=current
                )

                self.__last_recorded_samples += 1

                next_deadline = time.ticks_add(
                    next_deadline, self.__sample_period_ms)

                now = time.ticks_ms()
                while time.ticks_diff(
                        now, next_deadline) >= self.__sample_period_ms:
                    next_deadline = time.ticks_add(
                        next_deadline, self.__sample_period_ms
                    )

        except asyncio.CancelledError:
            self.__stop_requested = True
            raise

        except Exception as error:
            self.__last_error = str(error)
            self.__status = self.STATUS_ERROR
            raise

        finally:
            if self.__status != self.STATUS_ERROR:
                self.__status = self.STATUS_STOPPING

            try:
                self.__logger.stop()
            finally:
                self.__last_stop_timestamp_ms = time.ticks_ms()

                if self.__status != self.STATUS_ERROR:
                    self.__status = self.STATUS_IDLE

                self.__task = None

    async def stop(self) -> None:
        """
        Request graceful termination of the acquisition task.

        :return:
        """
        if self.__task is None:
            return

        self.__stop_requested = True

        try:
            await self.__task
        except asyncio.CancelledError:
            pass

    def is_recording(self) -> bool:
        """
        Check if the acquisition is currently recording.

        :return: True if status is recording, False otherwise.
        """
        return self.__status == self.STATUS_RECORDING

    def get_status(self) -> dict:
        """
        Return the current acquisition status and metrics.

        :return: dictionary with status, timing, and configuration information.
        """
        now = time.ticks_ms()

        duration_ms = 0
        if self.__last_start_timestamp_ms is not None:
            if self.__status == self.STATUS_RECORDING:
                duration_ms = time.ticks_diff(
                    now, self.__last_start_timestamp_ms)
            elif self.__last_stop_timestamp_ms is not None:
                duration_ms = time.ticks_diff(
                    self.__last_stop_timestamp_ms,
                    self.__last_start_timestamp_ms
                )

        return {
            "status": self.__status,
            "is_recording": self.is_recording(),
            "stop_requested": self.__stop_requested,
            "sample_period_ms": self.__sample_period_ms,
            "target_duration_ms": self.__duration_ms,
            "recorded_samples": self.__last_recorded_samples,
            "duration_ms": duration_ms,
            "last_error": self.__last_error,
            "ina228_config": self.__ina228_config
        }
