import requests
import json
import time

EVOLUTION_API_URL = "http://localhost:8080" 
EVOLUTION_GLOBAL_API_KEY = "sua_senha_secreta_global" 
NOME_INSTANCIA = "PizzariaMario"
WEBHOOK_URL = "http://host.docker.internal:5000/webhook" # Usando host.docker.internal pois a Evolution tá no Docker e o Cérebro no Windows

def configurar_webhook():
    print("="*50)
    print("CONFIGURANDO O WEBHOOK (A CONEXÃO ENTRE OUVIDO E CÉREBRO)")
    print("="*50)
    
    url = f"{EVOLUTION_API_URL}/webhook/set/{NOME_INSTANCIA}"
    
    headers = {
        "apikey": EVOLUTION_GLOBAL_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "url": WEBHOOK_URL,
        "webhook_by_events": False,
        "webhook_base64": False,
        "webhook_events": [
            "MESSAGES_UPSERT"
        ],
        "events": [
            "MESSAGES_UPSERT"
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        
        if response.status_code in [200, 201]:
            print(f"[SUCESSO] A Evolution agora vai mandar as mensagens da {NOME_INSTANCIA} para o seu Cérebro Python.")
            print(f"URL Configurda: {WEBHOOK_URL}")
        else:
            print(f"[ERRO] ERRO AO CONFIGURAR WEBHOOK.")
            print(f"Código: {response.status_code}")
            print(f"Detalhes: {response.text}")
            
    except Exception as e:
        print(f"[ERRO] ERRO DE CONEXÃO: {e}")
        print("A Evolution API está ligada?")

if __name__ == "__main__":
    configurar_webhook()
    print("\nPode fechar essa tela. Não esqueça de deixar o 'whatsapp.py' rodando na outra!")
    time.sleep(10)
