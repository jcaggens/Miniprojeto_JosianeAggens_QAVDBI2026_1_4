# Mini-Projeto Avaliativo - Análise Exploratória de Dados de Varejo
# Aluna: Josiane Aggens
# Turma: QAVDBI2026_1_4
#
# Para rodar (dentro da pasta do projeto):
#     python Miniprojeto_JosianeAggens_QAVDBI2026_1_4.py

from pathlib import Path

import pandas as pd
CAMINHO_CSV = Path("dados") / "Base Varejo.csv"

CAMINHO_SAIDA = Path("df_limpo.csv")


def titulo(texto):
    """Imprime um título para separar as partes do relatório."""
    print()
    print("=" * 60)
    print(texto)
    print("=" * 60)


# 1 - CARREGAR OS DADOS
def carregar_dados(caminho):
    """Lê o arquivo CSV e mostra as informações iniciais da base."""
    if not caminho.exists():
        raise FileNotFoundError(
            f"Arquivo não encontrado: {caminho.resolve()}\n"
        )
    df = pd.read_csv(caminho, sep=";")

    titulo("1. INFORMAÇÕES DA BASE")
    print("Quantidade de registros (linhas):", df.shape[0])
    print("Quantidade de colunas:", df.shape[1])
    print("\nNomes das colunas:")
    print(df.columns.tolist())
    print("\nTipos de dados de cada coluna:")
    print(df.dtypes)
    print("\nPrimeiras linhas da base:")
    print(df.head())
    print("\nInformações gerais (df.info()):")
    df.info()

    return df



# 2 - DIAGNÓSTICO DA QUALIDADE DOS DADOS

def diagnosticar_dados(df):
    """Procura problemas na base: nulos, duplicatas, textos, datas e números."""
    titulo("2. DIAGNÓSTICO DA QUALIDADE")

    # 2.1 Valores nulos por coluna (quantidade e porcentagem)
    print("--- Valores nulos por coluna ---")
    nulos = pd.DataFrame({
        "nulos": df.isna().sum(),
        "percentual (%)": (df.isna().mean() * 100).round(2),
    })
    print(nulos)

    # Colunas que estão 100% vazias (vieram do ";;;;" no final das linhas)
    colunas_vazias = [c for c in df.columns if df[c].isna().all()]
    print("\nColunas totalmente vazias:", colunas_vazias)

    # 2.2 Nulos "disfarçados": o texto "#N/D" (vem do Excel) e textos vazios
    print("\n--- Textos que representam ausência de informação ---")
    colunas_texto = df.select_dtypes(include="object").columns
    for coluna in colunas_texto:
        texto = df[coluna].astype(str).str.strip()
        qtd_nd = (texto == "#N/D").sum()
        qtd_vazio = (texto == "").sum()
        qtd_espacos = (df[coluna].astype(str) != texto).sum()
        print(f"{coluna}: '#N/D' = {qtd_nd} | vazios = {qtd_vazio} | "
              f"com espaços sobrando = {qtd_espacos}")

    # 2.3 Valores diferentes nas colunas de texto (para ver erros de escrita)
    print("\n--- Valores encontrados nas colunas de texto curtas ---")
    for coluna in ["CL_GENERO", "CL_SEG", "PR_CAT"]:
        print(f"{coluna}: {sorted(df[coluna].astype(str).unique())}")

    # 2.4 Consistência: cada cliente deveria ter sempre os mesmos dados
    # e cada produto sempre a mesma categoria e nome
    print("\n--- Consistência entre colunas ---")
    por_cliente = df.groupby("CL_ID")[["CL_GENERO", "CL_EC", "CL_FHL", "CL_SEG"]].nunique()
    print("Clientes com mais de um valor em gênero/estado civil/filhos/segmento:",
          (por_cliente > 1).any(axis=1).sum())
    por_produto = df.groupby("PR_ID")[["PR_CAT", "PR_NOME"]].nunique()
    print("Produtos com mais de uma categoria ou nome:",
          (por_produto > 1).any(axis=1).sum())

    # 2.5 Registros duplicados (linhas 100% iguais)
    print("\n--- Duplicatas ---")
    duplicadas = df.duplicated().sum()
    print("Linhas totalmente duplicadas:", duplicadas)
    dup_compra_produto = df.duplicated(subset=["CO_ID", "PR_ID"]).sum()
    print("Mesmo produto repetido na mesma compra (CO_ID + PR_ID):", dup_compra_produto)

    # 2.6 Datas
    print("\n--- Datas (coluna DATA) ---")
    datas_texto = df["DATA"].astype(str).str.strip()
    fora_do_padrao = (~datas_texto.str.match(r"^\d{2}/\d{2}/\d{4}$")).sum()
    print("Datas fora do padrão 00/00/0000:", fora_do_padrao)
    primeiro_numero = pd.to_numeric(datas_texto.str[:2], errors="coerce")
    segundo_numero = pd.to_numeric(datas_texto.str[3:5], errors="coerce")
    print("Datas com o 1º número maior que 12 (só pode ser dia/mês):",
          (primeiro_numero > 12).sum())
    print("Datas com o 2º número maior que 12 (só pode ser mês/dia):",
          (segundo_numero > 12).sum())
    datas_dia_mes = pd.to_datetime(datas_texto, format="%d/%m/%Y", errors="coerce")
    print("Lendo tudo como dia/mês, o arquivo fica em ordem de data?",
          datas_dia_mes.is_monotonic_increasing)
    print("-> Se não fica em ordem, as datas estão com formatos misturados.")

    # 2.7 Colunas numéricas
    print("\n--- Colunas numéricas ---")
    for coluna in ["CO_ID", "CL_ID", "CL_EC", "CL_FHL", "PR_ID"]:
        print(f"{coluna}: tipo = {df[coluna].dtype} | mínimo = {df[coluna].min()} | "
              f"máximo = {df[coluna].max()} | negativos = {(df[coluna] < 0).sum()}")

    # 2.8 Resumo do diagnóstico e o que vai ser feito
    print("\n--- Resumo do diagnóstico e ações ---")
    print(f"1) {len(colunas_vazias)} colunas totalmente vazias -> serão removidas.")
    print(f"2) '#N/D' em PR_CAT e PR_NOME ({(df['PR_CAT'] == '#N/D').sum()} linhas) "
          "-> categoria vira 'Sem Categoria' e nome vira 'Sem Nome'.")
    print(f"3) {duplicadas} linhas duplicadas -> serão removidas.")
    print("4) Datas com formatos misturados (dia/mês e mês/dia) -> serão corrigidas "
          "e convertidas para datetime.")
    print("5) Colunas numéricas já estão como número inteiro, sem negativos -> mantidas.")

    return colunas_vazias



