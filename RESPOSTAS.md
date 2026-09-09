# Computação Distribuída: Exercícios I (1.1 e 1.2)

Prof. Nabor C. Mendonça, Universidade de Fortaleza
Aluno: Matheus Diógenes Amorim - 2310277

---

# Exercício 1.1: Deduzir a fórmula da disponibilidade

## A pergunta que o exercício faz

Você tem `n` servidores fazendo a mesma coisa (são cópias, réplicas).
Cada um pode estar **ligado** ou **caído**.
O serviço só funciona se pelo menos `k` deles estiverem ligados.

**Pergunta: qual a chance do serviço estar funcionando agora?**

Os três ingredientes:

| | O que é | Exemplo |
|---|---|---|
| `n` | quantos servidores existem | `n = 3` |
| `k` | quantos precisam estar ligados para o serviço funcionar | `k = 2` |
| `p` | chance de **um** servidor estar ligado | `p = 0,9` (ele está no ar 90% do tempo) |

## Passo 1: pense em cada servidor como uma moeda viciada

Jogar a moeda = olhar o servidor agora. Ela cai:

- **cara** (ligado) com chance `p = 0,9`
- **coroa** (caído) com chance `1 − p = 0,1`

Com `n` servidores você joga `n` moedas ao mesmo tempo.
A pergunta vira: **qual a chance de sair pelo menos `k` caras?**

## Passo 2: vamos com 3 servidores (n = 3, p = 0,9)

Cada servidor está Ligado (L) ou Caído (C). Com 3 servidores existem 8 combinações
possíveis. A chance de cada uma sai **multiplicando**, porque um servidor não
interfere no outro:

| Combinação | Quantos ligados | Conta | Chance |
|---|---|---|---|
| L L L | 3 | 0,9 × 0,9 × 0,9 | **0,729** |
| L L C | 2 | 0,9 × 0,9 × 0,1 | 0,081 |
| L C L | 2 | 0,9 × 0,1 × 0,9 | 0,081 |
| C L L | 2 | 0,1 × 0,9 × 0,9 | 0,081 |
| L C C | 1 | 0,9 × 0,1 × 0,1 | 0,009 |
| C L C | 1 | 0,1 × 0,9 × 0,1 | 0,009 |
| C C L | 1 | 0,1 × 0,1 × 0,9 | 0,009 |
| C C C | 0 | 0,1 × 0,1 × 0,1 | **0,001** |

Somando as 8 linhas dá exatamente 1,000. Isso mostra que cobrimos todos os casos possíveis.

**Duas coisas importantes de reparar:**

1. As três linhas com "2 ligados" têm **a mesma chance** (0,081). Só muda *qual*
   servidor caiu. Então dá para juntar: chance de ter exatamente 2 ligados = **3 × 0,081 = 0,243**.
2. Esse **3** é só a contagem de *de quantos jeitos diferentes* isso pode acontecer.
   É exatamente isso que a notação `C(n, i)` significa: **"quantas combinações têm `i` ligados"**.
   Nada mais que isso.

A tabela de 8 linhas fica resumida em 4:

| Ligados | De quantos jeitos | Chance total |
|---|---|---|
| 3 | 1 | 0,729 |
| 2 | 3 | 0,243 |
| 1 | 3 | 0,027 |
| 0 | 1 | 0,001 |

## Passo 3: agora é só somar as linhas que interessam

**Se `k = 3`** (preciso dos 3 ligados) → só serve a primeira linha:

```
A = 0,729        que é 0,9 × 0,9 × 0,9  =  p³  =  pⁿ
```

**Se `k = 2`** (preciso de pelo menos 2) → somo as linhas de 3 e de 2 ligados:

```
A = 0,729 + 0,243 = 0,972
```

**Se `k = 1`** (basta 1 ligado) → somo as linhas de 3, 2 e 1:

```
A = 0,729 + 0,243 + 0,027 = 0,999
```

Aqui tem um atalho: em vez de somar 3 linhas, é mais fácil olhar **o que sobra**.
A única forma do serviço cair é os 3 caírem juntos (chance 0,001). Então:

```
A = 1 − 0,001 = 0,999        que é 1 − (1−p)ⁿ
```

## Passo 4: a fórmula geral

Tudo que fizemos foi: **listar em quantos servidores podem estar ligados, calcular a
chance de cada situação, e somar da linha `k` para cima.**

Escrito de forma compacta:

```
                       n
A(n, k, p)  =          Σ    C(n, i) · pⁱ · (1 − p)ⁿ⁻ⁱ
                      i=k
```

Traduzindo pedaço por pedaço:

