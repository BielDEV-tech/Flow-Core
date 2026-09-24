from pydantic import BaseModel

import sqlite3 as sql

from fastapi import FastAPI, Depends, HTTPException

from fastapi.security import HTTPBearer, OAuth2PasswordRequestForm

from auth import verificar_token, criar_hash, verificar_senha, token_api

import bcrypt

from fastapi.middleware.cors import CORSMiddleware

oauth2_scheme = HTTPBearer()

def usuario_atual(token=Depends(oauth2_scheme)):
    token = token.credentials.strip().strip('"')

    dados = verificar_token(token)

    if dados is None:
        raise HTTPException(
            status_code=401,
            detail="token invalido ou expirado"
        )

    return dados

def bancodados():
    conexao = sql.connect("flow.db")

    cursor = conexao.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS avaliacoesFLOW (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER NOT NULL,
        nota INTEGER NOT NULL,
        comentario TEXT NOT NULL
    )""")



    conexao.commit()
    conexao.close()

flow = FastAPI()

flow.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:5500", "http://localhost:5500"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
    return {"mensagem": "Ola!, sou a flow api e estou feliz em ajudar!"}

@flow.post("/UsersPost")
def post_User(usuario: postUser,
            security = Depends(usuario_atual)):

    role = security["role"]

    print("PRODUTO RECEBIDO PELO FASTAPI:")
    print(produto)

    if role not in ("admin", "moderador", "funcionario"):
        raise HTTPException(
            status_code=403,
            detail="sem permissao"
        )

    usuario_id = security["sub"]

    senha_hash = criar_hash(usuario.senha)

    conexao = sql.connect("flow.db")
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO dadosFLOW
        (nome, idade, cpf, assinatura, senha)
        VALUES (?, ?, ?, ?, ?)
    """, (
        usuario.nome,
        usuario.idade,
        usuario.cpf,
        usuario.assinatura,
        senha_hash
    ))

    conexao.commit()

    dados = cursor.lastrowid

    conexao.close()

    return {
        "id": dados,
        "nome": usuario.nome,
        "idade": usuario.idade,
        "cpf": usuario.cpf,
        "assinatura": usuario.assinatura,
        "acesso": usuario_id
    }

    if dados is None:
        raise HTTPException(
            status_code=404,
            detail="faça login para seguir com a acao"
        )

@flow.get("/usuario")
def cliente_id(
    usuario = Depends(usuario_atual)):

    usuario_id = usuario["sub"]

    conexao = sql.connect("flow.db")

    cursor = conexao.cursor()

    cursor.execute("SELECT id, nome, idade, cpf, assinatura FROM dadosFLOW WHERE id = ?", (usuario_id,))

    dados = cursor.fetchone()

    conexao.close()
    
    if dados is None:
        raise HTTPException(
            status_code=404,
            detail="usuario nao encontrado"
        )
        
    return {
        "id":dados[0],
        "nome": dados[1],
        "idade": dados[2],
        "cpf": dados[3],
        "assinatura": dados[4]
    }

@flow.get("/assinatura")
def buscar_assinatura(usuario = Depends(usuario_atual)):
    conexao = sql.connect("flow.db")

    cursor = conexao.cursor()

    usuario_id = usuario["sub"]

    cursor.execute("""SELECT id, nome, idade, assinatura FROM dadosFLOW WHERE id = ?""", (usuario_id,))

    mensalidade = cursor.fetchone()

    conexao.close()

    if mensalidade is None:
        raise HTTPException(
            status_code=404,
            detail="plano nao encontrado"
        )

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
    usuario = Depends(usuario_atual)):
    conexao = sql.connect("flow.db")

    cursor = conexao.cursor()

    role = usuario["role"]

    if role not in ("admin", "moderador", "funcionario"):
        raise HTTPException(
            status_code=403,
            detail="sem permissao"
        )

    cursor.execute(
        "UPDATE clientesFLOW SET nome = ?, cpf = ?, email  = ? WHERE id = ?",
        (clientes.nome,
        clientes.cpf,
        clientes.email,
        cliente_id)
    )

    conexao.commit()

    if cursor.rowcount == 0:
        conexao.close()

        raise HTTPException(
            status_code=404,
            detail="cliente nao encontrado"
        )

    conexao.commit()

    conexao.close()

    return {
        "mensagem": "cliente atualizado",
        "cliente_id": cliente_id,
        "atualizado_por": usuario["sub"]
    }


