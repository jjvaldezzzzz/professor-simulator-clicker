const BASE_URL = "http://localhost:8000";

function getJogadorId() {
    return localStorage.getItem("jogador_id");
}

function setJogadorId(id) {
    localStorage.setItem("jogador_id", String(id));
}

function setIsAdmin(value) {
    localStorage.setItem("is_admin", value ? "true" : "false");
}

function getIsAdmin() {
    return localStorage.getItem("is_admin") === "true";
}

function limparSessao() {
    localStorage.removeItem("jogador_id");
    localStorage.removeItem("saldo");
    localStorage.removeItem("is_admin");
    pararAutoClicker();
}

function setSaldo(valor) {
    if (typeof valor === "number" && !Number.isNaN(valor)) {
        localStorage.setItem("saldo", String(valor));
    }
}

function getSaldo() {
    const raw = localStorage.getItem("saldo");
    if (!raw) return null;
    const valor = Number(raw);
    return Number.isNaN(valor) ? null : valor;
}

function formatMoedas(valor) {
    return Number(valor).toFixed(2);
}

function atualizarSaldoNaTela(valor) {
    const el = document.getElementById("saldo-display");
    if (!el) return;

    if (valor === null || valor === undefined || Number.isNaN(valor)) {
        el.innerText = "--";
        return;
    }

    el.innerText = formatMoedas(valor);
}

async function apiFetch(endpoint, options = {}) {
    const method = options.method || "GET";
    const headers = Object.assign({}, options.headers || {});
    const config = { method, headers };

    if (options.body !== undefined && options.body !== null) {
        config.headers["Content-Type"] = "application/json";
        config.body = JSON.stringify(options.body);
    }

    const response = await fetch(`${BASE_URL}${endpoint}`, config);
    const text = await response.text();
    let data = null;

    if (text) {
        try {
            data = JSON.parse(text);
        } catch (error) {
            data = text;
        }
    }

    if (!response.ok) {
        const detail = data && data.detail ? data.detail : response.statusText || "Erro na API";
        const err = new Error(detail);
        err.status = response.status;
        err.data = data;
        throw err;
    }

    return data;
}

function verificarAutenticacao() {
    if (!getJogadorId() && !window.location.pathname.endsWith("index.html")) {
        window.location.href = "index.html";
        return;
    }

    if (getJogadorId()) {
        iniciarAutoClicker();
    }
}

let autoClickIntervalId = null;
let autoClickEmAndamento = false;

function iniciarAutoClicker() {
    if (autoClickIntervalId || !getJogadorId()) return;

    autoClickIntervalId = setInterval(async () => {
        if (autoClickEmAndamento) return;
        const jogadorId = getJogadorId();
        if (!jogadorId) return;

        autoClickEmAndamento = true;
        try {
            const data = await apiFetch(`/jogo/${jogadorId}/auto-click`, { method: "POST" });
            if (data && typeof data.novo_saldo === "number") {
                setSaldo(data.novo_saldo);
                atualizarSaldoNaTela(data.novo_saldo);
            }
        } catch (error) {
            // Mantem silencioso para nao poluir a UI em caso de falha temporaria
        } finally {
            autoClickEmAndamento = false;
        }
    }, 1000);
}

function pararAutoClicker() {
    if (autoClickIntervalId) {
        clearInterval(autoClickIntervalId);
        autoClickIntervalId = null;
    }
    autoClickEmAndamento = false;
}

async function carregarJogador() {
    const jogadorId = getJogadorId();
    if (!jogadorId) return null;

    try {
        const data = await apiFetch(`/jogadores/${jogadorId}`);
        if (typeof data.saldo === "number") {
            setSaldo(data.saldo);
            atualizarSaldoNaTela(data.saldo);
        }

        const nomeExibicaoEl = document.getElementById("nome-exibicao-atual");
        if (nomeExibicaoEl) {
            nomeExibicaoEl.innerText = data.nome_exibicao || data.nome || "--";
        }

        const nomeCadastroEl = document.getElementById("nome-cadastro");
        if (nomeCadastroEl) {
            nomeCadastroEl.innerText = data.nome || "--";
        }

        const emailEl = document.getElementById("email-display");
        if (emailEl) {
            emailEl.innerText = data.email || "--";
        }
        return data;
    } catch (error) {
        console.error("Falha ao carregar jogador:", error);
        return null;
    }
}