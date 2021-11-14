import socket 
import threading
import sys
from controller import Controller


class ServerClient:
    def __init__(self, conn, addr, index, name=""):
        self.conn = conn
        self.addr = addr
        self.index = index
        self.name = name


class Server:
    def __init__(self, port=5050, server_addr=socket.gethostbyname(socket.gethostname())):
        self.port = port
        self.server_addr = server_addr

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.server_addr, self.port))

        self.connections_counter = 0
        self.controller = Controller()
        self.clients = {}

    def check_if_exists(self, name):
        for client in self.clients.values():
            if client.name == name:
                return True

    def get_client_by_name(self, name):
        for client in self.clients.values():
            if client.name == name:
                return client

    def handle_client(self, conn, addr, index):
        print(f"[NEW CLIENT] {addr} connected.")
        
        start = True
        connected = True
        while connected:
            msg_length = conn.recv(64).decode("utf-8")
            if msg_length:
                msg_length = int(msg_length)
                msg = conn.recv(msg_length).decode("utf-8")

                if start:
                    username = msg[0:6]
                    if self.check_if_exists(username):
                        self.clients[index].conn.send((f"{username}" + "#@#" + "/username_taken").encode("utf-8"))
                        connected = False
                        self.connections_counter -= 1
                        self.clients.pop(index)
                        break
                    self.clients[index].name = username
                    start = False

                msg_text = msg[9:]
                if msg_text == "/quit":
                    self.clients[index].conn.send(("server" + "#@#" + "/quit").encode("utf-8"))
                    connected = False
                    self.connections_counter -= 1
                    self.clients.pop(index)
                    print(f"User {msg[0:6]} disconnected.")
                    print(f"[ACTIVE CLIENTS] {self.connections_counter}")
                elif msg_text == "/waluty":
                    self.clients[index].conn.send((f"server" + "#@#" + self.controller.get_currency_table()).encode("utf-8"))
                elif msg_text == "/pogoda":
                    self.clients[index].conn.send((f"server" + "#@#" + self.controller.get_weather()).encode("utf-8"))
                else:               
                    print(f"[{self.clients[index].name}, ({addr[1]})] {msg_text}")
                    for client in self.clients.values():
                        client.conn.send(msg.encode("utf-8"))

        conn.close()

    def stop(self):
        print("Disconnecting clients...")
        for client in self.clients.values():
            client.conn.send(("server" + "#@#" + "/quit").encode("utf-8"))
        print("Server stopping...")

    def run(self):
        self.server.listen()
        print(f"[START] Server is listening on {self.server_addr}")
        index = 0
        while True:
            try: 
                conn, addr = self.server.accept()
                self.clients[index] = ServerClient(conn, addr, index)
                thread = threading.Thread(target=self.handle_client, args=(conn, addr, index))
                thread.daemon = True
                thread.start()
                index += 1
                self.connections_counter += 1
                print(f"[ACTIVE CLIENTS] {self.connections_counter}")
            except KeyboardInterrupt:
                self.stop()
                sys.exit()


server = Server()
server.run()