@flow.get("/perfil")
def perfil(usuario = Depends(usuario_atual)):
    
    usuario_id = usuario["sub"]


    conexao = sql.connect("flow.db")
    cursor = conexao.cursor()

    cursor.execute(
        "SELECT id, nome, idade, cpf, assinatura FROM dadosFLOW WHERE id = ?",
        (usuario_id,))

    dados = cursor.fetchone()

    conexao.close()

    if dados is None:
        raise HTTPException(
            status_code=404,
            detail="usuario nao encontrado"
        )

    return {
        "id": dados[0],
        "nome": dados[1],
        "idade": dados[2],
        "cpf": dados[3],
        "assinatura": dados[4]
    }

@flow.post("/login")
def login_adm(usuario: Login):
    conexao = sql.connect("flow.db")

    cursor = conexao.cursor()

    cursor.execute("""
    SELECT id, idade, cpf, senha, role
    FROM dadosFLOW
    WHERE cpf = ?
    """, (usuario.cpf,))

    dados = cursor.fetchone()

    if dados is None:
        conexao.close()

        raise HTTPException(
            status_code=401,
            detail="CPF ou Senha Invalidos"
        )

    usuario_id = dados[0]
    senha_hash = dados[3]
    role = dados[4]

    senha_correta = verificar_senha(
        usuario.senha,
        senha_hash
    )

    if not senha_correta:
        conexao.close()

        raise HTTPException(
            status_code=401,
            detail="CPF ou Senha Invalidos"
        )

    token = token_api(usuario_id, role)

    return {
        "access_token": token,
        "token_type": "bearer"
    }

@flow.get("/responsavel")
def privada(usuario = Depends(usuario_atual)):
    
    role = usuario["role"]

    if role not in ("admin", "moderador", "funcionario"):
        raise HTTPException(
            status_code=403,
            detail="sem permissao"
        )

    return {
        "mensgem": "acesso permitido",
        "usuario": usuario["sub"]
    }

@flow.get("/usuario_comum")
def comum(usuario = Depends(usuario_atual)):

    role = usuario["role"]

    if role != "usuario":
        raise HTTPException(
            status_code=403,
            detail="sem permissao"
        )

    return {
        "mensagem": "usuario conctado",
        "usuario": usuario["sub"]
    }

@flow.post("/postar_produto")
def postproduto(produto: produtos, usuario = Depends(usuario_atual)):
    conexao = sql.connect("flow.db")

    cursor = conexao.cursor()

    log = usuario["sub"]

    role = usuario["role"]

    if role not in ("admin", "moderador", "funcionario"):
        raise HTTPException(
            status_code=403,
            detail="sem permissao"
        )

    if log is None:
        raise HTTPException(
            status_code=404,
            detail="faca login para entrar na pagina"
        )

    cursor.execute("""INSERT INTO produtosFLOW (id, nome, preco, descrisao, validade, incluso, mensalidade, video) VALUES (?, ?, ?, ?, ?, ?, ?) """, ( 
        produto.id,
        produto.nome,
        produto.preco,
        produto.descrisao,
        produto.validade,
        produto.incluso,
        produto.mensalidade,
        produto.video))

    conexao.commit()

    conexao.close()

    
    return {
        "id": produto.id,
        "nome": produto.nome,
        "preco": produto.preco,
        "descrisao": produto.descrisao,
        "validade": produto.validade,
        "incluso": produto.incluso,
        "mensalidade": produto.mensalidade,
        "Video": produto.video,
        "criado por": log
            }

@flow.get("/moderadores")
def moderador(usuario = Depends(usuario_atual)):

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

    conexao = sql.connect("flow.db")

    cursor = conexao.cursor()

    senha_hash = criar_hash(login.senha)

    cursor.execute("""INSERT INTO clientesFLOW (nome, senha, cpf, email, role) VALUES (?, ?, ?, ?, ?)""", (login.nome, senha_hash, login.cpf, login.email, "usuario"))

    conexao.commit()

    novo_id = cursor.lastrowid

    conexao.close()

    
    return {
        "nome": login.nome,
        "cpf": login.cpf,
        "email": login.email
    }

@flow.get("/funcionario_empregado")
def empregado(usuario = Depends(usuario_atual)):

    sub = usuario["sub"]

    role = usuario["role"]

    conexao = sql.connect("flow.db")

    cursor = conexao.cursor()

    if role != "admin":
        raise HTTPException(
            status_code=403,
            detail="sem permissao"
        )

    cursor.execute(
        "SELECT id, nome, idade, cpf, role FROM dadosFLOW WHERE id = ?",
    (sub,))

    dados = cursor.fetchone()

    return {
        "id": dados[0],
        "nome": dados[1],
        "idade": dados[2],
        "cpf": dados[3],
        "role": dados[4]
    }

