"""
================================================================================
TUTORIAL - PASSO 3: FAZER O SEU CÉREBRO (PYTHON) OUVIR A EVOLUTION
================================================================================

🎉 Parabéns! O seu Robô já tem um WhatsApp conectado (A loja PizzariaMario).
Se você mandar mensagem para esse número agora, a Evolution API vai receber,
mas ela não sabe o que responder. Ela precisa enviar essa mensagem para o seu "Cérebro"
(nosso arquivo em Python).

Como a Evolution e o Python estão no MESMO computador agora, eles podem conversar.

1. DESLIGUE O GERADOR DE QR CODE
   Role lá no final do arquivo onde diz: `criar_instancia_e_gerar_qrcode("PizzariaMario")`
   E coloque um "#" no começo da linha para desativar ela. (A instância já está criada!)

2. INICIE O SERVIDOR CÉREBRO
   Volte no seu terminal e rode o arquivo de novo:
   `python whatsapp.py`
   Ele vai dizer que o Flask está rodando na porta 5000 (http://127.0.0.1:5000).
   DEIXE ESSA TELA PRETA ABERTA. O seu cérebro está ligado e ouvindo!

3. CONECTE A EVOLUTION AO CÉREBRO (O WEBHOOK)
   Precisamos avisar a Evolution: "Quando chegar mensagem, mande para localhost:5000/webhook".
   Para fazer isso fácil, criei um script temporário pra você rodar.
   
   ABRA UM SEGUNDO TERMINAL (deixe o do Python rodando).
   Nesse NOVO terminal, rode o comando:
   python configurar_webhook.py

AVISE-ME ASSIM QUE COMPLETAR ESSE PASSO. No passo 4 finalmente você mandará uma mensagem "Oi" para o seu bot e ele vai responder o cardápio!
================================================================================
"""

import time
import random
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# ==========================================================
# CONFIGURAÇÃO DA EVOLUTION API (O MOTOR)
# ==========================================================
# Essa é a URL onde a Evolution API vai rodar (vamos configurar em casa)
EVOLUTION_API_URL = "http://localhost:8080" 
# Uma senha global que você vai criar para o seu servidor Evolution
EVOLUTION_GLOBAL_API_KEY = "sua_senha_secreta_global" 

# ==========================================================
# NOSSO BANCO DE DADOS DE EMPRESAS 
# ==========================================================
# Na Evolution API, cada cliente é separado por uma "Instância" (nome).
EMPRESAS = {
    "PizzariaMario": { # Nome da Instância do Cliente A
        "nome": "Pizzaria do Mario",
        "menu": "Olá! Bem-vindo à Pizzaria do Mario 🍕\n1 - Fazer Pedido\n2 - Falar com Atendente"
    },
    "ClinicaVida": { # Nome da Instância do Cliente B
        "nome": "Clínica Vida Saudável",
        "menu": "Olá! Clínica Vida Saudável agradece o contato 🏥\n1 - Marcar Consulta\n2 - Resultados de Exames"
    }
}

# ==========================================================
# FUNÇÃO PARA ENVIAR MENSAGENS PELA EVOLUTION API
# ==========================================================
def enviar_mensagem(instancia, numero_destino, texto):
    # A URL diz para qual instância (loja) a Evolution deve usar para enviar a mensagem
    url = f"{EVOLUTION_API_URL}/message/sendText/{instancia}"
    
    headers = {
        "apikey": EVOLUTION_GLOBAL_API_KEY, # A mesma senha configurada no servidor
        "Content-Type": "application/json"
    }
    
    data = {
        "number": numero_destino, # Numero ou JID completo (ex: 5511999999999 ou 12345@lid)
        "options": {
            "delay": 3000, # Atraso de 3s para parecer humano
            "presence": "composing" # Faz aparecer "Digitando..." no WhatsApp do cliente
        },
        "textMessage": {
            "text": texto # O menu ou resposta
        }
    }
    
    print(f"[{instancia}] Tentando enviar para: {numero_destino}")
    print(f"[{instancia}] URL: {url}")
    print(f"[{instancia}] Payload: {data}")
    
    # Faz o pedido (POST) para a Evolution disparar a mensagem
    try:
        response = requests.post(url, headers=headers, json=data)
        print(f"[{instancia}] Status da resposta: {response.status_code}")
        print(f"[{instancia}] Resposta da Evolution: {response.text[:500]}")
        return response
    except Exception as e:
        print(f"[{instancia}] ERRO ao enviar mensagem: {e}")
        return None

# ==========================================================
# WEBHOOK: ROTA PARA RECEBER AS MENSAGENS DA EVOLUTION
# ==========================================================
@app.route('/teste', methods=['GET'])
def teste():
    print("[TESTE] Alguem acessou a rota /teste!")
    return "Cerebro funcionando!", 200

