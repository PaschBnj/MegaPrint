from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# --- MEMÓRIA TEMPORÁRIA (RAM) ---
# AVISO: Se o Render reiniciar o servidor (o que acontece de vez em quando),
# essa lista é zerada. Para produção profissional, usaríamos um Banco de Dados.
pedidos_fila = []

@app.route('/')
def index():
    """Rota apenas para verificar se o site está no ar"""
    return f"Servidor de Impressão Online! Fila atual: {len(pedidos_fila)} pedidos."

# =================================================================
# ROTA 1: QUEM MANDA É O BOTCONVERSA (Webhook)
# =================================================================
@app.route('/webhook', methods=['POST'])
def receber_webhook():
    try:
        dados = request.json
        print(f"Recebido: {dados}") # Aparece no log do Render
        
        # Tenta pegar o texto de várias formas possíveis
        # O BotConversa pode mandar como 'cupom', 'message', 'text', etc.
        texto_pedido = dados.get('cupom') or dados.get('message') or dados.get('text')
        
        if not texto_pedido:
            texto_pedido = "Pedido sem texto (Verificar JSON)"

        # Se for uma lista (vários itens), transforma em texto corrido
        if isinstance(texto_pedido, list):
            texto_pedido = "\n".join(str(x) for x in texto_pedido)

        # Adiciona na fila para o seu PC buscar
        pedidos_fila.append({
            "texto": str(texto_pedido)
        })
        
        return jsonify({"status": "sucesso", "mensagem": "Pedido guardado na fila"}), 200

    except Exception as e:
        return jsonify({"status": "erro", "detalhes": str(e)}), 500

# =================================================================
# ROTA 2: QUEM MANDA É O SEU COMPUTADOR (Polling)
# =================================================================
@app.route('/buscar_pedido', methods=['GET'])
def entregar_para_pc():
    # Verifica se tem algo na fila
    if pedidos_fila:
        # Pega o primeiro da fila (o mais antigo) e REMOVE da lista
        pedido = pedidos_fila.pop(0)
        return jsonify(pedido) # Retorna: {"texto": "Conteúdo do pedido..."}
    else:
        # Se não tiver nada, retorna dicionário vazio
        return jsonify({})

# Necessário para rodar localmente (teste), mas no Render o Gunicorn ignora isso
if __name__ == '__main__':
    # Pega a porta do ambiente ou usa 5000
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
