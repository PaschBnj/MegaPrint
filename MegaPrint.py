import requests
import time
import win32print
import sys

# ================= CONFIGURAÇÕES =================
# Coloque aqui o link que o Render (ou PythonAnywhere) te deu.
# NÃO coloque a barra "/" no final.
URL_SERVIDOR = "https://api-impressora.onrender.com" 

# Nome exato da impressora no Windows
NOME_IMPRESSORA = "ESCRITORIO"
# =================================================

def imprimir_cupom(conteudo):
    """
    Função responsável por enviar os bytes brutos para a impressora
    """
    try:
        hPrinter = win32print.OpenPrinter(NOME_IMPRESSORA)
        try:
            hJob = win32print.StartDocPrinter(hPrinter, 1, ("Cupom Bot", None, "RAW"))
            win32print.StartPagePrinter(hPrinter)
            
            # --- Comandos ESC/POS (Linguagem da Impressora) ---
            CMD_INIT        = b'\x1b\x40'       # Iniciar
            CMD_CENTRALIZAR = b'\x1b\x61\x01'   # Centralizar
            CMD_ESQUERDA    = b'\x1b\x61\x00'   # Alinhar Esquerda
            CMD_NEGRITO_ON  = b'\x1b\x45\x01'   # Negrito Ligar
            CMD_NEGRITO_OFF = b'\x1b\x45\x00'   # Negrito Desligar
            CMD_CORTE       = b'\x1d\x56\x00'   # Cortar Papel
            
            # --- Montagem do Cupom ---
            win32print.WritePrinter(hPrinter, CMD_INIT)
            
            # Cabeçalho
            win32print.WritePrinter(hPrinter, CMD_CENTRALIZAR + CMD_NEGRITO_ON)
            win32print.WritePrinter(hPrinter, "=== NOVO PEDIDO ===\n\n".encode("cp850"))
            win32print.WritePrinter(hPrinter, CMD_NEGRITO_OFF + CMD_ESQUERDA)
            
            # Corpo do Texto
            # Tratamento para garantir que quebras de linha funcionem
            texto_formatado = str(conteudo).replace("\\n", "\n")
            win32print.WritePrinter(hPrinter, texto_formatado.encode("cp850", errors="ignore"))
            
            # Rodapé (Espaço para sair da máquina)
            win32print.WritePrinter(hPrinter, b"\n\n-------------------\n")
            win32print.WritePrinter(hPrinter, CMD_CENTRALIZAR)
            win32print.WritePrinter(hPrinter, b"BotConversa Imprime\n\n\n\n\n")
            
            # Cortar
            win32print.WritePrinter(hPrinter, CMD_CORTE)
            
            win32print.EndPagePrinter(hPrinter)
            win32print.EndDocPrinter(hPrinter)
            print(f" >> [SUCESSO] Impressão realizada!")
            
        finally:
            win32print.ClosePrinter(hPrinter)
    except Exception as e:
        print(f" >> [ERRO IMPRESSORA] Verifique se ela está ligada ou se o nome está certo.\nErro: {e}")

def iniciar_monitoramento():
    print("="*50)
    print(f" ROBÔ DE IMPRESSÃO INICIADO")
    print(f" Conectando em: {URL_SERVIDOR}")
    print(f" Impressora alvo: {NOME_IMPRESSORA}")
    print("="*50)
    print("Aguardando pedidos... (pressione Ctrl+C para parar)")

    endpoint = f"{URL_SERVIDOR}/buscar_pedido"

    while True:
        try:
            # Faz a requisição para a nuvem
            response = requests.get(endpoint, timeout=10)
            
            if response.status_code == 200:
                dados = response.json()
                
                # Verifica se veio um pedido de verdade (não vazio)
                # O servidor manda {} se não tiver nada
                if dados and "texto" in dados:
                    print(f"\n[NOVO PEDIDO RECEBIDO] Processando...")
                    imprimir_cupom(["texto"])
                else:
                    # Não tem pedido, apenas ignora
                    pass
            else:
                print(f"[ALERTA] Servidor respondeu com código {response.status_code}")

        except requests.exceptions.ConnectionError:
            print("[ERRO REDE] Sem internet ou servidor fora do ar. Tentando em 5s...", end="\r")
        except Exception as e:
            print(f"[ERRO DESCONHECIDO] {e}")

        # Espera 5 segundos antes de perguntar de novo
        time.sleep(1)

if __name__ == "__main__":
    iniciar_monitoramento()

