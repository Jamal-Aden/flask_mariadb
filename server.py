

#/flask_mariadb/server.py



import sys
import asyncio
import json
import signal
from collections import defaultdict
from client_server.database_handler import DatabaseHandler
from client_server.db import init_db

db_handler = DatabaseHandler()


#-------------------------------
#init_db(True)
init_db()
#db_handler.add_jama()
#-------------------------------



client_message_count = defaultdict(int)

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Connected to {addr}")

    try:
        while True:
            try:
                data = await reader.readuntil(b"\n")
            except asyncio.IncompleteReadError:
                # Client disconnected gracefully
                print(f"Connection closed by client {addr}")
                break
            except ConnectionResetError:
                # Client disconnected unexpectedly
                print(f"Connection reset by client {addr}")
                break

            if not data:
                break

            message = data.decode().strip()

            try:
                data_dict = json.loads(message)
                client_id = data_dict['client_id']
                #client_id = data_dict.pop('client_id','unknown')
                message_id = data_dict.pop('message_id', 'unknown')
                id_card_num = db_handler.save_person_data(**data_dict)

                # Update the message count for the client
                client_message_count[client_id] += 1

                #print(f"{client_id} : {id_card_num} : {message_id} : Messages received: {client_message_count[client_id]}")
                
                print(f"{client_id:<2} : {id_card_num:<8}  : No.Messages: {client_message_count[client_id]:>10}")

                ack_message = json.dumps({
                    "status": "ack",
                    "id_card_num": id_card_num,
                    "message_id": message_id
                }) + "\n"

                writer.write(ack_message.encode())
                await writer.drain()
            except Exception as e:
                print(f"Error processing data: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        print(f"Connection closed {addr}")
        if 'client_id' in locals():
            print(f"Client {client_id} sent {client_message_count[client_id]} messages")
        writer.close()
        await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    addr = server.sockets[0].getsockname()
    print(f'Serving on {addr}')

    async with server:
        await server.serve_forever()

def run():
    loop = asyncio.get_event_loop()

    server_task = loop.create_task(main())

    def shutdown():
        print("Shutdown initiated, stopping server...")
        server_task.cancel()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown)

    try:
        loop.run_until_complete(server_task)
    except asyncio.CancelledError:
        print("Server task was cancelled")
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        print("Server stopped.")

if __name__ == "__main__":
    run()


