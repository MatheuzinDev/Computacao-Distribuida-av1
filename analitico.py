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

if __name__ == "__main__":
    _autoteste()
