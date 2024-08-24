

#/flask_mariadb/client4.py

import asyncio
import csv
import json
import signal
import uuid
from client_server.helper_classes.diverse_gen import get_gen
from pathlib import Path




BASE_DIR = Path.cwd() / "client_server" / "data"

client_file = BASE_DIR / "county_census_final.csv"




class MessageHandler:
    def __init__(self):
        self.sent_messages = {}
        self.received_messages = {}

    def add_message(self, message_id, message):
        self.sent_messages[message_id] = message

    def get_message(self, message_id):
        return self.sent_messages.get(message_id)

    def add_received_message(self, id_card_num, message_id):
        self.received_messages[id_card_num] = message_id


class Client:
    def __init__(self, client_id, population_number, growth_rate, dgen, queue, message_handler):
        self.client_id = client_id
        self.population_number = population_number
        self.growth_rate = growth_rate
        self.dgen = dgen
        self.queue = queue
        self.message_handler = message_handler

    async def connect(self):
        self.reader, self.writer = await asyncio.open_connection('127.0.0.1', 8888)
        self.dgen.set_subcounty_codes_list(self.client_id)

    async def send_data(self):
        await self.connect()

        try:
            for _ in range(self.population_number):
                data = self.dgen.get_data(self.client_id)
                data['client_id'] = self.client_id
                message_id = str(uuid.uuid4())
                data['message_id'] = message_id
                message = json.dumps(data) + "\n"
                self.message_handler.add_message(message_id, message)

                self.writer.write(message.encode())
                await self.writer.drain()

                ack = await self.reader.readuntil(b"\n")
                ack_data = json.loads(ack.decode().strip())
                original_message = self.message_handler.get_message(ack_data['message_id'])
                if original_message:
                    s = f"{self.client_id}: {data['first_name']}, {data['last_name']}, {data['dob']}, {data['gender']}, {data['county']}, {data['subcounty']}, {ack_data['id_card_num']}"
                    print(s)
                    self.message_handler.add_received_message(ack_data['id_card_num'], message_id)

                # Adjust sleep time based on growth rate (percentage) and population size
                await asyncio.sleep(max(0.01, (1.0 / self.growth_rate)))
        except asyncio.CancelledError:
            print(f'Cancelled: Closing the connection for client {self.client_id}')
        finally:
            self.writer.close()
            await self.writer.wait_closed()


async def main():
    queue = asyncio.Queue()
    dgen = get_gen()
    message_handler = MessageHandler()
    clients = []

    # Read the CSV file and create clients based on the data
    with open(client_file, 'r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            client_id = int(row['County_Code'])
            population_number = int(row['Population_number'])
            growth_rate = float(row['Percentage'])
            clients.append(Client(client_id, population_number, growth_rate, dgen, queue, message_handler))

    # Use asyncio.gather for parallel execution
    tasks = await asyncio.gather(*[client.send_data() for client in clients])

    def shutdown():
        for task in tasks:
            task.cancel()

    for sig in (signal.SIGINT, signal.SIGTERM):
        signal.signal(sig, lambda s, f: shutdown())

    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        print("Shutdown initiated, waiting for tasks to complete...")
    finally:
        await queue.join()


if __name__ == "__main__":
    asyncio.run(main())
