"""
Config - Evolution API e WhatsApp
"""
import streamlit as st
import requests

if not st.session_state.get('logado'):
    st.warning("Faca login primeiro.")
    st.stop()

usuario = st.session_state['usuario']
if usuario['tipo'] != 'admin':
    st.warning("Apenas administradores.")
    st.stop()

with st.sidebar:
    st.markdown(f"### {usuario['nome']}")
    if st.button("Sair", use_container_width=True):
        st.session_state['logado'] = False
        st.rerun()

st.markdown("## ⚙️ Configuracoes")
st.markdown("---")

if 'evo_url' not in st.session_state:
    st.session_state['evo_url'] = "http://localhost:8080"
if 'evo_key' not in st.session_state:
    st.session_state['evo_key'] = "sua_senha_secreta_global"

st.subheader("Conexao com Evolution API")
c1, c2 = st.columns(2)
with c1:
    evo_url = st.text_input("URL da API", value=st.session_state['evo_url'])
with c2:
    evo_key = st.text_input("API Key", value=st.session_state['evo_key'], type="password")

if st.button("Testar Conexao"):
    try:
        resp = requests.get(f"{evo_url}/instance/fetchInstances",
                           headers={"apikey": evo_key}, timeout=5)
        if resp.status_code == 200:
            st.success("Conexao OK!")
            st.session_state['evo_url'] = evo_url
            st.session_state['evo_key'] = evo_key
        else:
            st.error(f"Erro {resp.status_code}")
    except Exception as e:
        st.error(f"Erro: {e}")

st.markdown("---")
st.subheader("Configurar Webhook")
c1, c2 = st.columns(2)
with c1:
    inst = st.text_input("Instancia", value="PizzariaMario")
with c2:
    wh_url = st.text_input("URL Webhook", value="http://host.docker.internal:5000/webhook")

if st.button("Configurar Webhook", use_container_width=True):
    try:
        r = requests.post(f"{st.session_state['evo_url']}/webhook/set/{inst}",
                         headers={"apikey": st.session_state['evo_key'],
                                  "Content-Type": "application/json"},
                         json={"url": wh_url, "webhook_by_events": False,
                               "events": ["MESSAGES_UPSERT"]})
        if r.status_code in [200, 201]:
            st.success(f"Webhook configurado! URL: {wh_url}")
        else:
            st.error(f"Erro: {r.text[:300]}")
    except Exception as e:
        st.error(f"Erro: {e}")
