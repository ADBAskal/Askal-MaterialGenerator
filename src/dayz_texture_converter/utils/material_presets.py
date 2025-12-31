#!/usr/bin/env python3
"""
Presets de materiais para diferentes tipos de superfície
Baseado na documentação oficial da Bohemia Interactive:
- https://community.bistudio.com/wiki/Super_shader
- https://community.bistudio.com/wiki/Texture_Map_Types

Canais SMDI (conforme documentação):
- R (Red): Sempre 255 (1.0) para todos os pixels
- G (Green): Specular Map (intensidade da reflexão)
- B (Blue): Gloss/Specular Power (preto=fosco, branco=brilhante)

Valores de Fresnel (N, K) da tabela oficial:
- N = índice de refração
- K = coeficiente de absorção
"""

from typing import Dict, Any, Tuple

class MaterialPresets:
    """Classe com presets de materiais para DayZ baseados na documentação oficial"""
    
    # Valores de Fresnel (N, K) da documentação oficial Bohemia Interactive
    FRESNEL_VALUES = {
        'aluminum': (1.3, 7),
        'cobalt': (0.2, 3),
        'copper': (2.08, 7.15),
        'gold': (0.3, 3),
        'iron': (3.12, 3.87),
        'lead': (1.44, 4.35),
        'molybdenum': (2.77, 3.74),
        'nickel': (2.59, 4.55),
        'palladium': (2.17, 5.22),
        'platinum': (2.92, 5.07),
        'silver': (0.2, 3),
        'titanium': (3.21, 4.01),
        'vanadium': (2.94, 3.50),
        'tungsten': (3.48, 2.79),
        # Valores empíricos para não-metais
        'plastic': (1.5, 0.01),
        'glass': (1.5, 0.0),
        'rubber': (1.52, 0.01),
        'fabric': (1.4, 0.01),
        'wood': (1.55, 0.01),
        'skin': (1.4, 0.01),
        'concrete': (1.5, 0.02),
        'default': (1, 1.05)  # Padrão DayZ
    }
    
    PRESETS = {
        'custom': {
            'name': 'Personalizado',
            'description': 'Configurações manuais',
            'metalness_opacity': 100.0,
            'roughness_opacity': 100.0,
            'opacity_value': 255,
            'base_color_rgb': {'r': 1.0, 'g': 1.0, 'b': 1.0},
            'fresnel_material': 'default'
        },
        
        'metal_polished': {
            'name': 'Metal Polido',
            'description': 'Metal brilhante (alumínio, aço inoxidável)',
            'metalness_opacity': 90.0,  # Muito metálico
            'roughness_opacity': 20.0,  # Muito liso
            'opacity_value': 255,
            'base_color_rgb': {'r': 0.9, 'g': 0.9, 'b': 0.9},
            'fresnel_material': 'aluminum'
        },
        
        'metal_worn': {
            'name': 'Metal Desgastado',
            'description': 'Metal oxidado ou desgastado (níquel)',
            'metalness_opacity': 70.0,  # Parcialmente metálico
            'roughness_opacity': 60.0,  # Rugosidade média
            'opacity_value': 255,
            'base_color_rgb': {'r': 0.8, 'g': 0.7, 'b': 0.6},
            'fresnel_material': 'nickel'
        },
        
        'gold': {
            'name': 'Ouro',
            'description': 'Metal dourado',
            'metalness_opacity': 95.0,
            'roughness_opacity': 15.0,
            'opacity_value': 255,
            'base_color_rgb': {'r': 1.0, 'g': 0.84, 'b': 0.0},
            'fresnel_material': 'gold'
        },
        
        'silver': {
            'name': 'Prata',
            'description': 'Metal prateado',
            'metalness_opacity': 95.0,
            'roughness_opacity': 15.0,
            'opacity_value': 255,
            'base_color_rgb': {'r': 0.97, 'g': 0.96, 'b': 0.91},
            'fresnel_material': 'silver'
        },
        
        'copper': {
            'name': 'Cobre',
            'description': 'Metal acobreado',
            'metalness_opacity': 90.0,
            'roughness_opacity': 25.0,
            'opacity_value': 255,
            'base_color_rgb': {'r': 0.95, 'g': 0.64, 'b': 0.54},
            'fresnel_material': 'copper'
        },
        
        'plastic_glossy': {
            'name': 'Plástico Brilhante',
            'description': 'Plástico novo e brilhante',
            'metalness_opacity': 5.0,   # Não metálico
            'roughness_opacity': 25.0,  # Bem liso
            'opacity_value': 255,
            'base_color_rgb': {'r': 1.0, 'g': 1.0, 'b': 1.0},
            'fresnel_material': 'plastic'
        },
        
        'plastic_matte': {
            'name': 'Plástico Fosco',
            'description': 'Plástico com acabamento fosco',
            'metalness_opacity': 0.0,   # Não metálico
            'roughness_opacity': 70.0,  # Rugoso
            'opacity_value': 255,
            'base_color_rgb': {'r': 1.0, 'g': 1.0, 'b': 1.0},
            'fresnel_material': 'plastic'
        },
        
        'fabric': {
            'name': 'Tecido',
            'description': 'Materiais têxteis como algodão',
            'metalness_opacity': 0.0,   # Não metálico
            'roughness_opacity': 85.0,  # Muito rugoso
            'opacity_value': 255,
            'base_color_rgb': {'r': 1.0, 'g': 1.0, 'b': 1.0},
            'fresnel_material': 'fabric'
        },
        
        'leather': {
            'name': 'Couro',
            'description': 'Couro natural ou sintético',
            'metalness_opacity': 0.0,   # Não metálico
            'roughness_opacity': 65.0,  # Rugosidade média-alta
            'opacity_value': 255,
            'base_color_rgb': {'r': 0.9, 'g': 0.8, 'b': 0.7},
            'fresnel_material': 'skin'
        },
        
        'rubber': {
            'name': 'Borracha',
            'description': 'Materiais de borracha',
            'metalness_opacity': 0.0,   # Não metálico
            'roughness_opacity': 75.0,  # Rugoso
            'opacity_value': 255,
            'base_color_rgb': {'r': 0.2, 'g': 0.2, 'b': 0.2},
            'fresnel_material': 'rubber'
        },
        
        'wood': {
            'name': 'Madeira',
            'description': 'Madeira natural',
            'metalness_opacity': 0.0,   # Não metálico
            'roughness_opacity': 70.0,  # Rugosidade média-alta
            'opacity_value': 255,
            'base_color_rgb': {'r': 0.8, 'g': 0.6, 'b': 0.4},
            'fresnel_material': 'wood'
        },
        
        'concrete': {
            'name': 'Concreto',
            'description': 'Superfícies de concreto',
            'metalness_opacity': 0.0,   # Não metálico
            'roughness_opacity': 80.0,  # Muito rugoso
            'opacity_value': 255,
            'base_color_rgb': {'r': 0.7, 'g': 0.7, 'b': 0.7},
            'fresnel_material': 'concrete'
        },
        
        'glass': {
            'name': 'Vidro',
            'description': 'Superfícies de vidro',
            'metalness_opacity': 0.0,   # Não metálico
            'roughness_opacity': 10.0,  # Muito liso
            'opacity_value': 200,   # Parcialmente transparente
            'base_color_rgb': {'r': 0.95, 'g': 0.98, 'b': 1.0},
            'fresnel_material': 'glass'
        }
    }
    
    @classmethod
    def get_fresnel_values(cls, material: str) -> Tuple[float, float]:
        """Retorna valores de Fresnel (N, K) para um material"""
        return cls.FRESNEL_VALUES.get(material, cls.FRESNEL_VALUES['default'])
    
    @classmethod
    def get_preset_names(cls) -> list:
        """Retorna lista de nomes dos presets"""
        return [preset['name'] for preset in cls.PRESETS.values()]
    
    @classmethod
    def get_preset_by_name(cls, name: str) -> Dict[str, Any]:
        """Retorna preset pelo nome"""
        for key, preset in cls.PRESETS.items():
            if preset['name'] == name:
                return preset.copy()
        return cls.PRESETS['custom'].copy()
    
    @classmethod
    def get_preset_by_key(cls, key: str) -> Dict[str, Any]:
        """Retorna preset pela chave"""
        return cls.PRESETS.get(key, cls.PRESETS['custom']).copy()
    
    @classmethod
    def get_preset_key_by_name(cls, name: str) -> str:
        """Retorna chave do preset pelo nome"""
        for key, preset in cls.PRESETS.items():
            if preset['name'] == name:
                return key
        return 'custom'
    
    @classmethod
    def apply_preset_to_settings(cls, settings: Dict[str, Any], preset_key: str) -> Dict[str, Any]:
        """Aplica preset às configurações"""
        preset = cls.get_preset_by_key(preset_key)
        
        # Aplicar configurações do preset
        settings['metalness_opacity'] = preset['metalness_opacity']
        settings['roughness_opacity'] = preset['roughness_opacity']
        settings['opacity_value'] = preset['opacity_value']
        settings['base_color_rgb'] = preset['base_color_rgb'].copy()
        settings['material_preset'] = preset_key
        
        # Adicionar valores de Fresnel
        fresnel_material = preset.get('fresnel_material', 'default')
        settings['fresnel_n'], settings['fresnel_k'] = cls.get_fresnel_values(fresnel_material)
        
        return settings
    
    @classmethod
    def get_preset_description(cls, preset_key: str) -> str:
        """Retorna descrição do preset"""
        preset = cls.get_preset_by_key(preset_key)
        return preset.get('description', 'Sem descrição')
    
    @classmethod
    def get_all_fresnel_materials(cls) -> list:
        """Retorna lista de todos os materiais com valores de Fresnel"""
        return list(cls.FRESNEL_VALUES.keys())