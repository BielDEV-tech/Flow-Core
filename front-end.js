const API_URL = "https://flow-core-api.onrender.com"

async function lerResposta(resposta) {
    const texto = await resposta.text();

    if (!texto) return {};

    try {
        return JSON.parse(texto);
    } catch {
        return {
            detail: "O servidor retornou uma resposta inválida."
        };
    }
}

// ======================================
// LOGIN ADMINISTRADOR
// ======================================

async function verificar() {
    const cpf = document.querySelector("#CPF").value.trim();
    const senha = document.querySelector("#senha").value;

    if (!cpf || !senha) {
        alert("Preencha o CPF e a senha.");
        return;
    }

    try {
        const resposta = await fetch(`${API_URL}/login`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                cpf: cpf,
                senha: senha
            })
        });

        const dados = await lerResposta(resposta);

        if (!resposta.ok) {
            throw new Error(
                dados.detail || "Usuário ou senha incorretos."
            );
        }

        if (!dados.access_token) {
            throw new Error("A API não retornou o token de acesso.");
        }

        localStorage.setItem("token_admin", dados.access_token);

        document.querySelector(".lancar-produto").style.display = "block";
        document.querySelector(".name").style.display = "none";
        document.querySelector(".Pass").style.display = "none";
        document.querySelector(".botao").style.display = "none";

        alert("Login realizado com sucesso!");

    } catch (erro) {
        console.error("Erro no login:", erro);
        alert(erro.message || "Não foi possível realizar o login.");
    }
}

// ======================================
// COLOCAR PRODUTO
// ======================================

async function colocarProduto() {
    const campos = {
        id: document.querySelector(".id"),
        nome: document.querySelector(".nomeProduto"),
        preco: document.querySelector(".preco"),
        descricao: document.querySelector(".descricao"),
        validade: document.querySelector(".validade"),
        incluso: document.querySelector(".incluso"),
        mensalidade: document.querySelector(".mensalidade"),
        video: document.querySelector(".video")
    };

    for (const [nome, campo] of Object.entries(campos)) {
        if (!campo) {
            console.error(`Campo não encontrado: ${nome}`);
            alert(`Erro no formulário: campo ${nome} não encontrado.`);
            return;
        }
    }

    const produto = {
        id: campos.id.value.trim(),
        nome: campos.nome.value.trim(),
        preco: campos.preco.value.trim(),
        descrisao: campos.descricao.value.trim(),
        validade: campos.validade.value.trim(),
        incluso: campos.incluso.value.trim(),
        mensalidade: campos.mensalidade.value.trim(),
        video: campos.video.value.trim()
    };

    if (
        !produto.id ||
        !produto.nome ||
        !produto.preco ||
        !produto.descrisao
    ) {
        alert("Preencha o ID, o nome, o preço e a descrição do produto.");
        return;
    }

    const preco = Number(produto.preco);

    if (!Number.isFinite(preco) || preco < 0) {
        alert("Informe um preço válido.");
        return;
    }

    produto.preco = preco;

    const token = localStorage.getItem("token_admin");

    if (!token) {
        alert("Faça login como administrador ou funcionário.");
        return;
    }

    try {
        const resposta = await fetch(`${API_URL}/postar_produto`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify(produto)
        });

        const dados = await lerResposta(resposta);

        if (!resposta.ok) {
            throw new Error(
                dados.detail || "Não foi possível cadastrar o produto."
            );
        }

        alert("Produto cadastrado com sucesso!");

        Object.values(campos).forEach(campo => {
            campo.value = "";
        });

        await carregarProdutos();

    } catch (erro) {
        console.error("Erro ao cadastrar produto:", erro);
        alert(erro.message || "Erro ao conectar com a API.");
    }
}

// ======================================
// CARREGAR PRODUTOS
// ======================================

