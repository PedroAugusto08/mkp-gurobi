# mkp-gurobi

Implementacao em Python/Gurobi da formulacao ILP para o Problema da Mochila
Multidimensional 0-1 (Multidimensional Knapsack Problem - MKP), usando
instancias publicas da OR-Library.

## Estrutura

```text
data/       Instancias da OR-Library e arquivo de referencias
src/        Codigo-fonte da implementacao
results/    Arquivos gerados pelos experimentos
```

## Escopo

O projeto reproduz a formulacao 0-1 apresentada no artigo
*The Multidimensional Knapsack Problem: Structure and Algorithms*, de
Puchinger, Raidl e Pferschy, resolvendo as instancias com a API Python do
Gurobi.

Nesta implementacao, o foco sera a modelagem ILP:

- variaveis binarias indicando se cada item e escolhido;
- funcao objetivo de maximizacao do lucro total;
- restricoes de capacidade para cada recurso.

Nao sao implementadas metaheuristicas; o solver Gurobi resolve diretamente a
formulacao inteira do MKP.

## Referencias das instancias

O arquivo `mkcbres.txt` contem os melhores valores viaveis conhecidos para as
instancias de Chu e Beasley. Esses valores sao usados como referencia de
comparacao, mas nao devem ser interpretados necessariamente como otimos
provados para todos os casos.

Por isso, o CSV final inclui duas colunas percentuais:

- `gap_to_reference_percent`: positivo quando o valor do Gurobi fica abaixo da
  referencia;
- `improvement_over_reference_percent`: positivo quando o Gurobi encontra valor
  maior que a referencia.

## Execucao

Por padrao, o script usa um subconjunto leve e medio autorizado para os
experimentos: todas as 30 instancias dos arquivos `mknapcb1`, `mknapcb2` e
`mknapcb4`. Assim, sao avaliadas 90 instancias cobrindo os tres grupos de
`alpha`, com limite de tempo padrao de 60 segundos por instancia.

```bash
python src/run_experiments.py --restart
```

Para deixar o limite explicito:

```bash
python src/run_experiments.py --restart --time-limit 60
```

Para executar o subconjunto representativo completo de 81 instancias:

```bash
python src/run_experiments.py --all-sizes --restart --time-limit 60
```

Para executar todas as 270 instancias:

```bash
python src/run_experiments.py --all-instances --restart --time-limit 60
```