# 3 - LIMPEZA E TRANSFORMAÇÃO

def converter_datas(coluna_data):
    texto = coluna_data.astype(str).str.strip()
    primeiro_numero = pd.to_numeric(texto.str[:2], errors="coerce")

    datas_dia_mes = pd.to_datetime(texto, format="%d/%m/%Y", errors="coerce")
    datas_mes_dia = pd.to_datetime(texto, format="%m/%d/%Y", errors="coerce")

    # where: mantém dia/mês quando o 1º número > 12, senão usa mês/dia
    return datas_dia_mes.where(primeiro_numero > 12, datas_mes_dia)


def validar_id_compra(df):
    """Confere a regra do número da compra (CO_ID) observada na base."""
    print("\n--- Validação do número da compra (CO_ID) ---")

    # Regra 1: CO_ID precisa ser número inteiro positivo
    co_id = pd.to_numeric(df["CO_ID"], errors="coerce")
    invalidos = (co_id.isna() | (co_id <= 0)).sum()
    print("CO_ID ausente, não numérico ou <= 0:", invalidos)

    # Regra 2: uma compra pertence a um único cliente e a uma única data
    por_compra = df.groupby("CO_ID")[["CL_ID", "DATA"]].nunique()
    compras_varios_clientes = (por_compra["CL_ID"] > 1).sum()
    compras_varias_datas = (por_compra["DATA"] > 1).sum()
    print("Compras com mais de um cliente:", compras_varios_clientes)
    print("Compras com mais de uma data:", compras_varias_datas)

    # Regra 3: o número da compra cresce junto com a data (é sequencial)
    compras = df[["CO_ID", "DATA"]].drop_duplicates().sort_values("CO_ID")
    voltas_no_tempo = (compras["DATA"].diff().dt.days < 0).sum()
    print("Compras com data menor que a compra anterior:", voltas_no_tempo)

    print("Quantidade de compras diferentes:", df["CO_ID"].nunique())
    if invalidos + compras_varios_clientes + compras_varias_datas + voltas_no_tempo == 0:
        print("-> Todos os CO_ID seguem a regra. Nenhum registro precisou ser separado.")
    else:
        print("-> Atenção: existem CO_ID fora da regra (ver números acima).")


