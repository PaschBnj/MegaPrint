from flask import Flask, request, jsonify
import win32print
import json

app = Flask(__name__)

# --- FUNÇÃO DE IMPRESSÃO (Sua parte original) ---
def imprimir_cupom(texto_para_imprimir):
    nome_impressora = "ESCRITORIO" 
    
    try:
        hPrinter = win32print.OpenPrinter(nome_impressora)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Cupom Bot", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)
            
            # --- COMANDOS DE FORMATAÇÃO (ESC/POS) ---
            CMD_CENTRALIZAR = b'\x1b\x61\x01'
            CMD_ESQUERDA    = b'\x1b\x61\x00'
            CMD_NEGRITO_ON  = b'\x1b\x45\x01'
            CMD_NEGRITO_OFF = b'\x1b\x45\x00'
            CMD_CORTE       = b'\x1d\x56\x00'
            
            # --- CONSTRUINDO O CUPOM ---
            
            # 1. Cabeçalho Centralizado e em Negrito
            win32print.WritePrinter(hPrinter, CMD_CENTRALIZAR + CMD_NEGRITO_ON)
            win32print.WritePrinter(hPrinter, "--- PEDIDO NOVO ---\n\n".encode("cp850"))
            win32print.WritePrinter(hPrinter, CMD_NEGRITO_OFF + CMD_ESQUERDA) # Volta ao normal
            
            # 2. O Texto do Pedido (Garante que é string)
            texto_str = str(texto_para_imprimir)
            
            # DICA: Substitui quebras de linha do JSON (\n) por quebras reais
            texto_final = texto_str.replace("\\n", "\n")
            
            win32print.WritePrinter(hPrinter, texto_final.encode("cp850", errors="ignore"))
            
            # 3. Rodapé com espaço extra para sair da máquina
            win32print.WritePrinter(hPrinter, b"\n\n\n-------------------\n")
            win32print.WritePrinter(hPrinter, b"    Fim do Pedido    \n\n\n\n\n") 
            
            # 4. Cortar
            win32print.WritePrinter(hPrinter, CMD_CORTE)
            
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
            print(" >> CUPOM IMPRESSO COM SUCESSO")
            
        finally:
            win32print.ClosePrinter(hPrinter)
    except Exception as e:
        print(f"ERRO: {e}")
# --- SERVIDOR WEBHOOK (A parte que faltava) ---
@app.route('/webhook', methods=['POST'])
def webhook():
    print("Recebi um chamado!")
    
    # Pega os dados brutos
    dados = request.json
    
    # --- A MÁGICA ACONTECE AQUI ---
    # Se o JSON for { "cupom": "Pedido de Pizza" }, ele pega só "Pedido de Pizza"
    # Se não achar 'cupom', tenta achar 'message', ou usa um padrão.
    texto_limpo = dados.get('cupom') or dados.get('message') or "Sem texto no pedido"
    
    # Se o texto for uma lista de itens (ex: arrays), transforma em string bonita
    if isinstance(texto_limpo, list):
        texto_limpo = "\n".join(str(x) for x in texto_limpo)
    
    # Manda imprimir só o recheio, sem a casca do JSON
    imprimir_cupom(texto_limpo)
    
    return jsonify({"status": "sucesso"})

# --- INICIAR O PROGRAMA ---
if __name__ == '__main__':
    # Isso mantém o programa rodando infinitamente esperando mensagens
    print("O Robô de Impressão está ONLINE e aguardando pedidos...")
    app.run(port=5000)