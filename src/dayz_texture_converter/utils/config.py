#!/usr/bin/env python3
"""
Configurações e constantes da aplicação
"""

from pathlib import Path
from typing import Dict, List, Tuple

class Config:
    """Classe de configuração da aplicação"""
    
    # Informações da aplicação
    APP_NAME = "DayZ Texture Converter"
    APP_VERSION = "1.0.0"
    APP_AUTHOR = "DayZ Modder"
    
    # Configurações da interface
    WINDOW_SIZE = (1200, 800)
    MIN_WINDOW_SIZE = (1000, 700)
    THEME = "dark"
    COLOR_THEME = "blue"
    
    # Formatos suportados
    SUPPORTED_IMAGE_FORMATS = ['.png', '.jpg', '.jpeg', '.tga', '.bmp']
    SUPPORTED_EXTENSIONS = ['*.png', '*.jpg', '*.jpeg', '*.tga', '*.bmp']
    
    # Configurações de processamento
    DEFAULT_RESOLUTION = 1024
    AVAILABLE_RESOLUTIONS = [512, 1024, 2048, 4096]
    PREVIEW_SIZE = 200
    
    # Configurações padrão de texturas
    DEFAULT_SETTINGS = {
        'base_color_rgb': {'r': 1.0, 'g': 1.0, 'b': 1.0},
        'normal_invert_green': False,
        'metalness_opacity': 100.0,
        'roughness_opacity': 100.0,
        'output_resolution': DEFAULT_RESOLUTION,
        'convert_to_paa': False,
        'remove_png_after_paa': True,
        'output_directory': ''
    }
    
    # Sufixos de arquivo DayZ
    DAYZ_SUFFIXES = {
        'base_color': '_co',
        'normal_map': '_nohq',
        'smdi': '_smdi'
    }
    
    # Sufixos comuns de entrada
    INPUT_SUFFIXES = {
        'base_color': ['_BaseColor', '_base_color', '_diffuse', '_albedo', '_co'],
        'normal_map': ['_Normal', '_normal', '_nohq', '_n'],
        'metalness': ['_Metallic', '_metallic', '_metalness', '_m'],
        'roughness': ['_Roughness', '_roughness', '_r']
    }
    
    # Filtros de arquivo para diálogos
    FILE_FILTERS = [
        ("Imagens", " ".join(SUPPORTED_EXTENSIONS)),
        ("PNG", "*.png"),
        ("JPEG", "*.jpg *.jpeg"),
        ("TGA", "*.tga"),
        ("BMP", "*.bmp"),
        ("Todos os arquivos", "*.*")
    ]
    
    # Configurações de SMDI
    SMDI_CONFIG = {
        'red_channel': 255,    # Sempre branco
        'green_channel': 'metalness',
        'blue_channel': 'glossiness',  # Roughness invertido
        'alpha_channel': 255   # Sempre branco
    }
    
    # Mensagens da interface
    MESSAGES = {
        'drag_drop_placeholder': "Arraste um arquivo ou clique em 'Procurar'",
        'conversion_success': "Texturas convertidas com sucesso!",
        'conversion_error': "Erro na conversão",
        'missing_textures': "Por favor, carregue as seguintes texturas:",
        'invalid_image': "Erro ao carregar imagem",
        'preview_error': "Erro ao gerar preview"
    }
    
    # Tooltips e descrições
    TOOLTIPS = {
        'base_color': "Textura de cor base (Diffuse/Albedo)",
        'normal_map': "Mapa de normais (pode precisar inverter canal verde)",
        'metalness': "Mapa de metalicidade (canal verde do SMDI)",
        'roughness': "Mapa de rugosidade (canal azul do SMDI, será invertido)",
        'invert_green': "Marque para converter de Unity para DayZ/Unreal",
        'realtime_preview': "Atualiza preview automaticamente ao fazer alterações",
        'rgb_sliders': "Ajusta multiplicadores RGB (0.0 = preto, 1.0 = normal, 2.0 = dobro)",
        'opacity_sliders': "Controla a intensidade do canal (0% = transparente, 100% = opaco)"
    }
    
    @classmethod
    def get_resolution_options(cls) -> List[str]:
        """Retorna opções de resolução formatadas"""
        return [f"{res}x{res}" for res in cls.AVAILABLE_RESOLUTIONS]
    
    @classmethod
    def parse_resolution(cls, resolution_str: str) -> int:
        """Converte string de resolução para inteiro"""
        return int(resolution_str.split('x')[0])
    
    @classmethod
    def get_output_filename(cls, base_name: str, texture_type: str) -> str:
        """Gera nome de arquivo de saída"""
        suffix = cls.DAYZ_SUFFIXES.get(texture_type, '')
        return f"{base_name}{suffix}.png"
    
    @classmethod
    def detect_texture_type(cls, filename: str) -> str:
        """Detecta tipo de textura baseado no nome do arquivo"""
        filename_lower = filename.lower()
        
        for texture_type, suffixes in cls.INPUT_SUFFIXES.items():
            for suffix in suffixes:
                if suffix.lower() in filename_lower:
                    return texture_type
        
        return 'unknown'
    
    @classmethod
    def clean_base_name(cls, filename: str) -> str:
        """Remove sufixos comuns do nome do arquivo"""
        name = Path(filename).stem
        
        # Testar todos os sufixos conhecidos
        all_suffixes = []
        for suffixes in cls.INPUT_SUFFIXES.values():
            all_suffixes.extend(suffixes)
        
        for suffix in all_suffixes:
            if name.lower().endswith(suffix.lower()):
                name = name[:-len(suffix)]
                break
        
        return name