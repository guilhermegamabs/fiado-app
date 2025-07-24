# db.py

import sqlite3

def conectar():
    return sqlite3.connect('fiado.db')

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fiados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            descricao TEXT,
            valor REAL,
            data TEXT,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            valor REAL,
            data TEXT,
            FOREIGN KEY(cliente_id) REFERENCES clientes(id)
        )
    ''')
    
    conn.commit()
    conn.close()

def inserir_cliente(nome):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO clientes (nome) VALUES (?)", (nome,))
    conn.commit()
    conn.close()

def buscar_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM clientes ORDER BY nome")
    resultados = cursor.fetchall()
    conn.close()
    return resultados  

def inserir_fiado(cliente_id, descricao, valor, data):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO fiados (cliente_id, descricao, valor, data) VALUES (?, ?, ?, ?)",
        (cliente_id, descricao, valor, data)
    )
    conn.commit()
    conn.close()
    
def buscar_fiados():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT f.id, c.nome, f.descricao, f.valor, f.data
        FROM fiados f
        JOIN clientes c ON f.cliente_id = c.id
        ORDER BY f.data DESC
    """)
    resultados = cursor.fetchall()
    conn.close()
    return resultados  # lista de tuplas (id, nome_cliente, descricao, valor, data)
    