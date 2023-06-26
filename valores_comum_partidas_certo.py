import random
import requests
import pandas as pd
import streamlit as st
from io import BytesIO
from openpyxl import load_workbook
from tabulate import tabulate

st.set_page_config(page_title="InPES Futebol Virtual", page_icon=":soccer:")

st.title('**Resultados do Futebol Virtual**')
st.write('\n\n')

# Perguntas para o usuário
primeiro_tempo1 = st.selectbox("Qual o resultado do primeiro tempo?", ['0x0','0x1','0x2','0x3','0x4','0x5','1x0','1x1','1x2','1x3','1x4','1x5','2x0','2x1','2x2','2x3','2x4','2x5','3x0','3x1','3x2','3x3','3x4','3x5','4x0','4x1','4x2','4x3','4x4','4x5','5x0','5x1','5x2','5x3','5x4','5x5'])
tempo_final1 = st.selectbox("Qual o resultado do tempo final?", ['0x0','0x1','0x2','0x3','0x4','0x5','1x0','1x1','1x2','1x3','1x4','1x5','2x0','2x1','2x2','2x3','2x4','2x5','3x0','3x1','3x2','3x3','3x4','3x5','4x0','4x1','4x2','4x3','4x4','4x5','5x0','5x1','5x2','5x3','5x4','5x5'])
num_total_partidas1 = st.number_input("Qual a quantidade de partidas após a ocorrência do padrão você deseja analisar?", min_value=1, value=50, step=1)
porcentagem_acerto1 = st.number_input("Porcentagem de acerto (Ambas marcaram em pelo menos uma das três partidas):", min_value=1, value=50, step=1)
porcentagem_desejada1 = st.number_input("Do total de partidas que deu certo, deseja verificar os valores em comum em até quantos % dessas partidas?", min_value=1, value=50, step=1)
num_conjuntos = 3