def limpar_dados(df_original, colunas_vazias):
    """Aplica a limpeza na cópia da base e devolve o df_limpo."""
    titulo("3. LIMPEZA DOS DADOS")

    # Trabalho numa cópia para não estragar a base original
    df_limpo = df_original.copy()
    linhas_antes, colunas_antes = df_limpo.shape

    # 3.1 Remover as colunas totalmente vazias (sobra do ";;;;" no fim das linhas)
    df_limpo = df_limpo.drop(columns=colunas_vazias)
    print(f"3.1 Removidas {len(colunas_vazias)} colunas vazias: {colunas_vazias}")

    # 3.2 Tirar espaços sobrando das colunas de texto
    for coluna in ["CL_GENERO", "CL_SEG", "PR_CAT", "PR_NOME"]:
        df_limpo[coluna] = df_limpo[coluna].astype("string").str.strip()
    print("3.2 Espaços extras removidos das colunas de texto.")

    # 3.3 Categorias vazias -> "Sem Categoria"
    # "#N/D" e texto vazio significam que a informação não existe
    df_limpo["PR_CAT"] = df_limpo["PR_CAT"].replace(["#N/D", ""], pd.NA)
    qtd_sem_categoria = df_limpo["PR_CAT"].isna().sum()
    df_limpo["PR_CAT"] = df_limpo["PR_CAT"].fillna("Sem Categoria")
    print(f"3.3 PR_CAT: {qtd_sem_categoria} valores sem categoria preenchidos com "
          "'Sem Categoria'.")

    # 3.4 Nome do produto vazio -> "Sem Nome"
    # Não removi essas linhas porque a compra, o cliente e a data estão corretos.
    df_limpo["PR_NOME"] = df_limpo["PR_NOME"].replace(["#N/D", ""], pd.NA)
    qtd_sem_nome = df_limpo["PR_NOME"].isna().sum()
    df_limpo["PR_NOME"] = df_limpo["PR_NOME"].fillna("Sem Nome")
    print(f"3.4 PR_NOME: {qtd_sem_nome} valores sem nome preenchidos com 'Sem Nome'.")

    # 3.5 Converter a data para datetime (corrigindo os formatos misturados)
    df_limpo["DATA"] = converter_datas(df_limpo["DATA"])
    datas_invalidas = df_limpo["DATA"].isna().sum()
    print(f"3.5 DATA convertida para datetime. Datas que não converteram: {datas_invalidas}")
    print(f"    Período da base: {df_limpo['DATA'].min().date()} até "
          f"{df_limpo['DATA'].max().date()}")
    print("    A base fica em ordem de data depois da correção?",
          df_limpo["DATA"].is_monotonic_increasing)

    # 3.6 Remover linhas duplicadas
    # Uma compra tem várias linhas (uma por produto), isso é normal.
    # Mas linha 100% igual (mesma compra, mesmo produto, mesma data e cliente) eu considero
    # registro repetido. Como a base não tem coluna de quantidade, não dá para saber se
    # era mais de uma unidade, então cada produto conta uma vez por compra.
    duplicadas = df_limpo.duplicated().sum()
    df_limpo = df_limpo.drop_duplicates().reset_index(drop=True)
    print(f"3.6 Removidas {duplicadas} linhas duplicadas.")

    # 3.7 Ajuste de tipos: as colunas de ID e códigos já são inteiros (int64)
    # e os textos ficaram como "string". Só confiro aqui.
    print("3.7 Tipos depois da limpeza:")
    print(df_limpo.dtypes)

    # 3.8 Regra do número da compra
    validar_id_compra(df_limpo)

    # 3.9 Antes e depois
    print("\n--- Tamanho da base ---")
    print(f"Antes da limpeza:  {linhas_antes} linhas e {colunas_antes} colunas")
    print(f"Depois da limpeza: {df_limpo.shape[0]} linhas e {df_limpo.shape[1]} colunas")

    resumo_limpeza = {
        "colunas_vazias": len(colunas_vazias),
        "sem_categoria": qtd_sem_categoria,
        "duplicadas": duplicadas,
        "linhas_antes": linhas_antes,
        "linhas_depois": df_limpo.shape[0],
    }
    return df_limpo, resumo_limpeza



# 4 - ESTATÍSTICA DO NÚMERO DE FILHOS (coluna CL_FHL)

