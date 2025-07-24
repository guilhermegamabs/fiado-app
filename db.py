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