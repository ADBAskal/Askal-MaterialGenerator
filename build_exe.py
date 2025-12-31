#!/usr/bin/env python3
"""
Script para gerar executável do ASKAL TOOLS - Gerador de Material
"""

import sys
import os
import shutil
from pathlib import Path
import subprocess

def build_executable():
    """Gera executável usando PyInstaller"""
    
    print("🔨 Construindo executável do ASKAL TOOLS - Gerador de Material...")
    
    # Verificar se PyInstaller está instalado
    try:
        import PyInstaller
        print("✅ PyInstaller encontrado")
    except ImportError:
        print("❌ PyInstaller não encontrado. Instalando...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Usar arquivo .spec personalizado
    spec_file = "askal_tools.spec"
    
    if not Path(spec_file).exists():
        print(f"❌ Arquivo {spec_file} não encontrado!")
        return False
    
    # Comando PyInstaller com .spec
    cmd = ["pyinstaller", "--clean", spec_file]
    
    try:
        print(f"🚀 Executando: {' '.join(cmd)}")
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        
        print("✅ Build concluído com sucesso!")
        
        # Verificar se o executável foi criado
        exe_path = Path("dist") / "ASKAL_TOOLS_Gerador_Material.exe"
        if exe_path.exists():
            print(f"📦 Executável criado: {exe_path}")
            print(f"📏 Tamanho: {exe_path.stat().st_size / (1024*1024):.1f} MB")
        else:
            print("❌ Executável não encontrado em dist/")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Erro no build: {e}")
        print(f"Saída: {e.stdout}")
        print(f"Erro: {e.stderr}")
        return False

def clean_build():
    """Limpa arquivos de build anteriores"""
    print("🧹 Limpando arquivos de build anteriores...")
    
    dirs_to_clean = ["build", "dist", "__pycache__"]
    files_to_clean = ["*.spec"]
    
    for dir_name in dirs_to_clean:
        if Path(dir_name).exists():
            shutil.rmtree(dir_name)
            print(f"🗑️ Removido: {dir_name}/")
    
    # Remover apenas .spec gerados automaticamente, não o nosso personalizado
    for spec_file in Path(".").glob("*.spec"):
        if spec_file.name != "askal_tools.spec":  # Preservar nosso .spec personalizado
            spec_file.unlink()
            print(f"🗑️ Removido: {spec_file}")

def create_portable_package():
    """Cria pacote portável com executável e documentação"""
    print("📦 Criando pacote portável...")
    
    package_dir = Path("ASKAL_TOOLS_Portable")
    
    # Remover pasta existente se houver
    if package_dir.exists():
        try:
            shutil.rmtree(package_dir)
            print("🗑️ Pasta anterior removida")
        except PermissionError:
            print("⚠️ Não foi possível remover pasta existente (arquivo em uso)")
            return None
    
    package_dir.mkdir()
    
    # Copiar executável
    exe_source = Path("dist") / "ASKAL_TOOLS_Gerador_Material.exe"
    if exe_source.exists():
        try:
            shutil.copy2(exe_source, package_dir / "ASKAL_TOOLS_Gerador_Material.exe")
            print("✅ Executável copiado")
            
            # Remover pasta dist após copiar (opcional)
            try:
                shutil.rmtree("dist")
                print("🗑️ Pasta dist removida (executável já copiado para pacote)")
            except Exception as e:
                print(f"⚠️ Não foi possível remover pasta dist: {e}")
                
        except PermissionError:
            print("⚠️ Não foi possível copiar executável (arquivo em uso)")
            return None
    else:
        print("❌ Executável não encontrado!")
        return None
    
    # Copiar ícone
    icon_source = Path("media") / "askal_logo.ico"
    if icon_source.exists():
        shutil.copy2(icon_source, package_dir / "askal_logo.ico")
        print("✅ Ícone copiado")
    
    # Copiar documentação essencial
    docs_to_copy = ["README.md", "LICENSE"]
    for doc in docs_to_copy:
        if Path(doc).exists():
            shutil.copy2(doc, package_dir / doc)
            print(f"✅ {doc} copiado")
    
    # Criar arquivo de instruções otimizado
    instructions = """# 🎮 ASKAL TOOLS - Gerador de Material para DayZ

## 🚀 Início Rápido
1. Execute `ASKAL_TOOLS_Gerador_Material.exe`
2. Arraste suas texturas ou clique para selecionar:
   - Base Color (Diffuse/Albedo)
   - Normal Map
   - Metalness 
   - Roughness
3. Ajuste configurações se necessário
4. Clique em "🚀 CONVERTER TEXTURAS"

## 📤 Saída Gerada
- `nome_co.png` - Base Color processado
- `nome_nohq.png` - Normal Map convertido  
- `nome_smdi.png` - SMDI (Surface Material Definition)
- `nome.rvmat` - Material definition (opcional)

## ⚙️ Recursos
✅ Preview em tempo real das texturas
✅ Conversão automática para .paa (se DayZ Tools instalado)
✅ Presets de materiais (Metal, Madeira, Plástico, etc.)
✅ Metal Fill e Gloss Fill para áreas sem cobertura
✅ Interface moderna e intuitiva
✅ Suporte a drag & drop

## 📋 Formatos Suportados
**Entrada:** PNG, JPG, JPEG, TGA, BMP
**Saída:** PNG, PAA (com DayZ Tools)
**Resoluções:** 512x512 até 4096x4096

## 🔧 Requisitos
- Windows 7 ou superior
- DayZ Tools (opcional, para conversão .paa)

## 🎯 Dicas
- Use texturas com mesma resolução para melhor resultado
- Normal Maps do Unity: ative "Inverter Canal Verde"
- Para materiais metálicos: use preset "Metal" 
- Para madeira: use preset "Madeira"

---
**Desenvolvido por ASKAL para a comunidade de modding do DayZ** 🎮
Versão Portable - Não requer instalação
"""
    
    with open(package_dir / "LEIA-ME.txt", "w", encoding="utf-8") as f:
        f.write(instructions)
    
    print(f"✅ Pacote portável criado: {package_dir}")
    
    # Mostrar estatísticas
    total_size = sum(f.stat().st_size for f in package_dir.rglob('*') if f.is_file())
    print(f"📏 Tamanho total: {total_size / (1024*1024):.1f} MB")
    
    return package_dir

def main():
    """Função principal"""
    print("🎮 ASKAL TOOLS - Build Portable\n")
    
    # Limpar build anterior
    clean_build()
    
    # Construir executável
    if build_executable():
        print("\n" + "="*50)
        print("✅ BUILD CONCLUÍDO COM SUCESSO!")
        print("="*50)
        
        # Criar pacote portável
        package_dir = create_portable_package()
        
        if package_dir:
            print(f"\n🎯 PACOTE PORTÁVEL PRONTO!")
            print(f"📁 Pasta: {package_dir}")
            print(f"🚀 Execute: {package_dir}/ASKAL_TOOLS_Gerador_Material.exe")
            print(f"\n💡 Para distribuir: Comprima a pasta '{package_dir}'")
            print(f"\n📝 Nota: A pasta 'dist/' foi removida (executável já copiado para o pacote)")
        else:
            print(f"\n⚠️ Erro ao criar pacote portável")
            print(f"📁 Executável disponível em: dist/ASKAL_TOOLS_Gerador_Material.exe")
        
    else:
        print("\n" + "="*50)
        print("❌ BUILD FALHOU!")
        print("="*50)
        print("Verifique os erros acima e tente novamente.")

if __name__ == "__main__":
    main()
    input("\nPressione Enter para sair...")