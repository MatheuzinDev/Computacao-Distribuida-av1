"""
Exercicio 1.2 - Executa os experimentos, grava as planilhas (CSV) e gera os
graficos 2D em ex1/resultados/.

Uso:  python main.py [--rodadas 100000]
"""

import argparse
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from analitico import disponibilidade, k_maioria
from simulador import simular

AQUI = os.path.dirname(os.path.abspath(__file__))
SAIDA = os.path.join(AQUI, "resultados")
os.makedirs(SAIDA, exist_ok=True)

NS = [1, 2, 3, 5, 7, 9, 11]                       
PS = [0.50, 0.60, 0.70, 0.80, 0.90, 0.95, 0.99]
P_FINO = np.linspace(0.0, 1.0, 501)               


def politicas(n):
    """k = 1, k = maioria (~n/2) e k = n, sem repetir quando n e pequeno."""
    pares = [("k=1", 1), ("k=maioria", k_maioria(n)), ("k=n", n)]
    vistos, saida = set(), []
    for rotulo, k in pares:
        if k not in vistos:
            vistos.add(k)
            saida.append((rotulo, k))
    return saida


def tabela_analitica():
    linhas = []
    for n in NS:
        for rotulo, k in politicas(n):
            for p in PS:
                linhas.append({"n": n, "politica": rotulo, "k": k, "p": p,
                               "A_analitico": disponibilidade(n, k, p)})
    df = pd.DataFrame(linhas)
    df.to_csv(os.path.join(SAIDA, "tabela1_analitico.csv"), index=False,
              float_format="%.8f")
    # versao "planilha": linhas = (n, politica), colunas = p
    largo = df.pivot_table(index=["n", "politica", "k"], columns="p",
                           values="A_analitico")
    largo.to_csv(os.path.join(SAIDA, "tabela1_analitico_planilha.csv"),
                 float_format="%.6f")
    return df, largo


def tabela_comparativa(rodadas, seed=2024):
    ns = [1, 3, 5, 7, 9]
    ps = [0.50, 0.70, 0.90, 0.95, 0.99]
    linhas = []
    for n in ns:
        for rotulo, k in politicas(n):
            for p in ps:
                a = disponibilidade(n, k, p)
                s = simular(n, k, p, rodadas=rodadas, seed=seed + n * 100 + k * 10)
                lo, hi = s.intervalo_wilson()
                erro = s.frequencia - a
                linhas.append({
                    "n": n, "politica": rotulo, "k": k, "p": p,
                    "A_analitico": a,
                    "A_simulado": s.frequencia,
                    "rodadas": rodadas,
                    "sucessos": s.sucessos,
                    "erro_absoluto": abs(erro),
                    "erro_relativo_pct": (abs(erro) / a * 100) if a > 0 else float("nan"),
                    "IC95_inf": lo, "IC95_sup": hi,
                    "A_dentro_do_IC95": bool(lo <= a <= hi),
                })
    df = pd.DataFrame(linhas)
    df.to_csv(os.path.join(SAIDA, "tabela2_analitico_vs_simulado.csv"),
              index=False, float_format="%.8f")
    return df


def _eixos(titulo, xlabel="p (disponibilidade de um servidor)",
           ylabel="A (disponibilidade do servico)"):
    fig, ax = plt.subplots(figsize=(8, 5.2))
    ax.set_title(titulo)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.grid(alpha=0.3)
    return fig, ax


def _salvar(fig, nome):
    caminho = os.path.join(SAIDA, nome)
    fig.tight_layout()
    fig.savefig(caminho, dpi=150)
    plt.close(fig)
    print("  gravado:", os.path.relpath(caminho, AQUI))


def graficos_analiticos():
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
        _salvar(fig, f"fig5_A_por_n_p{int(p*100)}.png")

def graficos_simulacao(df_cmp, rodadas):
    titulo = "Teoria x pratica: curva analitica e pontos simulados ({} rodadas)".format(
        f"{rodadas:,}".replace(",", "."))
    fig, ax = _eixos(titulo)
    cores = {"k=1": "tab:blue", "k=maioria": "tab:orange", "k=n": "tab:green"}
    n_alvo = 7
    for rotulo, k in politicas(n_alvo):
        ax.plot(P_FINO, [disponibilidade(n_alvo, k, p) for p in P_FINO],
                color=cores[rotulo], label=f"analitico {rotulo} (n={n_alvo})")
    sub = df_cmp[df_cmp["n"] == n_alvo]
    for rotulo, g in sub.groupby("politica"):
        ax.plot(g["p"], g["A_simulado"], "o", ms=9, mfc="none", mew=2,
                color=cores[rotulo], label=f"simulado {rotulo}")
    ax.legend(fontsize=8)
    ax.set_ylim(-0.02, 1.02)
    _salvar(fig, "fig7_teoria_vs_simulacao.png")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rodadas", type=int, default=100_000)
    args = ap.parse_args()

    print("== Exercicio 1.2 - parte 1: calculo analitico ==")
    df_a, largo = tabela_analitica()
    print(largo.round(4).to_string())

    print("\n== Exercicio 1.2 (cont.) - parte 2: simulador estocastico ==")
    df_cmp = tabela_comparativa(args.rodadas)
    mostrar = df_cmp[["n", "politica", "k", "p", "A_analitico", "A_simulado",
                      "erro_absoluto", "A_dentro_do_IC95"]]
    print(mostrar.to_string(index=False, float_format=lambda v: f"{v:.6f}"))

    media = df_cmp["erro_absoluto"].mean()
    maximo = df_cmp["erro_absoluto"].max()
    dentro = int(df_cmp["A_dentro_do_IC95"].sum())
    total = len(df_cmp)
    print(f"\nerro absoluto medio ....: {media:.6f}")
    print(f"erro absoluto maximo ...: {maximo:.6f}")
    print(f"limite tipico 1/sqrt(N) : {1/np.sqrt(args.rodadas):.6f}")
    print(f"configuracoes com A dentro do IC95%: {dentro}/{total} "
          f"({100*dentro/total:.1f}%)")

    print("\n== Graficos ==")
    graficos_analiticos()
    graficos_simulacao(df_cmp, args.rodadas)
    print("\nTudo gravado em:", SAIDA)


if __name__ == "__main__":
    main()
