"""Provides an interface to manage Wi-Fi connections and access point creation on MicroPython."""
import time
import network


class WiFiCustom:
    """Provides an interface to manage Wi-Fi connections and access point creation on MicroPython."""

    def __init__(self):
        """Initialize the Wi-Fi interface with no active connection."""
        self.__network_interface = None

    def instantiate_connection(self, ssid: str, key: str) -> None:
        """
        Connect to an existing Wi-Fi access point.

        :param ssid: network name to connect to.
        :param key: network password.
        :return:
        """
        self.__network_interface = network.WLAN(network.STA_IF)

        self.__network_interface.active(False)
        time.sleep(0.5)
        self.__network_interface.active(True)

        self.__network_interface.connect(ssid, key)

    def get_status(self) -> int:
        """
        Return the current connection status.

        :return: network status code.
        """
        return self.__network_interface.status()

    def get_ip_configuration(self) -> tuple | None:
        """
        Return the current IP configuration if connected.

        :return: tuple with IP, subnet, gateway and DNS, or None if not connected.
        """
        if self.__network_interface.status() == network.STAT_GOT_IP:
            return self.__network_interface.ifconfig()

        return None

    def create_wpa2_access_point(
            self,
            ssid: str,
            key: str) -> None:
        """
        Create a WPA2-secured Wi-Fi access point.

        :param ssid: name of the access point.
        :param key: password for the access point.
        :return:
        """
        self.__network_interface = network.WLAN(network.AP_IF)

        self.__network_interface.active(False)
        time.sleep(0.5)
        self.__network_interface.active(True)

        self.__network_interface.config(
            essid=ssid,
            authmode=network.AUTH_WPA2_PSK,
            password=key
        )

    def create_wpa3_access_point(
            self,
            ssid: str,
            key: str) -> None:
        """
        Create a WPA3-secured Wi-Fi access point.

        :param ssid: name of the access point.
        :param key: password for the access point.
        :return:
        """
        self.__network_interface = network.WLAN(network.AP_IF)

        self.__network_interface.active(False)
        time.sleep(0.5)
        self.__network_interface.active(True)

        self.__network_interface.config(
            essid=ssid,
            authmode=network.AUTH_WPA3_PSK,
            password=key
        )

    def create_open_access_point(
            self,
            ssid: str) -> None:
        """
        Create an open Wi-Fi access point with no authentication.

        :param ssid: name of the access point.
        :return:
        """
        self.__network_interface = network.WLAN(network.AP_IF)

        self.__network_interface.active(False)
        time.sleep(0.5)
        self.__network_interface.active(True)

        self.__network_interface.config(
            essid=ssid,
            authmode=network.AUTH_OPEN
        )
