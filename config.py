import os
import mysql.connector
from dotenv import load_dotenv
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend

def init():
    load_dotenv()

    global mydb
    mydb = mysql.connector.connect(
        host=os.getenv('HOST'),
        user=os.getenv('USERNAME'),
        password=os.getenv('PASSWORD'),
        database=os.getenv('DATABASE')
    )

    private_key = open('.ssh/id_rsa', 'r').read()
    global key
    key = serialization.load_ssh_private_key(private_key.encode(), password=b'')

    public_key = open('.ssh/id_rsa.pub', 'r').read()
    global pub_key
    pub_key = serialization.load_ssh_public_key(public_key.encode())