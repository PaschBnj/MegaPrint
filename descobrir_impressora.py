import win32print

def testar_todas_impressoras():
    # 1. Lista todas as impressoras instaladas
    impressoras = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL | win32print.PRINTER_ENUM_CONNECTIONS)
    
    print("--- INICIANDO TESTE ---")
    
    for i in impressoras:
        nome_impressora = i[2]
        
        # Só testa se tiver "POS-80C" no nome
        if "POS-80C" in nome_impressora:
            print(f"Tentando imprimir em: {nome_impressora}...")
            
            try:
                hPrinter = win32print.OpenPrinter(nome_impressora)
                try:
                    hJob = win32print.StartDocPrinter(hPrinter, 1, ("Teste Identificacao", None, "RAW"))
                    win32print.StartPagePrinter(hPrinter)
                    
                    # O TEXTO QUE VAI SAIR NO PAPEL
                    texto = f"\n\n================\nEU SOU A:\n{nome_impressora}\n================\n\n\n\x1d\x56\x00"
                    
                    win32print.WritePrinter(hPrinter, texto.encode("cp850"))
                    win32print.EndPagePrinter(hPrinter)
                    win32print.EndDocPrinter(hPrinter)
                    print(f"  -> Comando enviado com sucesso para {nome_impressora}!")
                except:
                    print(f"  -> Falha ao enviar dados para {nome_impressora}")
                finally:
                    win32print.ClosePrinter(hPrinter)
            except:
                print(f"  -> Não foi possível abrir a impressora {nome_impressora}")

    print("--- FIM DO TESTE ---")
    print("Olhe para o papel impresso e veja qual nome apareceu!")

if __name__ == '__main__':
    testar_todas_impressoras()