def gerar_resultados():

  sheet_id = '1-OpwOkZbencR-EGbQiTkgDWKzEY8Y-t0B7TlmRuUlaY'
  url = f'https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx'

  response = requests.get(url)
  data = response.content

  excel_data = pd.ExcelFile(BytesIO(data), engine='openpyxl')
  sheet_names = excel_data.sheet_names

  for sheet_name in sheet_names:
      
      # Tratando o arquivo Excel e obtendo o DataFrame tratado
      df = excel_data.parse(sheet_name)

      # Define a primeira linha como os nomes das colunas
      df.columns = df.iloc[0]

      # Remove a primeira linha, que agora são os nomes das colunas duplicados
      df = df[1:].reset_index(drop=True)

      # Obtém todas as colunas, exceto as duas últimas
      colunas_para_manter = df.columns[:-3]

      # Mantém apenas as colunas selecionadas
      df = df[colunas_para_manter]

      # Inverte o dataframe
      df = df.sort_index(ascending=False)

      # Reseta o index
      df = df.reset_index(drop=True)

      # Função para extrair os resultados do primeiro tempo, tempo final e partidas
      def extrair_resultados(resultado):
          if resultado != '?\n\n?':
              resultado_split = resultado.split('\n\n')
              primeiro_tempo = resultado_split[1]
              tempo_final = resultado_split[0]
              return primeiro_tempo, tempo_final
          else:
              return None, None

      # Criando listas vazias para armazenar os valores extraídos
      primeiro_tempo_list = []
      tempo_final_list = []
      partidas_list = []

      # Percorrendo o dataframe original e extraindo os resultados
      for index, row in df.iterrows():
          for col in df.columns[1:]:
              resultado = row[col]
              primeiro_tempo, tempo_final = extrair_resultados(resultado)
              primeiro_tempo_list.append(primeiro_tempo)
              tempo_final_list.append(tempo_final)
              partidas_list.append(col)

      # Criando o novo dataframe com as colunas desejadas
      df_novo = pd.DataFrame({
          'Primeiro tempo': primeiro_tempo_list,
          'Tempo final': tempo_final_list,
      })


      num_linhas = len(df_novo)
      df_novo['Partidas'] = range(1, num_linhas + 1)

      # Obtendo o nome da última coluna
      ultima_coluna = df_novo.columns[-1]

      # Extraindo a coluna "Partidas"
      coluna_partidas = df_novo.pop(ultima_coluna)

      # Inserindo a coluna "Partidas" na terceira posição
      df_novo.insert(0, ultima_coluna, coluna_partidas)

      df_novo = df_novo.dropna(subset=['Primeiro tempo', 'Tempo final'])

      df_novo = df_novo[~df_novo['Primeiro tempo'].str.contains('\.', na=False) & ~df_novo['Tempo final'].str.contains('\.', na=False)]

      df_novo['Primeiro tempo'] = df_novo['Primeiro tempo'].replace('oth', '9x9')

      # Remover células com valor "?"
      df_novo = df_novo[(df_novo['Primeiro tempo'] != '?') & (df_novo['Tempo final'] != '?')]

      df_analisar_st = df_novo

      # Transformar o dataframe em um dicionário

      def analisar_partidas(df, primeiro_tempo, tempo_final, num_total_partidas, num_conjuntos):
          resultado = {}
          partidas_selecionadas = df[(df['Primeiro tempo'] == primeiro_tempo) & (df['Tempo final'] == tempo_final)]['Partidas']

          for partida in partidas_selecionadas:
              lista_partidas = []
              inicio = partida - 1
              fim = inicio + num_total_partidas

              if fim > len(df):
                  continue  # Ignorar partidas que ultrapassam o tamanho do DataFrame

              for i in range(inicio, fim):
                  conjunto_partidas = []
                  for j in range(num_conjuntos):
                      indice = i + j + 1
                      if indice < len(df.index):
                          partida_tempo_final = df.loc[indice, 'Tempo final']
                          partida_primeiro_tempo = df.loc[indice, 'Primeiro tempo']
                          conjunto_partidas.append((partida_primeiro_tempo, partida_tempo_final))
                  lista_partidas.append(conjunto_partidas)

              resultado[partida] = lista_partidas

          return resultado

      # Solicitar informações do usuário
      primeiro_tempo = primeiro_tempo1
      tempo_final = tempo_final1
      num_total_partidas = num_total_partidas1
      porcentagem_acerto = porcentagem_acerto1
      porcentagem_desejada = porcentagem_desejada1
      num_conjuntos = 3

      # Redefinir o índice do DataFrame df_analisar_st
      df_analisar_st.reset_index(drop=True, inplace=True)

      # Chamada da função para análise das partidas
      resultado_analise = analisar_partidas(df_analisar_st, primeiro_tempo, tempo_final, num_total_partidas, num_conjuntos)

      st.write('No conjunto de dados ' + sheet_name)
      st.write('O padrão ' + primeiro_tempo + ' no Primeiro tempo e ' + tempo_final + ' no Tempo final aconteceu em ' + str(len(resultado_analise)) + ' partidas')

      def criar_novo_dicionario(resultado_analise, num_total_partidas):
          novo_dicionario = {}

          for i in range(num_total_partidas):
              novo_dicionario[i + 1] = []

              for chave in resultado_analise:
                  if i < len(resultado_analise[chave]):
                      novo_dicionario[i + 1].append(resultado_analise[chave][i])

              if len(novo_dicionario[i + 1]) == 0:
                  del novo_dicionario[i + 1]
                  break

          return novo_dicionario

      dicionario = criar_novo_dicionario(resultado_analise, num_total_partidas)

      # num_conjuntos = len(dicionario[1][0])  # Número de valores em cada lista
      num_total = len(resultado_analise) # Número total de ocorrências do padrão de resultados informado pelo usuário

      data = []  # Lista para armazenar os dados das linhas do dataframe

      for key, lista_chave in dicionario.items():
          row = [format(key)]
          AM_counts = [0] * num_conjuntos
          AN_counts = [0] * num_conjuntos
          Over_15_counts = [0] * num_conjuntos
          Over_25_counts = [0] * num_conjuntos
          Over_35_counts = [0] * num_conjuntos
          total_AM = 0
          total_AN = 0
          total_over_15 = 0
          total_over_25 = 0
          total_over_35 = 0

          for lista in lista_chave:
              AM_found = False
              AN_found = False
              over_15_found = False
              over_25_found = False
              over_35_found = False

              for i, val in enumerate(lista):
                  score1, score2 = val[1].split('x')
                  score1 = int(score1)
                  score2 = int(score2)

                  if not AM_found and score1 >= 1 and score2 >= 1:
                      AM_counts[i] += 1
                      AM_found = True

                      if score1 + score2 > 1.5 and score1 + score2 < 2.5 :
                          Over_15_counts[i] += 1
                          over_15_found = True

                      if score1 + score2 > 2.5 and not over_15_found and score1 + score2 < 3.5:  # Verificar se não foi contado como over 1.5
                          Over_25_counts[i] += 1
                          over_25_found = True

                      if score1 + score2 > 3.5 and not over_15_found and not over_25_found:  # Verificar se não foi contado como over 1.5 e over 2.5
                          Over_35_counts[i] += 1
                          over_35_found = True

                  if not AN_found and (score1 < 1 or score2 < 1):
                      AN_counts[i] += 1
                      AN_found = True

              total_AM += int(AM_found)
              total_AN += int(AN_found)
              total_over_15 += int(over_15_found)
              total_over_25 += int(over_25_found)
              total_over_35 += int(over_35_found)

          row.extend(Over_15_counts)
          row.extend(Over_25_counts)
          row.extend(Over_35_counts)
          row.extend(AM_counts)
          row.extend(AN_counts)
          row.append(sum(Over_15_counts))
          row.append(sum(Over_25_counts))
          row.append(sum(Over_35_counts))
          row.append(sum(AM_counts))
          row.append(sum(AN_counts))
          data.append(row)

      columns = ['Partidas após'] + [f'{i} (Over 1.5)' for i in range(1, num_conjuntos+1)] + [f'{i} (Over 2.5)' for i in range(1, num_conjuntos+1)] + [f'{i} (Over 3.5)' for i in range(1, num_conjuntos+1)] + [f'{i} (AM)' for i in range(1, num_conjuntos+1)] + [f'{i} (AN)' for i in range(1, num_conjuntos+1)] + ['Total Over 1.5', 'Total Over 2.5', 'Total Over 3.5', 'Total AM', 'Total AN']
      df = pd.DataFrame(data, columns=columns)
      df.iloc[:, 1:1+num_conjuntos*3] = df.iloc[:, 1:1+num_conjuntos*3].apply(pd.to_numeric)
      df['Total Over 1.5'] = df.iloc[:, 1:1+num_conjuntos].sum(axis=1)
      df['Total Over 2.5'] = df.iloc[:, 1+num_conjuntos:1+2*num_conjuntos].sum(axis=1)
      df['Total Over 3.5'] = df.iloc[:, 1+2*num_conjuntos:1+3*num_conjuntos].sum(axis=1)
      df['Total AM'] = df.iloc[:, 1+3*num_conjuntos:1+4*num_conjuntos].sum(axis=1)
      df['Total AN'] = df.iloc[:, 1+4*num_conjuntos:1+5*num_conjuntos].sum(axis=1)

      # Adicionar a porcentagem em relação ao número total de chaves
      total_percent = "{:.2%}".format(1 / num_total)

      # Aplicar formatação apenas a partir da segunda coluna em diante
      df.iloc[:, 1:] = df.iloc[:, 1:].applymap(lambda x: str(x) + f'/{num_total} ({float(x)/num_total:.2%})' if isinstance(x, int) else x)

      # Ordenar o DataFrame em ordem decrescente pelas colunas especificadas
      df = df.sort_values(by=['Total AM', 'Total AN', 'Total Over 1.5', 'Total Over 2.5', 'Total Over 3.5'], ascending=False)

      # Resetar os índices do DataFrame após a ordenação
      df = df.reset_index(drop=True)

      colunas = ['Partidas após', '1 (Over 1.5)', '2 (Over 1.5)', '3 (Over 1.5)',
                '1 (Over 2.5)', '2 (Over 2.5)', '3 (Over 2.5)', '1 (Over 3.5)',
                '2 (Over 3.5)', '3 (Over 3.5)', '1 (AM)', '2 (AM)', '3 (AM)', '1 (AN)',
                '2 (AN)', '3 (AN)', 'Total Over 1.5', 'Total Over 2.5',
                'Total Over 3.5', 'Total AM', 'Total AN']

      colunas_ordenadas = colunas[16:] + colunas[:16]  # Reorganize as colunas

      df = df.reindex(columns=colunas_ordenadas)

      # Selecionar a identificação de quantas partidas após

      # Criar uma lista para armazenar os valores da coluna "Partidas após"
      partidas_apos_lista = []

      # Iterar sobre as linhas do DataFrame
      for index, row in df.iterrows():
          total_am = row['Total AM']
          
          # Verificar se o valor dentro dos parênteses é maior que a porcentagem escolhida pelo usuário
          if float(total_am.split('(')[1].split(')')[0][:-1]) > porcentagem_acerto:
              
              # Calcular a diferença entre os valores antes e depois da /
              valores = total_am.split()[0].split('/')
              diferenca = int(valores[1]) - int(valores[0])
              
              # Verificar se a diferença é no mínimo 10
              if diferenca <= 10:
                  
                  # Adicionar o valor da coluna "Partidas após" à lista
                  partidas_apos_lista.append(row['Partidas após'])


      # Laço de repetição iterando sobre cada um dos identificadores de partidas após

  valores_int = [int(valor) for valor in partidas_apos_lista if int(valor) >= 21]

  for valor_partida in valores_int:

    num_colunas = 20

    # ESSE CÓDIGO SEPARA AS PARTIDAS EM AMBAS MARCARAM E AMBAS NÃO MARCARAM

    # Dicionários para armazenar as partidas
    ambas_marcaram = {}
    ambas_nao_marcaram = {}

    # Verifica cada chave e valor do dicionário
    for chave, valores in resultado_analise.items():
        lista = valores[valor_partida-1] if len(valores) > valor_partida-1 else []

        # Verifica se ocorreu "Ambas marcaram" na décima primeira lista
        ocorreu_ambas_marcaram = any(
            int(resultado[1].split('x')[0]) >= 1 and int(resultado[1].split('x')[1]) >= 1
            for resultado in lista
        )

        if ocorreu_ambas_marcaram:
            ambas_marcaram[chave] = valores
        else:
            ambas_nao_marcaram[chave] = valores

    # ESSE CÓDIGO TRANSFORMA OS VALORES DAS PARTIDAS EM CLASSES DE RESULTADOS

    def transformar_valores(valores):
        valores_transformados = []
        for resultados_partida in valores:
            resultados_partida_transformados = []
            for resultado in resultados_partida:
                # Dividir o valor no formato '0x0' em gols_casa e gols_visitante
                gols_casa, gols_visitante = resultado[1].split('x')
                gols_casa = int(gols_casa)
                gols_visitante = int(gols_visitante)

                # Determinar a descrição do resultado com base nos gols marcados por ambas as equipes
                descricao_resultado = "Ambas marcaram" if gols_casa > 0 and gols_visitante > 0 else "Ambas não marcaram"

                # Determinar o resultado da partida com base nos gols marcados por cada equipe
                resultado_partida = 'Casa' if gols_casa > gols_visitante else 'Fora' if gols_visitante > gols_casa else 'Empate'

                # Calcular a soma dos gols marcados
                soma_gols = gols_casa + gols_visitante

                # Determinar a faixa de gols com base na soma dos gols marcados
                if soma_gols >= 5:
                    faixa_gols = "Over 0.5 / Over 1.5 / Over 2.5 / Over 3.5 / 5+"
                elif soma_gols == 4:
                    faixa_gols = "Over 0.5 / Over 1.5 / Over 2.5 / Over 3.5"
                elif soma_gols == 3:
                    faixa_gols = "Over 0.5 / Over 1.5 / Over 2.5 / Under 3.5"
                elif soma_gols == 2:
                    faixa_gols = "Over 0.5 / Over 1.5 / Under 2.5 / Under 3.5"
                elif soma_gols == 1:
                    faixa_gols = "Over 0.5 / Under 1.5 / Under 2.5 / Under 3.5"
                else:
                    faixa_gols = "Under 0.5 / Under 1.5 / Under 2.5 / Under 3.5"

                # Concatenar as informações do resultado em uma string e adicionar à lista de resultados transformados
                resultados_partida_transformados.append(f"{descricao_resultado} - {resultado_partida} - {faixa_gols} - {resultado[0]}")

            # Adicionar a lista de resultados transformados à lista de valores transformados
            valores_transformados.append(resultados_partida_transformados)

        return valores_transformados

    def transformar_valores_dicionario(dicionario):
        dicionario_transformado = {}
        for chave, valores in dicionario.items():
            # Chamar a função transformar_valores para cada lista de valores no dicionário
            valores_transformados = transformar_valores(valores)
            # Adicionar os valores transformados ao novo dicionário com a mesma chave
            dicionario_transformado[chave] = valores_transformados

        return dicionario_transformado

    # Aplicar a transformação aos dicionários ambas_marcaram e ambas_nao_marcaram
    ambas_marcaram_transformado = transformar_valores_dicionario(ambas_marcaram)
    ambas_nao_marcaram_transformado = transformar_valores_dicionario(ambas_nao_marcaram)

    # ESSE CÓDIGO SELECIONA ALEATORIAMENTE 10 PARTIDAS DE AMBAS MARCARAM E PARTIDAS DE AMBAS NÃO MARCARAM

    # Criação de ambas_marcaram_anterior
    ambas_marcaram_anterior = {}
    ambas_marcaram_anterior = ambas_marcaram_transformado.copy()

    # Criação dos dicionários ambas_marcaram_partidas_anterior e ambas_nao_marcaram_partidas_anterior
    ambas_marcaram_partidas_anterior = {}
    ambas_nao_marcaram_partidas_anterior = {}

    # Verificação das chaves em ambas_marcaram_anterior
    for chave in ambas_marcaram_anterior:
        if chave in ambas_marcaram_anterior:
            lista_partidas_am = ambas_marcaram_anterior[chave]
            # Criação das variáveis das partidas
            primeira_partida = lista_partidas_am[valor_partida - 2][0]
            segunda_partida = lista_partidas_am[valor_partida - 3][0]
            terceira_partida = lista_partidas_am[valor_partida - 4][0]
            quarta_partida = lista_partidas_am[valor_partida - 5][0]
            quinta_partida = lista_partidas_am[valor_partida - 6][0]
            sexta_partida = lista_partidas_am[valor_partida - 7][0]
            setima_partida = lista_partidas_am[valor_partida - 8][0]
            oitava_partida = lista_partidas_am[valor_partida - 9][0]
            nona_partida = lista_partidas_am[valor_partida - 10][0]
            decima_partida = lista_partidas_am[valor_partida - 11][0]
            decima_primeira_partida = lista_partidas_am[valor_partida - 12][0]
            decima_segunda_partida = lista_partidas_am[valor_partida - 13][0]
            decima_terceira_partida = lista_partidas_am[valor_partida - 14][0]
            decima_quarta_partida = lista_partidas_am[valor_partida - 15][0]
            decima_quinta_partida = lista_partidas_am[valor_partida - 16][0]
            decima_sexta_partida = lista_partidas_am[valor_partida - 17][0]
            decima_setima_partida = lista_partidas_am[valor_partida - 18][0]
            decima_oitava_partida = lista_partidas_am[valor_partida - 19][0]
            decima_nona_partida = lista_partidas_am[valor_partida - 20][0]
            vigesima_partida = lista_partidas_am[valor_partida - 21][0]

            ambas_marcaram_partidas_anterior[chave] = [
                primeira_partida, segunda_partida, terceira_partida, quarta_partida, quinta_partida,
                sexta_partida, setima_partida, oitava_partida, nona_partida, decima_partida,
                decima_primeira_partida, decima_segunda_partida, decima_terceira_partida,
                decima_quarta_partida, decima_quinta_partida, decima_sexta_partida,
                decima_setima_partida, decima_oitava_partida, decima_nona_partida, vigesima_partida
            ]


    ambas_marcaram_partidas_anterior = dict(sorted(ambas_marcaram_partidas_anterior.items()))

    # Criação do DataFrame com as colunas
    colunas = []
    for i in range(1, num_colunas + 1):
        colunas.extend([f"{i} (AM/AN)", f"{i} (Resultado da partida)",f"{i} (Gols)", f"{i} (Primeiro tempo)"])

    df_ambas = pd.DataFrame(columns=colunas)

    # Preenchimento do DataFrame
    for chave, valores in ambas_marcaram_partidas_anterior.items():
        dados_chave = []
        for valor in valores:
            am_an, resultado, gols, primeiro_tempo = valor.split(' - ')
            dados_chave.extend([am_an, resultado, gols, primeiro_tempo])
        df_ambas.loc[chave] = dados_chave

    df_ambas_transposto = df_ambas.transpose()
    df_ambas_transposto = df_ambas_transposto[::-1]

    # Crie uma lista com os valores que serão preenchidos na coluna "Partidas atrás"
    valores = []
    for i in range(num_colunas, 0, -1):  # Percorre de 20 a 1 em ordem decrescente
        valores.extend([f"{i} (Primeiro tempo)", f"{i} (Gols)", f"{i} (Resultado da partida)", f"{i} (AM/AN)"])

    # Adicione a nova coluna "Partidas atrás" ao dataframe
    df_ambas_transposto.insert(0, "Partidas atrás", valores)

    df_ambas_transposto = df_ambas_transposto.reset_index(drop=True)

    def encontrar_valores_comuns(dataframe, porcentagem_desejada):
      porcentagem_desejada_metodo = porcentagem_desejada/10
      valores_comuns = []

      # Percorrendo as linhas do dataframe
      for i in range(len(dataframe)):
          linha = dataframe.iloc[i, :].tolist()  # Obtém os valores da linha

          # Verifica se é uma linha de gols
          if "Gols" in linha[0]:
              gols_values = set()

              # Percorre as colunas a partir da segunda coluna (índice 1)
              for j in range(1, len(linha)):
                  if linha[j] != 0:
                      gols = linha[j].split(" / ")
                      gols_values.update(gols)

              valores_comuns_linha = gols_values.copy()

              # Compara os valores de cada coluna com os valores em comum da linha
              for j in range(1, len(linha)):
                  if linha[j] != 0:
                      gols = linha[j].split(" / ")
                      valores_comuns_linha.intersection_update(gols)

              # Verifica se o número de valores em comum é maior ou igual a 70% do total de colunas
              if len(valores_comuns_linha) >= porcentagem_desejada_metodo * (len(linha) - 1):
                  valores_comuns.append(list(valores_comuns_linha))
              else:
                  valores_comuns.append(None)
          else:
              linha = linha[1:]  # Exclui a primeira coluna ('Partidas atrás')

              # Verifica se pelo menos 70% dos valores da linha são iguais
              if linha.count(linha[0]) >= porcentagem_desejada_metodo * (len(linha) - 1):
                  valores_comuns.append([linha[0]])  # Adiciona o valor comum à lista de valores comuns
              else:
                  valores_comuns.append(None)  # Se os valores não atingirem o critério, adiciona None à lista

      return valores_comuns, porcentagem_desejada

    valores_marcaram, porcentagem_desejada = encontrar_valores_comuns(df_ambas_transposto, porcentagem_desejada)

    # Criando o DataFrame final
    df_result = pd.DataFrame({
        'Linhas': [f'Valores comuns na linha {i}' for i in range(len(valores_marcaram))],
        'Ambas marcaram': valores_marcaram
    })

    # Sequência de índices desejada
    sequencia_indices = [76, 77, 78, 79, 72, 73, 74, 75, 68, 69, 70, 71, 64, 65, 66, 67, 60, 61, 62, 63, 56, 57, 58, 59, 52, 53, 54, 55, 48, 49, 50, 51, 44, 45, 46, 47, 40, 41, 42, 43, 36, 37, 38, 39, 32, 33, 34, 35, 28, 29, 30, 31, 24, 25, 26, 27, 20, 21, 22, 23, 16, 17, 18, 19, 12, 13, 14, 15, 8, 9, 10, 11, 4, 5, 6, 7, 0, 1, 2, 3]

    # Reordenar o DataFrame
    df_result = df_result.reindex(sequencia_indices)

    # Resetar o índice do DataFrame
    df_result = df_result.reset_index(drop=True)

    # Lista com os padrões de preenchimento
    padroes = [
        'Primeiro tempo',
        'Gols',
        'Resultado da partida',
        'AM/AN'
    ]

    # Função para preencher a coluna "Partidas atrás"
    def preencher_partidas_atras(row):
        valores = []
        for i in range(1, 21):
            for padrao in padroes:
                valores.append(f'{i} partida(s) atrás ({padrao})')
        return valores

    # Substituir a coluna "Linhas" pela coluna "Partidas atrás"
    df_result['Partidas atrás'] = preencher_partidas_atras(df_result)
    df_result = df_result.drop(columns='Linhas')

    # Reordenar as colunas
    df_result = df_result[['Partidas atrás', 'Ambas marcaram']]
    # Filtrar o dataframe para excluir as linhas com valores vazios na coluna "Ambas marcaram"
    df_result = df_result.dropna(subset=['Ambas marcaram'])
    st.write('Verificando ' + str(valor_partida) + ' após a ocorrência do padrão, esses foram os valores em comum em ' + str(porcentagem_desejada) + '% das partidas em que deu certo')
    
    st.write(df_result)
    
# Botão "Gerar resultados"
if st.button("Gerar resultados"):
    gerar_resultados()
