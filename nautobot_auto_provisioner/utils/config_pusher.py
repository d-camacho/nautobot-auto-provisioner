import os
from nautobot.dcim.models import Device
from netmiko import (
    ConnectHandler,
    NetmikoTimeoutException,
    NetmikoAuthenticationException
)


class ConfigPusher:
    def __init__(self, device: Device, config_path: str, logger, username: str, password: str):
        """
        Initialize ConfigPusher with a device, full config file path, Nautobot logger, and credentials.
        """
        self.device = device
        self.config_path = config_path
        self.logger = logger
        self.username = username
        self.password = password

        # Validate essential fields
        if not self.device.primary_ip:
            self.logger.critical(f"{device.name} has no primary IP assigned.")
            raise ValueError(f"{device.name} missing primary IP.")

        if not self.device.platform:
            self.logger.critical(f"{device.name} has no platform assigned.")
            raise ValueError(f"{device.name} missing platform.")

        if not self.device.platform.network_driver_mappings.get("netmiko"):
            self.logger.critical(f"No Netmiko driver mapping found for platform {device.platform.name}.")
            raise ValueError(f"Missing Netmiko driver for {device.platform.name}.")

    def get_config_from_repo(self) -> str | None:
        """
        Reads the configuration file from the given full path.
        """
        self.logger.debug(f"Looking for config at: {self.config_path}")

        if not os.path.exists(self.config_path):
            self.logger.error(f"Config file not found at {self.config_path}.")
            return None

        try:
            with open(self.config_path, "r") as f:
                config = f.read()
            self.logger.info(f"Successfully loaded config for {self.device.name}")
            return config
        except IOError as e:
            self.logger.error(f"Failed to read config at {self.config_path}: {e}", exc_info=True)
            return None

    def push(self) -> bool:
        """
        Pushes the configuration to the device using Netmiko.
        """
        config = self.get_config_from_repo()
        if not config:
            self.logger.warning(f"No configuration found for {self.device.name}. Skipping push.")
            return False

        try:
            with ConnectHandler(
                device_type=self.device.platform.network_driver_mappings["netmiko"],
                host=self.device.primary_ip.host,
                username=self.username,
                password=self.password,
            ) as net_conn:
                self.logger.info(f"Sending configuration to {self.device.name}...")
                net_conn.send_config_set(config.splitlines())
                net_conn.save_config()
                self.logger.info(f"Configuration pushed and saved on {self.device.name}")
                return True

        except NetmikoAuthenticationException:
            self.logger.error(f"Authentication failed for {self.device.name}.")
        except NetmikoTimeoutException:
            self.logger.error(f"Timeout while connecting to {self.device.name}.")
        except Exception as e:
            self.logger.error(f"Unexpected error during config push to {self.device.name}: {e}", exc_info=True)

        return False
