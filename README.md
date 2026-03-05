# 🤖 WhatsApp Bot — Plataforma SaaS

Plataforma de automação WhatsApp multi-empresa usando Evolution API.

## 🚀 Funcionalidades

- **Bot Multi-Loja**: Um servidor atende várias empresas
- **Respostas Automáticas**: Menu interativo por WhatsApp
- **Painel Web (Streamlit)**: Gerencie empresas, menus e configurações
- **Dashboard**: Métricas e status em tempo real

## 📋 Requisitos

- **Python 3.10+**
- **Docker** (para Evolution API + PostgreSQL)

## ⚡ Instalação

### 1. Instalar dependências
```bash
pip install -r requirements.txt
```

### 2. Subir a Evolution API
```bash
docker compose up -d
```

### 3. Conectar o WhatsApp
```bash
python whatsapp.py
```
Escaneie o QR Code ou use o Pairing Code.

### 4. Configurar o Webhook
```bash
python configurar_webhook.py
```

### 5. Abrir o Painel Web
```bash
streamlit run dashboard.py
```

## 🔐 Acesso ao Painel

| Tipo    | Email           | Senha    |
|---------|-----------------|----------|
| Admin   | admin@saas.com  | admin123 |

## 🏗️ Estrutura

```
├── whatsapp.py           # Bot principal (webhook)
├── database.py           # Banco de dados SQLite
├── dashboard.py          # Painel Streamlit
├── pages/                # Páginas do painel
│   ├── 1_📊_Painel.py
│   ├── 2_🏢_Empresas.py
│   └── 3_⚙️_Config.py
├── docker-compose.yml    # Evolution API + PostgreSQL
└── configurar_webhook.py # Configuração do webhook
```

## 📝 Licença

Uso pessoal / educacional.
