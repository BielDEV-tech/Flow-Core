# 🚀 Flow Core — MVP

Sistema web desenvolvido para a **Flow Core**, com foco em apresentar produtos digitais, permitir avaliações de clientes e disponibilizar uma área administrativa para gerenciamento do conteúdo.

> **Status do projeto: MVP (Minimum Viable Product)**  
> Esta versão contém as principais funcionalidades necessárias para validar a proposta do sistema. O projeto ainda pode receber novas funcionalidades, melhorias de segurança, otimizações e integrações em versões futuras.

---

## 📌 Sobre o projeto

O **Flow Core MVP** é uma aplicação web que combina uma interface para clientes com um sistema administrativo.

O projeto foi desenvolvido utilizando **HTML, CSS, JavaScript, Python, FastAPI e SQLite**, com autenticação baseada em tokens JWT.

A aplicação permite:

- Visualização dos produtos disponíveis
- Visualização de informações dos produtos
- Login de clientes
- Envio de avaliações
- Visualização das avaliações
- Login administrativo
- Gerenciamento de produtos
- Exclusão de produtos
- Exclusão de avaliações
- Controle de acesso por funções
- Interface responsiva
- Modo escuro

---

# 🎯 Objetivo do MVP

O objetivo principal deste MVP é criar uma primeira versão funcional da plataforma da Flow Core, permitindo testar a estrutura do sistema e suas principais funcionalidades antes de uma versão maior e mais completa.

O MVP foi pensado para validar principalmente:

- Fluxo de autenticação
- Comunicação entre frontend e backend
- Cadastro e gerenciamento de produtos
- Sistema de avaliações
- Controle de acesso administrativo
- Persistência de dados utilizando SQLite
- Estrutura inicial da plataforma

---

# 🧩 Funcionalidades

## 👤 Área do cliente

O cliente pode:

- Acessar a plataforma
- Visualizar produtos
- Consultar informações dos produtos
- Fazer login
- Enviar avaliações
- Visualizar avaliações existentes

---

## 🔐 Autenticação

O sistema possui autenticação para diferentes áreas da aplicação.

A autenticação utiliza:

- JWT
- Bearer Token
- Senhas protegidas
- Controle de funções

Os usuários administrativos possuem funções diferentes, como:

```text
admin
moderador
funcionario
```

Também existe autenticação específica para clientes.

---

# 🛠️ Área administrativa

A área administrativa permite gerenciar partes do conteúdo da plataforma.

Entre as funções disponíveis estão:

- Login administrativo
- Cadastro de produtos
- Visualização de produtos
- Exclusão de produtos
- Gerenciamento de avaliações
- Exclusão de avaliações
- Controle de acesso através de funções

---

# 🛒 Produtos

Os produtos são armazenados no banco de dados e carregados dinamicamente através da API.

Cada produto possui informações como:

```text
ID
Nome
Preço
Descrição
Validade
Incluso
Mensalidade
Vídeo
```

Os produtos podem ser cadastrados e removidos através da área administrativa.

---

# ⭐ Avaliações

O MVP também possui um sistema de avaliações.

Os clientes autenticados podem enviar:

- Nota
- Comentário

As avaliações ficam armazenadas no banco de dados e podem ser exibidas na página principal.

Usuários administrativos com permissão podem remover avaliações.

---

# 🗄️ Banco de dados

O projeto utiliza:

**SQLite**

Banco utilizado:

```text
flow.db
```

Principais tabelas:

```text
dadosFLOW
clientesFLOW
produtosFLOW
avaliacoesFLOW
```

O SQLite foi escolhido nesta etapa por ser simples e adequado para o desenvolvimento e validação do MVP.

---

# 🔌 API

O backend foi desenvolvido utilizando **FastAPI**.

Principais rotas utilizadas:

### Autenticação administrativa

```http
POST /login
```

### Perfil administrativo

```http
GET /perfil
```

### Autenticação do cliente

```http
POST /login_usuario
```

### Produtos

```http
GET /produtos
POST /postar_produto
DELETE /produtos/{produto_id}
```

### Avaliações

```http
GET /avaliacoes
POST /avaliacoes
DELETE /avaliacoes/{avaliacao_id}
```

As rotas protegidas utilizam autenticação através de:

```text
Authorization: Bearer TOKEN
```

---

# 💻 Tecnologias utilizadas

## Frontend

- HTML5
- CSS3
- JavaScript

## Backend

- Python
- FastAPI
- SQLite
- JWT
- bcrypt

---

# 📁 Estrutura do projeto

Uma estrutura básica do projeto:

