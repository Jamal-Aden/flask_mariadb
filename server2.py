

### `server.py`


import sys
import asyncio
import json
import signal
import logging
from collections import defaultdict
from client_server.database_handler import DatabaseHandler
from client_server.db import init_db

# Initialize database handler
db_handler = DatabaseHandler()

#init_db(True)
init_db()


# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Keep track of messages from clients
client_message_count = defaultdict(int)

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    logger.info(f"Connected to {addr}")

    try:
        while True:
            try:
                # Set a timeout for reading data
                data = await asyncio.wait_for(reader.readuntil(b"\n"), timeout=10)
            except asyncio.TimeoutError:
                logger.warning(f"Timeout reached: Closing connection to {addr}")
                break
            except asyncio.IncompleteReadError:
                logger.warning(f"Connection closed by client {addr}")
                break
            except ConnectionResetError:
                logger.error(f"Connection reset by client {addr}")
                break

            if not data:
                break

            message = data.decode().strip()

            try:
                data_dict = json.loads(message)
                client_id = data_dict['client_id']
                message_id = data_dict.pop('message_id', 'unknown')
                id_card_num = db_handler.save_person_data(**data_dict)

                client_message_count[client_id] += 1

                logger.info(f"{client_id:<2} : {id_card_num:<8}  : No.Messages: {client_message_count[client_id]:>10}")

                ack_message = json.dumps({
                    "status": "ack",
                    "id_card_num": id_card_num,
                    "message_id": message_id
                }) + "\n"

                writer.write(ack_message.encode())
                await writer.drain()
            except Exception as e:
                logger.error(f"Error processing data: {e}")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        logger.info(f"Connection closed {addr}")
        if 'client_id' in locals():
            logger.info(f"Client {client_id} sent {client_message_count[client_id]} messages")
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    addr = server.sockets[0].getsockname()
    logger.info(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

def run():
    loop = asyncio.get_event_loop()

    server_task = loop.create_task(main())

    async def shutdown(loop, signal=None):
        if signal:
            logger.info(f"Received exit signal {signal.name}...")

        tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]

        for task in tasks:
            task.cancel()

        await asyncio.gather(*tasks, return_exceptions=True)

        loop.stop()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(loop, signal=s)))

    try:
        loop.run_until_complete(server_task)
    except asyncio.CancelledError:
        logger.info("Server task was cancelled")
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        logger.info("Server stopped.")

if __name__ == "__main__":
    run()




