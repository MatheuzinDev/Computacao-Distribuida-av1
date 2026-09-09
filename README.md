# Computação Distribuída - Exercícios I

As respostas das questões, com explicações mais detalhadas, estão em
[`RESPOSTAS.md`](RESPOSTAS.md).

## Como executar o Exercício 1.2

No terminal, na pasta do projeto, instale as dependências:

```powershell
python -m pip install -r requirements.txt
```

Execute somente a parte 1, de cálculo analítico:

```powershell
python analitico.py
```

Execute somente a parte 2, de simulação:

```powershell
python simulador.py --rodadas 100000
```

Para executar as duas partes em sequência:

```powershell
python main.py --rodadas 100000
```

O parâmetro `--rodadas` define quantas rodadas o simulador executa. Os CSVs e os
gráficos gerados ficam na pasta `resultados/`.
