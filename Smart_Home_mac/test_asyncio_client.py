import asyncio

class ClientProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport

    def data_received(self, data):
        message = data.decode()
        print(f"收到回复: {message}")

async def send_messages():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    messages = ["消息1", "消息2", "消息3"]

    for message in messages:
        print(f"发送消息: {message}")
        writer.write(message.encode())
        await writer.drain()

        await asyncio.sleep(2)  # 模拟耗时

    writer.close()

loop = asyncio.get_event_loop()
client_coro = send_messages()
client_task = loop.create_task(client_coro)

loop.run_until_complete(client_task)
loop.close()