```text
Flow Core/
│
├── Back.py
├── auth.py
├── flow.db
│
├── FlowCore.html
├── AdminFlow.html
├── Login.html
│
├── flow.js
├── login.js
├── style.css
│
└── README.md
```

Os nomes dos arquivos podem variar conforme a organização utilizada durante o desenvolvimento.

---

# ▶️ Como executar

## 1. Instalar as dependências

No terminal:

```bash
pip install fastapi uvicorn pyjwt bcrypt
```

---

## 2. Iniciar o backend

Execute:

```bash
uvicorn Back:flow --reload
```

O backend será iniciado localmente.

---

## 3. Executar o frontend

O frontend pode ser executado utilizando o **Live Server** do VS Code.

Depois, abra a página principal pelo endereço fornecido pelo Live Server.

---

# 🔑 Fluxo de autenticação

### Cliente

```text
Cliente
   ↓
Login
   ↓
/login_usuario
   ↓
Token
   ↓
Acesso às funções autenticadas
```

### Administrador

```text
Administrador
      ↓
Login
      ↓
/login
      ↓
JWT
      ↓
Área administrativa
```

---

# 🎨 Interface

A interface foi desenvolvida com foco em:

- Legibilidade
- Design moderno
- Cards
- Responsividade
- Modo escuro
- Navegação simples
- Apresentação de produtos
- Área de avaliações

O CSS utiliza principalmente uma identidade visual baseada em tons escuros, azul, roxo, laranja, verde e branco.

---

# 📱 Responsividade

A interface foi planejada para funcionar em diferentes tamanhos de tela, incluindo:

- Computadores
- Notebooks
- Tablets
- Dispositivos móveis

---

# 🔒 Segurança

O MVP já possui alguns mecanismos básicos de segurança, como:

- JWT
- Bearer Token
- Senhas protegidas
- Rotas administrativas protegidas
- Controle de funções

> Como este é um MVP, a segurança ainda pode ser aprimorada antes de uma utilização em produção.

---

# 🚧 Limitações atuais do MVP

Por ser uma primeira versão, o projeto ainda possui pontos que podem ser melhorados.

Alguns exemplos:

- Melhorias de segurança
- Sistema de recuperação de senha
- Melhor gerenciamento de usuários
- Banco de dados mais robusto para produção
- Sistema de pagamentos
- Dashboard administrativo mais completo
- Upload real de imagens e vídeos
- Sistema de pedidos
- Notificações
- Melhor tratamento de erros
- Deploy em produção
- Variáveis de ambiente para informações sensíveis

Essas funcionalidades podem ser adicionadas em versões futuras.

---

# 🔮 Próximas versões

Possíveis evoluções do projeto:

### MVP
```text
✔ Autenticação
✔ Produtos
✔ Avaliações
✔ Área administrativa
✔ API
✔ Banco de dados
```

### Versão futura

```text
⬜ Sistema de pagamentos
⬜ Dashboard completo
⬜ Gerenciamento avançado de usuários
⬜ Upload de arquivos
⬜ Notificações
⬜ Recuperação de senha
⬜ Deploy
⬜ Melhorias de segurança
⬜ Integrações externas
```

---

# 📈 Evolução do projeto

O Flow Core foi estruturado para começar como um **MVP funcional** e evoluir gradualmente.

A ideia é utilizar esta primeira versão para validar a estrutura da aplicação e, posteriormente, adicionar novas funcionalidades conforme a necessidade do projeto.

```text
MVP
 ↓
Validação
 ↓
Melhorias
 ↓
Novas funcionalidades
 ↓
Versão completa
```

---

# 🎓 Objetivo de desenvolvimento

Além de funcionar como uma aplicação prática, o projeto também serve como demonstração de conhecimentos em:

- Desenvolvimento frontend
- Desenvolvimento backend
- APIs REST
- FastAPI
- SQLite
- Autenticação JWT
- JavaScript
- HTML
- CSS
- Integração frontend/backend
- CRUD
- Controle de acesso

---

# 👨‍💻 Desenvolvedor

Projeto desenvolvido para a **Flow Core**.

---

# 📄 Licença

Este projeto é um projeto próprio desenvolvido como **MVP**.

A definição de uma licença específica poderá ser adicionada posteriormente conforme a finalidade de distribuição do projeto.

---

## 🚀 Status

**Flow Core — MVP em desenvolvimento**

A aplicação já possui uma base funcional de frontend, backend, autenticação, produtos, avaliações e gerenciamento administrativo, servindo como ponto de partida para futuras versões do sistema.

Projeto versionado com Git e GitHub.