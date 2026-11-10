
import asyncio
import telnetlib3

ROUTER_IP = "192.168.99.1"
USERNAME = "netadmin"
PASSWORD = "NetAdmin2026!"

async def monitor_router():
    try:
        reader, writer = await telnetlib3.open_connection(
            host=ROUTER_IP,
            port=23,
            connect_minwait=1,
            connect_maxwait=3
        )

        print("Connected to R1")

        await asyncio.sleep(1)
        output = await reader.read(2000)
        print(output)

        writer.write(USERNAME + "\n")
        await writer.drain()
        await asyncio.sleep(1)

        output = await reader.read(2000)
        print(output)

        writer.write(PASSWORD + "\n")
        await writer.drain()
        await asyncio.sleep(1)

        output = await reader.read(2000)
        print(output)

        writer.write("show ip interface brief\n")
        await writer.drain()
        await asyncio.sleep(2)

        result = await reader.read(5000)

        print("\n===== R1 INTERFACE STATUS =====")
        print(result)

        writer.write("exit\n")
        await writer.drain()
        writer.close()

    except Exception as error:
        print("Connection failed:", error)

asyncio.run(monitor_router())
