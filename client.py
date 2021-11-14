import socket
import unicodedata
import Levenshtein as lev

class Client:
    def __init__(self, port=5050, server_addr="192.168.1.176", name="client"):
        self.port = port
        self.server_addr = server_addr
        self.socket = None
        self.name = name

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.server_addr, self.port))
        self.send_message(self.name)

    def parse_message(self, text):
        return f"{self.name}" + "#@#" + text

    def send_message(self, text):
        text = self.parse_message(text)
        msg = text.encode("utf-8")
        msg_length = len(msg)
        send_length = str(msg_length).encode("utf-8")
        send_length += b" " * (64 - len(send_length))
        self.socket.send(send_length)
        self.socket.send(msg)

    def decode_message(self):
        text = str(self.socket.recv(2048).decode("utf-8"))
        tmp = text.split("#@#")
        username = tmp[0]
        msg = "".join(tmp[1:])
        return username, msg

    def receive_message(self):
        return str(self.socket.recv(2048).decode("utf-8"))

    def recognize_commands(self, recognized_speech):
        if len(recognized_speech.split()) > 3:
            return False
        text = unicodedata.normalize("NFKD", recognized_speech.lower()).replace(u"ł", "l").encode("ascii", "ignore").decode("utf-8")
        print(text)
        for s in ['pogoda', 'podaj pogode', 'pokaz pogode', 'wyswietl pogode']:
            print(lev.distance(s, text))
            if lev.distance(s, text) < 2:
                self.send_message("/pogoda")
                return True
        
        for s in ['waluty', 'podaj waluty', 'pokaz waluty', 'wyswietl waluty', 'pokaz kursy walut', 'podaj kursy walut', 'wyswietl kursy walut']:
            if lev.distance(s, text) < 2:
                self.send_message("/waluty")
                return True

