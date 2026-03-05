"""
Empresas - Cadastro e Gerenciamento
"""
import streamlit as st
import database as db

if not st.session_state.get('logado'):
    st.warning("Faca login primeiro.")
    st.stop()

usuario = st.session_state['usuario']

with st.sidebar:
    st.markdown(f"### {usuario['nome']}")
    if st.button("Sair", use_container_width=True):
        st.session_state['logado'] = False
        st.rerun()

st.markdown("## 🏢 Gerenciar Empresas")
st.markdown("---")

if usuario['tipo'] == 'admin':
    tab_lista, tab_cadastro = st.tabs(["Empresas Cadastradas", "Cadastrar Nova"])

    with tab_lista:
        empresas = db.listar_empresas()
        if empresas:
            for empresa in empresas:
                status = "Ativa" if empresa['ativo'] else "Inativa"
                with st.expander(f"{empresa['nome_empresa']} - {status}"):
                    st.write(f"**Responsavel:** {empresa['responsavel']}")
                    st.write(f"**Email:** {empresa['email']}")
                    st.write(f"**Instancia:** {empresa['instancia_nome']}")
                    st.write(f"**Plano:** {empresa['plano'].title()}")
                    st.markdown("---")
                    novo_menu = st.text_area("Menu do Bot", value=empresa['menu_texto'],
                                            key=f"menu_{empresa['id']}", height=120)
                    c1, c2 = st.columns(2)
                    with c1:
                        if st.button("Salvar Menu", key=f"s_{empresa['id']}",
                                    use_container_width=True):
                            db.atualizar_menu(empresa['id'], novo_menu)
                            st.success("Menu atualizado!")
                            st.rerun()
                    with c2:
                        lbl = "Desativar" if empresa['ativo'] else "Ativar"
                        if st.button(lbl, key=f"t_{empresa['id']}",
                                    use_container_width=True):
                            db.alternar_status_empresa(empresa['id'])
                            st.rerun()
        else:
            st.info("Nenhuma empresa cadastrada.")

    with tab_cadastro:
        st.subheader("Nova Empresa")
        with st.form("form_nova"):
            c1, c2 = st.columns(2)
            with c1:
                nome_resp = st.text_input("Nome do Responsavel")
                email = st.text_input("Email")
                senha = st.text_input("Senha", type="password")
            with c2:
                nome_empresa = st.text_input("Nome da Empresa")
                instancia = st.text_input("Nome da Instancia")
                plano = st.selectbox("Plano", ["essencial", "profissional", "premium"])
            submit = st.form_submit_button("Cadastrar", use_container_width=True)
            if submit:
                if all([nome_resp, email, senha, nome_empresa, instancia]):
                    ok, msg = db.cadastrar_empresa(nome_resp, email, senha,
                                                   nome_empresa, instancia, plano)
                    if ok:
                        st.success(msg)
                        st.balloons()
                    else:
                        st.error(msg)
                else:
                    st.warning("Preencha todos os campos.")
else:
    empresa = db.obter_empresa_por_usuario(usuario['id'])
    if empresa:
        st.subheader(empresa['nome_empresa'])
        novo_menu = st.text_area("Menu do Bot:", value=empresa['menu_texto'], height=150)
        if st.button("Salvar", use_container_width=True):
            db.atualizar_menu(empresa['id'], novo_menu)
            st.success("Menu atualizado!")
