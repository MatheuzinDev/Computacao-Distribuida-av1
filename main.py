"""Executa as duas partes do Exercício 1.2."""

import argparse

from analitico import executar_analitico
from simulador import executar_simulacao


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--rodadas", type=int, default=100_000)
    args = parser.parse_args()

    executar_analitico()
    print()
    executar_simulacao(args.rodadas)


if __name__ == "__main__":
    main()
