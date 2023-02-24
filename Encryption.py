# -*- coding: utf-8 -*-
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

class Encryption():
    def __init__(self, password):
        self.generate_key(password)
        self.fernet = Fernet(self.key)
        
    def generate_key(self, password):      
        encodedpassword = password.encode() # Convert to type bytes
        salt = b'salt_' # CHANGE THIS - recommend using a key from os.urandom(16), must be of type bytes
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        self.key = base64.urlsafe_b64encode(kdf.derive(encodedpassword))

    def Encrypt(self, data):         
        return self.fernet.encrypt(data.encode())
    
    def Decrypt(self, encrypted):
        return self.fernet.decrypt(encrypted)

def int_to_bytes(x):
    return x.to_bytes((x.bit_length() + 7) // 8, 'big')

#import json
#password = 'e13bb7001404c476f0c60841464d31172ec2f0fb2ba2a8987abf71dd17ad5f32842db58917ac14b5313c52e399a553affb55a01d0601c7f7ab65367e00eb7822'
#message = '{"msgtype": "NetworkState.HANDSHAKE", "peer": ["178.118.85.77", 4319, "a537a6c9-7420-4a39-bd4d-0930390b22e5", null]}'
#encryption = Encryption(password)
#
#passint = int('0x{}'.format(password), 0)
#passbytes = int_to_bytes(passint)
#print(len(passbytes))
#encrypted = encryption.Encrypt(message)
#print(encrypted)
#decrypted = encryption.Decrypt(encrypted)
#print(decrypted)
#jsondata = json.loads(decrypted)
#print(jsondata)