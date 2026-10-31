import os
from contextlib import contextmanager

import psycopg
from pydantic import BaseModel
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import HTTPBearer
from fastapi.middleware.cors import CORSMiddleware

from auth import (
    verificar_token,
    criar_hash,
    verificar_senha,
    token_api
)


DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise RuntimeError(
        "A variável de ambiente DATABASE_URL não foi configurada."
    )


@contextmanager
def bancodados():
    with psycopg.connect(DATABASE_URL) as conexao:
        with conexao.cursor() as cursor:
            yield cursor


oauth2_scheme = HTTPBearer()

flow = FastAPI()

flow.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://flow-core-frontend.vercel.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def usuario_atual(token=Depends(oauth2_scheme)):
    token = token.credentials.strip().strip('"')
    dados = verificar_token(token)

    if dados is None:
        raise HTTPException(
            status_code=401,
            detail="token invalido ou expirado"
        )

    return dados


class postUser(BaseModel):
    nome: str
    idade: str
    cpf: str
    assinatura: str
    senha: str


class Login(BaseModel):
    cpf: str
    senha: str


class produtos(BaseModel):
    id: int
    nome: str
    preco: str
    descrisao: str
    validade: str
    incluso: str
    mensalidade: str
    video: str | None = None


class criar(BaseModel):
    nome: str
    senha: str
    cpf: str
    email: str


class AtualizarCliente(BaseModel):
    nome: str
    cpf: str
    email: str


class Avaliacao(BaseModel):
    nota: int
    comentario: str


@flow.get("/")
def home():
    return {
        "mensagem": "Ola!, sou a flow api e estou feliz em ajudar!"
    }


@flow.post("/UsersPost")
def post_User(
    usuario: postUser,
    security=Depends(usuario_atual)
):
    role = security["role"]

    if role not in ("admin", "moderador", "funcionario"):
        raise HTTPException(status_code=403, detail="sem permissao")

    usuario_id = security["sub"]
    senha_hash = criar_hash(usuario.senha)

    with bancodados() as cursor:
        cursor.execute("""
            INSERT INTO dadosflow
                (nome, idade, cpf, assinatura, senha, role)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        """, (
            usuario.nome,
            usuario.idade,
            usuario.cpf,
            usuario.assinatura,
            senha_hash,
            "funcionario"
        ))
        novo_id = cursor.fetchone()[0]

    return {
        "id": novo_id,
        "nome": usuario.nome,
        "idade": usuario.idade,
        "cpf": usuario.cpf,
        "assinatura": usuario.assinatura,
        "acesso": usuario_id
    }


@flow.get("/usuario")
def cliente_id(usuario=Depends(usuario_atual)):
    with bancodados() as cursor:
        cursor.execute("""
            SELECT id, nome, idade, cpf, assinatura
            FROM dadosflow WHERE id = %s
        """, (usuario["sub"],))
        dados = cursor.fetchone()

    if dados is None:
        raise HTTPException(status_code=404, detail="usuario nao encontrado")

    return {
        "id": dados[0],
        "nome": dados[1],
        "idade": dados[2],
        "cpf": dados[3],
        "assinatura": dados[4]
    }


@flow.get("/assinatura")
def buscar_assinatura(usuario=Depends(usuario_atual)):
    with bancodados() as cursor:
        cursor.execute("""
            SELECT id, nome, idade, assinatura
            FROM dadosflow WHERE id = %s
        """, (usuario["sub"],))
        mensalidade = cursor.fetchone()

    if mensalidade is None:
        raise HTTPException(status_code=404, detail="plano nao encontrado")

    return {
        "id": mensalidade[0],
        "nome": mensalidade[1],
        "idade": mensalidade[2],
        "assinatura": mensalidade[3]
    }


