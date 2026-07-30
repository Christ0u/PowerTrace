import uasyncio as asyncio

from src.classes.SDCardCustom import SDCardCustom
from src.classes.INA228Custom import INA228Custom
from src.classes.MeasurementLogger import MeasurementLogger
from src.classes.AcquisitionService import AcquisitionService
from src.classes.WiFiCustom import WiFiCustom
from src.website import PowerTrace

from src.config.config import SSID, WEB_SERVER_PORT

wifi: WiFiCustom = WiFiCustom()
wifi.create_open_access_point(SSID)


async def main():
    sdcard = SDCardCustom()
    ina228 = INA228Custom()
    logger = MeasurementLogger(sdcard=sdcard)

    acquisition_service = AcquisitionService(ina228=ina228, logger=logger)

    PowerTrace.configure_acquisition_service(acquisition_service)

    print("Starting web server...")
    await PowerTrace.application.start_server(port=int(WEB_SERVER_PORT))

if __name__ == "__main__":
    asyncio.run(main())
