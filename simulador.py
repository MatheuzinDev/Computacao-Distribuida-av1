"""
Exercicio 1.2 (cont.) - Simulador estocastico (Monte Carlo) da disponibilidade.

Ideia: em vez de calcular a probabilidade pela formula, nos *sorteamos* a
realidade muitas vezes e contamos com que frequencia o servico funcionou.

Para cada rodada:
    1. para cada um dos n servidores, sorteia-se u ~ Uniforme[0, 1);
    2. o servidor e considerado disponivel se u <= p;
    3. conta-se quantos servidores ficaram disponiveis;
    4. a rodada e um "sucesso" se esse total for >= k.

A frequencia experimental de disponibilidade e:

    A_sim = (numero de rodadas bem-sucedidas) / (numero total de rodadas)

Pela Lei dos Grandes Numeros, A_sim -> A(n, k, p) quando o numero de rodadas
cresce. Pelo Teorema Central do Limite, o erro tipico cai com 1/sqrt(rodadas).
"""

import argparse
from dataclasses import dataclass
import os
import random

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analitico import disponibilidade, politicas


AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "resultados")
P_FINO = np.linspace(0.0, 1.0, 501)


@dataclass
class ResultadoSimulacao:
    n: int
    k: int
    p: float
    rodadas: int
    sucessos: int

    @property
    def frequencia(self) -> float:
        return self.sucessos / self.rodadas

def simular(n: int, k: int, p: float, rodadas: int = 100_000,
            seed: int | None = None, tam_lote: int = 200_000) -> ResultadoSimulacao:
    if rodadas <= 0:
        raise ValueError("rodadas deve ser > 0")
    rng = np.random.default_rng(seed)
    sucessos = 0
    restantes = rodadas
    while restantes > 0:
        m = min(tam_lote, restantes)
        sorteios = rng.random((m, n))            
        disponiveis = (sorteios <= p).sum(axis=1)  
        sucessos += int((disponiveis >= k).sum()) 
        restantes -= m
    return ResultadoSimulacao(n=n, k=k, p=p, rodadas=rodadas, sucessos=sucessos)


def simular_didatico(n: int, k: int, p: float, rodadas: int = 10_000,
                     seed: int | None = None) -> ResultadoSimulacao:
    rnd = random.Random(seed)
    sucessos = 0
    for _ in range(rodadas):
        disponiveis = 0
        for _servidor in range(n):
            if rnd.random() <= p:
                disponiveis += 1
        if disponiveis >= k:
            sucessos += 1
    return ResultadoSimulacao(n=n, k=k, p=p, rodadas=rodadas, sucessos=sucessos)


def tabela_comparativa(rodadas: int, seed: int = 2024):
    """Gera a tabela da parte 2, comparando formula e simulacao."""
    ns = [1, 3, 5, 7, 9]
    ps = [0.50, 0.70, 0.90, 0.95, 0.99]
    linhas = []
    for n in ns:
        for rotulo, k in politicas(n):
            for p in ps:
                a = disponibilidade(n, k, p)
                s = simular(n, k, p, rodadas=rodadas, seed=seed + n * 100 + k * 10)
                erro = s.frequencia - a
                linhas.append({
                    "n": n, "politica": rotulo, "k": k, "p": p,
                    "A_analitico": a,
                    "A_simulado": s.frequencia,
                    "rodadas": rodadas,
                    "sucessos": s.sucessos,
                    "erro_absoluto": abs(erro),
                    "erro_relativo_pct": (abs(erro) / a * 100) if a > 0 else float("nan"),
                })
    df = pd.DataFrame(linhas)
    os.makedirs(SAIDA, exist_ok=True)
    df.to_csv(os.path.join(SAIDA, "tabela2_analitico_vs_simulado.csv"),
              index=False, float_format="%.8f")
    return df


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


def grafico_teoria_vs_simulacao(df_cmp, rodadas: int) -> None:
    """Gera o grafico da parte 2 para n=7."""
    titulo = "Teoria x pratica: curva analitica e pontos simulados ({} rodadas)".format(
        f"{rodadas:,}".replace(",", "."))
    fig, ax = _eixos(titulo)
    cores = {"k=1": "tab:blue", "k=maioria": "tab:orange", "k=n": "tab:green"}
    n_alvo = 7
    for rotulo, k in politicas(n_alvo):
        ax.plot(P_FINO, [disponibilidade(n_alvo, k, p) for p in P_FINO],
                color=cores[rotulo], label=f"analitico {rotulo} (n={n_alvo})")
    sub = df_cmp[df_cmp["n"] == n_alvo]
    for rotulo, grupo in sub.groupby("politica"):
        ax.plot(grupo["p"], grupo["A_simulado"], "o", ms=9, mfc="none", mew=2,
                color=cores[rotulo], label=f"simulado {rotulo}")
    ax.legend(fontsize=8)
    ax.set_ylim(-0.02, 1.02)
    _salvar(fig, "fig7_teoria_vs_simulacao.png")


def executar_simulacao(rodadas: int = 100_000) -> None:
    """Executa a parte 2 do Exercício 1.2."""
    print("Exercicio 1.2 (cont.) - parte 2: simulador estocastico")
    df_cmp = tabela_comparativa(rodadas)
    mostrar = df_cmp[["n", "politica", "k", "p", "A_analitico", "A_simulado",
                      "erro_absoluto"]]
    print(mostrar.to_string(index=False, float_format=lambda v: f"{v:.6f}"))

    media = df_cmp["erro_absoluto"].mean()
    maximo = df_cmp["erro_absoluto"].max()
    print(f"\nerro absoluto medio ....: {media:.6f}")
    print(f"erro absoluto maximo ...: {maximo:.6f}")
    print(f"limite tipico 1/sqrt(N) : {1 / np.sqrt(rodadas):.6f}")

    print("\nGraficos")
    grafico_teoria_vs_simulacao(df_cmp, rodadas)
    print("\nTudo gravado em:", SAIDA)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rodadas", type=int, default=100_000)
    args = parser.parse_args()
    executar_simulacao(args.rodadas)


if __name__ == "__main__":
    main()
