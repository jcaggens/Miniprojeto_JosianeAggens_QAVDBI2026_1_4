# Miniprojeto_JosianeAggens_QAVDBI2026_1_4

Mini-Projeto Avaliativo do Módulo 1 - Análise Exploratória de Dados de Varejo com Python e Pandas. Curso de Visualização de Dados e Business Intelligence.

**Aluna:** Josiane Cristine Aggens  
**Turma:** QAVDBI2026_1_4

---

## 1. Objetivo

Fazer uma Análise Exploratória de Dados (AED) de uma base real de compras de varejo usando Python e pandas: carregar os dados, encontrar problemas de qualidade, limpar, calcular estatísticas, fazer agrupamentos e tirar conclusões. No final a base limpa é salva em `df_limpo.csv`.

## 2. Base de dados

- Fonte: Kaggle - [Base Varejo](https://www.kaggle.com/datasets/namespaiva/base-varejo/data)
- Arquivo usado: `dados/Base Varejo.csv`
- Tamanho original: **830.000 linhas** e 14 colunas (10 com dados + 4 vazias por causa do `;;;;` no fim das linhas)
- Cada linha é **um produto dentro de uma compra**. Uma compra tem várias linhas.

| Coluna | O que é (pelo que deu para entender dos dados) |
|---|---|
| `DATA` | Data da compra |
| `CO_ID` | Número da compra |
| `CL_ID` | Código do cliente |
| `CL_GENERO` | Gênero do cliente (F / M) |
| `CL_EC` | Estado civil (códigos 1 a 5, sem dicionário) |
| `CL_FHL` | Número de filhos (0 a 4) |
| `CL_SEG` | Segmento do cliente (A, B, C, sem dicionário) |
| `PR_ID` | Código do produto |
| `PR_CAT` | Categoria do produto |
| `PR_NOME` | Nome do produto |

> A base **não tem coluna de preço/valor nem de quantidade**, então não foi possível calcular faturamento.

##  Etapas da análise

O script é dividido em funções, uma para cada etapa:

1. `carregar_dados` - lê o CSV e mostra linhas, colunas, tipos, primeiras linhas e `df.info()`.
2. `diagnosticar_dados` - procura nulos, `#N/D`, textos vazios, espaços, duplicatas, problemas de data e de números.
3. `limpar_dados` - faz a limpeza numa cópia (`df_limpo`), sem alterar a base original.
4. `calcular_estatisticas` - estatísticas do número de filhos (`CL_FHL`).
5. `analisar_agrupamentos` - agrupamentos por gênero e por categoria com `groupby`.
   `analises_extras` - compras por ano/mês e uma `pivot_table` de categoria x gênero.
6. `exportar_dados` - salva `df_limpo.csv` e confere o arquivo lendo de novo.
7. `gerar_conclusoes` - mostra os insights e as limitações.

##  Problemas de qualidade encontrados

| Problema | Onde | Quantidade |
|---|---|---|
| Colunas totalmente vazias | `Unnamed: 10` a `Unnamed: 13` | 4 colunas (100% nulas) |
| Nulo "disfarçado" (`#N/D`, vindo do Excel) | `PR_CAT` e `PR_NOME` (todas do produto `PR_ID` 107) | 3.650 linhas |
| Linhas totalmente duplicadas | mesma compra + mesmo produto | 96.553 linhas (11,6%) |
| Datas com formatos misturados | `DATA` | 484.735 linhas em dia/mês e o resto em mês/dia |

Não foram encontrados: textos vazios, espaços sobrando, números guardados como texto ou valores negativos.

**Sobre as datas:** o arquivo está em ordem de compra, mas lendo tudo como dia/mês as datas ficavam fora de ordem. Olhando a sequência, por exemplo `01/02/2019`, `01/09/2019`, `13/01/2019`, `19/01/2019`, deu para perceber que quando o primeiro número é até 12 a data está em **mês/dia/ano** (`01/02/2019` = 2 de janeiro), e quando é maior que 12 está em **dia/mês/ano**. Corrigindo assim, as datas ficam em ordem crescente no arquivo inteiro.

## Decisões de limpeza e justificativas

| # | O que foi feito | Quantidade | Justificativa |
|---|---|---|---|
| 1 | Remover as 4 colunas vazias | 4 colunas | Não têm nenhum dado |
| 2 | `str.strip()` nas colunas de texto | 0 alterações | Garantir que não ficam espaços sobrando |
| 3 | `#N/D` em `PR_CAT` → `"Sem Categoria"` | 3.650 | Pedido na atividade. As linhas não foram apagadas porque compra, cliente e data estão corretos |
| 4 | `#N/D` em `PR_NOME` → `"Sem Nome"` | 3.650 | Mesmo motivo |
| 5 | Converter `DATA` para datetime corrigindo os dois formatos | 0 datas inválidas | Necessário para análises por data. Período final: 02/01/2019 a 19/08/2022 |
| 6 | Remover linhas 100% duplicadas | 96.553 | Uma compra ter várias linhas é normal (uma por produto), mas a linha inteira repetida foi tratada como registro repetido. Como não existe coluna de quantidade, cada produto é contado uma vez por compra |
| 7 | Conferir os tipos | - | IDs e códigos já eram inteiros (`int64`), textos viraram `string` e `DATA` virou `datetime64` |
| 8 | Validar o número da compra (`CO_ID`) | 0 problemas | Ver abaixo |

**Regra do número da compra (`CO_ID`)** - verificado no script:

- todo `CO_ID` é número inteiro positivo (0 inválidos);
- cada compra tem **um único cliente** e **uma única data** (0 compras com mais de um);
- o número da compra **cresce junto com a data** (0 compras com data menor que a anterior).

Todos os registros seguem a regra, então nenhum precisou ser separado. Total de **18.471 compras**.

**Antes:** 830.000 linhas e 14 colunas → **Depois:** 733.447 linhas e 10 colunas.

## Estatísticas do número de filhos (`CL_FHL`)

A coluna já era inteira e sem nulos, então nada foi convertido ou excluído. Como cada cliente aparece em várias linhas, o cálculo principal foi feito com **uma linha por cliente** (1.000 clientes). O cálculo com todas as linhas aparece só para comparar.

| Estatística | Por cliente | Por linha (itens) |
|---|---|---|
| Média | 1,136 | 1,146 |
| Mediana | 0 | 0 |
| Desvio padrão (amostral) | 1,4133 | 1,4169 |
| Moda | 0 | 0 |
| Máximo | 4 | 4 |
| Mínimo | 0 | 0 |
| Contagem | 1.000 | 733.447 |

Distribuição dos clientes: 0 filhos = 52,7% | 1 = 12,5% | 2 = 13,0% | 3 = 12,1% | 4 = 9,7%.

**Interpretação:** mais da metade dos clientes não tem filhos, por isso a moda e a mediana são 0. A média (1,136) é maior que a mediana porque os clientes com 1 a 4 filhos puxam a média para cima. O desvio padrão é maior que a média, mostrando que os valores são bem espalhados.

## Resultados dos agrupamentos

Medidas usadas: **itens** = linhas da base limpa, **compras** = `CO_ID` diferentes, **clientes** = `CL_ID` diferentes.

**Agrupamento 1 - por gênero**

| Gênero | Itens | Compras | Clientes | % das compras | Compras por cliente | Itens por compra |
|---|---|---|---|---|---|---|
| F | 382.427 | 9.615 | 519 | 52,1 | 18,53 | 39,77 |
| M | 351.020 | 8.856 | 481 | 47,9 | 18,41 | 39,64 |

**Agrupamento 2 - por categoria de produto**

| Categoria | Itens | Compras com a categoria | Produtos diferentes | % dos itens | % das compras |
|---|---|---|---|---|---|
| ALIMENTOS | 384.197 | 18.267 | 120 | 52,4 | 98,9 |
| HIGIENE | 137.702 | 17.610 | 43 | 18,8 | 95,3 |
| LIMPEZA | 128.632 | 17.475 | 40 | 17,5 | 94,6 |
| BEBIDAS | 38.264 | 14.735 | 12 | 5,2 | 79,8 |
| PET | 28.553 | 13.495 | 9 | 3,9 | 73,1 |
| ACESSORIOS | 12.871 | 9.224 | 4 | 1,8 | 49,9 |
| Sem Categoria | 3.228 | 3.228 | 1 | 0,4 | 17,5 |

**Extra 1 - compras por ano**

| Ano | Compras | Itens | Clientes | Meses com dados | Compras por mês |
|---|---|---|---|---|---|
| 2019 | 4.483 | 176.103 | 986 | 12 | 373,6 |
| 2020 | 4.794 | 192.804 | 990 | 12 | 399,5 |
| 2021 | 5.505 | 216.813 | 995 | 12 | 458,8 |
| 2022 | 3.689 | 147.727 | 975 | 8 | 461,1 |

Mês com mais compras: outubro/2021 (686). Mês com menos compras: novembro/2019 (188).

**Extra 2 - % dos itens de cada categoria por gênero (`pivot_table`)**

| Categoria | F | M |
|---|---|---|
| ALIMENTOS | 52,4 | 52,4 |
| HIGIENE | 18,8 | 18,8 |
| LIMPEZA | 17,6 | 17,5 |
| BEBIDAS | 5,2 | 5,3 |
| PET | 3,9 | 3,9 |
| ACESSORIOS | 1,8 | 1,7 |
| Sem Categoria | 0,4 | 0,4 |

## Insights

1. **Gênero:** o gênero F fez mais compras (9.615, ou 52,1%) que o M (8.856). Mas as compras por cliente são quase iguais (18,53 x 18,41), então a diferença vem de existirem mais clientes mulheres (519 x 481), e não de elas comprarem com mais frequência. A divisão dos itens por categoria também é praticamente igual entre F e M (tabela do Extra 2).
2. **Alimentos dominam:** ALIMENTOS representa 52,4% dos itens e aparece em 98,9% das compras. Também é a categoria com mais produtos diferentes (120).
3. **Acessórios é a menor categoria:** só 1,8% dos itens e aparece em metade das compras (49,9%). Pet e Bebidas também têm participação pequena nos itens.
4. **Clientes sem filhos são maioria:** 52,7% dos clientes não têm filhos (moda e mediana = 0), e a média é de 1,136 filho por cliente.
5. **Qualidade da base:** 11,6% das linhas eram duplicadas, 3.650 linhas não tinham categoria (`#N/D`) e as datas estavam com formatos misturados. Sem a correção das datas, qualquer análise por mês ficaria errada.
6. **Crescimento no tempo:** a média de compras por mês subiu todo ano, de 373,6 em 2019 para 461,1 em 2022 (considerando que 2022 só tem 8 meses). O mês com mais compras foi outubro/2021 (686) e o com menos foi novembro/2019 (188).

## Reflexão teórica sobre ETL

ETL significa **Extract, Transform, Load** (Extrair, Transformar e Carregar). É o processo de pegar dados brutos e deixar eles prontos para análise.

- **Extract (Extração):** obter os dados da fonte. Aqui foi ler o arquivo `Base Varejo.csv` com `pd.read_csv()`, depois de abrir o arquivo e ver que o separador era `;`.
- **Transform (Transformação):** verificar a qualidade e corrigir os problemas. Neste projeto foi: tirar colunas vazias, trocar `#N/D` por "Sem Categoria"/"Sem Nome", remover duplicatas, corrigir e converter as datas para datetime e validar o número da compra.
- **Load (Carga):** colocar os dados tratados no destino. Aqui o destino é o arquivo `df_limpo.csv`, que o script salva e depois lê de novo para conferir.

Neste mini-projeto o ETL foi feito todo localmente, em um script Python, sem banco de dados ou ferramenta de empresa. Mas a ideia é a mesma de um ETL maior: o `df_limpo.csv` poderia ser carregado num banco ou numa ferramenta de BI.

## Reflexão sobre qualidade de dados

Se os dados têm erro, as conclusões também ficam erradas. Por isso a limpeza vem antes da análise. Relacionando com o que foi feito:

- **Completude** (ter a informação necessária): as 4 colunas vazias foram removidas e os `#N/D` foram marcados como "Sem Categoria". A base continua sem preço e quantidade, o que limita a análise.
- **Consistência** (não ter contradição): foi verificado que cada compra tem um único cliente e uma única data, e que cada cliente tem sempre o mesmo gênero e número de filhos.
- **Validade** (valores no formato certo): a coluna DATA tinha dois formatos misturados; foi corrigida e convertida para datetime sem nenhuma data inválida. Os números não tinham negativos.
- **Unicidade** (sem duplicatas indevidas): 96.553 linhas repetidas foram removidas, tomando cuidado para não tratar como erro o fato de uma compra ter várias linhas.
- **Precisão** (dados próximos da realidade): sem a correção das datas, por exemplo, 2 de janeiro seria lido como 1º de fevereiro, e as vendas por mês ficariam erradas.

**Sobre o processo:** os principais problemas foram as duplicatas, o `#N/D` e as datas. Nenhuma linha com informação útil foi apagada, só as repetidas. As decisões foram anotadas no código e no `registro.md`. Depois da limpeza, a base está pronta para ser usada num dashboard de BI (por exemplo, compras por mês, por categoria e por perfil de cliente).

## Limitações da análise

- Não existe coluna de preço/valor: não dá para calcular faturamento nem ticket médio.
- Não existe coluna de quantidade: as linhas duplicadas podiam ser mais de uma unidade do mesmo produto, mas não tem como confirmar.
- O produto `PR_ID` 107 continua sem categoria e sem nome.
- `CL_EC` (estado civil) e `CL_SEG` (segmento) são códigos sem dicionário explicando cada valor.
- O ano de 2022 está incompleto (a base termina em 19/08/2022).

## Conclusão

O projeto passou por todas as etapas de uma análise exploratória: leitura do CSV, diagnóstico, limpeza, estatísticas, agrupamentos e exportação. A parte que mais chamou atenção foi a das datas, que pareciam certas mas estavam com dois formatos misturados. Depois da limpeza a base ficou com 733.447 linhas, 18.471 compras e 1.000 clientes, e mostrou que alimentos dominam as compras, que a diferença entre gêneros vem do número de clientes, que a maioria dos clientes não tem filhos e que as compras por mês cresceram a cada ano.
