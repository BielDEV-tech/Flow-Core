
import os
import bcrypt
import jwt

from datetime import datetime, timedelta, timezone


SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise RuntimeError(
        "A variável de ambiente SECRET_KEY não foi configurada."
    )

ALGORITHM = "HS256"


def criar_hash(senha):
    senha_hash = bcrypt.hashpw(
        senha.encode("utf-8"),
        bcrypt.gensalt()
    )

    return senha_hash.decode("utf-8")


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

    return jwt.encode(
        payload,
        SECRET_KEY,
        algorithm=ALGORITHM
    )


def verificar_token(token):
    try:
        payload = jwt.decode(
            token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        return payload

    except jwt.PyJWTError:
        return None


def verificar_senha(senha, senha_hash):
    try:
        return bcrypt.checkpw(
            senha.encode("utf-8"),
            senha_hash.encode("utf-8")
        )
    except (ValueError, TypeError):
        return False
