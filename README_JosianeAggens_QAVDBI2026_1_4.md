# Como executar o projeto

**Aluna:** Josiane Cristine Aggens | **Turma:** QAVDBI2026_1_4

## No VS Code (no computador)

1. Baixe ou clone o repositório:

   ```bash
   git clone <link-do-repositório>
   ```

2. Verifique se o Python está instalado:

   ```bash
   python --version
   ```

3. Instale o pandas:

   ```bash
   python -m pip install pandas
   ```

4. Confira se o arquivo `Base Varejo.csv` está dentro da pasta `dados`. Se não estiver, baixe em https://www.kaggle.com/datasets/namespaiva/base-varejo/data e coloque lá.
5. Abra a pasta do projeto no VS Code e abra o terminal (menu *Terminal > New Terminal*).
6. Rode o script:

   ```bash
   python Miniprojeto_JosianeAggens_QAVDBI2026_1_4.py
   ```

   Se não funcionar, tente `python3` no lugar de `python`.

7. Leia o relatório que aparece no terminal (7 partes: informações, diagnóstico, limpeza, estatísticas, agrupamentos, exportação e conclusões).
8. Confira se o arquivo `df_limpo.csv` foi criado na pasta do projeto.

## No Google Colab

1. Envie os arquivos `Miniprojeto_JosianeAggens_QAVDBI2026_1_4.py` e `Base Varejo.csv` para o Colab.
2. No começo do script, troque o caminho do CSV, por exemplo:

   ```python
   CAMINHO_CSV = Path("Base Varejo.csv")
   ```

3. Rode numa célula:

   ```python
   !python Miniprojeto_JosianeAggens_QAVDBI2026_1_4.py
   ```

4. O `df_limpo.csv` vai aparecer na lista de arquivos do Colab.

