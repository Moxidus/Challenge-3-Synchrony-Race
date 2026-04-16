import asyncio
import re
import threading
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from bleak import BleakClient, BleakScanner

# --- Configuration ---
DEVICE_NAME = "Makeblock_LE001b1068770a"
RX_UUID = "0000ffe2-0000-1000-8000-00805f9b34fb"
TX_UUID = "0000ffe3-0000-1000-8000-00805f9b34fb"

# Global data storage for the plot
x_data, y_data = [0], [0]
data_lock = threading.Lock()

# Regex to find "X: 12.3 Y: 45.6" in the incoming string
POS_REGEX = re.compile(r"X:\s*([-+]?\d*\.\d+|\d+)\s*Y:\s*([-+]?\d*\.\d+|\d+)")

def on_message(sender, data: bytearray):
    text = data.decode("utf-8", errors="replace").strip()
    print(f"RX> {text}")
    
    # Parse coordinates
    match = POS_REGEX.search(text)
    if match:
        new_x = float(match.group(1))
        new_y = float(match.group(2))
        with data_lock:
            x_data.append(new_x)
            y_data.append(new_y)

async def run_ble():
    """Main BLE Loop"""
    print(f"Scanning for {DEVICE_NAME}...")
    device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=10.0)
    if not device:
        print("Device not found")
        return

    async with BleakClient(device) as client:
        print(f"Connected to {device.address}")
        await client.start_notify(RX_UUID, on_message)
        
        try:
            await client.write_gatt_char(TX_UUID, b"start track\n", response=False)
            await asyncio.sleep(0.5) 
        except Exception as e:
            print(f"BLE Error: {e}")


        while True:
            # Send 'getpos' command every 500ms
            try:
                await client.write_gatt_char(TX_UUID, b"getpos\n", response=False)
                await asyncio.sleep(0.5) 
            except Exception as e:
                print(f"BLE Error: {e}")
                break

def start_ble_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_until_complete(run_ble())

# --- Plotting Section ---
fig, ax = plt.subplots()
line, = ax.plot([], [], 'bo-', label="Robot Path")
point, = ax.plot([], [], 'ro', label="Current Position") # Highlight current pos

def init():
    ax.set_xlim(-7000, 10000) # Adjust based on your robot's workspace
    ax.set_ylim(-7000, 10000)
    ax.set_xlabel("X Position")
    ax.set_ylabel("Y Position")
    ax.grid(True)
    ax.legend()
    return line, point

def update(frame):
    with data_lock:
        if x_data:
            line.set_data(x_data, y_data)
            point.set_data([x_data[-1]], [y_data[-1]])
            
            # Optional: Auto-scale axes
            # ax.relim()
            # ax.autoscale_view()
    return line, point

if __name__ == "__main__":
    # 1. Start BLE in a background thread
    new_loop = asyncio.new_event_loop()
    t = threading.Thread(target=start_ble_loop, args=(new_loop,), daemon=True)
    t.start()

    # 2. Start Matplotlib Animation in the main thread
    ani = FuncAnimation(fig, update, init_func=init, interval=100, blit=True)
    plt.show()