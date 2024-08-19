import pigpio
import time

class PigpioManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(PigpioManager, cls).__new__(cls)
            cls._instance.pi = None
            cls._instance.connect_to_pigpio()
        return cls._instance

    def connect_to_pigpio(self):
        while self.pi is None or not self.pi.connected:
            try:
                self.pi = pigpio.pi()
                if not self.pi.connected:
                    raise Exception("Could not connect to pigpiod")
            except Exception as e:
                print(f"Failed to connect to pigpiod: {e}. Retrying in 5 seconds...")
                time.sleep(5)  # Backoff before retrying
                self.pi = None

    def get_pi(self):
        if self.pi is None or not self.pi.connected:
            self.connect_to_pigpio()
        return self.pi

    def close(self):
        if self.pi:
            self.pi.stop()
            self._instance = None
