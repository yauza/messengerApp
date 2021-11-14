import threading
import sys
from tkinter import *
from datetime import datetime
from client import Client
import speech_recognition as sr

class UI:
    def __init__(self, name="client", server_addr="192.168.1.176") -> None:
        self.name = name
        self.server_addr = server_addr
        self.root = Tk()
        self.root.title(self.name)
        self.root.protocol("WM_DELETE_WINDOW", self.on_quit)
        self.parse_name()

        self.line = 1

        self.client_thread = threading.Thread(target=self.print_received_messages)
        self.client_thread.daemon = True
        self.client_flag = True
        self.client = Client(server_addr=self.server_addr, name=self.name)
        self.create_widgets()

    def on_quit(self, cmd=False):
        if not cmd:
            self.client.send_message("/quit")
        self.client_flag = False
        self.root.destroy()
        sys.exit(0)

    def create_widgets(self):
        self.chat = Text(self.root, width=80, bg="gray64")
        self.chat.grid(row=0, column=0, columnspan=3, padx=10, pady=10)

        self.e = Entry(self.root, width=50, borderwidth=2, bg="gray64")
        self.e.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        self.button = Button(self.root, text="Send", bg="green", fg="red", padx=40, pady=10, command=lambda: self.button_click())
        self.button.grid(row=1, column=2, sticky="W")

        self.button = Button(self.root, text="Speak", padx=30, pady=10, command=lambda: self.record_speech())
        self.button.grid(row=1, column=2, sticky="E")

    def parse_name(self):
        if len(self.name) > 6:
            self.name = self.name[0:6]
        else:
            self.name = self.name.ljust(6, "-")

    def record_speech(self):
        recognizer = sr.Recognizer()
        with sr.Microphone() as source:
            audio_text = recognizer.listen(source, timeout=2)
            self.print_message("Nagrywanie zakończone.", "*utils")
            try:
                recognized_speech = recognizer.recognize_google(audio_text, language="pl")
                if not self.client.recognize_commands(recognized_speech):
                    self.e.insert(0, recognized_speech)
            except sr.UnknownValueError:
                self.print_message("Nie udało się poprawnie zarejestrować mowy. Proszę spróbować ponownie.", "*utils")

    def button_click(self):
        text = self.e.get()
        self.e.delete(0, END)
        self.client.send_message(text)

    def print_message(self, text, username):
        msg_time = datetime.now().strftime("%H:%M:%S")
        self.chat.insert(END, "[" + msg_time + " " + username + "] " + text + "\n")
        start = str(self.line) + ".0"
        end = str(self.line) + "." + str(17)
        self.chat.tag_add("here", start, end)
        self.chat.tag_config("here", background="black", foreground="green")
        self.line += 1

    def print_received_messages(self):
        while self.client_flag:
            username, text = self.client.decode_message()
            if text == "/quit":
                self.on_quit(True)
            elif text == "/username_taken":
                print("[ERROR] User with that name already exists. Pick different name.")
                sys.exit()
            else:
                self.print_message(text, username)

    def run(self):
        self.client_thread.start()
        self.root.mainloop()