@app.route('/webhook', methods=['POST'])
def receber_mensagens():
    print("\n" + "="*60)
    print("[WEBHOOK] Recebi uma requisicao no webhook!")
    print("="*60)
    body = request.get_json(force=True, silent=True)
    
    # Salvar TODOS os payloads em um log para debug
    import json, os
    from datetime import datetime
    caminho_log = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'payloads_log.txt')
    caminho_ultimo = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ultimo_payload.json')
    try:
        with open(caminho_ultimo, 'w', encoding='utf-8') as f:
            json.dump(body, f, ensure_ascii=False, indent=4)
        with open(caminho_log, 'a', encoding='utf-8') as f:
            f.write(f"\n{'='*60}\n")
            f.write(f"[{datetime.now().strftime('%H:%M:%S')}]\n")
            json.dump(body, f, ensure_ascii=False, indent=4)
            f.write("\n")
        print(f"[WEBHOOK] Payload salvo em log")
    except Exception as e:
        print(f"[WEBHOOK] ERRO ao salvar payload: {e}")
    
    if not body:
        print("[WEBHOOK] ERRO: Body vazio ou invalido!")
        return jsonify({"status": "erro", "motivo": "body vazio"}), 400
    
    # Mostra o evento recebido para debug
    evento = body.get('event', 'NENHUM')
    print(f"[WEBHOOK] Evento recebido: {evento}")
        
    # A Evolution manda varios "eventos". So queremos quando uma mensagem chegar.
    # Aceita tanto 'messages.upsert' (v1) quanto 'MESSAGES_UPSERT' (v2)
    evento_lower = evento.lower() if isinstance(evento, str) else ''
    if evento_lower in ('messages.upsert', 'messages_upsert'):
        
        # ---------------------------------------------------------------
        # EXTRAIR O NOME DA INSTÂNCIA (compatível com v1 e v2 da Evolution)
        # ---------------------------------------------------------------
        # A Evolution pode enviar 'instance' como string OU como objeto:
        #   v1: "instance": "PizzariaMario"
        #   v2: "instance": {"instanceName": "PizzariaMario", ...}
        instancia_raw = body.get('instance')
        if isinstance(instancia_raw, dict):
            instancia = instancia_raw.get('instanceName', instancia_raw.get('instance', ''))
        elif isinstance(instancia_raw, str):
            instancia = instancia_raw
        else:
            instancia = str(instancia_raw) if instancia_raw else ''
        
        print(f"[WEBHOOK] Instancia detectada: '{instancia}' (tipo original: {type(instancia_raw).__name__})")
        
        # ---------------------------------------------------------------
        # EXTRAIR DADOS DA MENSAGEM (compatível com diferentes estruturas)
        # ---------------------------------------------------------------
        dados = body.get('data', body)  # Fallback: dados podem estar direto no body
        
        # 'key' pode estar em data ou direto no body
        key_info = dados.get('key', {})
        mensagem_info = dados.get('message', {})
        
        # Ignora mensagens se foi enviada pela própria loja (fromMe: true)
        if key_info.get('fromMe'):
            print("[WEBHOOK] Ignorado: mensagem enviada pelo proprio bot (fromMe=true)")
            return jsonify({"status": "ignorado (mensagem do próprio bot)"}), 200
            
        # Pega do pacote de dados: O número/ID do cliente final
        # A Evolution pode usar formato @lid (Line ID) ou @s.whatsapp.net
        # Em AMBOS os casos, o remoteJid identifica quem mandou a mensagem
        # O campo 'sender' é o número do PROPRIO BOT, NAO usar!
        remote_jid = key_info.get('remoteJid', '')
        
        # IMPORTANTE: Para LID, manter o JID completo (ex: 150177843298351@lid)
        # A Evolution API precisa do JID completo para enviar corretamente
        # Se for @s.whatsapp.net, extrair só o número
        if '@lid' in remote_jid:
            remetente = remote_jid  # Manter completo: 150177843298351@lid
            print(f"[WEBHOOK] Formato LID detectado. Usando JID completo: {remetente}")
        else:
            remetente = remote_jid.split('@')[0]  # Extrair só o número
            print(f"[WEBHOOK] Formato normal. Numero: {remetente}")
        
        # Pega do pacote de dados: O texto que o cliente escreveu
        texto_recebido = ""
        if 'conversation' in mensagem_info:
            texto_recebido = mensagem_info['conversation']
        elif 'extendedTextMessage' in mensagem_info:
            texto_recebido = mensagem_info['extendedTextMessage'].get('text', '')
        
        # Fallback: tentar pegar de 'body' (campo usado em algumas versões)
        if not texto_recebido and 'body' in dados:
            texto_recebido = dados['body']
        # Outro fallback: pushName + messageType (para extrair texto de tipos variados)
        if not texto_recebido and 'messageType' in dados:
            print(f"[WEBHOOK] Tipo de mensagem nao-texto recebido: {dados.get('messageType')}")
        
        texto_recebido = texto_recebido.lower().strip() if texto_recebido else ""
            
        print(f"=====================================")
        print(f"Nova mensagem na LOJA: {instancia}")
        print(f"Cliente ({remetente}) disse: '{texto_recebido}'")
        print(f"=====================================")
        
        # --------------------------------------------------
        # LÓGICA MULTI-LOJAS (O mesmo servidor responde pra todo mundo)
        # --------------------------------------------------
        if instancia in EMPRESAS:
            empresa = EMPRESAS[instancia]
            
            if "oi" in texto_recebido or "olá" in texto_recebido or "ola" in texto_recebido:
                resposta = empresa["menu"]
            elif "1" in texto_recebido:
                resposta = f"Você escolheu a opção 1 da {empresa['nome']}."
            elif "2" in texto_recebido:
                resposta = f"Você escolheu a opção 2 da {empresa['nome']}."
            else:
                resposta = "Desculpe, não entendi. Digite 'Oi' para ver o menu."
            
            # Espera 4-5 segundos antes de responder (parecer mais humano)
            delay = random.uniform(4, 5)
            print(f"[WEBHOOK] Aguardando {delay:.1f}s antes de responder...")
            time.sleep(delay)
            
            print(f"[WEBHOOK] Enviando resposta: '{resposta[:50]}...'")
            enviar_mensagem(instancia, remetente, resposta)
            
        else:
            print(f"[WEBHOOK] ERRO: Instancia '{instancia}' NAO encontrada no dicionario EMPRESAS!")
            print(f"[WEBHOOK] Instancias disponiveis: {list(EMPRESAS.keys())}")
            
    else:
        print(f"[WEBHOOK] Evento '{evento}' ignorado (nao e mensagem)")
            
    return jsonify({"status": "ok"}), 200

