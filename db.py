import sqlite3
from datetime import datetime

def conectar():
    return sqlite3.connect("fiado.db")

def criar_tabelas():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL UNIQUE
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fiados (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            descricao TEXT,
            valor REAL,
            data TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pagamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            cliente_id INTEGER,
            valor REAL,
            data TEXT,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id)
        )
    ''')
    conn.commit()
    conn.close()

def inserir_cliente(nome):
    conn = conectar()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO clientes (nome) VALUES (?)", (nome,))
        conn.commit()
    except sqlite3.IntegrityError:
        pass  # Cliente já existe
    conn.close()

def buscar_clientes():
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute("SELECT id, nome FROM clientes")
    res = cursor.fetchall()
    conn.close()
    return res

def inserir_fiado(cliente_id, descricao, valor, data):
    conn = conectar()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO fiados (cliente_id, descricao, valor, data) VALUES (?, ?, ?, ?)",
        (cliente_id, descricao, valor, data)
    )
    conn.commit()
    conn.close()

def buscar_fiados_por_cliente(nome_cliente):
    conn = conectar()
    cursor = conn.cursor()

    # Pega id do cliente pelo nome
    cursor.execute("SELECT id FROM clientes WHERE nome = ?", (nome_cliente,))
    cliente = cursor.fetchone()
    if not cliente:
        conn.close()
        return [], 0, None, 0
    cliente_id = cliente[0]

    # Busca fiados para esse cliente
    cursor.execute("SELECT * FROM fiados WHERE cliente_id = ?", (cliente_id,))
    fiados = cursor.fetchall()
    print("FIADOS:", fiados)  # DEBUG para conferir

    total = sum(f[3] for f in fiados)  # f[3] é valor

    # Busca último pagamento
    cursor.execute(
        "SELECT data, valor FROM pagamentos WHERE cliente_id = ? ORDER BY data DESC LIMIT 1",
        (cliente_id,)
    )
    ultima = cursor.fetchone()
    conn.close()

    return fiados, total, ultima[0] if ultima else None, ultima[1] if ultima else 0

def registrar_pagamento(nome_cliente, valor):
    conn = conectar()
    cursor = conn.cursor()

    # Buscar cliente
    cursor.execute("SELECT id FROM clientes WHERE nome = ?", (nome_cliente,))
    cliente = cursor.fetchone()
    if not cliente:
        conn.close()
        return "Cliente não encontrado."

    cliente_id = cliente[0]

    # Buscar total devido
    cursor.execute("SELECT SUM(valor) FROM fiados WHERE cliente_id = ?", (cliente_id,))
    total_devido = cursor.fetchone()[0] or 0

    if valor > total_devido:
        conn.close()
        return f"Erro: pagamento R$ {valor:.2f} maior que total devido R$ {total_devido:.2f}."

    data = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute(
        "INSERT INTO pagamentos (cliente_id, valor, data) VALUES (?, ?, ?)",
        (cliente_id, valor, data)
    )

    # Ajustar fiados do mais antigo para o mais recente
    cursor.execute("SELECT id, valor FROM fiados WHERE cliente_id = ? ORDER BY data", (cliente_id,))
    fiados = cursor.fetchall()

    restante = valor
    for fid, val in fiados:
        if restante <= 0:
            break
        if restante >= val:
            cursor.execute("DELETE FROM fiados WHERE id = ?", (fid,))
            restante -= val
        else:
            novo_valor = val - restante
            cursor.execute("UPDATE fiados SET valor = ? WHERE id = ?", (novo_valor, fid))
            restante = 0

    conn.commit()
    conn.close()
    return None
