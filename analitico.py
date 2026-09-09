"""
Exercicio 1.1 e 1.2 (parte 1) - Calculo analitico da disponibilidade de um
servico replicado em n servidores.

Modelo:
    - Sao n servidores replicados, independentes entre si.
    - Cada servidor esta disponivel, num dado instante, com probabilidade p.
    - O servico so e acessado de forma consistente se pelo menos k dos n
      servidores estiverem disponiveis.

Seja X a variavel aleatoria "numero de servidores disponiveis". Como sao n
ensaios de Bernoulli independentes e identicos, X ~ Binomial(n, p):

    P(X = i) = C(n, i) * p^i * (1 - p)^(n - i)

A disponibilidade do servico e a probabilidade de X ser pelo menos k:

    A(n, k, p) = P(X >= k) = SOMA_{i=k}^{n} C(n, i) * p^i * (1 - p)^(n - i)

Casos extremos:
    k = 1 (consulta)     -> A = 1 - (1 - p)^n      (complemento de "todos fora")
    k = n (atualizacao)  -> A = p^n                (todos precisam estar no ar)
"""

from math import comb, fsum
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd


AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "resultados")
NS = [1, 2, 3, 5, 7, 9, 11]
PS = [0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.99]
P_FINO = np.linspace(0.0, 1.0, 501)


def validar(n: int, k: int, p: float) -> None:
    if not isinstance(n, int) or n <= 0:
        raise ValueError(f"n deve ser inteiro > 0 (recebido: {n})")
    if not isinstance(k, int) or not (0 < k <= n):
        raise ValueError(f"k deve ser inteiro com 0 < k <= n (recebido: k={k}, n={n})")
    if not (0.0 <= p <= 1.0):
        raise ValueError(f"p deve estar em [0, 1] (recebido: {p})")


def disponibilidade(n: int, k: int, p: float) -> float:
    """
    Formula geral (quorum de k entre n):

        A(n, k, p) = SOMA_{i=k}^{n} C(n, i) * p^i * (1 - p)^(n - i)

    Somamos a cauda superior da binomial. Usamos math.fsum para reduzir o erro
    de arredondamento acumulado da soma em ponto flutuante.
    """
    validar(n, k, p)
    q = 1.0 - p
    termos = [comb(n, i) * (p ** i) * (q ** (n - i)) for i in range(k, n + 1)]
    return min(1.0, max(0.0, fsum(termos)))
def disponibilidade_consulta(n: int, p: float) -> float:
    validar(n, 1, p)
    return 1.0 - (1.0 - p) ** n

def disponibilidade_atualizacao(n: int, p: float) -> float:
    validar(n, n, p)
    return p ** n

def k_maioria(n: int) -> int:
    return n // 2 + 1


def politicas(n: int) -> list[tuple[str, int]]:
    """Retorna as politicas k=1, maioria e k=n, sem repeticoes."""
    pares = [("k=1", 1), ("k=maioria", k_maioria(n)), ("k=n", n)]
    vistos, saida = set(), []
    for rotulo, k in pares:
        if k not in vistos:
            vistos.add(k)
            saida.append((rotulo, k))
    return saida


def politicas_k(n: int) -> dict:
    return {"k=1 (consulta)": 1, "k=maioria (~n/2)": k_maioria(n), "k=n (atualizacao)": n}

def _autoteste() -> None:
    for n in range(1, 26):
        for p in [0.0, 0.01, 0.25, 0.5, 0.75, 0.9, 0.99, 1.0]:
            assert abs(disponibilidade(n, 1, p) - disponibilidade_consulta(n, p)) < 1e-12
            assert abs(disponibilidade(n, n, p) - disponibilidade_atualizacao(n, p)) < 1e-12
            valores = [disponibilidade(n, k, p) for k in range(1, n + 1)]
            assert all(valores[i] >= valores[i + 1] - 1e-12 for i in range(len(valores) - 1))
    assert disponibilidade(1, 1, 0.9) == 0.9
    assert abs(disponibilidade(3, 2, 0.9) - (3 * 0.81 * 0.1 + 0.729)) < 1e-12


def _eixos(titulo: str, xlabel: str = "p (disponibilidade de um servidor)",
           ylabel: str = "A (disponibilidade do servico)"):
    fig, ax = plt.subplots(figsize=(8, 5.2))
    ax.set_title(titulo)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3)
    return fig, ax


