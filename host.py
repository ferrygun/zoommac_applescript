import asyncio
from bleak import BleakScanner, BleakClient

dev_name = "mpy-uart"
_UART_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
_UART_TX_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"
_UART_RX_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"

toggle_status_audio = False
toggle_status_video = False

async def notification_handler(sender: int, data: bytearray):
    print(f"Received message from {sender}: {data.decode()}")

    if data.decode() == 'a':
        global toggle_status_audio
        toggle_status_audio = not toggle_status_audio
        if(toggle_status_audio):
            script = "start_audio.scpt"
        else:
            script = "stop_audio.scpt"
                                        
        run_applescript(script)
    
    if data.decode() == 'v':
        global toggle_status_video
        toggle_status_video = not toggle_status_video
        if(toggle_status_video):
            script = "start_video.scpt"
        else:
            script = "stop_video.scpt"
                                        
        run_applescript(script)

async def discover_device():
    scanner = BleakScanner()
    await scanner.start()
    await asyncio.sleep(3)  # Allow time for scanning
    devices = scanner.discovered_devices

    for dev in devices:
        print(dev.name)
        if dev.name == dev_name:
            print(f"Found {dev_name} at {dev.address}")
            return dev.address

    print(f"{dev_name} not found.")
    return None

async def send_message(client, message):
    try:
        await client.write_gatt_char(_UART_RX_UUID, message.encode(), True)
        print(f"Message sent: {message}")
    except Exception as e:
        print(f"Failed to send message: {str(e)}")


async def run(loop):
    while True:
        device_address = await discover_device()
        if not device_address:
            print(f"Retrying in 3 seconds...")
            await asyncio.sleep(3)
            continue

        try:
            async with BleakClient(device_address, loop=loop) as client:
                # Enable notifications on TX characteristic
                await client.start_notify(_UART_TX_UUID, notification_handler)

                print(f"Listening for incoming messages on {_UART_TX_UUID}. Press Ctrl+C to stop.")


                while True:
                    await asyncio.sleep(1)

                    # Execute AppleScript and get the output
                    script_video = "stat_video.scpt"  
                    output_video = await execute_applescript(script_video)
                    print(f"Video stat: {output_video}")
                    await send_message(client, "vid_" + output_video)

                    script_audio = "stat_audio.scpt"  
                    output_audio = await execute_applescript(script_audio)
                    print(f"Audio stat: {output_audio}")
                    await send_message(client, "aud_" + output_audio)

        except Exception as e:
            print(f"Connection failed: {str(e)}")
            print(f"Retrying in 3 seconds...")
            await asyncio.sleep(3)

import subprocess

async def execute_applescript(script_path):
    try:
        process = await asyncio.create_subprocess_exec(
            "osascript", script_path,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            print('AppleScript executed successfully')
            return stdout.decode().strip()
        else:
            print(f"Error executing AppleScript: {stderr.decode().strip()}")
            return None

    except Exception as e:
        print(f"Error executing AppleScript: {str(e)}")
        return None


def run_applescript(script_path):
    try:
        subprocess.run(["osascript", script_path], check=True)
        print('run script')
    except subprocess.CalledProcessError as e:
        print(f"Error executing AppleScript: {e}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run(loop))
