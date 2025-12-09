from flask import Flask, request, jsonify
import os

app = Flask(__name__)
pedidos_fila = []

@app.route('/')
def index():
    return "Servidor de Impressão (Formatador de Cupom) Online!"

@app.route('/webhook', methods=['POST'])
def receber_webhook():
    try:
        dados = request.json
        print(f"--- DEBUG RAW: {dados} ---", flush=True) # Pra gente ver no log se precisar

        # 1. Pega o dado bruto (pode vir como lista ou texto)
        conteudo = dados.get('cupom') or dados.get('message') or "Sem dados"

        # 2. SE FOR LISTA (O problema do ['texto']), PEGA SÓ O TEXTO
        if isinstance(conteudo, list):
            # Pega o primeiro item da lista e garante que é string
            if len(conteudo) > 0:
                texto_base = str(conteudo[0])
            else:
                texto_base = "Lista Vazia"
        else:
            texto_base = str(conteudo)

        # 3. FORMATAÇÃO VISUAL (A Faxina)
        # Vamos desgrudar o nome do telefone e dar destaque aos campos
        
        texto_formatado = texto_base
        
        # Garante quebras de linha reais
        texto_formatado = texto_formatado.replace("\\n", "\n") 
        
        # Desgruda "NomeTelefone" -> "Nome\nTelefone"
        texto_formatado = texto_formatado.replace("Telefone:", "\nTelefone:")
        
        # Pula linha nos campos principais para ficar fácil de ler
        texto_formatado = texto_formatado.replace("Endereço:", "\nEndereço:")
        
        # Adiciona uma linha separadora antes do Pedido
        texto_formatado = texto_formatado.replace("Pedido (lanches", "\n--------------------------------\nPedido (lanches")
        
        texto_formatado = texto_formatado.replace("Valor total:", "\n\nValor total:")
        texto_formatado = texto_formatado.replace("Forma de pagamento:", "\nForma de pagamento:")
        texto_formatado = texto_formatado.replace("Observações", "\n--------------------------------\nObservações")

        # 4. Coloca na fila para o seu PC buscar
        pedidos_fila.append({"texto": texto_formatado})
        
        return jsonify({"status": "sucesso", "msg": "Cupom formatado"}), 200

    except Exception as e:
        print(f"ERRO NO SERVIDOR: {e}")
        return jsonify({"status": "erro", "detalhes": str(e)}), 500

@app.route('/buscar_pedido', methods=['GET'])
def entregar_para_pc():
    if pedidos_fila:
        return jsonify(pedidos_fila.pop(0))
    return jsonify({})
