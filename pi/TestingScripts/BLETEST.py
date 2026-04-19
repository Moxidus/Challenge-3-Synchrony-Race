import asyncio
from bleak import BleakClient, BleakScanner
 
DEVICE_NAME = "Makeblock_LE001b1068770a"
RX_UUID = "0000ffe2-0000-1000-8000-00805f9b34fb"  # notify/read incoming
TX_UUID = "0000ffe3-0000-1000-8000-00805f9b34fb"  # write outgoing
 
write_lock = asyncio.Lock()
 
def on_message(sender, data: bytearray):
    text = data.decode("utf-8", errors="replace").strip()
    print(f"\nRX> {text}")
 
async def safe_write(client: BleakClient, message: str):
    async with write_lock:
        payload = (message + "\n").encode("utf-8")
 
        # Try write-with-response first because it prevents overlapping writes better.
        # If the characteristic does not support it, fall back to write-without-response.
        try:
            await client.write_gatt_char(TX_UUID, payload, response=True)
        except Exception:
            await client.write_gatt_char(TX_UUID, payload, response=False)
            await asyncio.sleep(0.15)
 
async def main():
    print(f"Scanning for {DEVICE_NAME!r}...")
    device = await BleakScanner.find_device_by_name(DEVICE_NAME, timeout=10.0)
 
    if not device:
        print("Device not found")
        return
 
    print("Found:", device.name, device.address)
 
    async with BleakClient(device) as client:
        print("Connected:", client.is_connected)
 
        # Make sure services are discovered on this connection
        _ = client.services
 
        await client.start_notify(RX_UUID, on_message)
        print("Listening. Type commands, or 'exit' to quit.")
 
        while True:
            msg = await asyncio.to_thread(input, "TX> ")
            msg = msg.strip()
 
            if not msg:
                continue
 
            if msg.lower() in {"exit", "quit"}:
                break
 
            if not client.is_connected:
                print("Disconnected")
                break
 
            try:
                await safe_write(client, msg)
            except Exception as e:
                print("Write failed:", repr(e))
                break
 
        try:
            await client.stop_notify(RX_UUID)
        except Exception:
            pass
 
if __name__ == "__main__":
    asyncio.run(main())