@flow.post("/login_usuario")
def login_usuario(login: criar):
    conexao = sql.connect("flow.db")

    cursor = conexao.cursor()

    cursor.execute("""SELECT id, senha, role FROM clientesFLOW WHERE cpf = ?""", (login.cpf,))

    dados = cursor.fetchone()

    if dados is None:
        raise HTTPException(
            status_code=401,
            detail="cpf ou senha invalidos"
        )

    usuario_id = dados[0]
    senha_hash = dados[1]
    role = dados[2]

    senha_correta = verificar_senha(
        login.senha,
        senha_hash,
    )

    if not senha_correta:
        conexao.close()

        raise HTTPException(
            status_code=401,
            detail="cpf ou senha invalidos"
        )

    token = token_api(usuario_id, role)

    conexao.close()

    return {
        "chave de acesso": token,
        "token type": "bearer"
    }

@flow.get("/produtos")
def produto():
    conexao = sql.connect("flow.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT id, nome, preco, descrisao, validade, incluso, mensalidade, video
        FROM produtosFLOW
    """)

    produtos = cursor.fetchall()

    conexao.close()

    lista_produtos = []

    for produto in produtos:

        lista_produtos.append({
            "id": produto[0],
            "nome": produto[1],
            "preco": produto[2],
            "descrisao": produto[3],
            "validade": produto[4],
            "incluso": produto[5],
            "mensalidade": produto[6],
            "video": produto[7]
        })

    return lista_produtos

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

    if avaliacao.nota < 1 or avaliacao.nota > 5:
        raise HTTPException(
            status_code=400,
            detail="A nota deve ser entre 1 e 5"
        )

    conexao = sql.connect("flow.db")
    cursor = conexao.cursor()

    cursor.execute("""
        INSERT INTO avaliacoesFLOW
        (usuario_id, nota, comentario)
        VALUES (?, ?, ?)
    """, (
        usuario["sub"],
        avaliacao.nota,
        avaliacao.comentario
    ))

    conexao.commit()
    conexao.close()

    return {
        "mensagem": "Avaliação enviada com sucesso"
    }

@flow.get("/avaliacoes")
def listar_avaliacoes():

    conexao = sql.connect("flow.db")
    cursor = conexao.cursor()

    cursor.execute("""
        SELECT
            avaliacoesFLOW.id,
            clientesFLOW.nome,
            avaliacoesFLOW.nota,
            avaliacoesFLOW.comentario
        FROM avaliacoesFLOW
        INNER JOIN clientesFLOW
        ON avaliacoesFLOW.usuario_id = clientesFLOW.id
        ORDER BY avaliacoesFLOW.id DESC
    """)

    avaliacoes = cursor.fetchall()

    conexao.close()

    lista = []

    for avaliacao in avaliacoes:
        lista.append({
            "id": avaliacao[0],
            "nome": avaliacao[1],
            "nota": avaliacao[2],
            "comentario": avaliacao[3]
        })

    return lista

@flow.delete("/avaliacoes/{avaliacao_id}")
def apagar_avaliacao(
    avaliacao_id: int,
    usuario=Depends(usuario_atual)
):

    role = usuario["role"]

    if role not in ("admin", "moderador", "funcionario"):
        raise HTTPException(
            status_code=403,
            detail="sem permissao"
        )

    conexao = sql.connect("flow.db")
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM avaliacoesFLOW WHERE id = ?",
        (avaliacao_id,)
    )

    conexao.commit()

    apagou = cursor.rowcount

    conexao.close()

    if apagou == 0:
        raise HTTPException(
            status_code=404,
            detail="avaliacao nao encontrada"
        )

    return {
        "mensagem": "Avaliacao apagada com sucesso"
    }

@flow.delete("/produtos/{produto_id}")
def apagar_produto(
    produto_id: int,
    usuario=Depends(usuario_atual)
):

    role = usuario["role"]

    if role not in ("admin", "moderador", "funcionario"):
        raise HTTPException(
            status_code=403,
            detail="sem permissao"
        )

    conexao = sql.connect("flow.db")
    cursor = conexao.cursor()

    cursor.execute(
        "DELETE FROM produtosFLOW WHERE id = ?",
        (produto_id,)
    )

    conexao.commit()

    apagou = cursor.rowcount

    conexao.close()

    if apagou == 0:
        raise HTTPException(
            status_code=404,
            detail="produto nao encontrado"
        )

    return {
        "mensagem": "Produto apagado com sucesso"
    }