| Pedaço | Significa |
|---|---|
| `pⁱ` | os `i` servidores ligados estão todos ligados |
| `(1−p)ⁿ⁻ⁱ` | os outros `n − i` estão todos caídos |
| `C(n, i)` | de quantos jeitos isso pode acontecer (foi o "3" da nossa tabela) |
| somar de `i = k` até `n` | "pelo menos k" quer dizer k, **ou** k+1, **ou** k+2... até n |

E os dois casos extremos que o enunciado manda deduzir primeiro são só atalhos dessa
mesma fórmula:

| Caso | Por quê | Fórmula |
|---|---|---|
| **`k = 1`** (consulta / leitura) | só cai se **todos** caírem | `A = 1 − (1 − p)ⁿ` |
| **`k = n`** (atualização / escrita) | precisa de **todos** ligados | `A = pⁿ` |

---

# Exercício 1.2 (parte 1): Cálculo analítico

Código: [`analitico.py`](analitico.py) · Resultados: `resultados/tabela1_analitico.csv`

Programação da fórmula passando   vários valores de `n`, `k` e `p`.

## Tabela: disponibilidade A(n, k, p)

As três políticas comparadas, como o enunciado pede: `k = 1`, `k ≈ n/2` (maioria) e `k = n`.

| n | política | k | p=0,50 | p=0,60 | p=0,70 | p=0,80 | p=0,90 | p=0,95 | p=0,99 |
|--:|---|--:|--:|--:|--:|--:|--:|--:|--:|
| 1 | k=1 | 1 | 0,5000 | 0,6000 | 0,7000 | 0,8000 | 0,9000 | 0,9500 | 0,9900 |
| 2 | k=1 | 1 | 0,7500 | 0,8400 | 0,9100 | 0,9600 | 0,9900 | 0,9975 | 0,9999 |
| 2 | k=maioria | 2 | 0,2500 | 0,3600 | 0,4900 | 0,6400 | 0,8100 | 0,9025 | 0,9801 |
| 3 | k=1 | 1 | 0,8750 | 0,9360 | 0,9730 | 0,9920 | 0,9990 | 0,9999 | 1,0000 |
| 3 | k=maioria | 2 | 0,5000 | 0,6480 | 0,7840 | 0,8960 | 0,9720 | 0,9928 | 0,9997 |
| 3 | k=n | 3 | 0,1250 | 0,2160 | 0,3430 | 0,5120 | 0,7290 | 0,8574 | 0,9703 |
| 5 | k=1 | 1 | 0,9688 | 0,9898 | 0,9976 | 0,9997 | 1,0000 | 1,0000 | 1,0000 |
| 5 | k=maioria | 3 | 0,5000 | 0,6826 | 0,8369 | 0,9421 | 0,9914 | 0,9988 | 1,0000 |
| 5 | k=n | 5 | 0,0312 | 0,0778 | 0,1681 | 0,3277 | 0,5905 | 0,7738 | 0,9510 |
| 7 | k=1 | 1 | 0,9922 | 0,9984 | 0,9998 | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| 7 | k=maioria | 4 | 0,5000 | 0,7102 | 0,8740 | 0,9667 | 0,9973 | 0,9998 | 1,0000 |
| 7 | k=n | 7 | 0,0078 | 0,0280 | 0,0824 | 0,2097 | 0,4783 | 0,6983 | 0,9321 |
| 9 | k=1 | 1 | 0,9980 | 0,9997 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| 9 | k=maioria | 5 | 0,5000 | 0,7334 | 0,9012 | 0,9804 | 0,9991 | 1,0000 | 1,0000 |
| 9 | k=n | 9 | 0,0020 | 0,0101 | 0,0404 | 0,1342 | 0,3874 | 0,6302 | 0,9135 |
| 11 | k=1 | 1 | 0,9995 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 | 1,0000 |
| 11 | k=maioria | 6 | 0,5000 | 0,7535 | 0,9218 | 0,9883 | 0,9997 | 1,0000 | 1,0000 |
| 11 | k=n | 11 | 0,0005 | 0,0036 | 0,0198 | 0,0859 | 0,3138 | 0,5688 | 0,8953 |

## O que a tabela está dizendo

### 1. Colocar mais servidores pode ajudar ou atrapalhar: depende do `k`

Olhe só a coluna `p = 0,90`, comparando 1 servidor com 9 servidores:

| Política | com 1 servidor | com 9 servidores | resultado |
|---|---|---|---|
| `k = 1` (basta um) | 0,9000 | 0,9999999 | melhorou muito |
| `k = maioria` (5 de 9) | 0,9000 | 0,9991 | melhorou |
| `k = n` (todos) | 0,9000 | **0,3874** | **piorou muito** |

