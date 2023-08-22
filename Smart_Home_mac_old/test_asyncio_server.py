import asyncio


class ServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        self.transport = transport
        self.queue = asyncio.Queue()

    def data_received(self, data):
        message = data.decode()
        print(f"收到消息: {message}")
        self.queue.put_nowait(message)

    async def send_message(self, message):
        self.transport.write(message.encode())

    async def process_messages(self):
        while True:
            message = await self.queue.get()
            await self.send_message(message)


loop = asyncio.get_event_loop()
coro = loop.create_server(ServerProtocol, '127.0.0.1', 8888)
server = loop.run_until_complete(coro)

try:
    loop.run_until_complete(server.serve_forever())
except KeyboardInterrupt:
    pass

server.close()
loop.run_until_complete(server.wait_closed())
loop.close()
