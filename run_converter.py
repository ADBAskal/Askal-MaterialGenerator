#!/usr/bin/env python3
"""
ASKAL TOOLS - Gerador de Material para DayZ
Execute este arquivo para abrir a interface gráfica
"""

import sys
import os
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

def main():
    """Função principal"""
    try:
        print("🎮 Iniciando ASKAL TOOLS - Gerador de Material...")
        
        # Verificar se é executável PyInstaller
        is_executable = hasattr(sys, '_MEIPASS')
        if is_executable:
            print("📦 Executando como executável PyInstaller")
        else:
            print("🐍 Executando como script Python")
        
        # Verificar dependências críticas
        missing_deps = []
        
        try:
            import customtkinter
            print("✅ customtkinter OK")
        except ImportError:
            missing_deps.append("customtkinter")
            
        try:
            import tkinterdnd2
            print("✅ tkinterdnd2 OK")
        except ImportError:
            missing_deps.append("tkinterdnd2")
            
        try:
            from PIL import Image, ImageTk, ImageDraw
            print("✅ PIL OK")
        except ImportError as e:
            missing_deps.append(f"PIL ({e})")
            
        try:
            import numpy as np
            print("✅ numpy OK")
        except ImportError:
            missing_deps.append("numpy")
        
        if missing_deps:
            print(f"❌ Dependências faltando: {', '.join(missing_deps)}")
            print("📦 Instale as dependências com: pip install -r requirements.txt")
            if is_executable:
                print("⚠️ Se você está usando o executável, recompile com: python build_exe.py")
            input("Pressione Enter para sair...")
            return
        
        # Importar e executar a aplicação
        print("📥 Importando módulos da aplicação...")
        from dayz_texture_converter.gui.main_window import MainWindow
        
        print("✅ Dependências OK, criando interface...")
        app = MainWindow()
        
        print("🚀 Iniciando loop principal da aplicação...")
        app.run()
        
    except ImportError as e:
        print(f"❌ Erro de importação: {e}")
        print("📦 Verifique se todas as dependências estão instaladas")
        import traceback
        traceback.print_exc()
        
        if not hasattr(sys, '_MEIPASS'):
            input("Pressione Enter para sair...")
        else:
            print("Aplicação será fechada em 10 segundos...")
            import time
            time.sleep(10)
            
    except Exception as e:
        print(f"❌ Erro ao iniciar aplicação: {e}")
        import traceback
        traceback.print_exc()
        
        # Não pedir input se for executável para evitar "lost sys.stdin"
        if not hasattr(sys, '_MEIPASS'):
            input("Pressione Enter para sair...")
        else:
            print("Aplicação será fechada em 10 segundos...")
            import time
            time.sleep(10)

if __name__ == "__main__":
    main()