async function carregarProdutos() {
    const container = document.querySelector("#produtos");

    if (!container) {
        console.error("Elemento #produtos não encontrado.");
        return;
    }

    try {
        const resposta = await fetch(`${API_URL}/produtos`);
        const dados = await lerResposta(resposta);

        if (!resposta.ok) {
            throw new Error(
                dados.detail || "Não foi possível carregar os produtos."
            );
        }

        if (!Array.isArray(dados)) {
            throw new Error("A API retornou uma lista de produtos inválida.");
        }

        container.replaceChildren();

        dados.forEach(produto => {
            const card = document.createElement("div");
            card.className = "card";

            const nome = document.createElement("h3");
            nome.textContent = produto.nome ?? "Produto sem nome";
            card.appendChild(nome);

            const preco = document.createElement("p");
            preco.textContent = `Preço: R$ ${produto.preco ?? "0,00"}`;
            card.appendChild(preco);

            const descricao = document.createElement("p");
            descricao.textContent = produto.descrisao ?? "";
            card.appendChild(descricao);

            if (produto.validade) {
                const validade = document.createElement("p");
                validade.textContent = `Validade: ${produto.validade}`;
                card.appendChild(validade);
            }

            if (produto.incluso) {
                const incluso = document.createElement("p");
                incluso.textContent = `Incluso: ${produto.incluso}`;
                card.appendChild(incluso);
            }

            if (produto.mensalidade) {
                const mensalidade = document.createElement("p");
                mensalidade.textContent =
                    `Mensalidade: R$ ${produto.mensalidade}`;
                card.appendChild(mensalidade);
            }

            if (produto.video) {
                try {
                    const url = new URL(produto.video);

                    if (
                        url.protocol === "https:" ||
                        url.protocol === "http:"
                    ) {
                        const video = document.createElement("video");
                        video.className = "video-produto";
                        video.src = url.href;
                        video.controls = true;
                        video.preload = "metadata";
                        video.style.maxWidth = "100%";

                        card.appendChild(video);
                    }
                } catch {
                    console.warn("URL de vídeo inválida:", produto.video);
                }
            }

            container.appendChild(card);
        });

    } catch (erro) {
        console.error("Erro ao carregar produtos:", erro);
        container.textContent = "Não foi possível carregar os produtos.";
    }
}

// ======================================
// IR PARA AVALIAÇÃO
// ======================================

function irParaAvaliacao() {
    const token = localStorage.getItem("token_usuario");

    if (!token) {
        localStorage.setItem("avaliar", "true");
        window.location.href = "login.html";
        return;
    }

    abrirFormularioAvaliacao();
}

// ======================================
// ABRIR FORMULÁRIO DE AVALIAÇÃO
// ======================================

function abrirFormularioAvaliacao() {
    let formulario = document.querySelector("#formularioAvaliacao");

    if (!formulario) {
        formulario = document.createElement("div");
        formulario.id = "formularioAvaliacao";

        const titulo = document.createElement("h3");
        titulo.textContent = "Deixe sua avaliação";

        const nota = document.createElement("select");
        nota.id = "notaAvaliacao";
        nota.required = true;

        const opcaoInicial = document.createElement("option");
        opcaoInicial.value = "";
        opcaoInicial.textContent = "Escolha uma nota";
        nota.appendChild(opcaoInicial);

        for (let i = 1; i <= 5; i++) {
            const opcao = document.createElement("option");
            opcao.value = String(i);
            opcao.textContent = `${i} estrela${i > 1 ? "s" : ""}`;
            nota.appendChild(opcao);
        }

        const comentario = document.createElement("textarea");
        comentario.id = "comentarioAvaliacao";
        comentario.placeholder = "Escreva sua avaliação...";
        comentario.maxLength = 2000;
        comentario.required = true;

        const enviar = document.createElement("button");
        enviar.type = "button";
        enviar.textContent = "Enviar avaliação";
        enviar.addEventListener("click", enviarAvaliacao);

        formulario.append(titulo, nota, comentario, enviar);

        document.body.appendChild(formulario);
    }

    formulario.style.display = "block";
}

// ======================================
// ENVIAR AVALIAÇÃO
// ======================================

