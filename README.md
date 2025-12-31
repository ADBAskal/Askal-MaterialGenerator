# ASKAL TOOLS - Gerador de Material para DayZ

![ASKAL TOOLS](https://i.ibb.co/pjrT3fnb/Askal-Horiz.png)

Uma ferramenta moderna e intuitiva para converter texturas PBR em materiais compatíveis com DayZ, desenvolvida especialmente para a comunidade de modding.

### Language adaptations soon!

## 💬 Comunidade & Suporte

[![Discord](https://img.shields.io/badge/Discord-7289DA?style=for-the-badge&logo=discord&logoColor=white)](https://discord.com/invite/3xqWvuqKTg)
[![Ko-Fi](https://img.shields.io/badge/Ko--fi-F16061?style=for-the-badge&logo=ko-fi&logoColor=white)](https://ko-fi.com/askaltools)

Junte-se à nossa comunidade no Discord para suporte, discussões e atualizações! Se este projeto te ajudou, considere apoiar o desenvolvimento através do Ko-Fi.

## 🎯 Características

- **Interface Moderna**: Design dark theme com preview em tempo real
- **Conversão Automática**: Processa texturas PBR para formato DayZ
- **Preview Integrado**: Visualização instantânea das texturas processadas
- **Suporte PAA**: Conversão automática para .paa (requer DayZ Tools)
- **Geração RVMAT**: Criação automática de arquivos de material
- **Presets de Material**: Templates para diferentes tipos de superfície

## 🚀 Instalação

### Opção 1: Executável (Recomendado)
1. Baixe o executável da seção [Releases](../../releases)
2. Execute `ASKAL_TOOLS_Gerador_Material.exe`
3. Pronto para usar!

### Opção 2: Código Fonte
```bash
git clone https://github.com/seu-usuario/askal-tools-gerador-material.git
cd askal-tools-gerador-material
pip install -r requirements.txt
python run_converter.py
```

## 📋 Requisitos

- **Windows 7 ou superior**
- **DayZ Tools** (opcional, para conversão .paa)
- **Python 3.8+** (apenas para execução do código fonte)

## 🎮 Como Usar

1. **Carregue as Texturas**:
   - Base Color (Diffuse/Albedo)
   - Normal Map
   - Metalness
   - Roughness

2. **Ajuste as Configurações**:
   - RGB da Base Color
   - Opacidade das texturas
   - Metal Fill e Gloss Fill
   - Preset de material

3. **Configure a Saída**:
   - Pasta de destino
   - Resolução final
   - Conversão para .paa
   - Geração de RVMAT

4. **Converta**:
   - Clique em "CONVERTER TEXTURAS"
   - Aguarde o processamento
   - Arquivos prontos na pasta de destino!

## 📁 Arquivos Gerados

| Arquivo | Descrição |
|---------|-----------|
| `nome_co.png/paa` | Base Color processado |
| `nome_nohq.png/paa` | Normal Map convertido |
| `nome_smdi.png/paa` | SMDI (Surface Material Definition) |
| `nome.rvmat` | Arquivo de material (opcional) |

## 🔧 Recursos Avançados

### Metal Fill & Gloss Fill
Preenche áreas sem cobertura de metal ou brilho com valores base, garantindo que toda a superfície tenha propriedades definidas.

### Presets de Material
Templates pré-configurados com valores de Fresnel corretos para diferentes materiais:
- Metal
- Madeira
- Plástico
- Vidro
- Tecido
- E mais...

### Conversão de Normal Maps
Converte automaticamente normal maps do Unity (DirectX) para DayZ (OpenGL) invertendo o canal verde.

## 🛠️ Desenvolvimento

### Estrutura do Projeto
```
src/
├── dayz_texture_converter/
│   ├── core/           # Processamento de texturas
│   ├── gui/            # Interface gráfica
│   └── utils/          # Utilitários e presets
media/                  # Assets (logo, etc.)
run_converter.py        # Ponto de entrada
build_exe.py           # Script de compilação
```

### Compilar Executável
```bash
python build_exe.py
```

## 📝 Changelog

### v2.0 - ASKAL TOOLS
- ✨ Nova identidade visual ASKAL
- 🎨 Interface completamente redesenhada
- 🔄 Preview em tempo real
- 📋 Sistema de presets de material
- 🔧 Metal Fill e Gloss Fill
- 📄 Geração automática de RVMAT
- 🎮 Conversão automática para PAA

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor:

1. Faça um fork do projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🎮 Para a Comunidade DayZ

Desenvolvido com ❤️ para a comunidade de modding do DayZ. 

**ASKAL TOOLS** - Facilitando a criação de conteúdo para DayZ desde 2024.

---

### 📞 Suporte

- **Issues**: [GitHub Issues](../../issues)
- **Discord**: [Comunidade ASKAL](https://discord.com/invite/3xqWvuqKTg)
- **Email**: contato@askal.tools

### 🙏 Agradecimentos

- Bohemia Interactive pela documentação oficial
- Comunidade DayZ de modding
- Contribuidores do projeto
