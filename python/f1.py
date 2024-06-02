import csv
import infobd
import os
from datetime import date
from time import sleep

import pymysql
# import acesso_db
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from funcoes import paispiloto

caminho_csv = "E:\\00 - GITHUB\\prjCampeosF1\\csv\\campeoes_f1.csv"

# Cria o driver para automatizar o navegador
chrome_options = Options()
# não fecha o chrome
#chrome_options.add_experimental_option("Detach", True)
#chrome_options.set_capability("detach", True)
# abre oculto o navegador
#chrome_options.add_argument("headLess")

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)

#########  FUNCOES DO PROJETO  #############
######## FUNÇÃO LER ARQUIVO .CSV E GRAVAR NO BD ##########
#https://www.w3schools.com/python/python_mysql_where.asp
# FUNÇÃO PARA GRAVAR NO BD (NUVEM)
def gravarnobanco():
    connection = pymysql.connect(
        host=infobd.host,
        user=infobd.user,
        password=infobd.password,
        database=infobd.database,
        port=infobd.port
    )
    print(connection)

    # Cursor (quem "escreve" os comandos no banco):
    cursor = connection.cursor()

    # criando o banco
    # cursor.execute("CREATE DATABASE dbf1")

    # verifica se criou
    cursor.execute("SHOW DATABASES")

    for x in cursor:
        print(x)

    # DELETAR A TABELA PARA NAO DAR ERRO DUPLICACAO
    cursor.execute("DROP TABLE IF EXISTS tbf1")

    # cria a tabela caso nao exista
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS tbf1 (ID int PRIMARY KEY NOT NULL, ano char(4), piloto varchar(40), equipe varchar(50), paisorigem varchar(50), data_busca datetime);")
    # veja se criou a tabela
    cursor.execute("SHOW TABLES")

    for x in cursor:
        print(x)

    # AGORA É LER O ARQUIVO E GRAVAR TUDO
    # inserindo registro novo
    sqli = "INSERT INTO tbf1 (ID, ano, piloto, equipe, paisorigem, data_busca ) VALUES (%s, %s, %s, %s, %s, %s)"

    with open(caminho_csv, "r") as arqlido:
        leitor_csv = csv.reader(arqlido, delimiter=";")
        for linha in leitor_csv:
            val = (linha[0], linha[1], linha[2], linha[3], linha[4], linha[5])
            cursor.execute(sqli, val)
    connection.commit()

    print(cursor.rowcount, "registro inserido.")

    # fecha conexao com o BD
    cursor.close()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

########## FUNCAO PARA DELETAR ARQ CSV
def deleta_arq_csv():
    nome_arquivo = caminho_csv
    # Verifique se o arquivo existe e então o delete
    if os.path.isfile(nome_arquivo):
        os.remove(nome_arquivo)
    else:
        # Informe o usuário se o arquivo não existir
        print(f"Erro: arquivo {nome_arquivo} não encontrado para remover")
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

########## FUNCAO PARA ESCREVER ARQ CSV
def escreverarq(lista):

    with open(caminho_csv, mode="a", encoding='utf-8', newline='') as arq_csv:
        escritor = csv.writer(arq_csv, delimiter=";")
        escritor.writerow(lista)
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@

###########  FUNÇÃO PARA ACESSAR O SITE, RASPAR OS DADOS
###########  E GRAVAR NO ARQUIVO .CSV
def raspagem():

    print('=======================================')

    # Acessa o site
    driver.get("https://autoesporte.globo.com/curiosidades/noticia/2023/03/relembre-todos-os-campeoes-da-f1-desde-1950.ghtml")
    sleep(3)

    bveja_mais = driver.find_element(By.ID,'mc-read-more-btn')
    driver.execute_script("arguments[0].click()", bveja_mais)
    sleep(3)

    titulo = driver.find_element(By.CLASS_NAME,'content-head__title').text
    print('TITULO DA PAGINA: ' + titulo)

    tabela_campeoes = driver.find_element(By.XPATH, '//*[@id="mc-article-body"]/article/div[1]/div[4]/div[5]/div/div/div/div/div[1]/table/tbody')

    linhas_tabela = tabela_campeoes.find_elements(By.TAG_NAME, 'tr')
    print('Nº Linhas da tabela: ', len(linhas_tabela))
    cont = 0
    for linha in linhas_tabela[1:]:
        print(linha.text)

        dados = linha.find_elements(By.TAG_NAME, 'td')
        cont += 1
        try:
            ano = dados[0].text
        except:
            ano = 'null'

        try:
            piloto = dados[1].text
        except:
            piloto = 'null'

        try:
            equipe = dados[2].text
        except:
            equipe = 'null'

        pais_do_piloto = paispiloto(piloto)
        escreverarq([str(cont), ano, piloto, equipe, pais_do_piloto, date.today()])

    # vou gravar por ultimo 2023
    escreverarq(['74', '2023', 'Max Verstappen', 'Red Bull', 'Holanda', date.today()])

    #arq_csv.close()
#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@


# ================ PROGRAMA PRINCIPAL =============================
# começa deletando o arquivo
deleta_arq_csv()
raspagem()
gravarnobanco()