@flow.put("/clientes/{cliente_id}")
def atualizar_cliente(
    cliente_id: int,
    clientes: AtualizarCliente,
    usuario=Depends(usuario_atual)
):
    if usuario["role"] not in ("admin", "moderador", "funcionario"):
        raise HTTPException(status_code=403, detail="sem permissao")

    with bancodados() as cursor:
        cursor.execute("""
            UPDATE clientesflow
            SET nome = %s, cpf = %s, email = %s
            WHERE id = %s
        """, (
            clientes.nome,
            clientes.cpf,
            clientes.email,
            cliente_id
        ))

        if cursor.rowcount == 0:
            raise HTTPException(status_code=404, detail="cliente nao encontrado")

    return {
        "mensagem": "cliente atualizado",
        "cliente_id": cliente_id,
        "atualizado_por": usuario["sub"]
    }


@flow.get("/perfil")
def perfil(usuario=Depends(usuario_atual)):
    with bancodados() as cursor:
        cursor.execute("""
            SELECT id, nome, idade, cpf, assinatura
            FROM dadosflow WHERE id = %s
        """, (usuario["sub"],))
        dados = cursor.fetchone()

    if dados is None:
        raise HTTPException(status_code=404, detail="usuario nao encontrado")

    return {
        "id": dados[0],
        "nome": dados[1],
        "idade": dados[2],
        "cpf": dados[3],
        "assinatura": dados[4]
    }


@flow.post("/login")
def login_adm(usuario: Login):
    with bancodados() as cursor:
        cursor.execute("""
            SELECT id, idade, cpf, senha, role
            FROM dadosflow WHERE cpf = %s
        """, (usuario.cpf,))
        dados = cursor.fetchone()

    if dados is None or not verificar_senha(usuario.senha, dados[3]):
        raise HTTPException(
            status_code=401,
            detail="CPF ou Senha Invalidos"
        )

    token = token_api(dados[0], dados[4])

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@flow.get("/responsavel")
def privada(usuario=Depends(usuario_atual)):
    role = usuario["role"]

    if role not in ("admin", "moderador", "funcionario"):
        raise HTTPException(status_code=403, detail="sem permissao")

    return {
        "mensgem": "acesso permitido",
        "usuario": usuario["sub"]
    }


@flow.get("/usuario_comum")
def comum(usuario=Depends(usuario_atual)):
    if usuario["role"] != "usuario":
        raise HTTPException(status_code=403, detail="sem permissao")

    return {
        "mensagem": "usuario conctado",
        "usuario": usuario["sub"]
    }


@flow.get("/moderadores")
def moderador(usuario=Depends(usuario_atual)):
    log = usuario["sub"]
    role = usuario["role"]

    if role not in ("admin", "moderador"):
        raise HTTPException(
            status_code=403,
            detail="sem permisssao para essa funçao"
        )

    return {
        "mensagem": f"ola {role}",
        "id conectado": log
    }


@flow.post("/criar_user")
def criar_user(login: criar):
    senha_hash = criar_hash(login.senha)

    with bancodados() as cursor:
        cursor.execute("""
            INSERT INTO clientesflow (nome, senha, cpf, email, role)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING id
        """, (
            login.nome,
            senha_hash,
            login.cpf,
            login.email,
            "usuario"
        ))
        novo_id = cursor.fetchone()[0]

    return {
        "nome": login.nome,
        "cpf": login.cpf,
        "email": login.email
    }


@flow.get("/funcionario_empregado")
def empregado(usuario=Depends(usuario_atual)):
    sub = usuario["sub"]

    if usuario["role"] != "admin":
        raise HTTPException(status_code=403, detail="sem permissao")

    with bancodados() as cursor:
        cursor.execute("""
            SELECT id, nome, idade, cpf, role
            FROM dadosflow WHERE id = %s
        """, (sub,))
        dados = cursor.fetchone()

    if dados is None:
        raise HTTPException(status_code=404, detail="usuario nao encontrado")

    return {
        "id": dados[0],
        "nome": dados[1],
        "idade": dados[2],
        "cpf": dados[3],
        "role": dados[4]
    }



