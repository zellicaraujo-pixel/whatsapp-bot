"""
Painel - Metricas e Status do Sistema
"""
import streamlit as st
import requests
import database as db

if not st.session_state.get('logado'):
    st.warning("Faca login primeiro.")
    st.stop()

usuario = st.session_state['usuario']

EVOLUTION_API_URL = "http://localhost:8080"
EVOLUTION_API_KEY = "sua_senha_secreta_global"

with st.sidebar:
    st.markdown(f"### {usuario['nome']}")
    st.caption(f"{usuario['tipo'].upper()}")
    if st.button("Sair", use_container_width=True):
        st.session_state['logado'] = False
        st.session_state['usuario'] = None
        st.rerun()

st.markdown("## 📊 Painel de Controle")
st.caption("Visao geral do sistema")
st.markdown("---")

st.subheader("Status do Servidor")
try:
    resp = requests.get(f"{EVOLUTION_API_URL}/instance/fetchInstances",
                       headers={"apikey": EVOLUTION_API_KEY}, timeout=5)
    api_online = resp.status_code == 200
except Exception:
    api_online = False

if api_online:
    st.success("Evolution API Online")
else:
    st.error("Evolution API Offline")

st.markdown("---")

if usuario['tipo'] == 'admin':
    st.subheader("Metricas das Empresas")
    empresas = db.listar_empresas()
    ativas = [e for e in empresas if e['ativo']]

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total", len(empresas))
    m2.metric("Ativas", len(ativas))
    m3.metric("Inativas", len(empresas) - len(ativas))
    m4.metric("Taxa", f"{(len(ativas)/max(len(empresas),1)*100):.0f}%")
else:
    empresa = db.obter_empresa_por_usuario(usuario['id'])
    if empresa:
        st.subheader(f"{empresa['nome_empresa']}")
        c1, c2 = st.columns(2)
        c1.metric("Status", "Ativa" if empresa['ativo'] else "Inativa")
        c2.metric("Plano", empresa['plano'].title())
