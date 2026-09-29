import jwt
from datetime import datetime, timedelta, timezone
import bcrypt
import sqlite3 as sql
import os


SECRET_KEY = os.getenv(
    "SECRET_KEY",
    "chave-temporaria-apenas-para-desenvolvimento"
)

ALGORITHM = "HS256"


def criar_hash(senha):

    senha_hash = bcrypt.hashpw(
        senha.encode(),
        bcrypt.gensalt()
    )

    return senha_hash.decode()


def token_api(usuario_id, role):

    expiracao = (
        datetime.now(timezone.utc)
        + timedelta(minutes=15)
    )

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

    except Exception:

        return None


def verificar_senha(
    senha,
    senha_hash
):

    return bcrypt.checkpw(
        senha.encode(),
        senha_hash.encode()
    )