@flow.post("/login_usuario")
def login_usuario(login: criar):
    with bancodados() as cursor:
        cursor.execute("""
            SELECT id, senha, role
            FROM dadosflow WHERE cpf = %s
        """, (login.cpf,))
        dados = cursor.fetchone()

    if dados is None or not verificar_senha(login.senha, dados[1]):
        raise HTTPException(
            status_code=401,
            detail="cpf ou senha invalidos"
        )

    token = token_api(dados[0], dados[2])

    return {
        "access_token": token,
        "token_type": "bearer"
    }


@flow.get("/produtos")
def produto():
    with bancodados() as cursor:
        cursor.execute("""
            SELECT id, nome, preco, descrisao, validade,
                   incluso, mensalidade, video
            FROM produtosflow
            ORDER BY id
        """)
        produtos_lista = cursor.fetchall()

    return [
        {
            "id": item[0],
            "nome": item[1],
            "preco": item[2],
            "descrisao": item[3],
            "validade": item[4],
            "incluso": item[5],
            "mensalidade": item[6],
            "video": item[7]
        }
        for item in produtos_lista
    ]


@flow.post("/avaliacoes")
def criar_avaliacao(
    avaliacao: Avaliacao,
    usuario=Depends(usuario_atual)
):
    if usuario["role"] != "usuario":
        raise HTTPException(
            status_code=403,
            detail="Apenas clientes podem fazer avaliações"
        )

    if not 1 <= avaliacao.nota <= 5:
        raise HTTPException(
            status_code=400,
            detail="A nota deve ser entre 1 e 5"
        )

    with bancodados() as cursor:
        cursor.execute("""
            INSERT INTO avaliacoesflow (usuario_id, nota, comentario)
            VALUES (%s, %s, %s)
        """, (
            usuario["sub"],
            avaliacao.nota,
            avaliacao.comentario
        ))

    return {"mensagem": "Avaliação enviada com sucesso"}

@flow.get("/avaliacoes")
def listar_avaliacoes():
    with bancodados() as cursor:
        cursor.execute("""
            SELECT a.id, c.nome, a.nota, a.comentario
            FROM avaliacoesflow AS a
            INNER JOIN clientesflow AS c ON a.usuario_id = c.id
            ORDER BY a.id DESC
        """)
        avaliacoes = cursor.fetchall()

    return [
        {
            "id": item[0],
            "nome": item[1],
            "nota": item[2],
            "comentario": item[3]
        }
        for item in avaliacoes
    ]


@flow.delete("/avaliacoes/{avaliacao_id}")
def apagar_avaliacao(
    avaliacao_id: int,
    usuario=Depends(usuario_atual)
):
    if usuario["role"] not in ("admin", "moderador", "funcionario"):
        raise HTTPException(status_code=403, detail="sem permissao")

    with bancodados() as cursor:
        cursor.execute(
            "DELETE FROM avaliacoesflow WHERE id = %s",
            (avaliacao_id,)
        )
        apagou = cursor.rowcount

    if apagou == 0:
        raise HTTPException(
            status_code=404,
            detail="avaliacao nao encontrada"
        )

    return {"mensagem": "Avaliacao apagada com sucesso"}


@flow.delete("/produtos/{produto_id}")
def apagar_produto(
    produto_id: int,
    usuario=Depends(usuario_atual)
):
    if usuario["role"] not in ("admin", "moderador", "funcionario"):
        raise HTTPException(status_code=403, detail="sem permissao")

    with bancodados() as cursor:
        cursor.execute(
            "DELETE FROM produtosflow WHERE id = %s",
            (produto_id,)
        )
        apagou = cursor.rowcount

    if apagou == 0:
        raise HTTPException(
            status_code=404,
            detail="produto nao encontrado"
        )

    return {"mensagem": "Produto apagado com sucesso"}
