#!/usr/bin/env python3
"""
Processador principal de texturas para DayZ
"""

import numpy as np
from PIL import Image
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import os
import subprocess
import shutil

class TextureProcessor:
    """Classe principal para processamento de texturas do DayZ"""
    
    def __init__(self):
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.tga', '.bmp']
        # Caminho padrão do ImageToPAA (DayZ Tools)
        self.imagetopaa_path = self._find_imagetopaa_path()
    
    def _find_imagetopaa_path(self) -> Optional[str]:
        """Encontra o caminho do ImageToPAA.exe"""
        possible_paths = [
            r"C:\Program Files (x86)\Steam\steamapps\common\DayZ Tools\Bin\ImageToPAA\ImageToPAA.exe",
            r"C:\Program Files\Steam\steamapps\common\DayZ Tools\Bin\ImageToPAA\ImageToPAA.exe",
            r"D:\Steam\steamapps\common\DayZ Tools\Bin\ImageToPAA\ImageToPAA.exe",
            r"E:\Steam\steamapps\common\DayZ Tools\Bin\ImageToPAA\ImageToPAA.exe"
        ]
        
        for path in possible_paths:
            if Path(path).exists():
                return path
        
        return None
    
    def set_imagetopaa_path(self, path: str):
        """Define manualmente o caminho do ImageToPAA"""
        if Path(path).exists():
            self.imagetopaa_path = path
            return True
        return False
    
    def process_textures(self, textures: Dict[str, str], settings: Dict[str, Any]) -> List[str]:
        """
        Processa todas as texturas e gera os arquivos finais para DayZ
        
        Args:
            textures: Dicionário com caminhos das texturas
            settings: Configurações de processamento
            
        Returns:
            Lista com caminhos dos arquivos gerados
        """
        output_files = []
        
        try:
            # Determinar pasta de saída
            output_dir = Path(settings.get('output_directory', ''))
            if not output_dir or not output_dir.exists():
                # Usar pasta da primeira textura como fallback
                first_texture_path = next(iter(textures.values()))
                output_dir = Path(first_texture_path).parent
            
            # Determinar nome base (remover sufixos comuns)
            base_name = self._get_base_name(next(iter(textures.values())))
            
            # Lista para arquivos PNG temporários (se converter para PAA)
            temp_png_files = []
            
            # Processar Base Color
            if textures.get('base_color'):
                base_color_output = self._process_base_color(
                    textures['base_color'], 
                    settings, 
                    output_dir, 
                    base_name
                )
                if base_color_output:
                    output_files.append(base_color_output)
                    temp_png_files.append(base_color_output)
            
            # Processar Normal Map
            if textures.get('normal_map'):
                normal_output = self._process_normal_map(
                    textures['normal_map'], 
                    settings, 
                    output_dir, 
                    base_name
                )
                if normal_output:
                    output_files.append(normal_output)
                    temp_png_files.append(normal_output)
            
            # Processar SMDI (Metalness + Roughness)
            if textures.get('metalness') and textures.get('roughness'):
                smdi_output = self._process_smdi(
                    textures['metalness'],
                    textures['roughness'],
                    settings,
                    output_dir,
                    base_name
                )
                if smdi_output:
                    output_files.append(smdi_output)
                    temp_png_files.append(smdi_output)
            
            # Converter para PAA se solicitado
            if settings.get('convert_to_paa', False):
                paa_files = self._convert_to_paa(temp_png_files, settings)
                if paa_files:
                    # Substituir arquivos PNG pelos PAA na lista de saída
                    output_files = paa_files
                    
                    # Remover arquivos PNG temporários
                    if settings.get('remove_png_after_paa', True):
                        for png_file in temp_png_files:
                            try:
                                Path(png_file).unlink()
                            except Exception as e:
                                print(f"Aviso: Não foi possível remover {png_file}: {e}")
            
            return output_files
            
        except Exception as e:
            raise Exception(f"Erro no processamento: {str(e)}")
    
    def _convert_to_paa(self, png_files: List[str], settings: Dict[str, Any]) -> List[str]:
        """Converte arquivos PNG para PAA usando ImageToPAA"""
        if not self.imagetopaa_path:
            raise Exception("ImageToPAA.exe não encontrado. Instale o DayZ Tools ou configure o caminho manualmente.")
        
        paa_files = []
        
        for png_file in png_files:
            try:
                png_path = Path(png_file)
                paa_path = png_path.with_suffix('.paa')
                
                # Executar ImageToPAA
                result = subprocess.run(
                    [self.imagetopaa_path, str(png_path), str(paa_path)],
                    capture_output=True,
                    text=True,
                    timeout=30  # Timeout de 30 segundos
                )
                
                if result.returncode == 0 and paa_path.exists():
                    paa_files.append(str(paa_path))
                    print(f"✅ Convertido para PAA: {paa_path.name}")
                else:
                    print(f"❌ Erro ao converter {png_path.name} para PAA:")
                    print(f"   {result.stderr}")
                    # Manter o PNG se a conversão falhar
                    paa_files.append(png_file)
                    
            except subprocess.TimeoutExpired:
                print(f"❌ Timeout ao converter {png_file} para PAA")
                paa_files.append(png_file)
            except Exception as e:
                print(f"❌ Erro ao converter {png_file} para PAA: {e}")
                paa_files.append(png_file)
        
        return paa_files
    
    def _get_base_name(self, file_path: str) -> str:
        """Extrai o nome base removendo sufixos comuns"""
        path = Path(file_path)
        name = path.stem
        
        # Remover sufixos comuns
        suffixes = ['_BaseColor', '_base_color', '_diffuse', '_albedo', '_co',
                   '_Normal', '_normal', '_nohq', '_n',
                   '_Metallic', '_metallic', '_metalness', '_m',
                   '_Roughness', '_roughness', '_r']
        
        for suffix in suffixes:
            if name.lower().endswith(suffix.lower()):
                name = name[:-len(suffix)]
                break
        
        return name
    
    def _load_and_resize_image(self, file_path: str, target_size: Tuple[int, int]) -> Image.Image:
        """Carrega e redimensiona uma imagem"""
        img = Image.open(file_path)
        
        # Converter para RGB se necessário
        if img.mode not in ['RGB', 'RGBA', 'L']:
            img = img.convert('RGB')
        
        # Redimensionar se necessário
        if img.size != target_size:
            img = img.resize(target_size, Image.Resampling.LANCZOS)
        
        return img
    
    def _process_base_color(self, file_path: str, settings: Dict[str, Any], 
                          output_dir: Path, base_name: str) -> Optional[str]:
        """Processa a textura Base Color"""
        try:
            resolution = settings.get('output_resolution', 1024)
            target_size = (resolution, resolution)
            
            # Carregar imagem
            img = self._load_and_resize_image(file_path, target_size)
            
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
                img = Image.fromarray(img_array.astype(np.uint8), mode=img.mode)
            
            # Salvar
            output_path = output_dir / f"{base_name}_co.png"
            img.save(output_path, "PNG")
            
            return str(output_path)
            
        except Exception as e:
            raise Exception(f"Erro ao processar Base Color: {str(e)}")
    
    def _process_normal_map(self, file_path: str, settings: Dict[str, Any], 
                          output_dir: Path, base_name: str) -> Optional[str]:
        """Processa o Normal Map"""
        try:
            resolution = settings.get('output_resolution', 1024)
            target_size = (resolution, resolution)
            
            # Carregar imagem
            img = self._load_and_resize_image(file_path, target_size)
            
            # Converter para RGB se necessário
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Inverter canal verde se necessário
            if settings.get('normal_invert_green', False):
                img_array = np.array(img)
                img_array[:, :, 1] = 255 - img_array[:, :, 1]  # Inverter canal verde
                img = Image.fromarray(img_array)
            
            # Salvar
            output_path = output_dir / f"{base_name}_nohq.png"
            img.save(output_path, "PNG")
            
            return str(output_path)
            
        except Exception as e:
            raise Exception(f"Erro ao processar Normal Map: {str(e)}")
    
    def _process_smdi(self, metalness_path: str, roughness_path: str, 
                     settings: Dict[str, Any], output_dir: Path, base_name: str) -> Optional[str]:
        """Processa e combina Metalness e Roughness em SMDI com sistema avançado"""
        try:
            resolution = settings.get('output_resolution', 1024)
            target_size = (resolution, resolution)
            
            # Carregar imagens
            metalness_img = self._load_and_resize_image(metalness_path, target_size)
            roughness_img = self._load_and_resize_image(roughness_path, target_size)
            
            # Converter para grayscale
            if metalness_img.mode != 'L':
                metalness_img = metalness_img.convert('L')
            if roughness_img.mode != 'L':
                roughness_img = roughness_img.convert('L')
            
            # Converter para arrays numpy
            metalness_array = np.array(metalness_img, dtype=np.float32)
            roughness_array = np.array(roughness_img, dtype=np.float32)
            
            height, width = metalness_array.shape
            
            # ============================================================
            # METAL FILL - Preenche áreas sem metal com um valor base
            # ============================================================
            # Quando a textura de metalness não cobre toda a superfície,
            # isso preenche as áreas "vazias" (pretas/escuras) com metal
            
            metal_fill_enabled = settings.get('metal_override_enabled', False)
            metal_fill_value = settings.get('metal_override_value', 0)  # 0-255
            
            if metal_fill_enabled and metal_fill_value > 0:
                # Criar camada base preenchida com o valor de metal
                metal_base = np.full((height, width), metal_fill_value, dtype=np.float32)
                
                # Combinar: onde a textura original tem valor, usa ela; 
                # onde não tem (ou é baixo), usa o valor base
                # Usa o MÁXIMO entre a base e a textura original
                metalness_array = np.maximum(metalness_array, metal_base)
            
            # ============================================================
            # GLOSS FILL - Preenche áreas sem brilho com um valor base
            # ============================================================
            gloss_fill_enabled = settings.get('gloss_override_enabled', False)
            gloss_fill_value = settings.get('gloss_override_value', 0)  # 0-255
            
            # Primeiro converter roughness para glossiness
            glossiness_array = 255.0 - roughness_array
            
            if gloss_fill_enabled and gloss_fill_value > 0:
                # Criar camada base preenchida com o valor de gloss
                gloss_base = np.full((height, width), gloss_fill_value, dtype=np.float32)
                
                # Combinar: usa o MÁXIMO entre a base e a textura original
                glossiness_array = np.maximum(glossiness_array, gloss_base)
            
            # Aplicar opacidade (após os fills)
            metalness_opacity = settings.get('metalness_opacity', 100.0) / 100.0
            roughness_opacity = settings.get('roughness_opacity', 100.0) / 100.0
            
            metalness_array *= metalness_opacity
            glossiness_array *= roughness_opacity
            
            # Criar canais SMDI conforme documentação oficial Bohemia Interactive
            # R = 1 (sempre 255), G = Specular Map, B = Gloss/Specular Power
            
            # Canal Red: SEMPRE 255 (conforme documentação oficial)
            red_channel = np.full((height, width), 255, dtype=np.uint8)
            
            # Canal Green: Specular Map (baseado em metalness)
            green_channel = np.clip(metalness_array, 0, 255).astype(np.uint8)
            
            # Canal Blue: Gloss/Specular Power
            blue_channel = np.clip(glossiness_array, 0, 255).astype(np.uint8)
            
            # Canal Alpha: Opacity configurável
            alpha_value = settings.get('opacity_value', 255)
            alpha_channel = np.full((height, width), alpha_value, dtype=np.uint8)
            
            # Combinar canais
            smdi_array = np.stack([red_channel, green_channel, blue_channel, alpha_channel], axis=2)
            smdi_img = Image.fromarray(smdi_array, mode='RGBA')
            
            # Salvar SMDI
            output_path = output_dir / f"{base_name}_smdi.png"
            smdi_img.save(output_path, "PNG")
            
            # Gerar RVMAT se solicitado
            if settings.get('generate_rvmat', False):
                self._generate_rvmat_file(base_name, settings, output_dir)
            
            return str(output_path)
            
        except Exception as e:
            raise Exception(f"Erro ao processar SMDI: {str(e)}")
    
    def _generate_rvmat_file(self, base_name: str, settings: Dict[str, Any], output_dir: Path):
        """Gera arquivo RVMAT automaticamente com estrutura correta do DayZ (Super Shader)
        
        Baseado na documentação oficial: https://community.bistudio.com/wiki/Super_shader
        
        Estrutura dos 7 Stages:
        - Stage1: Normal Map (_NOHQ)
        - Stage2: Detail Map (_DT) - textura procedural padrão
        - Stage3: Macro Map (_MC) - textura procedural padrão
        - Stage4: Ambient Shadow (_AS) - textura procedural padrão
        - Stage5: Specular Map (_SMDI)
        - Stage6: Fresnel - função procedural com N e K
        - Stage7: Environment Map - reflexão do ambiente
        """
        try:
            # Configurações do material baseadas no preset
            material_preset = settings.get('material_preset', 'custom')
            
            # Valores de Fresnel (N, K) baseados na documentação oficial
            # N = índice de refração, K = coeficiente de absorção
            fresnel_values = {
                'metal_polished': (1.3, 7),      # Alumínio
                'metal_worn': (2.59, 4.55),      # Níquel
                'plastic_glossy': (1.5, 0.01),   # Plástico
                'fabric': (1.4, 0.01),           # Tecido
                'glass': (1.5, 0.0),             # Vidro
                'rubber': (1.52, 0.01),          # Borracha
                'wood': (1.55, 0.01),            # Madeira
                'skin': (1.4, 0.01),             # Pele
                'gold': (0.3, 3),                # Ouro
                'silver': (0.2, 3),              # Prata
                'copper': (2.08, 7.15),          # Cobre
                'custom': (1, 1.05)              # Padrão DayZ
            }
            
            # Ajustar valores baseado no preset
            if material_preset == 'metal_polished':
                ambient = [0.75, 0.75, 0.75, 1]
                diffuse = [0.75, 0.75, 0.75, 1]
                specular = [0.9, 0.9, 0.9, 1]
                specular_power = 100
            elif material_preset == 'metal_worn':
                ambient = [0.75, 0.75, 0.75, 1]
                diffuse = [0.75, 0.75, 0.75, 1]
                specular = [0.7, 0.7, 0.7, 1]
                specular_power = 80
            elif material_preset == 'plastic_glossy':
                ambient = [0.75, 0.75, 0.75, 1]
                diffuse = [0.75, 0.75, 0.75, 1]
                specular = [0.8, 0.8, 0.8, 1]
                specular_power = 90
            elif material_preset == 'fabric':
                ambient = [0.75, 0.75, 0.75, 1]
                diffuse = [0.75, 0.75, 0.75, 1]
                specular = [0.3, 0.3, 0.3, 1]
                specular_power = 30
            else:
                # Padrão similar ao DayZ (unitra_wilga.rvmat)
                ambient = [0.75, 0.75, 0.75, 1]
                diffuse = [0.75, 0.75, 0.75, 1]
                specular = [0.9, 0.9, 0.9, 1]
                specular_power = 100
            
            # Obter valores de Fresnel
            fresnel_n, fresnel_k = fresnel_values.get(material_preset, (1, 1.05))
            
            # Calcular caminho relativo das texturas
            texture_path = self._calculate_relative_texture_path(output_dir, base_name)
            
            # Conteúdo do RVMAT com estrutura correta (7 Stages como no DayZ)
            rvmat_content = f"""ambient[] = {{{ambient[0]},{ambient[1]},{ambient[2]},{ambient[3]}}};
diffuse[] = {{{diffuse[0]},{diffuse[1]},{diffuse[2]},{diffuse[3]}}};
forcedDiffuse[] = {{0,0,0,0}};
emmisive[] = {{0,0,0,1}};
specular[] = {{{specular[0]},{specular[1]},{specular[2]},{specular[3]}}};
specularPower = {specular_power};
PixelShaderID = "Super";
VertexShaderID = "Super";

class Stage1
{{
    texture = "{texture_path}_nohq.paa";
    uvSource = "tex";
    class uvTransform
    {{
        aside[] = {{1,0,0}};
        up[] = {{0,1,0}};
        dir[] = {{0,0,0}};
        pos[] = {{0,0,0}};
    }};
}};

class Stage2
{{
    texture = "#(argb,8,8,3)color(0.5,0.5,0.5,1,DT)";
    uvSource = "tex";
    class uvTransform
    {{
        aside[] = {{1,0,0}};
        up[] = {{0,1,0}};
        dir[] = {{0,0,0}};
        pos[] = {{0,0,0}};
    }};
}};

class Stage3
{{
    texture = "#(argb,8,8,3)color(0,0,0,0,MC)";
    uvSource = "tex";
    class uvTransform
    {{
        aside[] = {{1,0,0}};
        up[] = {{0,1,0}};
        dir[] = {{0,0,0}};
        pos[] = {{0,0,0}};
    }};
}};

class Stage4
{{
    texture = "#(argb,8,8,3)color(1,1,1,1,AS)";
    uvSource = "tex";
    class uvTransform
    {{
        aside[] = {{1,0,0}};
        up[] = {{0,1,0}};
        dir[] = {{0,0,0}};
        pos[] = {{0,0,0}};
    }};
}};

class Stage5
{{
    texture = "{texture_path}_smdi.paa";
    uvSource = "tex";
    class uvTransform
    {{
        aside[] = {{1,0,0}};
        up[] = {{0,1,0}};
        dir[] = {{0,0,0}};
        pos[] = {{0,0,0}};
    }};
}};

class Stage6
{{
    texture = "#(ai,64,64,1)fresnel({fresnel_n},{fresnel_k})";
    uvSource = "tex";
    class uvTransform
    {{
        aside[] = {{1,0,0}};
        up[] = {{0,1,0}};
        dir[] = {{0,0,0}};
        pos[] = {{0,0,0}};
    }};
}};

class Stage7
{{
    texture = "dz\\data\\data\\env_land_co.paa";
    uvSource = "tex";
    class uvTransform
    {{
        aside[] = {{1,0,0}};
        up[] = {{0,1,0}};
        dir[] = {{0,0,0}};
        pos[] = {{0,0,0}};
    }};
}};
"""
            
            # Salvar arquivo RVMAT
            rvmat_path = output_dir / f"{base_name}.rvmat"
            with open(rvmat_path, 'w', encoding='utf-8') as f:
                f.write(rvmat_content)
            
            print(f"✅ Arquivo RVMAT gerado: {rvmat_path.name}")
            print(f"   Estrutura: 7 Stages (Super Shader completo)")
            print(f"   Material: {material_preset}")
            print(f"   Caminho das texturas: {texture_path}_*.paa")
            
        except Exception as e:
            print(f"⚠️ Erro ao gerar RVMAT: {str(e)}")
    
    def _calculate_relative_texture_path(self, output_dir: Path, base_name: str) -> str:
        """Calcula caminho relativo das texturas para o RVMAT"""
        try:
            # Converter para string e normalizar
            output_path = str(output_dir).replace('\\', '/')
            
            # Remover letra da unidade se presente (ex: P:/ -> /)
            if len(output_path) >= 2 and output_path[1] == ':':
                output_path = output_path[2:]  # Remove "P:"
            
            # Remover barra inicial se presente
            if output_path.startswith('/'):
                output_path = output_path[1:]
            
            # Tratar caminhos relativos (começam com ./ ou ../)
            if output_path.startswith('./') or output_path.startswith('../'):
                # Para caminhos relativos, usar apenas o nome base
                return base_name
            
            # Construir caminho final
            if output_path:
                texture_path = f"{output_path}/{base_name}".replace('/', '\\')
            else:
                texture_path = base_name
            
            return texture_path
            
        except Exception as e:
            print(f"⚠️ Erro ao calcular caminho: {str(e)}")
            # Fallback para apenas o nome base
            return base_name
    
    def validate_texture_file(self, file_path: str) -> bool:
        """Valida se um arquivo é uma textura suportada"""
        try:
            path = Path(file_path)
            
            # Verificar extensão
            if path.suffix.lower() not in self.supported_formats:
                return False
            
            # Tentar abrir como imagem
            with Image.open(file_path) as img:
                img.verify()
            
            return True
            
        except Exception:
            return False
    
    def get_texture_info(self, file_path: str) -> Dict[str, Any]:
        """Obtém informações sobre uma textura"""
        try:
            with Image.open(file_path) as img:
                return {
                    'size': img.size,
                    'mode': img.mode,
                    'format': img.format,
                    'has_transparency': img.mode in ['RGBA', 'LA'] or 'transparency' in img.info
                }
        except Exception as e:
            return {'error': str(e)}
    
    def is_paa_conversion_available(self) -> bool:
        """Verifica se a conversão para PAA está disponível"""
        return self.imagetopaa_path is not None and Path(self.imagetopaa_path).exists()
    
    def get_imagetopaa_status(self) -> Dict[str, Any]:
        """Retorna status do ImageToPAA"""
        if self.imagetopaa_path:
            path_obj = Path(self.imagetopaa_path)
            return {
                'available': path_obj.exists(),
                'path': str(path_obj),
                'exists': path_obj.exists()
            }
        else:
            return {
                'available': False,
                'path': None,
                'exists': False,
                'message': 'ImageToPAA.exe não encontrado. Instale o DayZ Tools.'
            }