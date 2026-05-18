// frontend/js/api.js

const BASE_URL = "http://localhost:8000";

// Função para pegar o ID do jogador salvo no navegador
function getJogadorId() {
    return localStorage.getItem("jogador_id");
}

// Redireciona para o login se o jogador não estiver autenticado
function verificarAutenticacao() {
    if (!getJogadorId() && !window.location.pathname.endsWith("index.html")) {
        window.location.href = "index.html";
    }
}