def estatisticas_basicas(serie):
    """Calcula as 7 estatísticas pedidas para uma coluna numérica."""
    return {
        "Média": round(serie.mean(), 4),
        "Mediana": serie.median(),
        "Desvio padrão": round(serie.std(), 4),  # amostral (ddof=1), padrão do pandas
        "Moda": serie.mode().tolist(),            # pode ter mais de uma moda
        "Máximo": serie.max(),
        "Mínimo": serie.min(),
        "Contagem": serie.count(),
    }


def calcular_estatisticas(df_limpo):
    """Calcula as estatísticas do número de filhos dos clientes."""
    titulo("4. ESTATÍSTICAS DO NÚMERO DE FILHOS (CL_FHL)")

    df_limpo["CL_FHL"] = pd.to_numeric(df_limpo["CL_FHL"], errors="coerce")
    print("Valores inválidos em CL_FHL:", df_limpo["CL_FHL"].isna().sum())

    # Cada cliente aparece em muitas linhas (uma por produto comprado).
    clientes = df_limpo.drop_duplicates(subset="CL_ID")
    filhos_por_cliente = clientes["CL_FHL"].dropna()

    if filhos_por_cliente.empty:
        print("Não há valores válidos para calcular as estatísticas.")
        return None

    est_clientes = estatisticas_basicas(filhos_por_cliente)
    print("\n>> Considerando 1 linha por cliente (clientes únicos):")
    for nome, valor in est_clientes.items():
        print(f"   {nome}: {valor}")
        
    est_linhas = estatisticas_basicas(df_limpo["CL_FHL"].dropna())
    print("\n>> Considerando todas as linhas da base limpa (cada item comprado):")
    for nome, valor in est_linhas.items():
        print(f"   {nome}: {valor}")

    print("\n>> Distribuição dos clientes por número de filhos:")
    distribuicao = filhos_por_cliente.value_counts().sort_index()
    porcentagem = (distribuicao / distribuicao.sum() * 100).round(1)
    print(pd.DataFrame({"clientes": distribuicao, "%": porcentagem}))

    # Interpretação simples, montada com os números calculados
    print("\n>> Interpretação:")
    moda = est_clientes["Moda"]
    print(f"   - O número de filhos vai de {est_clientes['Mínimo']} a "
          f"{est_clientes['Máximo']}.")
    print(f"   - O valor mais comum (moda) é {moda}, com "
          f"{porcentagem.loc[moda[0]]}% dos clientes.")
    print(f"   - A mediana é {est_clientes['Mediana']} e a média é "
          f"{est_clientes['Média']}. Quando a média é maior que a mediana, quer dizer que "
          "os clientes com mais filhos 'puxam' a média para cima.")
    print(f"   - O desvio padrão ({est_clientes['Desvio padrão']}) é maior que a própria "
          "média, ou seja, os valores são bem espalhados entre 0 e o máximo.")

    return {"clientes": est_clientes, "linhas": est_linhas, "porcentagem": porcentagem}



# 5 - AGRUPAMENTOS

def analisar_agrupamentos(df_limpo):
    """Faz os agrupamentos com groupby e mostra os resultados."""
    titulo("5. ANÁLISE POR AGRUPAMENTOS")
    print("Obs.: a base NÃO tem coluna de preço/valor, então não dá para calcular")
    print("faturamento. As medidas usadas são: linhas (itens), compras únicas e clientes.")

    total_compras = df_limpo["CO_ID"].nunique()

    # Agrupamento 1 - Gênero do cliente
    # linhas = itens comprados | compras = CO_ID diferentes | clientes = CL_ID diferentes
    print("\n--- Agrupamento 1: por gênero (CL_GENERO) ---")
    por_genero = (
        df_limpo
        .groupby("CL_GENERO", dropna=False)
        .agg(
            itens=("CO_ID", "size"),
            compras=("CO_ID", "nunique"),
            clientes=("CL_ID", "nunique"),
        )
        .sort_values("compras", ascending=False)
    )
    por_genero["% das compras"] = (por_genero["compras"] / total_compras * 100).round(1)
    por_genero["compras por cliente"] = (por_genero["compras"] / por_genero["clientes"]).round(2)
    por_genero["itens por compra"] = (por_genero["itens"] / por_genero["compras"]).round(2)
    print(por_genero)

    # Agrupamento 2 - Categoria do produto
    # itens = linhas da categoria | compras = em quantas compras a categoria apareceu
    print("\n--- Agrupamento 2: por categoria de produto (PR_CAT) ---")
    por_categoria = (
        df_limpo
        .groupby("PR_CAT", dropna=False)
        .agg(
            itens=("PR_CAT", "size"),
            compras=("CO_ID", "nunique"),
            produtos_diferentes=("PR_ID", "nunique"),
        )
        .sort_values("itens", ascending=False)
    )
    por_categoria["% dos itens"] = (
        por_categoria["itens"] / por_categoria["itens"].sum() * 100
    ).round(1)
    por_categoria["% das compras com a categoria"] = (
        por_categoria["compras"] / total_compras * 100
    ).round(1)
    print(por_categoria)

    return {"genero": por_genero, "categoria": por_categoria, "total_compras": total_compras}


