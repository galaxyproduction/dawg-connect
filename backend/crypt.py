import config
import jwt
from passlib.hash import sha256_crypt

def encode_jwt(uid, fname, type):
    payload = { 'uid': uid, 'first_name': fname, 'type': type }

    token = jwt.encode(
        payload=payload,
        key=config.key,
        algorithm='RS256'
    )

    return token

def decode_jwt(token):
    header_data = jwt.get_unverified_header(token)
    decoded_token = jwt.decode(token, key=config.pub_key, algorithms=[header_data['alg'], ])

    return decoded_token

def encrypt_password(password):
    return sha256_crypt.encrypt(password)

def decrypt_password(user_pass, hashed_pass):
    return sha256_crypt.verify(user_pass, hashed_pass)