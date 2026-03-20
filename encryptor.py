import os
import base64
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass

def generate_key_from_password(password: str, salt: bytes = None) -> tuple:
    """
    Generate an AES-256 key from a password using PBKDF2.
    
    Args:
        password: User password
        salt: Salt for key derivation (if None, generates random salt)
    
    Returns:
        tuple: (key, salt) where key is base64 encoded for Fernet
    """
    if salt is None:
        salt = os.urandom(16)
    
    # Use PBKDF2 to derive a key from the password
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=480000,  # High iteration count for security
    )
    
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key, salt

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

def encrypt_folder(folder_path: str, password: str = None, save_salt: bool = True) -> bool:
    """
    Encrypt all files in a given folder using AES-256.
    
    Args:
        folder_path: Path to the folder containing files to encrypt
        password: Password for encryption (if None, prompts user)
        save_salt: Whether to save the salt to a file (for decryption)
    
    Returns:
        bool: True if successful, False otherwise
    """
    # Get password if not provided
    if password is None:
        password = getpass.getpass("Enter encryption password: ")
        confirm_password = getpass.getpass("Confirm password: ")
        
        if password != confirm_password:
            print("Error: Passwords do not match!")
            return False
    
    # Convert to Path object
    folder = Path(folder_path)
    
    if not folder.exists() or not folder.is_dir():
        print(f"Error: {folder_path} is not a valid directory")
        return False
    
    # Generate key and salt
    salt = os.urandom(16)
    key, salt = generate_key_from_password(password, salt)
    
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