# ==========================================================
# FUNÇÕES PARA GERAR A INSTÂNCIA (PASSO 2)
# ==========================================================
def criar_instancia_e_gerar_qrcode(nome_instancia):
    """
    1. Cria a instância (celular virtual) na Evolution
    2. Pede pra Evolution gerar o QRCode pra lermos
    """
    print(f"\n[SISTEMA] Iniciando processo para a loja: {nome_instancia}")
    
    # URL da API local
    url_criar = f"{EVOLUTION_API_URL}/instance/create"
    url_conectar = f"{EVOLUTION_API_URL}/instance/connect/{nome_instancia}"
    
    headers = {
        "apikey": EVOLUTION_GLOBAL_API_KEY,
        "Content-Type": "application/json"
    }

    # =======================================================
    # PASSO A: Tenta criar a Instância
    # =======================================================
    payload_criar = {
        "instanceName": nome_instancia,
        "token": f"token_{nome_instancia}", # Senha individual dessa loja (opcional, mas bom ter)
        "qrcode": True # Pede pra já devolver o QRCode
    }
    
    try:
        print("[SISTEMA] Tentando criar/acessar a instância no Motor...")
        resposta_criar = requests.post(url_criar, headers=headers, json=payload_criar)
        dados_criar = resposta_criar.json()
        
        # A Evolution v1.8 retorna um erro 403 The instance "PizzariaMario" is already in use
        # Se isso acontecer, significa que ela já existe. Então a gente ignora o erro e segue em frente
        if resposta_criar.status_code != 201 and "already in use" not in str(dados_criar):
             print(f"[ERRO] Falha ao criar instância: {dados_criar}")
             return
            
    except Exception as e:
        print(f"[ERRO DE CONEXÃO] O Motor Evolution está ligado no Docker? Erro: {e}")
        return

    # =======================================================
    # PASSO B: Pede o QRCode
    # =======================================================
    print("[SISTEMA] Aguardando a geração do QR Code...")
    time.sleep(2) # Espera 2 segundinhos pro motor respirar
    
    resposta_conectar = requests.get(url_conectar, headers=headers)
    dados_conectar = resposta_conectar.json()
    
    if "base64" in dados_conectar:
        # Pega a imagem do QRCode (vem num formato de texto longo chamado Base64)
        qrcode_base64 = dados_conectar["base64"]
        
        print("\n" + "="*50)
        print("[SUCESSO] QR CODE GERADO COM SUCESSO! [SUCESSO]")
        print("="*50)
        print("\nPara ler este QR Code (já que estamos no terminal escuro):")
        print("1. Copie todo esse texto gigantesco abaixo:")
        print(f"\n{qrcode_base64}\n")
        print("2. Abra seu navegador e acesse o site: https://base64.guru/converter/decode/image")
        print("3. Cole o texto gigante lá e clique em 'Decode Base64 to Image'")
        print("4. O QR Code real vai aparecer na sua tela! Leia com o WhatsApp do celular.")
        print("="*50 + "\n")
    else:
        # Se não vier Base64, pode ser que o celular JÁ ESTEJA conectado
        if dados_conectar.get("instance", {}).get("state") == "open":
            print(f"\n[SUCESSO] A loja {nome_instancia} já está conectada ao WhatsApp perfeitamente!")
        else:
            print(f"\n[SISTEMA] Resposta inesperada ao pedir QRCode: {dados_conectar}")


if __name__ == '__main__':
    print("Iniciando o cérebro do robô...")
    
    # ---- PASSO 2 (AÇÃO) ----
    # COMO VOCÊ JÁ LEU O QR CODE, COLOQUE UM # NA LINHA ABAIXO PARA DESATIVAR
    criar_instancia_e_gerar_qrcode("PizzariaMario")
    
    # ------------------------
    
    # Mantem o servidor vivo para ouvir futuras mensagens (Passo 3/4)
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