def _salvar(fig, nome: str) -> None:
    os.makedirs(SAIDA, exist_ok=True)
    caminho = os.path.join(SAIDA, nome)
    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)
    print("  gravado:", os.path.relpath(caminho, AQUI))


def tabela_analitica():
    """Gera as duas tabelas CSV da parte analitica."""
    linhas = []
    for n in NS:
        for rotulo, k in politicas(n):
            for p in PS:
                linhas.append({"n": n, "politica": rotulo, "k": k, "p": p,
                               "A_analitico": disponibilidade(n, k, p)})
    df = pd.DataFrame(linhas)
    os.makedirs(SAIDA, exist_ok=True)
    df.to_csv(os.path.join(SAIDA, "tabela1_analitico.csv"), index=False,
              float_format="%.8f")
    largo = df.pivot_table(index=["n", "politica", "k"], columns="p",
                           values="A_analitico")
    largo.to_csv(os.path.join(SAIDA, "tabela1_analitico_planilha.csv"),
                 float_format="%.6f")
    return df, largo


def graficos_analiticos() -> None:
    fig, ax = _eixos("Caso k = 1 (consulta): A = 1 - (1-p)^n\nreplicar aumenta a disponibilidade")
    for n in NS:
        ax.plot(P_FINO, [disponibilidade(n, 1, p) for p in P_FINO], label=f"n = {n}")
    ax.legend(ncol=2)
    ax.set_ylim(-0.02, 1.02)
    _salvar(fig, "fig1_k1_consulta.png")

    fig, ax = _eixos("Caso k = n (atualizacao): A = p^n\nreplicar reduz a disponibilidade")
    for n in NS:
        ax.plot(P_FINO, [disponibilidade(n, n, p) for p in P_FINO], label=f"n = {n}")
    ax.legend(ncol=2)
    ax.set_ylim(-0.02, 1.02)
    _salvar(fig, "fig2_kn_atualizacao.png")

    fig, ax = _eixos("Caso k = maioria (~n/2): efeito limiar em p = 0,5")
    for n in [1, 3, 5, 7, 9, 11, 21, 51]:
        ax.plot(P_FINO, [disponibilidade(n, k_maioria(n), p) for p in P_FINO],
                label=f"n = {n} (k={k_maioria(n)})")
    ax.axvline(0.5, color="k", ls=":", lw=1)
    ax.legend(ncol=2, fontsize=8)
    ax.set_ylim(-0.02, 1.02)
    _salvar(fig, "fig3_maioria_limiar.png")

    fig, ax = _eixos("Disponibilidade x p, para n = 1, 2, ... e k = 1 / k = n")
    for i, n in enumerate([1, 2, 3, 5, 9]):
        cor = plt.cm.viridis(i / 4)
        ax.plot(P_FINO, [disponibilidade(n, 1, p) for p in P_FINO], color=cor,
                ls="-", label=f"n={n}, k=1")
        ax.plot(P_FINO, [disponibilidade(n, n, p) for p in P_FINO], color=cor,
                ls="--", label=f"n={n}, k=n")
    ax.legend(ncol=2, fontsize=8)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    _salvar(fig, "fig4_enunciado_k1_vs_kn.png")

    for p in [0.90, 0.99]:
        fig, ax = _eixos(f"Disponibilidade x numero de servidores (p = {p})",
                         xlabel="n (numero de servidores)")
        ns = list(range(1, 26))
        ax.plot(ns, [disponibilidade(n, 1, p) for n in ns], "o-", label="k = 1")
        ax.plot(ns, [disponibilidade(n, k_maioria(n), p) for n in ns], "s-", label="k = maioria")
        ax.plot(ns, [disponibilidade(n, n, p) for n in ns], "^-", label="k = n")
        ax.legend()
        ax.set_ylim(-0.02, 1.02)
        _salvar(fig, f"fig5_A_por_n_p{int(p * 100)}.png")


def executar_analitico() -> None:
    """Executa a parte 1 do Exercício 1.2."""
    print("Exercicio 1.2 - parte 1: calculo analitico")
    _, largo = tabela_analitica()
    print(largo.round(4).to_string())
    print("\nGraficos")
    graficos_analiticos()
    print("\nTudo gravado em:", SAIDA)


if __name__ == "__main__":
    _autoteste()
    executar_analitico()
