"""
==============================================================================
BANCO DE DADOS - Plataforma SaaS WhatsApp
==============================================================================
Gerencia usuarios (admin e empresas) e seus dados no SQLite.
"""

import sqlite3
import hashlib
import os
from datetime import datetime

# Caminho do banco de dados (mesmo diretorio do script)
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'plataforma.db')


def conectar():
    """Cria conexao com o banco SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Retorna dicionarios ao inves de tuplas
    return conn


def hash_senha(senha):
    """Gera hash SHA-256 da senha."""
    return hashlib.sha256(senha.encode('utf-8')).hexdigest()


def criar_tabelas():
    """Cria as tabelas do banco se nao existirem e insere o admin padrao."""
    conn = conectar()
    cursor = conn.cursor()
    
    # Tabela de usuarios (login)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            tipo TEXT NOT NULL DEFAULT 'empresa',
            ativo INTEGER NOT NULL DEFAULT 1,
            criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime'))
        )
    ''')
    
    # Tabela de empresas (dados do robo)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS empresas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            usuario_id INTEGER NOT NULL,
            nome_empresa TEXT NOT NULL,
            instancia_nome TEXT UNIQUE NOT NULL,
            menu_texto TEXT NOT NULL DEFAULT 'Ola! Bem-vindo. Digite 1 para opcao A ou 2 para opcao B.',
            plano TEXT NOT NULL DEFAULT 'essencial',
            ativo INTEGER NOT NULL DEFAULT 1,
            criado_em TEXT NOT NULL DEFAULT (datetime('now', 'localtime')),
            FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
        )
    ''')
    
    # Criar admin padrao se nao existir
    admin_existe = cursor.execute(
        "SELECT id FROM usuarios WHERE email = ?", ("admin@saas.com",)
    ).fetchone()
    
    if not admin_existe:
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (?, ?, ?, ?)",
            ("Administrador", "admin@saas.com", hash_senha("admin123"), "admin")
        )
        print("[DB] Conta admin criada: admin@saas.com / admin123")
    
    conn.commit()
    conn.close()


def autenticar(email, senha):
    """
    Verifica email e senha. 
    Retorna dict do usuario se OK, ou None se falhar.
    """
    conn = conectar()
    usuario = conn.execute(
        "SELECT * FROM usuarios WHERE email = ? AND senha_hash = ? AND ativo = 1",
        (email, hash_senha(senha))
    ).fetchone()
    conn.close()
    
    if usuario:
        return dict(usuario)
    return None


def cadastrar_empresa(nome_responsavel, email, senha, nome_empresa, instancia_nome, plano="essencial"):
    """
    Cadastra um novo usuario do tipo 'empresa' e sua empresa.
    Retorna (True, msg) ou (False, msg_erro).
    """
    conn = conectar()
    cursor = conn.cursor()
    
    try:
        # Cria o usuario
        cursor.execute(
            "INSERT INTO usuarios (nome, email, senha_hash, tipo) VALUES (?, ?, ?, ?)",
            (nome_responsavel, email, hash_senha(senha), "empresa")
        )
        usuario_id = cursor.lastrowid
        
        # Cria a empresa vinculada
        cursor.execute(
            "INSERT INTO empresas (usuario_id, nome_empresa, instancia_nome, plano) VALUES (?, ?, ?, ?)",
            (usuario_id, nome_empresa, instancia_nome, plano)
        )
        
        conn.commit()
        return True, f"Empresa '{nome_empresa}' cadastrada com sucesso!"
        
    except sqlite3.IntegrityError as e:
        conn.rollback()
        if "email" in str(e):
            return False, "Esse email ja esta cadastrado."
        elif "instancia_nome" in str(e):
            return False, "Esse nome de instancia ja esta em uso."
        return False, f"Erro ao cadastrar: {e}"
    finally:
        conn.close()


def listar_empresas():
    """Retorna todas as empresas com dados do usuario responsavel."""
    conn = conectar()
    empresas = conn.execute('''
        SELECT e.*, u.nome as responsavel, u.email
        FROM empresas e
        JOIN usuarios u ON e.usuario_id = u.id
        ORDER BY e.criado_em DESC
    ''').fetchall()
    conn.close()
    return [dict(e) for e in empresas]


def obter_empresa_por_usuario(usuario_id):
    """Retorna a empresa vinculada a um usuario."""
    conn = conectar()
    empresa = conn.execute(
        "SELECT * FROM empresas WHERE usuario_id = ?", (usuario_id,)
    ).fetchone()
    conn.close()
    return dict(empresa) if empresa else None


def atualizar_menu(empresa_id, novo_menu):
    """Atualiza o texto do menu de uma empresa."""
    conn = conectar()
    conn.execute(
        "UPDATE empresas SET menu_texto = ? WHERE id = ?",
        (novo_menu, empresa_id)
    )
    conn.commit()
    conn.close()


def alternar_status_empresa(empresa_id):
    """Ativa/desativa uma empresa."""
    conn = conectar()
    empresa = conn.execute("SELECT ativo FROM empresas WHERE id = ?", (empresa_id,)).fetchone()
    if empresa:
        novo_status = 0 if empresa['ativo'] else 1
        conn.execute("UPDATE empresas SET ativo = ? WHERE id = ?", (novo_status, empresa_id))
        conn.commit()
    conn.close()


def obter_empresas_ativas():
    """
    Retorna um dicionario das empresas ativas no formato que o whatsapp.py espera.
    Ex: {"PizzariaMario": {"nome": "Pizzaria do Mario", "menu": "Ola! ..."}}
    """
    conn = conectar()
    empresas = conn.execute(
        "SELECT instancia_nome, nome_empresa, menu_texto FROM empresas WHERE ativo = 1"
    ).fetchall()
    conn.close()
    
    resultado = {}
    for e in empresas:
        resultado[e['instancia_nome']] = {
            "nome": e['nome_empresa'],
            "menu": e['menu_texto']
        }
    return resultado


# Criar tabelas automaticamente ao importar o modulo
criar_tabelas()