São os **mesmos** 9 servidores nos três casos. Só muda a exigência.

Por quê? Porque `n` aparece nas duas fórmulas com efeitos opostos:
`1 − (1−p)ⁿ` **cresce** quando `n` cresce, mas `pⁿ` **encolhe** quando `n` cresce
(é multiplicar por 0,9 várias vezes seguidas).

### 2. Com `k = 1`, cada servidor extra ajuda menos que o anterior

A chance de **cair** é `(1−p)ⁿ`. Cada servidor novo multiplica essa chance por `(1−p)`.
Com `p = 0,9` a chance de queda vai de 10% → 1% → 0,1% → 0,01%...

Só que, em ganho real:

- de 1 para 2 servidores: ganha 9 pontos percentuais
- de 8 para 9 servidores: ganha menos de 0,00001

**Na prática:** o custo cresce em linha reta (cada servidor custa o mesmo), mas o ganho
vira quase nada. É por isso que os sistemas reais usam 3 ou 5 réplicas, e não 20.

### 3. Exigir `k = n` (todos) é o pior projeto possível

`A = pⁿ` transforma redundância em fragilidade: basta **um** servidor cair para o
serviço inteiro parar. Com servidores muito bons (`p = 0,99`) e `n = 11`, a
disponibilidade despenca para **0,8953**. Isso equivale a quase 1 dia fora do ar a cada 10 dias.

Por isso sistemas reais **não** exigem que a escrita chegue em todas as réplicas de uma
vez de forma síncrona.

<!-- ### 4. A maioria tem um comportamento curioso: um "ponto de virada" em p = 0,5

Repare na coluna `p = 0,50`: a linha da maioria dá **exatamente 0,5000 para todo n ímpar**
(n=3, 5, 7, 9 e 11, todos com 0,5000). Não é coincidência.

Se cada servidor é uma moeda honesta, "ter maioria ligada" e "ter maioria caída" são
situações igualmente prováveis. Empate perfeito, não importa quantos servidores.

E aí:

- se `p` for **maior** que 0,5 → colocar mais servidores empurra a disponibilidade **para 1**
  (`n=3, p=0,7` → 0,7840, mas `n=11, p=0,7` → 0,9218)
- se `p` for **menor** que 0,5 → colocar mais servidores empurra **para 0**
- exatamente em `p = 0,5` → fica travado em 0,5 para sempre

É por isso que, no gráfico `fig3`, as curvas vão ficando cada vez mais parecidas com um
**degrau** conforme `n` aumenta. Com muitos servidores, ou quase sempre tem maioria, ou
quase nunca tem. O meio-termo some. -->

### 4. Conclusão prática: separe a exigência da leitura da exigência da escrita

Com `n = 5` e `p = 0,9`:

| Operação | Exigência | Disponibilidade |
|---|---|---|
| ler de 1 réplica | `k = 1` | 0,99999 |
| escrever em 3 réplicas | `k = 3` | 0,9914 |
| escrever em 5 réplicas | `k = 5` | 0,5905 |

Dá para ter consistência **e** alta disponibilidade ao mesmo tempo, desde que não se
exija *todas* as réplicas. Essa é exatamente a ideia dos sistemas de quórum
(a regra `R + W > n`, que garante que o grupo de leitura e o de escrita sempre têm ao
menos uma réplica em comum).

## Gráficos gerados (pasta `resultados/`)

| Arquivo | O que mostra |
|---|---|
| `fig1_k1_consulta.png` | `k = 1`: quanto mais servidores, melhor |
| `fig2_kn_atualizacao.png` | `k = n`: quanto mais servidores, pior |
| `fig3_maioria_limiar.png` | maioria: o degrau se formando em `p = 0,5` |
| `fig4_enunciado_k1_vs_kn.png` | reproduz a figura do slide (k=1 sólido, k=n tracejado) |
| `fig5_A_por_n_p90.png` / `_p99.png` | disponibilidade × número de servidores |
| `fig7_teoria_vs_simulacao.png` | valores analíticos e simulados lado a lado |

---

# Exercício 1.2 (cont.): Simulador estocástico

Código: [`simulador.py`](simulador.py) · Resultados: `resultados/tabela2_analitico_vs_simulado.csv`

## A ideia: em vez de calcular, testar

Na parte 1 nós **calculamos** a probabilidade com a fórmula.
Aqui fazemos o contrário: **simulamos a realidade muitas vezes e contamos** quantas
vezes deu certo. É a diferença entre calcular que uma moeda dá cara em 50% das vezes e
jogar a moeda 100.000 vezes para ver o que acontece.