async function enviarAvaliacao() {
    const notaCampo = document.querySelector("#notaAvaliacao");
    const comentarioCampo = document.querySelector("#comentarioAvaliacao");

    if (!notaCampo || !comentarioCampo) {
        alert("O formulário de avaliação não foi encontrado.");
        return;
    }

    const nota = Number(notaCampo.value);
    const comentario = comentarioCampo.value.trim();

    if (!Number.isInteger(nota) || nota < 1 || nota > 5) {
        alert("Escolha uma nota entre 1 e 5.");
        return;
    }

    if (!comentario || comentario.length > 2000) {
        alert("Escreva uma avaliação com até 2000 caracteres.");
        return;
    }

    const token = localStorage.getItem("token_usuario");

    if (!token) {
        alert("Faça login como usuário para avaliar.");
        return;
    }

    try {
        const resposta = await fetch(`${API_URL}/avaliacoes`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${token}`
            },
            body: JSON.stringify({
                nota: nota,
                comentario: comentario
            })
        });

        const dados = await lerResposta(resposta);

        if (!resposta.ok) {
            throw new Error(
                dados.detail || "Não foi possível enviar a avaliação."
            );
        }

        alert("Avaliação enviada com sucesso!");

        notaCampo.value = "";
        comentarioCampo.value = "";

        const formulario = document.querySelector("#formularioAvaliacao");

        if (formulario) {
            formulario.style.display = "none";
        }

        await carregarAvaliacoes();

    } catch (erro) {
        console.error("Erro ao enviar avaliação:", erro);
        alert(erro.message || "Erro ao conectar com a API.");
    }
}

// ======================================
// CARREGAR AVALIAÇÕES
// ======================================


async function carregarAvaliacoes() {

    try {

        const resposta =
            await fetch(
                `${API_URL}/avaliacoes`
            );

        if (!resposta.ok) {

            throw new Error(
                "Erro ao buscar avaliações"
            );

        }

        const avaliacoes =
            await resposta.json();

        const lista =
            document.querySelector(
                "#listaAvaliacoes"
            );

        if (!lista) {

            return;

        }

        lista.replaceChildren();

        if (
            !Array.isArray(avaliacoes) ||
            avaliacoes.length === 0
        ) {

            const mensagem =
                document.createElement("p");

            mensagem.textContent =
                "Ainda não temos avaliações. Seja o primeiro a avaliar!";

            lista.appendChild(mensagem);

            return;

        }

        avaliacoes.forEach(
            (avaliacao) => {

                const card =
                    document.createElement("div");

                card.classList.add(
                    "card-avaliacao"
                );

                const nome =
                    document.createElement("h3");

                nome.textContent =
                    String(avaliacao.nome ?? "");

                const nota =
                    document.createElement("p");

                nota.classList.add("nota");

                const valorNota =
                    Number(avaliacao.nota);

                if (
                    Number.isInteger(valorNota) &&
                    valorNota >= 1 &&
                    valorNota <= 5
                ) {

                    nota.textContent =
                        "⭐".repeat(valorNota);

                } else {

                    nota.textContent = "Sem nota";

                }

                const comentario =
                    document.createElement("p");

                comentario.textContent =
                    String(avaliacao.comentario ?? "");

                card.append(
                    nome,
                    nota,
                    comentario
                );

                lista.appendChild(card);

            }
        );

    } catch (erro) {

        console.error(
            "Erro ao carregar avaliações:",
            erro
        );

    }

}



// ======================================
// ABRIR ÁREA DE AVALIAÇÕES
// ======================================

function abrirAvaliacoes() {
    let container = document.querySelector("#listaAvaliacoes");

    if (!container) {
        container = document.createElement("div");
        container.id = "listaAvaliacoes";

        const titulo = document.createElement("h2");
        titulo.textContent = "Avaliações";

        container.appendChild(titulo);
        document.body.appendChild(container);
    }

    container.style.display = "block";

    carregarAvaliacoes();
}

// ======================================
// QUANDO O SITE CARREGAR
// ======================================

window.addEventListener("DOMContentLoaded", () => {
    carregarProdutos();
    carregarAvaliacoes();

    const token = localStorage.getItem("token_usuario");
    const querAvaliar = localStorage.getItem("avaliar");

    if (token && querAvaliar === "true") {
        localStorage.removeItem("avaliar");
        abrirFormularioAvaliacao();
    }
});

// ======================================
// MODO DARK
// ======================================

const botaoDark =
    document.querySelector(
        "#modoDark"
    )


if (botaoDark) {

    botaoDark.addEventListener(
        "click",
        () => {

            document.body.classList.toggle(
                "dark"
            )


            if (
                document.body.classList.contains(
                    "dark"
                )
            ) {

                botaoDark.textContent =
                    "☀️"


                localStorage.setItem(
                    "modoDark",
                    "ativado"
                )

            } else {

                botaoDark.textContent =
                    "🌙"


                localStorage.setItem(
                    "modoDark",
                    "desativado"
                )
            }
        }
    )
}


// ======================================
// RECUPERAR MODO DARK
// ======================================

const modoSalvo =
    localStorage.getItem(
        "modoDark"
    )


if (
    modoSalvo === "ativado"
) {

    document.body.classList.add(
        "dark"
    )


    if (botaoDark) {

        botaoDark.textContent =
            "☀️"
    }
}