def analises_extras(df_limpo):
    """Análises a mais (opcionais): compras ao longo do tempo e pivot_table."""
    titulo("5.1 ANÁLISES EXTRAS")

    # Extra 1 - Compras por ano
    # Como 2022 só vai até agosto, também calculo a média de compras por mês
    # em cada ano, para comparar de forma justa.
    print("--- Extra 1: compras por ano ---")
    df_tempo = df_limpo.copy()
    df_tempo["ANO"] = df_tempo["DATA"].dt.year
    df_tempo["MES"] = df_tempo["DATA"].dt.to_period("M")
    por_ano = df_tempo.groupby("ANO").agg(
        compras=("CO_ID", "nunique"),
        itens=("CO_ID", "size"),
        clientes=("CL_ID", "nunique"),
        meses_com_dados=("MES", "nunique"),
    )
    por_ano["compras por mês"] = (por_ano["compras"] / por_ano["meses_com_dados"]).round(1)
    print(por_ano)

    # Mês com mais e com menos compras
    compras_por_mes = df_tempo.groupby("MES")["CO_ID"].nunique()
    print(f"\nMês com mais compras: {compras_por_mes.idxmax()} "
          f"({compras_por_mes.max()} compras)")
    print(f"Mês com menos compras: {compras_por_mes.idxmin()} "
          f"({compras_por_mes.min()} compras)")

    # Extra 2 - pivot_table: % dos itens de cada categoria dentro de cada gênero
    print("\n--- Extra 2: % dos itens de cada categoria por gênero (pivot_table) ---")
    tabela = pd.pivot_table(
        df_limpo,
        index="PR_CAT",
        columns="CL_GENERO",
        values="CO_ID",
        aggfunc="size",
    )
    tabela_pct = (tabela / tabela.sum() * 100).round(1)
    tabela_pct = tabela_pct.sort_values("F", ascending=False)
    print(tabela_pct)

    return {"por_ano": por_ano, "compras_por_mes": compras_por_mes, "pivot": tabela_pct}



# 6 - EXPORTAR A BASE LIMPA

def exportar_dados(df_limpo, caminho_saida):
    """Salva o df_limpo em CSV e confere se o arquivo ficou certo."""
    titulo("6. EXPORTAÇÃO")
    df_limpo.to_csv(caminho_saida, index=False, encoding="utf-8-sig")

    # Conferência: leio o arquivo de novo e comparo
    conferencia = pd.read_csv(caminho_saida, parse_dates=["DATA"])
    print("Arquivo salvo em:", caminho_saida.resolve())
    print("Registros exportados:", len(conferencia))
    print("Mesmo número de linhas do df_limpo?", len(conferencia) == len(df_limpo))
    print("Mesmas colunas?", conferencia.columns.tolist() == df_limpo.columns.tolist())
    print("DATA voltou como data?", str(conferencia["DATA"].dtype).startswith("datetime"))
    print("Datas iguais às do df_limpo?", conferencia["DATA"].equals(df_limpo["DATA"]))



# 7 - CONCLUSÕES

