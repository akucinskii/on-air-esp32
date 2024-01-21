import asyncio
from bleak import BleakScanner, BleakClient
import cv2
import numpy as np
import pyautogui
import time

class MicrophoneChecker:
    def __init__(self, icon_path='./microphone_icon.png'):
        self.icon_path = icon_path

    def check_microphone(self):
        # Take screenshot
        print("Taking screenshot...")
        screenshot = pyautogui.screenshot()

        # Convert the screenshot to a numpy array and then to grayscale
        screenshot_np = np.array(screenshot)
        gray_screenshot = cv2.cvtColor(screenshot_np, cv2.COLOR_BGR2GRAY)

        # Load the microphone icon image
        microphone_icon = cv2.imread(self.icon_path, 0)

        # Use template matching to find the microphone icon in the screenshot
        print("Checking microphone...")
        res = cv2.matchTemplate(gray_screenshot, microphone_icon, cv2.TM_CCOEFF_NORMED)
        threshold = 0.8
        loc = np.where(res >= threshold)

    
        # If the microphone icon is found in the screenshot, the microphone is in use
        if len(loc[0]) > 0:
            print("Test result: Microphone is in use")
            return True
        print("Test result: Microphone is not in use")
        return False
    
class BluetoothConnector:
    def __init__(self, device_name="MyESP32"):
        self.device_name = device_name

    async def connect(self):
        scanner = BleakScanner()
        devices = await scanner.discover()
        for device in devices:
            print(device)

        my_device = None
        for device in devices:
            if device.name == self.device_name:
                my_device = device
                break

        if my_device:
            print(f"Connecting to {my_device}")
            client = BleakClient(my_device)

            try:
                await client.connect()
                print(f"Connected: {client.is_connected}")

                services = await client.get_services()
                for service in services:
                    print(f"Service: {service.uuid}")
                    for char in service.characteristics:
                        print(f"Characteristic: {char.uuid}")
                # Check microphone and send the status to ESP device
                mic_checker = MicrophoneChecker()
                while True:
                    check = mic_checker.check_microphone()
                    data = "MICROPHONE ON 1" if check else "MICROPHONE OFF 0"
                    data = data.encode()  # Convert string to bytes
                    print(f"Sending data: {bytearray(data)}")
                    # This True param is important, without it the data will not be sent. Nice docs ¯\_(ツ)_/¯
                    await client.write_gatt_char("beb5483e-36e1-4688-b7f5-ea07361b26a8", bytearray(data), True)
                    value = await client.read_gatt_char("beb5483e-36e1-4688-b7f5-ea07361b26a8")
                    print(f"Received data: {value}")


                    time.sleep(5)  # Wait for 5 seconds before sending the next data

            except Exception as e:
                print(f"Failed to connect: {e}")



bluetooth_connector = BluetoothConnector()
loop = asyncio.get_event_loop()
loop.run_until_complete(bluetooth_connector.connect())
loop.close()