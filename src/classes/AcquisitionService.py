import time
import uasyncio as asyncio

from src.classes.INA228Custom import INA228Custom
from src.classes.MeasurementLogger import MeasurementLogger

from src.config.config import MIN_SAMPLE_PERIOD_MS, MAX_SAMPLE_PERIOD_MS


class AcquisitionService:
    STATUS_IDLE = "idle"
    STATUS_RECORDING = "recording"
    STATUS_STOPPING = "stopping"
    STATUS_ERROR = "error"

    def __init__(
            self,
            ina228: INA228Custom,
            logger: MeasurementLogger,
            sample_period_ms: int = 200):

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

    def set_sample_period_ms(self, sample_period_ms: int) -> None:
        if sample_period_ms < MIN_SAMPLE_PERIOD_MS:
            raise ValueError("sample_period_ms is too small")

        if sample_period_ms > MAX_SAMPLE_PERIOD_MS:
            raise ValueError("sample_period_ms is too large")

        self.__sample_period_ms = sample_period_ms

    async def start(
            self,
            duration_ms: int | None = 30_000,
            truncate: bool = True) -> None:
        if self.__task is not None and not self.__task.done():
            raise Exception("Acquisition is already running")

        self.__stop_requested = False
        self.__last_error = None
        self.__last_recorded_samples = 0
        self.__last_start_timestamp_ms = time.ticks_ms()
        self.__last_stop_timestamp_ms = None
        self.__duration_ms = duration_ms
        self.__status = self.STATUS_RECORDING

        self.__task = asyncio.create_task(
            self.__run(duration_ms=duration_ms, truncate=truncate)
        )

    async def __run(self, duration_ms: int | None, truncate: bool) -> None:
        self.__logger.start(truncate=truncate)
        start_time = time.ticks_ms()

        try:
            while not self.__stop_requested:
                now = time.ticks_ms()
                elapsed = time.ticks_diff(now, start_time)

                if duration_ms is not None and elapsed >= duration_ms:
                    break

                measurements = self.__ina228.get_measurements()

                self.__logger.log(
                    timestamp=elapsed,
                    bus_voltage=measurements.bus_voltage,
                    current=measurements.current
                )

                self.__last_recorded_samples += 1
                await asyncio.sleep_ms(self.__sample_period_ms)

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
        if self.__task is None:
            return

        self.__stop_requested = True

        try:
            await self.__task
        except asyncio.CancelledError:
            pass

    def is_recording(self) -> bool:
        return self.__status == self.STATUS_RECORDING

    def get_status(self) -> dict:
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
            "last_error": self.__last_error
        }
