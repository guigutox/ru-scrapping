import psycopg2
import json
import os
from dotenv import load_dotenv  # Importando dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Conexão com o banco de dados PostgreSQL usando variáveis de ambiente
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),       # Nome do banco de dados
    user=os.getenv("DB_USER"),         # Usuário do banco de dados
    password=os.getenv("DB_PASSWORD"),  # Senha do banco de dados
    host=os.getenv("DB_HOST"),          # Host do banco de dados
    port=os.getenv("DB_PORT")           # Porta do banco de dados
)
cursor = conn.cursor()

# Criação da tabela com colunas separadas para arroz branco e integral
cursor.execute("""
    CREATE TABLE IF NOT EXISTS cardapios (
        id SERIAL PRIMARY KEY,
        campus VARCHAR(100),
        data DATE,
        refeicao VARCHAR(50),
        prato_principal TEXT,
        prato_veg TEXT,
        arroz_branco TEXT,
        arroz_integral TEXT,
        feijao TEXT,
        guarnicao TEXT,
        salada TEXT
    );
""")
conn.commit()

# Abrir e carregar o arquivo JSON
with open('cardapios.json', 'r', encoding='utf-8') as f:
    cardapios = json.load(f)

# Função auxiliar para separar o arroz branco e o integral
def separar_arroz(arroz_lista):
    arroz_branco = 'Não Encontrado'
    arroz_integral = 'Não Encontrado'
    for arroz in arroz_lista:
        if 'Branco' in arroz:
            arroz_branco = arroz
        elif 'Integral' in arroz:
            arroz_integral = arroz
    return arroz_branco, arroz_integral

# Inserir os dados no banco de dados
for campus, dias in cardapios.items():
    for dia in dias:
        data = dia['data']
        for refeicao, pratos in dia['cardapio'].items():
            # Extrair os pratos para as colunas apropriadas
            prato_principal = ', '.join(pratos.get('prato_principal', ['Não Encontrado']))
            prato_veg = ', '.join(pratos.get('prato_veg', ['Não Encontrado']))
            
            # Separar arroz branco e arroz integral
            arroz_lista = pratos.get('arroz', ['Não Encontrado'])
            arroz_branco, arroz_integral = separar_arroz(arroz_lista)
            
            feijao = ', '.join(pratos.get('feijao', ['Não Encontrado']))
            guarnicao = ', '.join(pratos.get('guarnicao', ['Não Encontrado']))
            salada = ', '.join(pratos.get('salada', ['Não Encontrado']))

            # Inserir uma única linha com todos os pratos
            cursor.execute("""
                INSERT INTO cardapios (campus, data, refeicao, prato_principal, prato_veg, arroz_branco, arroz_integral, feijao, guarnicao, salada)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
            """, (campus, data, refeicao, prato_principal, prato_veg, arroz_branco, arroz_integral, feijao, guarnicao, salada))

# Confirmar a transação e fechar a conexão
conn.commit()
cursor.close()
conn.close()
