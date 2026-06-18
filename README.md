# mkp-gurobi

Implementacao em Python/Gurobi da formulação ILP para o Problema da Mochila
Multidimensional 0-1 (Multidimensional Knapsack Problem - MKP), usando
instâncias públicas da OR-Library.

## Estrutura

```text
data/       Instâncias da OR-Library e arquivo de referências
src/        Código-fonte da implementação
results/    Arquivos gerados pelos experimentos
```

## Escopo

O projeto reproduz a formulação 0-1 apresentada no artigo
*The Multidimensional Knapsack Problem: Structure and Algorithms*, de
Puchinger, Raidl e Pferschy, resolvendo as instâncias com a API Python do
Gurobi.

Nesta implementação, o foco será a modelagem ILP:

- variáveis binárias indicando se cada item é escolhido;
- função objetivo de maximização do lucro total;
- restrições de capacidade para cada recurso.
