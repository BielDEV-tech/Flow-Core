import jwt

from datetime import datetime, timedelta, timezone

import bcrypt

import sqlite3 as sql

SECRET_KEY = "minha-chave-secreta-super-segura-2026"
ALGORITHM = "HS256"

senha = "123456"

def criar_hash(senha):
    senha_hash = bcrypt.hashpw(
        senha.encode(),
        bcrypt.gensalt()
    )

    return senha_hash.decode()

criar_hash(senha)

def token_api(usuario_id, role):

    expiracao = datetime.now(timezone.utc) + timedelta(minutes=15)

    payload = {
        "sub": str(usuario_id),
        "role": role,
        "exp": expiracao
    }

    token = jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )

    return token

def verificar_token(token):

    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except Exception as erro:

        return None

def verificar_senha(senha, senha_hash):

    return bcrypt.checkpw(
        senha.encode(),
        senha_hash.encode()
    )

senha = "123456"

senha_hash = criar_hash(senha)

def teste():

    print("HASH:")
    print(senha_hash)

    print("CORRETA:")
    print(verificar_senha("123456", senha_hash))

    print("ERRADA:")
    print(verificar_senha("654321", senha_hash))

    print(verificar_token(token))