Uma "rodada" é uma fotografia do sistema num instante. Em cada rodada:

1. para **cada** servidor, sorteia-se um número aleatório entre 0 e 1;
2. se o número sorteado for **≤ p**, o servidor está ligado; senão, está caído;
3. conta-se quantos ficaram ligados;
4. se esse total for **≥ k**, a rodada foi um **sucesso**.

No fim:

```
disponibilidade experimental = número de sucessos ÷ número de rodadas
```

> **Por que o passo 2 funciona?** Se você sorteia um número qualquer entre 0 e 1, a
> chance dele cair abaixo de 0,9 é... 90%. Exatamente o `p` que queríamos.

O código tem duas versões, que fazem a mesma coisa:

- `simular_didatico()`: dois laços `for` explícitos, escrito literalmente igual ao
  texto do enunciado (fácil de ler, lento);
- `simular()`: mesma lógica usando NumPy, sorteando uma tabela inteira de números de
  uma vez (ilegível para iniciante, mas ~100× mais rápido). É a usada nos experimentos.

## Comparação: fórmula × simulação (100.000 rodadas)

| n | política | k | p | fórmula | simulação | diferença |
|--:|---|--:|--:|--:|--:|--:|
| 1 | k=1 | 1 | 0,50 | 0,500000 | 0,498840 | 0,001160 |
| 3 | k=maioria | 2 | 0,70 | 0,784000 | 0,779800 | 0,004200 |
| 3 | k=n | 3 | 0,90 | 0,729000 | 0,726790 | 0,002210 |
| 5 | k=maioria | 3 | 0,90 | 0,991440 | 0,991720 | 0,000280 |
| 5 | k=n | 5 | 0,50 | 0,031250 | 0,030690 | 0,000560 |
| 7 | k=1 | 1 | 0,90 | 1,000000 | 1,000000 | 0,000000 |
| 7 | k=n | 7 | 0,90 | 0,478297 | 0,476600 | 0,001697 |
| 9 | k=maioria | 5 | 0,50 | 0,500000 | 0,503450 | 0,003450 |
| 9 | k=n | 9 | 0,95 | 0,630249 | 0,626990 | 0,003259 |

(A tabela completa, com as 65 configurações, está no CSV.)

Resumo geral:

```
diferença média ........: 0,000638
diferença máxima .......: 0,004200
margem esperada (1/√N) .: 0,003162
```

## O que esses resultados mostram

- A simulação ficou próxima da fórmula. A diferença média foi `0,000638`.
- Pequenas diferenças são normais, pois cada rodada depende de sorteio.
- Os maiores desvios aparecem quando o resultado fica perto de 0,5. Quando ele está perto
  de 0 ou 1, a simulação costuma variar menos.
- Para este caso, a fórmula é mais rápida e exata. A simulação é útil quando o modelo fica
  mais complexo, por exemplo, com servidores de confiabilidades diferentes ou falhas ligadas.


# Como executar

O projeto requer Python 3.10 ou superior.

Instale as dependências externas:

```powershell
python -m pip install -r requirements.txt
```

Para executar somente a parte 1, de cálculo analítico:

```powershell
python analitico.py
```

Para executar somente a parte 2, de simulação:

```powershell
python simulador.py --rodadas 100000
```

Para executar as duas partes em sequência:

```powershell
python main.py --rodadas 100000
```

O argumento `--rodadas` define quantas execuções são usadas em cada simulação. Se ele
for omitido, o programa usa 100.000 rodadas.

## Arquivos CSV gerados

Os arquivos abaixo são recriados pelos comandos de cada parte.

| Arquivo | Gerado por | Conteúdo |
|---|---|---|
| `tabela1_analitico.csv` | `analitico.py` | Cada linha representa uma combinação de `n`, política, `k` e `p`; a coluna `A_analitico` contém a disponibilidade calculada pela fórmula. É adequado para filtrar e analisar dados com ferramentas como Pandas. |
| `tabela1_analitico_planilha.csv` | `analitico.py` | Contém os mesmos cálculos analíticos, mas cada valor de `p` é uma coluna. É mais fácil de visualizar em Excel ou LibreOffice. |
| `tabela2_analitico_vs_simulado.csv` | `simulador.py` | Coloca o valor analítico e o simulado lado a lado. Também registra rodadas, sucessos e erros. |

| Arquivo | O que faz |
|---|---|
| `analitico.py` | calcula a disponibilidade e executa a parte 1 |
| `simulador.py` | executa a parte 2 e compara fórmula com simulação |
| `main.py` | executa as duas partes do Exercício 1.2 |
| `resultados/` | as planilhas e os gráficos gerados |
