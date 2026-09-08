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

from dataclasses import dataclass
from math import sqrt
import random

import numpy as np


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

    @property
    def erro_padrao(self) -> float:
        f = self.frequencia
        return sqrt(max(f * (1.0 - f), 0.0) / self.rodadas)

    def intervalo_wilson(self, z: float = 1.96) -> tuple:
        """
        Intervalo de confianca de 95% (Wilson). Preferido ao intervalo normal
        simples porque continua valido quando f fica proximo de 0 ou de 1 -
        exatamente o que acontece nos casos p alto / p baixo deste exercicio.
        """
        N, f = self.rodadas, self.frequencia
        denom = 1.0 + z * z / N
        centro = (f + z * z / (2 * N)) / denom
        margem = (z * sqrt(f * (1 - f) / N + z * z / (4 * N * N))) / denom
        return (max(0.0, centro - margem), min(1.0, centro + margem))


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


if __name__ == "__main__":
    from analitico import disponibilidade

    print(f"{'n':>3} {'k':>3} {'p':>5} {'analitico':>10} {'simulado':>10} {'erro':>9}")
    for (n, k, p) in [(1, 1, 0.9), (5, 1, 0.9), (5, 3, 0.9), (5, 5, 0.9), (10, 6, 0.6)]:
        a = disponibilidade(n, k, p)
        s = simular(n, k, p, rodadas=200_000, seed=42)
        print(f"{n:>3} {k:>3} {p:>5.2f} {a:>10.6f} {s.frequencia:>10.6f} {abs(a - s.frequencia):>9.6f}")
