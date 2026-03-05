"""
Dashboard Principal — Login e Navegação
"""
import streamlit as st
import database as db

# ==============================================================================
# CONFIGURAÇÃO DA PÁGINA
# ==============================================================================
st.set_page_config(
    page_title="WhatsApp Bot — Painel",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# CSS CUSTOMIZADO
# ==============================================================================
st.markdown("""
<style>
    /* Esconder menu padrão e footer */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Cores e fontes */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    
    /* Login card */
    .login-container {
        max-width: 420px;
        margin: 60px auto;
        padding: 40px;
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border-radius: 20px;
        border: 1px solid rgba(255,255,255,0.08);
        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    }
    
    .login-title {
        text-align: center;
        font-size: 28px;
        font-weight: 700;
        background: linear-gradient(135deg, #25D366, #128C7E);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 8px;
    }
    
    .login-subtitle {
        text-align: center;
        color: #8892b0;
        font-size: 14px;
        margin-bottom: 30px;
    }
    
    /* Botão verde WhatsApp */
    .stButton > button {
        background: linear-gradient(135deg, #25D366 0%, #128C7E 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px 24px;
        font-weight: 600;
        font-size: 16px;
        width: 100%;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(37, 211, 102, 0.3);
    }
    
    /* Sidebar */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a192f 0%, #1a1a2e 100%);
    }
    
    /* Métricas */
    [data-testid="stMetric"] {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 20px;
    }
    
    [data-testid="stMetric"] label,
    [data-testid="stMetric"] [data-testid="stMetricLabel"],
    [data-testid="stMetric"] [data-testid="stMetricValue"],
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {
        color: #ffffff !important;
    }
    
    [data-testid="stMetric"] [data-testid="stMetricValue"] {
        font-size: 28px;
        font-weight: 700;
    }
    
    /* Inputs */
    .stTextInput > div > div > input {
        border-radius: 10px;
        border: 1px solid rgba(255,255,255,0.1);
        background: rgba(255,255,255,0.03);
    }
    
    /* Status badges */
    .status-ativo {
        background: rgba(37, 211, 102, 0.15);
        color: #25D366;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    
    .status-inativo {
        background: rgba(255, 71, 87, 0.15);
        color: #ff4757;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Header com gradiente */
    .header-gradient {
        background: linear-gradient(135deg, #25D366 0%, #128C7E 50%, #075E54 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 32px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# FUNÇÕES AUXILIARES
# ==============================================================================
def fazer_login(email, senha):
    """Tenta autenticar o usuário."""
    usuario = db.autenticar(email, senha)
    if usuario:
        st.session_state['logado'] = True
        st.session_state['usuario'] = usuario
        return True
    return False


def fazer_logout():
    """Limpa a sessão."""
    st.session_state['logado'] = False
    st.session_state['usuario'] = None
    st.rerun()


# ==============================================================================
# INICIALIZAR SESSÃO
# ==============================================================================
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
    st.session_state['usuario'] = None


# ==============================================================================
# PÁGINA DE LOGIN
# ==============================================================================
def pagina_login():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    
    with col2:
        st.markdown("")
        st.markdown("")
        
        # Logo e título
        st.markdown('<p class="login-title">🤖 WhatsApp Bot</p>', unsafe_allow_html=True)
        st.markdown('<p class="login-subtitle">Plataforma de Automação Multi-Empresa</p>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Formulário de login
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="admin@saas.com")
            senha = st.text_input("🔑 Senha", type="password", placeholder="••••••••")
            
            st.markdown("")
            submit = st.form_submit_button("Entrar", use_container_width=True)
            
            if submit:
                if email and senha:
                    if fazer_login(email, senha):
                        st.rerun()
                    else:
                        st.error("❌ Email ou senha incorretos!")
                else:
                    st.warning("⚠️ Preencha todos os campos.")
        
        st.markdown("")
        st.markdown(
            '<p style="text-align:center; color:#4a5568; font-size:12px;">'
            'Admin padrão: admin@saas.com / admin123</p>',
            unsafe_allow_html=True
        )


# ==============================================================================
# PÁGINA PRINCIPAL (PÓS-LOGIN)
# ==============================================================================
def pagina_principal():
    usuario = st.session_state['usuario']
    
    # Sidebar
    with st.sidebar:
        st.markdown(f"### 👤 {usuario['nome']}")
        st.caption(f"📧 {usuario['email']}")
        st.caption(f"🏷️ Tipo: **{usuario['tipo'].upper()}**")
        st.markdown("---")
        
        if st.button("🚪 Sair", use_container_width=True):
            fazer_logout()
    
    # Conteúdo principal
    st.markdown('<p class="header-gradient">🤖 WhatsApp Bot — Painel</p>', unsafe_allow_html=True)
    st.caption("Plataforma de automação multi-empresa")
    st.markdown("---")
    
    if usuario['tipo'] == 'admin':
        mostrar_visao_admin()
    else:
        mostrar_visao_empresa(usuario)


def mostrar_visao_admin():
    """Visão do administrador com métricas gerais."""
    empresas = db.listar_empresas()
    ativas = [e for e in empresas if e['ativo']]
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("🏢 Total Empresas", len(empresas))
    col2.metric("✅ Ativas", len(ativas))
    col3.metric("❌ Inativas", len(empresas) - len(ativas))
    col4.metric("📊 Taxa Ativa", f"{(len(ativas)/max(len(empresas),1)*100):.0f}%")
    
    st.markdown("---")
    
    # Lista de empresas
    st.subheader("📋 Empresas Cadastradas")
    
    if empresas:
        for empresa in empresas:
            status = "🟢 Ativa" if empresa['ativo'] else "🔴 Inativa"
            with st.expander(f"{empresa['nome_empresa']} — {status}"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Responsável:** {empresa['responsavel']}")
                    st.write(f"**Email:** {empresa['email']}")
                    st.write(f"**Instância:** `{empresa['instancia_nome']}`")
                with col2:
                    st.write(f"**Plano:** {empresa['plano'].title()}")
                    st.write(f"**Criado em:** {empresa['criado_em']}")
                
                st.markdown("**Menu do Bot:**")
                st.code(empresa['menu_texto'], language=None)
    else:
        st.info("Nenhuma empresa cadastrada ainda. Vá em **🏢 Empresas** para cadastrar.")


def mostrar_visao_empresa(usuario):
    """Visão da empresa (não-admin)."""
    empresa = db.obter_empresa_por_usuario(usuario['id'])
    
    if empresa:
        st.subheader(f"🏢 {empresa['nome_empresa']}")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("📊 Status", "Ativa" if empresa['ativo'] else "Inativa")
        with col2:
            st.metric("💼 Plano", empresa['plano'].title())
        
        st.markdown("---")
        st.subheader("💬 Menu do Bot")
        st.code(empresa['menu_texto'], language=None)
        st.info("Para editar o menu, vá em **🏢 Empresas**.")
    else:
        st.warning("⚠️ Nenhuma empresa vinculada à sua conta.")


# ==============================================================================
# ROTEAMENTO
# ==============================================================================
if st.session_state['logado']:
    pagina_principal()
else:
    pagina_login()