def gerar_conclusoes(df_limpo, resumo_limpeza, estatisticas, agrupamentos, extras):
    """Mostra os principais insights usando os números calculados antes."""
    titulo("7. CONCLUSÕES")

    genero = agrupamentos["genero"]
    categoria = agrupamentos["categoria"]
    est = estatisticas["clientes"]
    pct_filhos = estatisticas["porcentagem"]

    # Gênero com mais compras (a tabela já está ordenada por compras)
    g1, g2 = genero.index[0], genero.index[1]
    print(f"1) Gênero: o gênero {g1} fez {genero.loc[g1, 'compras']} compras "
          f"({genero.loc[g1, '% das compras']}%) contra {genero.loc[g2, 'compras']} do "
          f"gênero {g2}. Mas as compras por cliente são parecidas "
          f"({genero.loc[g1, 'compras por cliente']} x {genero.loc[g2, 'compras por cliente']}), "
          f"então a diferença vem de ter mais clientes {g1} "
          f"({genero.loc[g1, 'clientes']} x {genero.loc[g2, 'clientes']}).")

    # Categoria com mais itens e a com menos (sem contar "Sem Categoria")
    categorias_reais = categoria.drop(index="Sem Categoria", errors="ignore")
    c_maior = categorias_reais.index[0]
    c_menor = categorias_reais.index[-1]
    print(f"2) Categorias: {c_maior} é a categoria com mais itens vendidos "
          f"({categorias_reais.loc[c_maior, '% dos itens']}% dos itens) e aparece em "
          f"{categorias_reais.loc[c_maior, '% das compras com a categoria']}% das compras. "
          f"{c_menor} é a que menos aparece "
          f"({categorias_reais.loc[c_menor, '% dos itens']}% dos itens).")

    print(f"3) Filhos: {pct_filhos.loc[0]}% dos {est['Contagem']} clientes não têm filhos "
          f"(moda = {est['Moda']} e mediana = {est['Mediana']}). A média é "
          f"{est['Média']} filhos por cliente, com máximo de {est['Máximo']}.")

    pct_duplicadas = round(resumo_limpeza["duplicadas"] / resumo_limpeza["linhas_antes"] * 100, 1)
    print(f"4) Qualidade: {resumo_limpeza['duplicadas']} linhas duplicadas "
          f"({pct_duplicadas}% da base) foram removidas, {resumo_limpeza['sem_categoria']} "
          "linhas com '#N/D' viraram 'Sem Categoria' e as datas tinham formatos misturados "
          "(dia/mês e mês/dia), o que foi corrigido.")

    print(f"5) Período: a base vai de {df_limpo['DATA'].min().date()} até "
          f"{df_limpo['DATA'].max().date()}, com {agrupamentos['total_compras']} compras "
          f"de {df_limpo['CL_ID'].nunique()} clientes.")

    # Evolução no tempo (das análises extras)
    por_ano = extras["por_ano"]
    primeiro_ano, ultimo_ano = por_ano.index[0], por_ano.index[-1]
    mes = extras["compras_por_mes"]
    print(f"6) Tempo: a média de compras por mês passou de "
          f"{por_ano.loc[primeiro_ano, 'compras por mês']} em {primeiro_ano} para "
          f"{por_ano.loc[ultimo_ano, 'compras por mês']} em {ultimo_ano} "
          f"(em {ultimo_ano} só há {por_ano.loc[ultimo_ano, 'meses_com_dados']} meses). "
          f"O mês com mais compras foi {mes.idxmax()} ({mes.max()}) e o com menos foi "
          f"{mes.idxmin()} ({mes.min()}).")

    print("\nLimitações e problemas que continuam:")
    print("- Não existe coluna de preço/valor: não dá para calcular faturamento.")
    print("- Não existe coluna de quantidade: as linhas duplicadas podiam ser mais de uma "
          "unidade do mesmo produto, mas não tem como confirmar.")
    print("- Um produto (PR_ID 107) continua sem categoria e sem nome ('Sem Categoria').")
    print("- CL_EC (estado civil) e CL_SEG (segmento) são códigos sem dicionário explicando "
          "o significado de cada valor.")
    print("- O ano de 2022 está incompleto (a base termina em agosto).")



# PROGRAMA PRINCIPAL

def main():
    print("=" * 60)
    print("MINI-PROJETO - ANÁLISE EXPLORATÓRIA DE VAREJO")
    print("=" * 60)

    try:
        df_original = carregar_dados(CAMINHO_CSV)
    except FileNotFoundError as erro:
        print("ERRO:", erro)
        return

    colunas_vazias = diagnosticar_dados(df_original)
    df_limpo, resumo_limpeza = limpar_dados(df_original, colunas_vazias)
    estatisticas = calcular_estatisticas(df_limpo)
    agrupamentos = analisar_agrupamentos(df_limpo)
    extras = analises_extras(df_limpo)
    exportar_dados(df_limpo, CAMINHO_SAIDA)
    gerar_conclusoes(df_limpo, resumo_limpeza, estatisticas, agrupamentos, extras)

    print()
    print("=" * 60)
    print("FIM DO RELATÓRIO")
    print("=" * 60)


if __name__ == "__main__":
    main()
