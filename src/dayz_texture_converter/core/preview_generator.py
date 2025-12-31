#!/usr/bin/env python3
"""
Gerador de previews para texturas
"""

import numpy as np
from PIL import Image
from typing import Dict, Optional, Any, Tuple
from pathlib import Path

class PreviewGenerator:
    """Classe para gerar previews das texturas processadas"""
    
    def __init__(self):
        self.preview_size = 200
    
    def generate_previews(self, textures: Dict[str, str], settings: Dict[str, Any], 
                         preview_size: int = 200) -> Dict[str, Optional[np.ndarray]]:
        """
        Gera previews de todas as texturas
        
        Args:
            textures: Dicionário com caminhos das texturas
            settings: Configurações de processamento
            preview_size: Tamanho do preview em pixels
            
        Returns:
            Dicionário com arrays numpy dos previews
        """
        self.preview_size = preview_size
        previews = {}
        
        try:
            # Preview do Base Color
            if textures.get('base_color'):
                previews['base_color_preview'] = self._generate_base_color_preview(
                    textures['base_color'], settings
                )
            
            # Preview do Normal Map
            if textures.get('normal_map'):
                previews['normal_preview'] = self._generate_normal_preview(
                    textures['normal_map'], settings
                )
            
            # Preview do SMDI
            if textures.get('metalness') and textures.get('roughness'):
                previews['smdi_preview'] = self._generate_smdi_preview(
                    textures['metalness'], textures['roughness'], settings
                )
            
            return previews
            
        except Exception as e:
            print(f"Erro ao gerar previews: {str(e)}")
            return {}
    
    def _load_and_resize_for_preview(self, file_path: str) -> Image.Image:
        """Carrega e redimensiona imagem para preview"""
        img = Image.open(file_path)
        
        # Redimensionar mantendo proporção
        img.thumbnail((self.preview_size, self.preview_size), Image.Resampling.LANCZOS)
        
        # Criar imagem quadrada com fundo transparente/preto
        if img.mode == 'RGBA':
            background = Image.new('RGBA', (self.preview_size, self.preview_size), (0, 0, 0, 0))
        else:
            background = Image.new('RGB', (self.preview_size, self.preview_size), (0, 0, 0))
            if img.mode != 'RGB':
                img = img.convert('RGB')
        
        # Centralizar imagem
        x = (self.preview_size - img.width) // 2
        y = (self.preview_size - img.height) // 2
        
        if img.mode == 'RGBA':
            background.paste(img, (x, y), img)
        else:
            background.paste(img, (x, y))
        
        return background
    
    def _generate_base_color_preview(self, file_path: str, settings: Dict[str, Any]) -> Optional[np.ndarray]:
        """Gera preview do Base Color com ajustes RGB"""
        try:
            img = self._load_and_resize_for_preview(file_path)
            
            # Aplicar ajustes RGB
            if img.mode in ['RGB', 'RGBA']:
                img_array = np.array(img, dtype=np.float32)
                
                rgb_settings = settings.get('base_color_rgb', {'r': 1.0, 'g': 1.0, 'b': 1.0})
                
                # Aplicar multiplicadores RGB
                if len(img_array.shape) == 3:  # RGB ou RGBA
                    img_array[:, :, 0] *= rgb_settings['r']  # Red
                    img_array[:, :, 1] *= rgb_settings['g']  # Green
                    img_array[:, :, 2] *= rgb_settings['b']  # Blue
                
                # Clampar valores
                img_array = np.clip(img_array, 0, 255)
                return img_array.astype(np.uint8)
            
            return np.array(img)
            
        except Exception as e:
            print(f"Erro no preview Base Color: {str(e)}")
            return None
    
    def _generate_normal_preview(self, file_path: str, settings: Dict[str, Any]) -> Optional[np.ndarray]:
        """Gera preview do Normal Map"""
        try:
            img = self._load_and_resize_for_preview(file_path)
            
            # Converter para RGB se necessário
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            img_array = np.array(img)
            
            # Inverter canal verde se necessário
            if settings.get('normal_invert_green', False):
                img_array[:, :, 1] = 255 - img_array[:, :, 1]  # Inverter canal verde
            
            return img_array
            
        except Exception as e:
            print(f"Erro no preview Normal Map: {str(e)}")
            return None
    
    def _generate_smdi_preview(self, metalness_path: str, roughness_path: str, 
                              settings: Dict[str, Any]) -> Optional[np.ndarray]:
        """Gera preview do SMDI combinado"""
        try:
            # Carregar imagens
            metalness_img = self._load_and_resize_for_preview(metalness_path)
            roughness_img = self._load_and_resize_for_preview(roughness_path)
            
            # Converter para grayscale
            if metalness_img.mode != 'L':
                metalness_img = metalness_img.convert('L')
            if roughness_img.mode != 'L':
                roughness_img = roughness_img.convert('L')
            
            # Redimensionar para o mesmo tamanho se necessário
            if metalness_img.size != roughness_img.size:
                target_size = (self.preview_size, self.preview_size)
                metalness_img = metalness_img.resize(target_size, Image.Resampling.LANCZOS)
                roughness_img = roughness_img.resize(target_size, Image.Resampling.LANCZOS)
            
            # Converter para arrays numpy
            metalness_array = np.array(metalness_img, dtype=np.float32)
            roughness_array = np.array(roughness_img, dtype=np.float32)
            
            height, width = metalness_array.shape
            
            # ============================================================
            # METAL FILL - Preenche áreas sem metal com valor base
            # ============================================================
            metal_fill_enabled = settings.get('metal_override_enabled', False)
            metal_fill_value = settings.get('metal_override_value', 0)
            
            if metal_fill_enabled and metal_fill_value > 0:
                metal_base = np.full((height, width), metal_fill_value, dtype=np.float32)
                metalness_array = np.maximum(metalness_array, metal_base)
            
            # ============================================================
            # GLOSS FILL - Preenche áreas sem brilho com valor base
            # ============================================================
            gloss_fill_enabled = settings.get('gloss_override_enabled', False)
            gloss_fill_value = settings.get('gloss_override_value', 0)
            
            # Converter roughness para glossiness
            glossiness_array = 255.0 - roughness_array
            
            if gloss_fill_enabled and gloss_fill_value > 0:
                gloss_base = np.full((height, width), gloss_fill_value, dtype=np.float32)
                glossiness_array = np.maximum(glossiness_array, gloss_base)
            
            # Aplicar opacidade
            metalness_opacity = settings.get('metalness_opacity', 100.0) / 100.0
            roughness_opacity = settings.get('roughness_opacity', 100.0) / 100.0
            
            metalness_array *= metalness_opacity
            glossiness_array *= roughness_opacity
            
            # Criar canais SMDI
            # Canal Red: sempre branco (255)
            red_channel = np.full((height, width), 255, dtype=np.uint8)
            
            # Canal Green: Metalness (com fill aplicado)
            green_channel = np.clip(metalness_array, 0, 255).astype(np.uint8)
            
            # Canal Blue: Glossiness (com fill aplicado)
            blue_channel = np.clip(glossiness_array, 0, 255).astype(np.uint8)
            
            # Combinar canais RGB para visualização
            smdi_array = np.stack([red_channel, green_channel, blue_channel], axis=2)
            
            return smdi_array
            
        except Exception as e:
            print(f"Erro no preview SMDI: {str(e)}")
            return None
    
    def generate_channel_visualization(self, texture_path: str, channel: str = 'rgb') -> Optional[np.ndarray]:
        """
        Gera visualização de canais específicos
        
        Args:
            texture_path: Caminho da textura
            channel: 'r', 'g', 'b', 'a', ou 'rgb'
            
        Returns:
            Array numpy da visualização
        """
        try:
            img = self._load_and_resize_for_preview(texture_path)
            
            if img.mode not in ['RGB', 'RGBA']:
                img = img.convert('RGB')
            
            img_array = np.array(img)
            
            if channel == 'r':
                # Mostrar apenas canal vermelho
                result = np.zeros_like(img_array)
                result[:, :, 0] = img_array[:, :, 0]
                return result
            elif channel == 'g':
                # Mostrar apenas canal verde
                result = np.zeros_like(img_array)
                result[:, :, 1] = img_array[:, :, 1]
                return result
            elif channel == 'b':
                # Mostrar apenas canal azul
                result = np.zeros_like(img_array)
                result[:, :, 2] = img_array[:, :, 2]
                return result
            elif channel == 'a' and img.mode == 'RGBA':
                # Mostrar canal alpha como grayscale
                alpha = img_array[:, :, 3]
                return np.stack([alpha, alpha, alpha], axis=2)
            else:
                # Mostrar RGB normal
                return img_array[:, :, :3]
                
        except Exception as e:
            print(f"Erro na visualização de canal: {str(e)}")
            return None
    
    def create_comparison_preview(self, original_path: str, processed_array: np.ndarray) -> Optional[np.ndarray]:
        """
        Cria preview de comparação lado a lado
        
        Args:
            original_path: Caminho da textura original
            processed_array: Array da textura processada
            
        Returns:
            Array numpy com comparação lado a lado
        """
        try:
            # Carregar original
            original_img = self._load_and_resize_for_preview(original_path)
            original_array = np.array(original_img)
            
            # Garantir que ambas tenham o mesmo número de canais
            if len(original_array.shape) == 3 and len(processed_array.shape) == 3:
                if original_array.shape[2] != processed_array.shape[2]:
                    if original_array.shape[2] == 4 and processed_array.shape[2] == 3:
                        # Adicionar canal alpha ao processado
                        alpha = np.full((processed_array.shape[0], processed_array.shape[1], 1), 255, dtype=np.uint8)
                        processed_array = np.concatenate([processed_array, alpha], axis=2)
                    elif original_array.shape[2] == 3 and processed_array.shape[2] == 4:
                        # Remover canal alpha do processado
                        processed_array = processed_array[:, :, :3]
            
            # Redimensionar se necessário
            if original_array.shape[:2] != processed_array.shape[:2]:
                from PIL import Image
                processed_img = Image.fromarray(processed_array)
                processed_img = processed_img.resize(original_array.shape[1::-1], Image.Resampling.LANCZOS)
                processed_array = np.array(processed_img)
            
            # Criar comparação lado a lado
            comparison = np.concatenate([original_array, processed_array], axis=1)
            
            return comparison
            
        except Exception as e:
            print(f"Erro na comparação: {str(e)}")
            return None