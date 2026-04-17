import asyncio
import re
import threading
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.animation import FuncAnimation
from matplotlib.widgets import TextBox, Button
from bleak import BleakClient, BleakScanner
from collections import deque
import time

# --- Configuration ---
# DEVICE_NAME = "Makeblock_LE001b1068770a" # daughter ship
DEVICE_NAME = "Makeblock_LE001b1069005f" # mother ship
RX_UUID = "0000ffe2-0000-1000-8000-00805f9b34fb"
TX_UUID = "0000ffe3-0000-1000-8000-00805f9b34fb"

# Global data
x_data, y_data = [0], [0]
data_lock = threading.Lock()
log_messages = deque(maxlen=12)   # rolling log shown in the plot window
log_lock = threading.Lock()

ble_client = None
ble_loop = None
write_lock = None

POS_REGEX = re.compile(r"X:\s*([-+]?\d*\.\d+|\d+)\s*Y:\s*([-+]?\d*\.\d+|\d+)")

def add_log(msg: str):
    ts = time.strftime("%H:%M:%S")
    with log_lock:
        log_messages.append(f"[{ts}]  {msg}")

def on_message(sender, data: bytearray):
    text = data.decode("utf-8", errors="replace").strip()
    add_log(f"RX> {text}")
    match = POS_REGEX.search(text)
    if match:
        new_x = float(match.group(1))
        new_y = float(match.group(2))
        with data_lock:
            x_data.append(new_x)
            y_data.append(new_y)

async def safe_write(client: BleakClient, message: str):
    async with write_lock:
        payload = (message + "\n").encode("utf-8")
        try:
            await client.write_gatt_char(TX_UUID, payload, response=True)
        except Exception:
            await client.write_gatt_char(TX_UUID, payload, response=False)
            await asyncio.sleep(0.15)

def send_command(msg: str):
    if ble_loop and ble_client and ble_client.is_connected:
        add_log(f"TX> {msg}")
        asyncio.run_coroutine_threadsafe(safe_write(ble_client, msg), ble_loop)
    else:
        add_log("Not connected yet.")

async def run_ble():
    global ble_client, write_lock
    write_lock = asyncio.Lock()
    add_log(f"Scanning for {DEVICE_NAME}...")

    device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=10.0)
    if not device:
        add_log("Device not found.")
        return

    async with BleakClient(device) as client:
        ble_client = client
        add_log(f"Connected to {device.address}")
        await client.start_notify(RX_UUID, on_message)

        # try:
        #     await safe_write(client, "start track")
        #     await asyncio.sleep(0.5)
        # except Exception as e:
        #     add_log(f"BLE Error: {e}")

        while True:
            try:
                await safe_write(client, "getpos")
                await asyncio.sleep(0.5)
            except Exception as e:
                add_log(f"BLE Error: {e}")
                break

def start_ble_loop():
    global ble_loop
    ble_loop = asyncio.new_event_loop()
    asyncio.set_event_loop(ble_loop)
    ble_loop.run_until_complete(run_ble())

# --- Plot Layout ---
fig = plt.figure(figsize=(10, 8))
fig.patch.set_facecolor("#1e1e2e")

gs = gridspec.GridSpec(
    3, 1,
    height_ratios=[6, 2, 0.6],
    hspace=0.35,
    left=0.1, right=0.95, top=0.95, bottom=0.08
)

# Top: path plot
ax_plot = fig.add_subplot(gs[0])
ax_plot.set_facecolor("#12121f")
ax_plot.set_xlim(-7000, 10000)
ax_plot.set_ylim(-7000, 10000)
ax_plot.set_xlabel("X Position", color="#aaaacc")
ax_plot.set_ylabel("Y Position", color="#aaaacc")
ax_plot.tick_params(colors="#aaaacc")
ax_plot.grid(True, color="#2a2a4a", linewidth=0.5)
for spine in ax_plot.spines.values():
    spine.set_edgecolor("#2a2a4a")

line, = ax_plot.plot([], [], 'o-', color="#5b9cf6", linewidth=1.2, markersize=3, label="Path")
point, = ax_plot.plot([], [], 'o', color="#f87171", markersize=8, label="Current")
ax_plot.legend(facecolor="#1e1e2e", labelcolor="#ccccee", edgecolor="#2a2a4a")

# Middle: log panel
ax_log = fig.add_subplot(gs[1])
ax_log.set_facecolor("#12121f")
ax_log.set_xticks([])
ax_log.set_yticks([])
for spine in ax_log.spines.values():
    spine.set_edgecolor("#2a2a4a")
ax_log.set_title("Log", color="#aaaacc", fontsize=9, loc="left", pad=4)
log_text = ax_log.text(
    0.01, 0.97, "",
    transform=ax_log.transAxes,
    va="top", ha="left",
    fontsize=8.5,
    fontfamily="monospace",
    color="#a0f0a0",
    linespacing=1.6,
    wrap=False
)

# Bottom: TextBox + Send button
ax_input = fig.add_axes([0.10, 0.01, 0.72, 0.045])
ax_btn   = fig.add_axes([0.84, 0.01, 0.11, 0.045])

text_box = TextBox(ax_input, "", initial="", color="#12121f", hovercolor="#1a1a30")
text_box.label.set_color("#aaaacc")
text_box.text_disp.set_color("#e0e0ff")
text_box.text_disp.set_fontfamily("monospace")

send_btn = Button(ax_btn, "Send", color="#2a3a5a", hovercolor="#3a4a6a")
send_btn.label.set_color("#e0e0ff")

def submit(text):
    msg = text.strip()
    if msg:
        send_command(msg)
    text_box.set_val("")

text_box.on_submit(submit)
send_btn.on_clicked(lambda _: submit(text_box.text))

# --- Animation ---
def init():
    line.set_data([], [])
    point.set_data([], [])
    log_text.set_text("")
    return line, point, log_text

def update(frame):
    with data_lock:
        if x_data:
            line.set_data(x_data, y_data)
            point.set_data([x_data[-1]], [y_data[-1]])

    with log_lock:
        log_text.set_text("\n".join(log_messages))

    return line, point, log_text

if __name__ == "__main__":
    ble_thread = threading.Thread(target=start_ble_loop, daemon=True)
    ble_thread.start()

    ani = FuncAnimation(fig, update, init_func=init, interval=100, blit=True)
    plt.show()