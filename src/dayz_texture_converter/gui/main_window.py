#!/usr/bin/env python3
"""
DayZ Texture Converter - Interface Moderna
Design: Borderless, Dark Theme, Dynamic Colors
"""

import customtkinter as ctk
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image, ImageTk, ImageDraw
import numpy as np
from pathlib import Path
import threading
from typing import Optional, Dict, Any, Tuple
import tkinter as tk
from tkinter import filedialog, messagebox
import colorsys
import sys

from ..core.texture_processor import TextureProcessor
from ..core.preview_generator import PreviewGenerator
from ..utils.material_presets import MaterialPresets


class MainWindow:
    def __init__(self):
        # Cores do tema
        self.colors = {
            'bg_dark': '#0d0d0d',
            'bg_card': '#1a1a1a',
            'bg_card_hover': '#252525',
            'accent': '#3b82f6',
            'accent_hover': '#60a5fa',
            'text': '#ffffff',
            'text_muted': '#888888',
            'border': '#333333',
            'success': '#22c55e',
            'warning': '#f59e0b',
            'error': '#ef4444'
        }
        
        # Janela principal - Configuração melhorada para PyInstaller
        self.root = TkinterDnD.Tk()
        self.root.title("ASKAL TOOLS - Gerador de Material")
        self.root.geometry("1500x950")
        self.root.minsize(1300, 850)
        self.root.configure(bg=self.colors['bg_dark'])
        
        # Configurar ícone da janela
        self.icon_loaded = False
        try:
            print("🎯 Configurando ícone da aplicação...")
            
            # Usar método melhorado
            if self._set_tkinter_icon():
                self.icon_loaded = True
            else:
                print("⚠️ Falha ao carregar ícone via Tkinter, tentando fallback...")
                self._try_png_icon()
                
        except Exception as e:
            print(f"⚠️ Erro geral ao carregar ícone: {e}")
            self._try_png_icon()
        
        # Configuração de janela melhorada para executável
        self.use_borderless = False  # Desabilitar borderless por padrão
        
        # Configurar ícone da barra de tarefas no Windows
        self._configure_taskbar_icon()
        
        # Configurar ícone da barra de tarefas no Windows
        self._configure_taskbar_icon()
        
        # Tentar configuração borderless apenas se não for executável PyInstaller
        if not hasattr(sys, '_MEIPASS'):
            try:
                # Remover decorações mas manter na taskbar
                self.root.overrideredirect(True)
                self.use_borderless = True
                
                # Garantir que apareça no Alt+Tab e barra de tarefas (Windows)
                import ctypes
                from ctypes import wintypes
                
                # Aguardar janela ser criada
                self.root.update_idletasks()
                hwnd = self.root.winfo_id()
                
                # Remover WS_EX_TOOLWINDOW para aparecer na barra de tarefas
                # Adicionar WS_EX_APPWINDOW para forçar aparição na taskbar
                GWL_EXSTYLE = -20
                WS_EX_TOOLWINDOW = 0x00000080
                WS_EX_APPWINDOW = 0x00040000
                
                # Obter estilo atual
                current_style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
                
                # Remover TOOLWINDOW e adicionar APPWINDOW
                new_style = (current_style & ~WS_EX_TOOLWINDOW) | WS_EX_APPWINDOW
                ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, new_style)
                
                # Forçar atualização da barra de tarefas
                ctypes.windll.user32.ShowWindow(hwnd, 0)  # SW_HIDE
                ctypes.windll.user32.ShowWindow(hwnd, 5)  # SW_SHOW
                
                print("✅ Configuração borderless aplicada")
                
            except Exception as e:
                print(f"⚠️ Erro na configuração borderless: {e}")
                # Fallback: usar janela normal
                self.root.overrideredirect(False)
                self.use_borderless = False
        else:
            print("📦 Executável detectado - usando janela padrão para melhor compatibilidade")
            self.use_borderless = False
        
        # Variáveis para arrastar janela
        self._drag_data = {"x": 0, "y": 0}
        
        # Configuração do tema
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Processadores
        self.processor = TextureProcessor()
        self.preview_generator = PreviewGenerator()
        self.material_presets = MaterialPresets()
        
        # Estado das texturas
        self.textures = {
            'base_color': None,
            'normal_map': None,
            'metalness': None,
            'roughness': None
        }
        
        # Thumbnails das texturas carregadas
        self.texture_thumbnails = {}
        self.texture_accent_colors = {}
        
        # Preview habilitado por padrão
        self.real_time_preview = tk.BooleanVar(value=True)
        
        # Configurações
        self.settings = {
            'base_color_rgb': {'r': 1.0, 'g': 1.0, 'b': 1.0},
            'normal_invert_green': False,
            'metalness_opacity': 100.0,
            'roughness_opacity': 100.0,
            'output_resolution': 1024,
            'convert_to_paa': False,
            'remove_png_after_paa': True,
            'output_directory': '',
            'specular_mode': 'auto',
            'specular_value': 128,
            'opacity_value': 255,
            'generate_rvmat': False,
            'material_preset': 'custom',
            'metal_override_enabled': False,
            'metal_override_value': 128,
            'gloss_override_enabled': False,
            'gloss_override_value': 128
        }
        
        self.setup_ui()
        self.center_window()
        
        # Aplicar preset inicial e atualizar RVMAT
        self.update_rvmat_preview()
        
        # Forçar configuração final do ícone após tudo estar pronto
        self.root.after(100, self._final_icon_setup)
    
    def _try_png_icon(self):
        """Tenta carregar ícone PNG como fallback"""
        try:
            if self._set_png_icon_tkinter():
                self.icon_loaded = True
                print("✅ Ícone PNG carregado como fallback")
            else:
                print("❌ Falha ao carregar qualquer ícone")
                        
        except Exception as e:
            print(f"⚠️ Erro no fallback PNG: {e}")
    
    def _configure_taskbar_icon(self):
        """Configura ícone específico para a barra de tarefas do Windows"""
        try:
            # Primeiro, tentar configurar via Tkinter (método mais simples)
            self._set_tkinter_icon()
            
            # Depois, forçar via Windows API para garantir
            if sys.platform == "win32":
                self._set_windows_api_icon()
                
        except Exception as e:
            print(f"⚠️ Erro na configuração do ícone da taskbar: {e}")
    
    def _set_tkinter_icon(self):
        """Configura ícone via Tkinter"""
        icon_paths = self._get_icon_paths()
        
        # Tentar .ico primeiro
        for icon_path in icon_paths:
            if icon_path.suffix.lower() == '.ico' and icon_path.exists():
                try:
                    # Método 1: iconbitmap
                    self.root.iconbitmap(str(icon_path))
                    # Método 2: wm_iconbitmap (alternativo)
                    self.root.wm_iconbitmap(str(icon_path))
                    print(f"✅ Ícone Tkinter configurado: {icon_path}")
                    return True
                except Exception as e:
                    print(f"⚠️ Erro Tkinter {icon_path}: {e}")
                    continue
        
        # Se .ico falhar, tentar PNG
        return self._set_png_icon_tkinter()
    
    def _set_png_icon_tkinter(self):
        """Configura ícone PNG via Tkinter"""
        icon_paths = self._get_icon_paths(extension='.png')
        
        for icon_path in icon_paths:
            if icon_path.exists():
                try:
                    from PIL import Image, ImageTk
                    
                    # Carregar e redimensionar
                    img = Image.open(icon_path)
                    
                    # Criar múltiplos tamanhos
                    sizes = [16, 32, 48, 64]
                    icons = []
                    
                    for size in sizes:
                        resized = img.resize((size, size), Image.Resampling.LANCZOS)
                        photo = ImageTk.PhotoImage(resized)
                        icons.append(photo)
                        # Manter referência para evitar garbage collection
                        setattr(self, f'icon_photo_{size}', photo)
                    
                    # Definir ícone principal (maior primeiro)
                    self.root.iconphoto(True, *reversed(icons))
                    print(f"✅ Ícone PNG Tkinter configurado: {icon_path}")
                    return True
                    
                except Exception as e:
                    print(f"⚠️ Erro PNG Tkinter {icon_path}: {e}")
                    continue
        
        return False
    
    def _set_windows_api_icon(self):
        """Força configuração via Windows API"""
        try:
            import ctypes
            from ctypes import wintypes
            
            # Aguardar janela ser criada
            self.root.update_idletasks()
            hwnd = self.root.winfo_id()
            
            icon_paths = self._get_icon_paths()
            
            for icon_path in icon_paths:
                if icon_path.suffix.lower() == '.ico' and icon_path.exists():
                    try:
                        # Carregar ícone usando LoadImage
                        hicon_large = ctypes.windll.user32.LoadImageW(
                            None,  # hInst
                            str(icon_path),  # name
                            1,  # IMAGE_ICON
                            32,  # cx (ícone grande)
                            32,  # cy
                            0x00000010  # LR_LOADFROMFILE
                        )
                        
                        hicon_small = ctypes.windll.user32.LoadImageW(
                            None,  # hInst
                            str(icon_path),  # name
                            1,  # IMAGE_ICON
                            16,  # cx (ícone pequeno)
                            16,  # cy
                            0x00000010  # LR_LOADFROMFILE
                        )
                        
                        if hicon_large:
                            # WM_SETICON = 0x0080
                            # ICON_BIG = 1, ICON_SMALL = 0
                            ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 1, hicon_large)
                            print(f"✅ Ícone grande Windows API: {icon_path}")
                        
                        if hicon_small:
                            ctypes.windll.user32.SendMessageW(hwnd, 0x0080, 0, hicon_small)
                            print(f"✅ Ícone pequeno Windows API: {icon_path}")
                        
                        # Forçar atualização da janela
                        ctypes.windll.user32.UpdateWindow(hwnd)
                        
                        # Também tentar SetClassLongPtr para ícone da classe
                        if hicon_large:
                            GCL_HICON = -14
                            ctypes.windll.user32.SetClassLongPtrW(hwnd, GCL_HICON, hicon_large)
                        
                        if hicon_small:
                            GCL_HICONSM = -34
                            ctypes.windll.user32.SetClassLongPtrW(hwnd, GCL_HICONSM, hicon_small)
                        
                        return True
                        
                    except Exception as e:
                        print(f"⚠️ Erro Windows API {icon_path}: {e}")
                        continue
            
            return False
            
        except Exception as e:
            print(f"⚠️ Erro geral Windows API: {e}")
            return False
    
    def _get_icon_paths(self, extension='.ico'):
        """Retorna lista de caminhos possíveis para o ícone"""
        icon_paths = []
        
        # Se for executável PyInstaller
        if hasattr(sys, '_MEIPASS'):
            base_path = Path(sys._MEIPASS)
            icon_paths.extend([
                base_path / "media" / f"askal_logo{extension}",
                base_path / f"askal_logo{extension}",
            ])
        
        # Caminhos padrão para desenvolvimento
        icon_paths.extend([
            Path(f"media/askal_logo{extension}"),
            Path(f"./media/askal_logo{extension}"),
            Path.cwd() / "media" / f"askal_logo{extension}"
        ])
        
        return icon_paths
    
    def _final_icon_setup(self):
        """Configuração final do ícone após a janela estar completamente carregada"""
        try:
            print("🔄 Aplicando configuração final do ícone...")
            
            # Forçar configuração via Windows API novamente
            if sys.platform == "win32":
                self._set_windows_api_icon()
            
            # Tentar definir título da janela novamente (às vezes ajuda)
            self.root.title("ASKAL TOOLS - Gerador de Material")
            
            # Forçar atualização da janela
            self.root.update_idletasks()
            
            print("✅ Configuração final do ícone concluída")
            
        except Exception as e:
            print(f"⚠️ Erro na configuração final do ícone: {e}")
        
    def center_window(self):
        """Centraliza a janela na tela"""
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')
    
    def setup_ui(self):
        """Configura a interface principal"""
        # Container principal com borda
        border_frame = tk.Frame(self.root, bg=self.colors['border'])
        border_frame.pack(fill="both", expand=True, padx=1, pady=1)
        
        self.main_container = tk.Frame(border_frame, bg=self.colors['bg_dark'])
        self.main_container.pack(fill="both", expand=True)
        
        # Barra de título customizada
        self.setup_title_bar()
        
        # Área de conteúdo
        content = tk.Frame(self.main_container, bg=self.colors['bg_dark'])
        content.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # Grid layout: Esquerda (texturas) | Centro (preview) | Direita (RVMAT)
        content.grid_columnconfigure(0, weight=1, minsize=300)
        content.grid_columnconfigure(1, weight=2, minsize=550)
        content.grid_columnconfigure(2, weight=1, minsize=350)
        content.grid_rowconfigure(0, weight=1)
        
        # Painel esquerdo - Texturas de entrada
        self.setup_left_panel(content)
        
        # Painel central - Preview e controles
        self.setup_center_panel(content)
        
        # Painel direito - RVMAT Preview
        self.setup_right_panel(content)
    
    def setup_title_bar(self):
        """Cria barra de título customizada (apenas se borderless)"""
        # Só criar barra de título customizada se estiver usando borderless
        if not self.use_borderless:
            return
            
        title_bar = tk.Frame(self.main_container, bg=self.colors['bg_card'], height=40)
        title_bar.pack(fill="x", side="top")
        title_bar.pack_propagate(False)
        
        # Bind para arrastar janela
        title_bar.bind('<Button-1>', self.start_drag)
        title_bar.bind('<B1-Motion>', self.do_drag)
        
        # Ícone e título
        title_frame = tk.Frame(title_bar, bg=self.colors['bg_card'])
        title_frame.pack(side="left", padx=15)
        
        # Carregar logo ASKAL
        try:
            # Tentar diferentes caminhos possíveis para o logo
            possible_paths = [
                Path("media/askal_logo.png"),  # PNG original
                Path("./media/askal_logo.png"),  # Explicitamente relativo
                Path.cwd() / "media" / "askal_logo.png",  # Usando diretório atual
                Path(__file__).parent.parent.parent / "media" / "askal_logo.png",  # Relativo ao arquivo atual
            ]
            
            logo_loaded = False
            for logo_path in possible_paths:
                try:
                    if logo_path.exists():
                        print(f"Logo encontrado em: {logo_path}")
                        logo_img = Image.open(logo_path)
                        logo_img = logo_img.resize((20, 20), Image.Resampling.LANCZOS)
                        self.logo_photo = ImageTk.PhotoImage(logo_img)
                        
                        logo_label = tk.Label(title_frame, image=self.logo_photo,
                                             bg=self.colors['bg_card'])
                        logo_label.pack(side="left", pady=10)
                        logo_loaded = True
                        break
                except Exception as e:
                    print(f"Erro ao tentar carregar de {logo_path}: {e}")
                    continue
            
            if not logo_loaded:
                print("Logo não encontrado em nenhum caminho, usando fallback")
                # Fallback para círculo colorido se logo não encontrado
                icon_canvas = tk.Canvas(title_frame, width=20, height=20, 
                                       bg=self.colors['bg_card'], highlightthickness=0)
                icon_canvas.pack(side="left", pady=10)
                icon_canvas.create_oval(2, 2, 18, 18, fill=self.colors['accent'], outline="")
                
        except Exception as e:
            print(f"Erro geral ao carregar logo: {e}")
            # Fallback para círculo colorido
            icon_canvas = tk.Canvas(title_frame, width=20, height=20, 
                                   bg=self.colors['bg_card'], highlightthickness=0)
            icon_canvas.pack(side="left", pady=10)
            icon_canvas.create_oval(2, 2, 18, 18, fill=self.colors['accent'], outline="")
        
        title_label = tk.Label(title_frame, text="ASKAL TOOLS - Gerador de Material", 
                              font=("Segoe UI", 12, "bold"),
                              bg=self.colors['bg_card'], fg=self.colors['text'])
        title_label.pack(side="left", padx=(10, 0), pady=10)
        title_label.bind('<Button-1>', self.start_drag)
        title_label.bind('<B1-Motion>', self.do_drag)
        
        # Versão
        version_label = tk.Label(title_frame, text="v2.0", 
                                font=("Segoe UI", 9),
                                bg=self.colors['bg_card'], fg=self.colors['text_muted'])
        version_label.pack(side="left", padx=(8, 0), pady=10)
        
        # Botões de controle da janela
        controls = tk.Frame(title_bar, bg=self.colors['bg_card'])
        controls.pack(side="right", padx=5)
        
        # Minimizar
        min_btn = tk.Label(controls, text="─", font=("Segoe UI", 12),
                          bg=self.colors['bg_card'], fg=self.colors['text_muted'],
                          cursor="hand2", width=3)
        min_btn.pack(side="left", padx=2, pady=8)
        min_btn.bind('<Button-1>', lambda e: self.root.iconify())
        min_btn.bind('<Enter>', lambda e: min_btn.configure(fg=self.colors['text']))
        min_btn.bind('<Leave>', lambda e: min_btn.configure(fg=self.colors['text_muted']))
        
        # Maximizar
        max_btn = tk.Label(controls, text="□", font=("Segoe UI", 12),
                          bg=self.colors['bg_card'], fg=self.colors['text_muted'],
                          cursor="hand2", width=3)
        max_btn.pack(side="left", padx=2, pady=8)
        max_btn.bind('<Button-1>', self.toggle_maximize)
        max_btn.bind('<Enter>', lambda e: max_btn.configure(fg=self.colors['text']))
        max_btn.bind('<Leave>', lambda e: max_btn.configure(fg=self.colors['text_muted']))
        
        # Fechar
        close_btn = tk.Label(controls, text="✕", font=("Segoe UI", 11),
                            bg=self.colors['bg_card'], fg=self.colors['text_muted'],
                            cursor="hand2", width=3)
        close_btn.pack(side="left", padx=2, pady=8)
        close_btn.bind('<Button-1>', lambda e: self.root.quit())
        close_btn.bind('<Enter>', lambda e: close_btn.configure(bg=self.colors['error'], fg='white'))
        close_btn.bind('<Leave>', lambda e: close_btn.configure(bg=self.colors['bg_card'], fg=self.colors['text_muted']))
    
    def start_drag(self, event):
        """Inicia arraste da janela"""
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
    
    def do_drag(self, event):
        """Executa arraste da janela"""
        x = self.root.winfo_x() + (event.x - self._drag_data["x"])
        y = self.root.winfo_y() + (event.y - self._drag_data["y"])
        self.root.geometry(f"+{x}+{y}")
    
    def toggle_maximize(self, event=None):
        """Alterna maximização da janela"""
        if hasattr(self, '_is_maximized') and self._is_maximized:
            self.root.geometry(self._normal_geometry)
            self._is_maximized = False
        else:
            self._normal_geometry = self.root.geometry()
            self.root.geometry(f"{self.root.winfo_screenwidth()}x{self.root.winfo_screenheight()}+0+0")
            self._is_maximized = True

    
    def setup_left_panel(self, parent):
        """Painel esquerdo - Texturas de entrada"""
        left_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        left_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        
        # Título
        title = tk.Label(left_frame, text="📁 Texturas", 
                        font=("Segoe UI", 14, "bold"),
                        bg=self.colors['bg_dark'], fg=self.colors['text'])
        title.pack(anchor="w", pady=(0, 10))
        
        # Container direto para os cards (sem scroll)
        cards_container = tk.Frame(left_frame, bg=self.colors['bg_dark'])
        cards_container.pack(fill="both", expand=True)
        
        # Cards de textura
        texture_configs = [
            ("Base Color", "base_color", "🎨", "Diffuse/Albedo"),
            ("Normal Map", "normal_map", "🗺️", "Mapa de normais"),
            ("Metalness", "metalness", "⚙️", "Canal verde SMDI"),
            ("Roughness", "roughness", "✨", "Canal azul SMDI")
        ]
        
        for title, key, icon, desc in texture_configs:
            self.create_texture_card(cards_container, title, key, icon, desc)
    
    def create_texture_card(self, parent, title: str, key: str, icon: str, description: str):
        """Cria card de textura com thumbnail"""
        # Card container
        card = tk.Frame(parent, bg=self.colors['bg_card'])
        card.pack(fill="x", pady=(0, 8))
        
        # Armazenar referência do card para atualizar cor
        setattr(self, f"{key}_card", card)
        
        # Header do card
        header = tk.Frame(card, bg=self.colors['bg_card'])
        header.pack(fill="x", padx=12, pady=(12, 8))
        
        # Ícone e título
        title_frame = tk.Frame(header, bg=self.colors['bg_card'])
        title_frame.pack(side="left")
        
        icon_label = tk.Label(title_frame, text=icon, font=("Segoe UI", 14),
                             bg=self.colors['bg_card'], fg=self.colors['text'])
        icon_label.pack(side="left")
        
        title_label = tk.Label(title_frame, text=title, font=("Segoe UI", 11, "bold"),
                              bg=self.colors['bg_card'], fg=self.colors['text'])
        title_label.pack(side="left", padx=(6, 0))
        
        # Descrição
        desc_label = tk.Label(header, text=description, font=("Segoe UI", 9),
                             bg=self.colors['bg_card'], fg=self.colors['text_muted'])
        desc_label.pack(side="right")
        
        # Área de drop/thumbnail
        drop_frame = tk.Frame(card, bg=self.colors['border'], height=70)
        drop_frame.pack(fill="x", padx=12, pady=(0, 12))
        drop_frame.pack_propagate(False)
        
        inner_drop = tk.Frame(drop_frame, bg=self.colors['bg_dark'])
        inner_drop.pack(fill="both", expand=True, padx=1, pady=1)
        
        # Canvas para thumbnail ou placeholder
        thumb_canvas = tk.Canvas(inner_drop, bg=self.colors['bg_dark'], 
                                highlightthickness=0, cursor="hand2",
                                width=240, height=66)
        thumb_canvas.pack(fill="both", expand=True)
        
        # Placeholder text - centralizado
        thumb_canvas.create_text(
            120, 33,
            text="📂 Arraste ou clique",
            fill=self.colors['text_muted'],
            font=("Segoe UI", 9),
            tags="placeholder"
        )
        
        # Armazenar referência
        setattr(self, f"{key}_canvas", thumb_canvas)
        setattr(self, f"{key}_drop_frame", drop_frame)
        
        # Bindings
        thumb_canvas.bind('<Button-1>', lambda e, k=key: self.browse_texture(k))
        thumb_canvas.drop_target_register(DND_FILES)
        thumb_canvas.dnd_bind('<<Drop>>', lambda e, k=key: self.drop_texture(e, k))
        
        # Hover effects
        def on_enter(e, frame=drop_frame):
            frame.configure(bg=self.colors['accent'])
        def on_leave(e, frame=drop_frame):
            frame.configure(bg=self.colors['border'])
        
        thumb_canvas.bind('<Enter>', on_enter)
        thumb_canvas.bind('<Leave>', on_leave)
    
    def setup_center_panel(self, parent):
        """Painel central - Preview e controles"""
        center_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        center_frame.grid(row=0, column=1, sticky="nsew", padx=8)
        
        # Título com toggle de preview
        header = tk.Frame(center_frame, bg=self.colors['bg_dark'])
        header.pack(fill="x", pady=(0, 10))
        
        title = tk.Label(header, text="👁️ Preview & Controles", 
                        font=("Segoe UI", 14, "bold"),
                        bg=self.colors['bg_dark'], fg=self.colors['text'])
        title.pack(side="left")
        
        # Toggle preview em tempo real
        preview_toggle = tk.Frame(header, bg=self.colors['bg_dark'])
        preview_toggle.pack(side="right")
        
        self.preview_indicator = tk.Canvas(preview_toggle, width=40, height=20,
                                          bg=self.colors['bg_dark'], highlightthickness=0)
        self.preview_indicator.pack(side="left", padx=(0, 8))
        self.draw_toggle(True)
        self.preview_indicator.bind('<Button-1>', self.toggle_preview)
        
        preview_label = tk.Label(preview_toggle, text="Auto Preview",
                                font=("Segoe UI", 9),
                                bg=self.colors['bg_dark'], fg=self.colors['text_muted'])
        preview_label.pack(side="left")
        
        # Container principal
        main_container = tk.Frame(center_frame, bg=self.colors['bg_dark'])
        main_container.pack(fill="both", expand=True)
        
        # Seção de Preview (topo)
        preview_section = tk.Frame(main_container, bg=self.colors['bg_card'])
        preview_section.pack(fill="x", pady=(0, 10))
        
        preview_inner = tk.Frame(preview_section, bg=self.colors['bg_card'])
        preview_inner.pack(fill="x", padx=15, pady=15)
        
        preview_inner.grid_columnconfigure(0, weight=1)
        preview_inner.grid_columnconfigure(1, weight=1)
        preview_inner.grid_columnconfigure(2, weight=1)
        
        # Preview cards
        self.create_preview_card(preview_inner, "Base Color", "base_color_preview", 0)
        self.create_preview_card(preview_inner, "Normal Map", "normal_preview", 1)
        self.create_preview_card(preview_inner, "SMDI Final", "smdi_preview", 2)
        
        # Seção de Ajustes
        self.setup_adjustments_section(main_container)
        
        # Seção SMDI
        self.setup_smdi_section(main_container)
    
    def create_preview_card(self, parent, title: str, key: str, column: int):
        """Cria card de preview"""
        card = tk.Frame(parent, bg=self.colors['bg_dark'])
        card.grid(row=0, column=column, sticky="nsew", padx=5, pady=(0, 10))
        
        # Título
        title_label = tk.Label(card, text=title, font=("Segoe UI", 10, "bold"),
                              bg=self.colors['bg_dark'], fg=self.colors['text'])
        title_label.pack(pady=(0, 5))
        
        # Canvas de preview
        canvas = tk.Canvas(card, width=150, height=150, 
                          bg='#1f1f1f', highlightthickness=1,
                          highlightbackground=self.colors['border'])
        canvas.pack()
        
        setattr(self, f"{key}_canvas", canvas)
    
    
    def setup_adjustments_section(self, parent):
        """Seção de ajustes básicos"""
        # Card de ajustes
        adjustments_card = tk.Frame(parent, bg=self.colors['bg_card'])
        adjustments_card.pack(fill="x", pady=(0, 10))
        
        # Título
        adj_title = tk.Label(adjustments_card, text="🎨 Ajustes das Texturas",
                            font=("Segoe UI", 12, "bold"),
                            bg=self.colors['bg_card'], fg=self.colors['text'])
        adj_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Grid de controles
        grid = tk.Frame(adjustments_card, bg=self.colors['bg_card'])
        grid.pack(fill="x", padx=15, pady=(0, 15))
        
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)
        
        # RGB Controls
        rgb_frame = tk.Frame(grid, bg=self.colors['bg_dark'])
        rgb_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 10))
        
        rgb_title = tk.Label(rgb_frame, text="🎨 Ajuste RGB (Base Color)",
                            font=("Segoe UI", 10, "bold"),
                            bg=self.colors['bg_dark'], fg=self.colors['text'])
        rgb_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        for color, label in [('r', 'Vermelho'), ('g', 'Verde'), ('b', 'Azul')]:
            self.create_slider_control(rgb_frame, label, f"rgb_{color}", 0.0, 2.0, 1.0,
                                       lambda v, c=color: self.update_rgb(c, v))
        
        # Normal Map Controls
        normal_frame = tk.Frame(grid, bg=self.colors['bg_dark'])
        normal_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=(0, 10))
        
        normal_title = tk.Label(normal_frame, text="🗺️ Normal Map",
                               font=("Segoe UI", 10, "bold"),
                               bg=self.colors['bg_dark'], fg=self.colors['text'])
        normal_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Checkbox inverter verde
        invert_frame = tk.Frame(normal_frame, bg=self.colors['bg_dark'])
        invert_frame.pack(fill="x", padx=10, pady=5)
        
        self.invert_green_var = tk.BooleanVar(value=False)
        invert_check = tk.Checkbutton(invert_frame, text="Inverter Canal Verde (Unity → DayZ)",
                                      variable=self.invert_green_var,
                                      command=self.update_invert_green,
                                      bg=self.colors['bg_dark'], fg=self.colors['text'],
                                      selectcolor=self.colors['bg_card'],
                                      activebackground=self.colors['bg_dark'],
                                      activeforeground=self.colors['text'],
                                      font=("Segoe UI", 9))
        invert_check.pack(anchor="w")
        
        # Opacidades
        opacity_frame = tk.Frame(grid, bg=self.colors['bg_dark'])
        opacity_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        
        opacity_title = tk.Label(opacity_frame, text="🔆 Opacidade das Texturas",
                                font=("Segoe UI", 10, "bold"),
                                bg=self.colors['bg_dark'], fg=self.colors['text'])
        opacity_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        opacity_grid = tk.Frame(opacity_frame, bg=self.colors['bg_dark'])
        opacity_grid.pack(fill="x", padx=10)
        opacity_grid.grid_columnconfigure(0, weight=1)
        opacity_grid.grid_columnconfigure(1, weight=1)
        
        # Metalness opacity
        metal_op = tk.Frame(opacity_grid, bg=self.colors['bg_dark'])
        metal_op.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.create_slider_control(metal_op, "Metalness", "metalness_opacity", 0, 100, 100,
                                   lambda v: self.update_opacity('metalness_opacity', v), suffix="%")
        
        # Roughness opacity
        rough_op = tk.Frame(opacity_grid, bg=self.colors['bg_dark'])
        rough_op.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        self.create_slider_control(rough_op, "Roughness", "roughness_opacity", 0, 100, 100,
                                   lambda v: self.update_opacity('roughness_opacity', v), suffix="%")
    
    def setup_smdi_section(self, parent):
        """Seção de configurações SMDI"""
        # Card SMDI
        smdi_card = tk.Frame(parent, bg=self.colors['bg_card'])
        smdi_card.pack(fill="x", pady=(0, 10))
        
        # Título
        smdi_title = tk.Label(smdi_card, text="⚙️ Configurações SMDI Avançadas",
                             font=("Segoe UI", 12, "bold"),
                             bg=self.colors['bg_card'], fg=self.colors['text'])
        smdi_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        grid = tk.Frame(smdi_card, bg=self.colors['bg_card'])
        grid.pack(fill="x", padx=15, pady=(0, 15))
        
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)
        grid.grid_columnconfigure(2, weight=1)
        
        # Metal Fill
        metal_frame = tk.Frame(grid, bg=self.colors['bg_dark'])
        metal_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=(0, 10))
        
        metal_title = tk.Label(metal_frame, text="🔧 Metal Fill",
                              font=("Segoe UI", 10, "bold"),
                              bg=self.colors['bg_dark'], fg=self.colors['text'])
        metal_title.pack(anchor="w", padx=10, pady=(10, 2))
        
        metal_desc = tk.Label(metal_frame, text="Preenche áreas sem metal",
                             font=("Segoe UI", 8),
                             bg=self.colors['bg_dark'], fg=self.colors['text_muted'])
        metal_desc.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.metal_override_var = tk.BooleanVar(value=False)
        metal_check = tk.Checkbutton(metal_frame, text="Habilitar",
                                     variable=self.metal_override_var,
                                     command=self.update_metal_fill,
                                     bg=self.colors['bg_dark'], fg=self.colors['text'],
                                     selectcolor=self.colors['bg_card'],
                                     activebackground=self.colors['bg_dark'],
                                     font=("Segoe UI", 9))
        metal_check.pack(anchor="w", padx=10)
        
        self.create_slider_control(metal_frame, "Valor Base", "metal_override", 0, 255, 128,
                                   self.update_metal_fill_value, enabled=False)
        
        # Gloss Fill
        gloss_frame = tk.Frame(grid, bg=self.colors['bg_dark'])
        gloss_frame.grid(row=0, column=1, sticky="nsew", padx=(4, 4), pady=(0, 10))
        
        gloss_title = tk.Label(gloss_frame, text="✨ Gloss Fill",
                              font=("Segoe UI", 10, "bold"),
                              bg=self.colors['bg_dark'], fg=self.colors['text'])
        gloss_title.pack(anchor="w", padx=10, pady=(10, 2))
        
        gloss_desc = tk.Label(gloss_frame, text="Preenche áreas sem brilho",
                             font=("Segoe UI", 8),
                             bg=self.colors['bg_dark'], fg=self.colors['text_muted'])
        gloss_desc.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.gloss_override_var = tk.BooleanVar(value=False)
        gloss_check = tk.Checkbutton(gloss_frame, text="Habilitar",
                                     variable=self.gloss_override_var,
                                     command=self.update_gloss_fill,
                                     bg=self.colors['bg_dark'], fg=self.colors['text'],
                                     selectcolor=self.colors['bg_card'],
                                     activebackground=self.colors['bg_dark'],
                                     font=("Segoe UI", 9))
        gloss_check.pack(anchor="w", padx=10)
        
        self.create_slider_control(gloss_frame, "Valor Base", "gloss_override", 0, 255, 128,
                                   self.update_gloss_fill_value, enabled=False)
        
        # Material Preset e Alpha
        preset_frame = tk.Frame(grid, bg=self.colors['bg_dark'])
        preset_frame.grid(row=0, column=2, sticky="nsew", padx=(8, 0), pady=(0, 10))
        
        # Preset
        preset_title = tk.Label(preset_frame, text="📋 Material Preset",
                               font=("Segoe UI", 10, "bold"),
                               bg=self.colors['bg_dark'], fg=self.colors['text'])
        preset_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.preset_var = tk.StringVar(value="Personalizado")
        preset_combo = ctk.CTkComboBox(preset_frame,
                                       values=self.material_presets.get_preset_names(),
                                       variable=self.preset_var,
                                       command=self.on_preset_changed,
                                       width=140)
        preset_combo.pack(anchor="w", padx=10, pady=5)
        
        # Alpha
        alpha_title = tk.Label(preset_frame, text="🔲 Canal Alpha",
                              font=("Segoe UI", 10, "bold"),
                              bg=self.colors['bg_dark'], fg=self.colors['text'])
        alpha_title.pack(anchor="w", padx=10, pady=(15, 5))
        
        self.create_slider_control(preset_frame, "Opacity", "opacity", 0, 255, 255,
                                   self.update_opacity_value)
    
    def draw_toggle(self, state: bool):
        """Desenha toggle switch"""
        self.preview_indicator.delete("all")
        if state:
            # ON
            self.preview_indicator.create_oval(2, 2, 18, 18, fill=self.colors['accent'], outline="")
            self.preview_indicator.create_oval(22, 2, 38, 18, fill=self.colors['accent'], outline="")
            self.preview_indicator.create_rectangle(10, 2, 30, 18, fill=self.colors['accent'], outline="")
            self.preview_indicator.create_oval(20, 1, 38, 19, fill="white", outline="")
        else:
            # OFF
            self.preview_indicator.create_oval(2, 2, 18, 18, fill=self.colors['border'], outline="")
            self.preview_indicator.create_oval(22, 2, 38, 18, fill=self.colors['border'], outline="")
            self.preview_indicator.create_rectangle(10, 2, 30, 18, fill=self.colors['border'], outline="")
            self.preview_indicator.create_oval(2, 1, 20, 19, fill="white", outline="")
    
    def toggle_preview(self, event=None):
        """Alterna preview automático"""
        current = self.real_time_preview.get()
        self.real_time_preview.set(not current)
        self.draw_toggle(not current)
        if not current:
            self.generate_preview()

    
    def setup_controls_section(self, parent):
        """Seção de controles abaixo dos previews"""
        controls_frame = tk.Frame(parent, bg=self.colors['bg_card'])
        controls_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", pady=(10, 0))
        
        # Notebook para organizar controles
        notebook_frame = tk.Frame(controls_frame, bg=self.colors['bg_card'])
        notebook_frame.pack(fill="both", expand=True)
        
        # Tabs customizadas
        tabs_frame = tk.Frame(notebook_frame, bg=self.colors['bg_dark'])
        tabs_frame.pack(fill="x", pady=(0, 10))
        
        self.current_tab = tk.StringVar(value="adjustments")
        
        tabs = [
            ("🎨 Ajustes", "adjustments"),
            ("⚙️ SMDI", "smdi"),
            ("📤 Saída", "output")
        ]
        
        for text, tab_id in tabs:
            btn = tk.Label(tabs_frame, text=text, font=("Segoe UI", 10),
                          bg=self.colors['bg_dark'], fg=self.colors['text_muted'],
                          cursor="hand2", padx=15, pady=8)
            btn.pack(side="left")
            btn.bind('<Button-1>', lambda e, t=tab_id: self.switch_tab(t))
            setattr(self, f"tab_{tab_id}", btn)
        
        # Highlight tab inicial
        self.tab_adjustments.configure(bg=self.colors['bg_card'], fg=self.colors['text'])
        
        # Container de conteúdo das tabs
        self.tab_content = tk.Frame(notebook_frame, bg=self.colors['bg_card'])
        self.tab_content.pack(fill="both", expand=True)
        
        # Criar conteúdo de cada tab
        self.create_adjustments_tab()
        self.create_smdi_tab()
        self.create_output_tab()
        
        # Mostrar tab inicial
        self.adjustments_content.pack(fill="both", expand=True)
    
    def switch_tab(self, tab_id: str):
        """Troca de tab"""
        # Esconder todas as tabs
        for content in [self.adjustments_content, self.smdi_content, self.output_content]:
            content.pack_forget()
        
        # Reset visual de todas as tabs
        for t in ["adjustments", "smdi", "output"]:
            tab = getattr(self, f"tab_{t}")
            tab.configure(bg=self.colors['bg_dark'], fg=self.colors['text_muted'])
        
        # Ativar tab selecionada
        active_tab = getattr(self, f"tab_{tab_id}")
        active_tab.configure(bg=self.colors['bg_card'], fg=self.colors['text'])
        
        # Mostrar conteúdo
        content = getattr(self, f"{tab_id}_content")
        content.pack(fill="both", expand=True)
        
        self.current_tab.set(tab_id)
    
    def create_adjustments_tab(self):
        """Tab de ajustes básicos"""
        self.adjustments_content = tk.Frame(self.tab_content, bg=self.colors['bg_card'])
        
        # Grid de controles
        grid = tk.Frame(self.adjustments_content, bg=self.colors['bg_card'])
        grid.pack(fill="both", expand=True, padx=10, pady=10)
        
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)
        
        # RGB Controls
        rgb_frame = tk.Frame(grid, bg=self.colors['bg_dark'])
        rgb_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=(0, 10))
        
        rgb_title = tk.Label(rgb_frame, text="🎨 Ajuste RGB (Base Color)",
                            font=("Segoe UI", 10, "bold"),
                            bg=self.colors['bg_dark'], fg=self.colors['text'])
        rgb_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        for color, label in [('r', 'Vermelho'), ('g', 'Verde'), ('b', 'Azul')]:
            self.create_slider_control(rgb_frame, label, f"rgb_{color}", 0.0, 2.0, 1.0,
                                       lambda v, c=color: self.update_rgb(c, v))
        
        # Normal Map Controls
        normal_frame = tk.Frame(grid, bg=self.colors['bg_dark'])
        normal_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 10))
        
        normal_title = tk.Label(normal_frame, text="🗺️ Normal Map",
                               font=("Segoe UI", 10, "bold"),
                               bg=self.colors['bg_dark'], fg=self.colors['text'])
        normal_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Checkbox inverter verde
        invert_frame = tk.Frame(normal_frame, bg=self.colors['bg_dark'])
        invert_frame.pack(fill="x", padx=10, pady=5)
        
        self.invert_green_var = tk.BooleanVar(value=False)
        invert_check = tk.Checkbutton(invert_frame, text="Inverter Canal Verde (Unity → DayZ)",
                                      variable=self.invert_green_var,
                                      command=self.update_invert_green,
                                      bg=self.colors['bg_dark'], fg=self.colors['text'],
                                      selectcolor=self.colors['bg_card'],
                                      activebackground=self.colors['bg_dark'],
                                      activeforeground=self.colors['text'],
                                      font=("Segoe UI", 9))
        invert_check.pack(anchor="w")
        
        # Opacidades
        opacity_frame = tk.Frame(grid, bg=self.colors['bg_dark'])
        opacity_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(0, 10))
        
        opacity_title = tk.Label(opacity_frame, text="🔆 Opacidade das Texturas",
                                font=("Segoe UI", 10, "bold"),
                                bg=self.colors['bg_dark'], fg=self.colors['text'])
        opacity_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        opacity_grid = tk.Frame(opacity_frame, bg=self.colors['bg_dark'])
        opacity_grid.pack(fill="x", padx=10)
        opacity_grid.grid_columnconfigure(0, weight=1)
        opacity_grid.grid_columnconfigure(1, weight=1)
        
        # Metalness opacity
        metal_op = tk.Frame(opacity_grid, bg=self.colors['bg_dark'])
        metal_op.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        self.create_slider_control(metal_op, "Metalness", "metalness_opacity", 0, 100, 100,
                                   lambda v: self.update_opacity('metalness_opacity', v), suffix="%")
        
        # Roughness opacity
        rough_op = tk.Frame(opacity_grid, bg=self.colors['bg_dark'])
        rough_op.grid(row=0, column=1, sticky="ew", padx=(10, 0))
        self.create_slider_control(rough_op, "Roughness", "roughness_opacity", 0, 100, 100,
                                   lambda v: self.update_opacity('roughness_opacity', v), suffix="%")
    
    def create_smdi_tab(self):
        """Tab de configurações SMDI"""
        self.smdi_content = tk.Frame(self.tab_content, bg=self.colors['bg_card'])
        
        grid = tk.Frame(self.smdi_content, bg=self.colors['bg_card'])
        grid.pack(fill="both", expand=True, padx=10, pady=10)
        
        grid.grid_columnconfigure(0, weight=1)
        grid.grid_columnconfigure(1, weight=1)
        
        # Metal Fill
        metal_frame = tk.Frame(grid, bg=self.colors['bg_dark'])
        metal_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=(0, 10))
        
        metal_title = tk.Label(metal_frame, text="🔧 Metal Fill",
                              font=("Segoe UI", 10, "bold"),
                              bg=self.colors['bg_dark'], fg=self.colors['text'])
        metal_title.pack(anchor="w", padx=10, pady=(10, 2))
        
        metal_desc = tk.Label(metal_frame, text="Preenche áreas sem metal",
                             font=("Segoe UI", 8),
                             bg=self.colors['bg_dark'], fg=self.colors['text_muted'])
        metal_desc.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.metal_override_var = tk.BooleanVar(value=False)
        metal_check = tk.Checkbutton(metal_frame, text="Habilitar",
                                     variable=self.metal_override_var,
                                     command=self.update_metal_fill,
                                     bg=self.colors['bg_dark'], fg=self.colors['text'],
                                     selectcolor=self.colors['bg_card'],
                                     activebackground=self.colors['bg_dark'],
                                     font=("Segoe UI", 9))
        metal_check.pack(anchor="w", padx=10)
        
        self.create_slider_control(metal_frame, "Valor Base", "metal_override", 0, 255, 128,
                                   self.update_metal_fill_value, enabled=False)
        
        # Gloss Fill
        gloss_frame = tk.Frame(grid, bg=self.colors['bg_dark'])
        gloss_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=(0, 10))
        
        gloss_title = tk.Label(gloss_frame, text="✨ Gloss Fill",
                              font=("Segoe UI", 10, "bold"),
                              bg=self.colors['bg_dark'], fg=self.colors['text'])
        gloss_title.pack(anchor="w", padx=10, pady=(10, 2))
        
        gloss_desc = tk.Label(gloss_frame, text="Preenche áreas sem brilho",
                             font=("Segoe UI", 8),
                             bg=self.colors['bg_dark'], fg=self.colors['text_muted'])
        gloss_desc.pack(anchor="w", padx=10, pady=(0, 5))
        
        self.gloss_override_var = tk.BooleanVar(value=False)
        gloss_check = tk.Checkbutton(gloss_frame, text="Habilitar",
                                     variable=self.gloss_override_var,
                                     command=self.update_gloss_fill,
                                     bg=self.colors['bg_dark'], fg=self.colors['text'],
                                     selectcolor=self.colors['bg_card'],
                                     activebackground=self.colors['bg_dark'],
                                     font=("Segoe UI", 9))
        gloss_check.pack(anchor="w", padx=10)
        
        self.create_slider_control(gloss_frame, "Valor Base", "gloss_override", 0, 255, 128,
                                   self.update_gloss_fill_value, enabled=False)
        
        # Material Preset e Alpha
        bottom_frame = tk.Frame(grid, bg=self.colors['bg_dark'])
        bottom_frame.grid(row=1, column=0, columnspan=2, sticky="nsew")
        
        bottom_frame.grid_columnconfigure(0, weight=1)
        bottom_frame.grid_columnconfigure(1, weight=1)
        
        # Preset
        preset_frame = tk.Frame(bottom_frame, bg=self.colors['bg_dark'])
        preset_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5), pady=10)
        
        preset_title = tk.Label(preset_frame, text="📋 Preset de Material",
                               font=("Segoe UI", 10, "bold"),
                               bg=self.colors['bg_dark'], fg=self.colors['text'])
        preset_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.preset_var = tk.StringVar(value="Personalizado")
        preset_combo = ctk.CTkComboBox(preset_frame,
                                       values=self.material_presets.get_preset_names(),
                                       variable=self.preset_var,
                                       command=self.on_preset_changed,
                                       width=200)
        preset_combo.pack(anchor="w", padx=10, pady=5)
        
        # Alpha
        alpha_frame = tk.Frame(bottom_frame, bg=self.colors['bg_dark'])
        alpha_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0), pady=10)
        
        alpha_title = tk.Label(alpha_frame, text="🔲 Canal Alpha",
                              font=("Segoe UI", 10, "bold"),
                              bg=self.colors['bg_dark'], fg=self.colors['text'])
        alpha_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.create_slider_control(alpha_frame, "Opacity", "opacity", 0, 255, 255,
                                   self.update_opacity_value)

    
    def create_output_tab(self):
        """Tab de configurações de saída"""
        self.output_content = tk.Frame(self.tab_content, bg=self.colors['bg_card'])
        
        grid = tk.Frame(self.output_content, bg=self.colors['bg_card'])
        grid.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Pasta de destino
        dest_frame = tk.Frame(grid, bg=self.colors['bg_dark'])
        dest_frame.pack(fill="x", pady=(0, 10))
        
        dest_title = tk.Label(dest_frame, text="📁 Pasta de Destino",
                             font=("Segoe UI", 10, "bold"),
                             bg=self.colors['bg_dark'], fg=self.colors['text'])
        dest_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        dest_input = tk.Frame(dest_frame, bg=self.colors['bg_dark'])
        dest_input.pack(fill="x", padx=10, pady=(0, 10))
        
        self.dest_entry = tk.Entry(dest_input, font=("Segoe UI", 10),
                                   bg=self.colors['bg_card'], fg=self.colors['text'],
                                   insertbackground=self.colors['text'],
                                   relief="flat", highlightthickness=1,
                                   highlightbackground=self.colors['border'])
        self.dest_entry.pack(side="left", fill="x", expand=True, ipady=8)
        self.dest_entry.insert(0, "P:\\" if Path("P:\\").exists() else "")
        
        dest_btn = tk.Button(dest_input, text="Procurar", font=("Segoe UI", 9),
                            bg=self.colors['accent'], fg="white",
                            activebackground=self.colors['accent_hover'],
                            relief="flat", cursor="hand2",
                            command=self.browse_output_directory)
        dest_btn.pack(side="right", padx=(10, 0), ipady=5, ipadx=10)
        
        # Resolução e opções
        options_frame = tk.Frame(grid, bg=self.colors['bg_dark'])
        options_frame.pack(fill="x", pady=(0, 10))
        
        options_frame.grid_columnconfigure(0, weight=1)
        options_frame.grid_columnconfigure(1, weight=1)
        
        # Resolução
        res_frame = tk.Frame(options_frame, bg=self.colors['bg_dark'])
        res_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        
        res_title = tk.Label(res_frame, text="📐 Resolução",
                            font=("Segoe UI", 10, "bold"),
                            bg=self.colors['bg_dark'], fg=self.colors['text'])
        res_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.resolution_var = tk.StringVar(value="1024x1024")
        res_combo = ctk.CTkComboBox(res_frame,
                                    values=["512x512", "1024x1024", "2048x2048", "4096x4096"],
                                    variable=self.resolution_var,
                                    width=150)
        res_combo.pack(anchor="w", padx=10, pady=5)
        
        # PAA Options
        paa_frame = tk.Frame(options_frame, bg=self.colors['bg_dark'])
        paa_frame.grid(row=0, column=1, sticky="nsew", padx=(5, 0))
        
        paa_title = tk.Label(paa_frame, text="🎮 Conversão PAA",
                            font=("Segoe UI", 10, "bold"),
                            bg=self.colors['bg_dark'], fg=self.colors['text'])
        paa_title.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Status do ImageToPAA
        paa_status = self.processor.get_imagetopaa_status()
        status_text = "✅ DayZ Tools OK" if paa_status['available'] else "❌ DayZ Tools não encontrado"
        status_color = self.colors['success'] if paa_status['available'] else self.colors['error']
        
        status_label = tk.Label(paa_frame, text=status_text, font=("Segoe UI", 9),
                               bg=self.colors['bg_dark'], fg=status_color)
        status_label.pack(anchor="w", padx=10)
        
        self.convert_paa_var = tk.BooleanVar(value=False)
        paa_check = tk.Checkbutton(paa_frame, text="Converter para .paa",
                                   variable=self.convert_paa_var,
                                   command=self.update_paa_setting,
                                   bg=self.colors['bg_dark'], fg=self.colors['text'],
                                   selectcolor=self.colors['bg_card'],
                                   activebackground=self.colors['bg_dark'],
                                   font=("Segoe UI", 9),
                                   state="normal" if paa_status['available'] else "disabled")
        paa_check.pack(anchor="w", padx=10)
        
        self.remove_png_var = tk.BooleanVar(value=True)
        png_check = tk.Checkbutton(paa_frame, text="Remover .png após conversão",
                                   variable=self.remove_png_var,
                                   bg=self.colors['bg_dark'], fg=self.colors['text'],
                                   selectcolor=self.colors['bg_card'],
                                   activebackground=self.colors['bg_dark'],
                                   font=("Segoe UI", 9))
        png_check.pack(anchor="w", padx=10)
        
        # RVMAT
        rvmat_frame = tk.Frame(grid, bg=self.colors['bg_dark'])
        rvmat_frame.pack(fill="x", pady=(0, 10))
        
        self.generate_rvmat_var = tk.BooleanVar(value=False)
        rvmat_check = tk.Checkbutton(rvmat_frame, text="📄 Gerar arquivo RVMAT automaticamente",
                                     variable=self.generate_rvmat_var,
                                     bg=self.colors['bg_dark'], fg=self.colors['text'],
                                     selectcolor=self.colors['bg_card'],
                                     activebackground=self.colors['bg_dark'],
                                     font=("Segoe UI", 10, "bold"))
        rvmat_check.pack(anchor="w", padx=10, pady=10)
        
        # Botão converter
        convert_frame = tk.Frame(grid, bg=self.colors['bg_dark'])
        convert_frame.pack(fill="x", pady=10)
        
        self.convert_btn = tk.Button(convert_frame, text="🚀 CONVERTER TEXTURAS",
                                     font=("Segoe UI", 14, "bold"),
                                     bg=self.colors['accent'], fg="white",
                                     activebackground=self.colors['accent_hover'],
                                     relief="flat", cursor="hand2",
                                     command=self.convert_textures)
        self.convert_btn.pack(fill="x", padx=10, ipady=15)
    
    def create_slider_control(self, parent, label: str, key: str, 
                             min_val: float, max_val: float, default: float,
                             callback, suffix: str = "", enabled: bool = True):
        """Cria controle de slider customizado"""
        frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        frame.pack(fill="x", padx=10, pady=5)
        
        # Label e valor
        header = tk.Frame(frame, bg=self.colors['bg_dark'])
        header.pack(fill="x")
        
        lbl = tk.Label(header, text=label, font=("Segoe UI", 9),
                      bg=self.colors['bg_dark'], fg=self.colors['text_muted'])
        lbl.pack(side="left")
        
        value_lbl = tk.Label(header, text=f"{default:.2f}{suffix}" if isinstance(default, float) and max_val <= 2 else f"{int(default)}{suffix}",
                            font=("Segoe UI", 9, "bold"),
                            bg=self.colors['bg_dark'], fg=self.colors['text'])
        value_lbl.pack(side="right")
        setattr(self, f"{key}_value_label", value_lbl)
        
        # Slider
        slider = ctk.CTkSlider(frame, from_=min_val, to=max_val,
                               number_of_steps=int((max_val - min_val) * (100 if max_val <= 2 else 1)),
                               command=lambda v: self._slider_callback(v, key, callback, suffix, max_val),
                               progress_color=self.colors['accent'],
                               button_color=self.colors['accent'],
                               button_hover_color=self.colors['accent_hover'])
        slider.set(default)
        slider.pack(fill="x", pady=(5, 0))
        
        if not enabled:
            slider.configure(state="disabled")
        
        setattr(self, f"{key}_slider", slider)
    
    def _slider_callback(self, value, key: str, callback, suffix: str, max_val: float):
        """Callback genérico para sliders"""
        label = getattr(self, f"{key}_value_label", None)
        if label:
            if max_val <= 2:
                label.configure(text=f"{value:.2f}{suffix}")
            else:
                label.configure(text=f"{int(value)}{suffix}")
        callback(value)

    
    def setup_right_panel(self, parent):
        """Painel direito - RVMAT Preview + Configurações de Saída"""
        right_frame = tk.Frame(parent, bg=self.colors['bg_dark'])
        right_frame.grid(row=0, column=2, sticky="nsew", padx=(8, 0))
        
        # RVMAT Preview (parte superior)
        rvmat_section = tk.Frame(right_frame, bg=self.colors['bg_dark'])
        rvmat_section.pack(fill="both", expand=True, pady=(0, 10))
        
        # Título RVMAT
        rvmat_title = tk.Label(rvmat_section, text="📄 RVMAT Preview", 
                              font=("Segoe UI", 14, "bold"),
                              bg=self.colors['bg_dark'], fg=self.colors['text'])
        rvmat_title.pack(anchor="w", pady=(0, 10))
        
        # Card do RVMAT
        rvmat_card = tk.Frame(rvmat_section, bg=self.colors['bg_card'])
        rvmat_card.pack(fill="both", expand=True)
        
        # Text widget para preview do RVMAT
        text_frame = tk.Frame(rvmat_card, bg=self.colors['bg_card'])
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.rvmat_text = tk.Text(text_frame, font=("Consolas", 9),
                                  bg='#0f0f0f', fg=self.colors['text_muted'],
                                  insertbackground=self.colors['text'],
                                  relief="flat", wrap="none",
                                  highlightthickness=1,
                                  highlightbackground=self.colors['border'],
                                  height=12)
        self.rvmat_text.pack(side="left", fill="both", expand=True)
        
        scrollbar = tk.Scrollbar(text_frame, command=self.rvmat_text.yview)
        scrollbar.pack(side="right", fill="y")
        self.rvmat_text.configure(yscrollcommand=scrollbar.set)
        
        # Seção de Saída (parte inferior)
        self.setup_output_section(right_frame)
        
        # Preview inicial do RVMAT
        self.update_rvmat_preview()
    
    def setup_output_section(self, parent):
        """Seção de configurações de saída"""
        # Card de saída
        output_card = tk.Frame(parent, bg=self.colors['bg_card'])
        output_card.pack(fill="x")
        
        # Título
        output_title = tk.Label(output_card, text="📤 Configurações de Saída",
                               font=("Segoe UI", 12, "bold"),
                               bg=self.colors['bg_card'], fg=self.colors['text'])
        output_title.pack(anchor="w", padx=15, pady=(15, 10))
        
        content = tk.Frame(output_card, bg=self.colors['bg_card'])
        content.pack(fill="x", padx=15, pady=(0, 15))
        
        # Pasta de destino
        dest_frame = tk.Frame(content, bg=self.colors['bg_dark'])
        dest_frame.pack(fill="x", pady=(0, 10))
        
        dest_label = tk.Label(dest_frame, text="📁 Pasta de Destino",
                             font=("Segoe UI", 10, "bold"),
                             bg=self.colors['bg_dark'], fg=self.colors['text'])
        dest_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        dest_input = tk.Frame(dest_frame, bg=self.colors['bg_dark'])
        dest_input.pack(fill="x", padx=10, pady=(0, 10))
        
        self.dest_entry = tk.Entry(dest_input, font=("Segoe UI", 9),
                                   bg=self.colors['bg_card'], fg=self.colors['text'],
                                   insertbackground=self.colors['text'],
                                   relief="flat", highlightthickness=1,
                                   highlightbackground=self.colors['border'])
        self.dest_entry.pack(side="left", fill="x", expand=True, ipady=6)
        # Definir caminho padrão P:/ se existir
        default_path = "P:\\" if Path("P:\\").exists() else str(Path.home())
        self.dest_entry.insert(0, default_path)
        self.settings['output_directory'] = default_path
        
        dest_btn = tk.Button(dest_input, text="...", font=("Segoe UI", 9),
                            bg=self.colors['accent'], fg="white",
                            activebackground=self.colors['accent_hover'],
                            relief="flat", cursor="hand2", width=3,
                            command=self.browse_output_directory)
        dest_btn.pack(side="right", padx=(5, 0), ipady=4)
        
        # Resolução
        res_frame = tk.Frame(content, bg=self.colors['bg_dark'])
        res_frame.pack(fill="x", pady=(0, 10))
        
        res_label = tk.Label(res_frame, text="📐 Resolução",
                            font=("Segoe UI", 10, "bold"),
                            bg=self.colors['bg_dark'], fg=self.colors['text'])
        res_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        self.resolution_var = tk.StringVar(value="1024x1024")
        res_combo = ctk.CTkComboBox(res_frame,
                                    values=["512x512", "1024x1024", "2048x2048", "4096x4096"],
                                    variable=self.resolution_var,
                                    width=120)
        res_combo.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Opções PAA e RVMAT
        options_frame = tk.Frame(content, bg=self.colors['bg_dark'])
        options_frame.pack(fill="x", pady=(0, 10))
        
        options_label = tk.Label(options_frame, text="🎮 Opções de Conversão",
                                font=("Segoe UI", 10, "bold"),
                                bg=self.colors['bg_dark'], fg=self.colors['text'])
        options_label.pack(anchor="w", padx=10, pady=(10, 5))
        
        # Status do ImageToPAA
        paa_status = self.processor.get_imagetopaa_status()
        status_text = "✅ DayZ Tools OK" if paa_status['available'] else "❌ DayZ Tools não encontrado"
        status_color = self.colors['success'] if paa_status['available'] else self.colors['error']
        
        status_label = tk.Label(options_frame, text=status_text, font=("Segoe UI", 8),
                               bg=self.colors['bg_dark'], fg=status_color)
        status_label.pack(anchor="w", padx=10)
        
        self.convert_paa_var = tk.BooleanVar(value=False)
        paa_check = tk.Checkbutton(options_frame, text="Converter para .paa",
                                   variable=self.convert_paa_var,
                                   command=self.update_paa_setting,
                                   bg=self.colors['bg_dark'], fg=self.colors['text'],
                                   selectcolor=self.colors['bg_card'],
                                   activebackground=self.colors['bg_dark'],
                                   font=("Segoe UI", 9),
                                   state="normal" if paa_status['available'] else "disabled")
        paa_check.pack(anchor="w", padx=10)
        
        self.remove_png_var = tk.BooleanVar(value=True)
        png_check = tk.Checkbutton(options_frame, text="Remover .png após conversão",
                                   variable=self.remove_png_var,
                                   bg=self.colors['bg_dark'], fg=self.colors['text'],
                                   selectcolor=self.colors['bg_card'],
                                   activebackground=self.colors['bg_dark'],
                                   font=("Segoe UI", 9))
        png_check.pack(anchor="w", padx=10)
        
        self.generate_rvmat_var = tk.BooleanVar(value=False)
        rvmat_check = tk.Checkbutton(options_frame, text="Gerar arquivo RVMAT",
                                     variable=self.generate_rvmat_var,
                                     bg=self.colors['bg_dark'], fg=self.colors['text'],
                                     selectcolor=self.colors['bg_card'],
                                     activebackground=self.colors['bg_dark'],
                                     font=("Segoe UI", 9))
        rvmat_check.pack(anchor="w", padx=10, pady=(0, 10))
        
        # Botão converter
        self.convert_btn = tk.Button(options_frame, text="🚀 CONVERTER TEXTURAS",
                                     font=("Segoe UI", 12, "bold"),
                                     bg=self.colors['accent'], fg="white",
                                     activebackground=self.colors['accent_hover'],
                                     relief="flat", cursor="hand2",
                                     command=self.convert_textures)
        self.convert_btn.pack(fill="x", padx=10, ipady=12)
    
    def update_rvmat_preview(self):
        """Atualiza preview do RVMAT em tempo real"""
        try:
            # Gerar preview baseado nas configurações atuais
            preset = self.settings.get('material_preset', 'custom')
            
            # Obter valores de Fresnel do preset atual
            fresnel_n = self.settings.get('fresnel_n', 1.0)
            fresnel_k = self.settings.get('fresnel_k', 1.05)
            
            # Determinar nome base das texturas
            texture_name = "texture"
            if self.textures.get('base_color'):
                base_path = Path(self.textures['base_color'])
                texture_name = base_path.stem
                # Remover sufixos comuns
                suffixes = ['_BaseColor', '_base_color', '_diffuse', '_albedo', '_co']
                for suffix in suffixes:
                    if texture_name.lower().endswith(suffix.lower()):
                        texture_name = texture_name[:-len(suffix)]
                        break
            
            # Caminho das texturas (sem drive letter)
            output_dir = self.settings.get('output_directory', '')
            if output_dir:
                # Remover drive letter se presente
                if len(output_dir) >= 2 and output_dir[1] == ':':
                    texture_path = output_dir[2:].replace('\\', '/').lstrip('/')
                else:
                    texture_path = output_dir.replace('\\', '/')
                
                if texture_path:
                    texture_path = f"{texture_path}/{texture_name}".replace('/', '\\')
                else:
                    texture_path = texture_name
            else:
                texture_path = texture_name
            
            # Valores do material baseados no preset
            preset_data = self.material_presets.get_preset_by_key(preset)
            
            # Informações sobre as configurações atuais
            metalness_opacity = self.settings.get('metalness_opacity', 100)
            roughness_opacity = self.settings.get('roughness_opacity', 100)
            opacity_value = self.settings.get('opacity_value', 255)
            rgb = self.settings.get('base_color_rgb', {'r': 1.0, 'g': 1.0, 'b': 1.0})
            
            # Status das texturas carregadas
            textures_status = []
            for tex_type, path in self.textures.items():
                if path:
                    textures_status.append(f"✅ {tex_type.replace('_', ' ').title()}")
                else:
                    textures_status.append(f"❌ {tex_type.replace('_', ' ').title()}")
            
            rvmat_preview = f'''// ========================================
// ASKAL TOOLS - Gerador de Material
// ========================================
// Preset: {preset_data.get('name', 'Personalizado')}
// Material: {preset_data.get('fresnel_material', 'default')}
// Fresnel N={fresnel_n}, K={fresnel_k}
//
// Configurações Atuais:
// - Metalness Opacity: {metalness_opacity:.0f}%
// - Roughness Opacity: {roughness_opacity:.0f}%
// - Alpha Value: {opacity_value}
// - RGB Adjust: R={rgb['r']:.2f}, G={rgb['g']:.2f}, B={rgb['b']:.2f}
//
// Texturas:
{chr(10).join(f"// {status}" for status in textures_status)}
//
// Caminho de saída: {output_dir or 'Não definido'}
// ========================================

ambient[] = {{0.75,0.75,0.75,1}};
diffuse[] = {{0.75,0.75,0.75,1}};
forcedDiffuse[] = {{0,0,0,0}};
emmisive[] = {{0,0,0,1}};
specular[] = {{0.9,0.9,0.9,1}};
specularPower = 100;
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
}};'''
            
            self.rvmat_text.configure(state="normal")
            self.rvmat_text.delete("1.0", "end")
            self.rvmat_text.insert("1.0", rvmat_preview)
            self.rvmat_text.configure(state="disabled")
            
            # Syntax highlighting básico
            self.highlight_rvmat_syntax()
            
        except Exception as e:
            print(f"Erro ao atualizar RVMAT preview: {e}")
    
    def highlight_rvmat_syntax(self):
        """Aplica syntax highlighting ao RVMAT"""
        self.rvmat_text.tag_configure("keyword", foreground=self.colors['accent'])
        self.rvmat_text.tag_configure("string", foreground="#22c55e")
        self.rvmat_text.tag_configure("number", foreground="#f59e0b")
        self.rvmat_text.tag_configure("class", foreground="#a855f7")
        
        # Aplicar tags
        content = self.rvmat_text.get("1.0", "end")
        
        keywords = ["ambient", "diffuse", "forcedDiffuse", "emmisive", "specular", 
                   "specularPower", "PixelShaderID", "VertexShaderID", "texture", "uvSource"]
        
        for keyword in keywords:
            start = "1.0"
            while True:
                pos = self.rvmat_text.search(keyword, start, stopindex="end")
                if not pos:
                    break
                end = f"{pos}+{len(keyword)}c"
                self.rvmat_text.tag_add("keyword", pos, end)
                start = end
        
        # Classes
        import re
        for match in re.finditer(r'class\s+(\w+)', content):
            line = content[:match.start()].count('\n') + 1
            col = match.start() - content.rfind('\n', 0, match.start()) - 1
            self.rvmat_text.tag_add("class", f"{line}.{col}", f"{line}.{col + len(match.group())}")
    
    # ==================== CALLBACKS ====================
    
    def browse_texture(self, texture_type: str):
        """Abre diálogo para selecionar textura"""
        file_path = filedialog.askopenfilename(
            title=f"Selecionar {texture_type.replace('_', ' ').title()}",
            filetypes=[
                ("Imagens", "*.png *.jpg *.jpeg *.tga *.bmp"),
                ("PNG", "*.png"),
                ("JPEG", "*.jpg *.jpeg"),
                ("TGA", "*.tga"),
                ("Todos os arquivos", "*.*")
            ]
        )
        
        if file_path:
            self.load_texture(texture_type, file_path)
    
    def drop_texture(self, event, texture_type: str):
        """Processa arquivo arrastado"""
        files = self.root.tk.splitlist(event.data)
        if files:
            file_path = files[0].strip('{}')
            self.load_texture(texture_type, file_path)
    
    def load_texture(self, texture_type: str, file_path: str):
        """Carrega uma textura e atualiza thumbnail"""
        try:
            # Validar imagem
            img = Image.open(file_path)
            img.verify()
            img = Image.open(file_path)  # Reabrir após verify
            
            # Armazenar caminho
            self.textures[texture_type] = file_path
            
            # Criar thumbnail
            thumb_size = (100, 60)
            img.thumbnail(thumb_size, Image.Resampling.LANCZOS)
            
            # Extrair cor dominante para accent
            accent_color = self.extract_dominant_color(img)
            self.texture_accent_colors[texture_type] = accent_color
            
            # Atualizar canvas
            canvas = getattr(self, f"{texture_type}_canvas")
            canvas.delete("all")
            
            # Converter para PhotoImage
            photo = ImageTk.PhotoImage(img)
            self.texture_thumbnails[texture_type] = photo
            
            # Posicionar thumbnail à esquerda
            canvas.create_image(55, 28, image=photo, anchor="center")
            
            # Adicionar nome do arquivo à direita
            filename = Path(file_path).name
            if len(filename) > 18:
                filename = filename[:15] + "..."
            canvas.create_text(170, 33, text=filename, 
                             fill=self.colors['text'],
                             font=("Segoe UI", 8),
                             anchor="center")
            
            # Atualizar cor do card baseado na imagem
            card = getattr(self, f"{texture_type}_card", None)
            drop_frame = getattr(self, f"{texture_type}_drop_frame", None)
            
            if drop_frame and accent_color:
                drop_frame.configure(bg=accent_color)
            
            # Atualizar preview
            if self.real_time_preview.get():
                self.generate_preview()
            
            # Atualizar RVMAT com novo nome de textura
            self.update_rvmat_preview()
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar imagem: {str(e)}")
    
    def extract_dominant_color(self, img: Image.Image) -> str:
        """Extrai cor dominante de uma imagem"""
        try:
            # Reduzir para análise
            small = img.copy()
            small.thumbnail((50, 50))
            
            if small.mode != 'RGB':
                small = small.convert('RGB')
            
            # Pegar pixels
            pixels = list(small.getdata())
            
            # Calcular média
            r = sum(p[0] for p in pixels) // len(pixels)
            g = sum(p[1] for p in pixels) // len(pixels)
            b = sum(p[2] for p in pixels) // len(pixels)
            
            # Aumentar saturação
            h, l, s = colorsys.rgb_to_hls(r/255, g/255, b/255)
            s = min(1.0, s * 1.5)
            l = max(0.3, min(0.6, l))
            r, g, b = colorsys.hls_to_rgb(h, l, s)
            
            return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"
        except:
            return self.colors['accent']
    
    def darken_color(self, hex_color: str, factor: float) -> str:
        """Escurece uma cor hex"""
        try:
            hex_color = hex_color.lstrip('#')
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            r = int(r * factor)
            g = int(g * factor)
            b = int(b * factor)
            
            return f"#{r:02x}{g:02x}{b:02x}"
        except:
            return self.colors['bg_card']

    
    def update_rgb(self, color: str, value: float):
        """Atualiza configuração RGB"""
        self.settings['base_color_rgb'][color] = float(value)
        if self.real_time_preview.get():
            self.generate_preview()
        # Atualizar RVMAT em tempo real
        self.update_rvmat_preview()
    
    def update_invert_green(self):
        """Atualiza inversão do canal verde"""
        self.settings['normal_invert_green'] = self.invert_green_var.get()
        if self.real_time_preview.get():
            self.generate_preview()
        # Atualizar RVMAT em tempo real
        self.update_rvmat_preview()
    
    def update_opacity(self, key: str, value: float):
        """Atualiza opacidade"""
        self.settings[key] = float(value)
        if self.real_time_preview.get():
            self.generate_preview()
        # Atualizar RVMAT em tempo real
        self.update_rvmat_preview()
    
    def update_metal_fill(self):
        """Atualiza Metal Fill"""
        enabled = self.metal_override_var.get()
        self.settings['metal_override_enabled'] = enabled
        
        slider = getattr(self, "metal_override_slider", None)
        if slider:
            slider.configure(state="normal" if enabled else "disabled")
        
        if self.real_time_preview.get():
            self.generate_preview()
        # Atualizar RVMAT em tempo real
        self.update_rvmat_preview()
    
    def update_metal_fill_value(self, value: float):
        """Atualiza valor do Metal Fill"""
        self.settings['metal_override_value'] = int(value)
        if self.real_time_preview.get():
            self.generate_preview()
        # Atualizar RVMAT em tempo real
        self.update_rvmat_preview()
    
    def update_gloss_fill(self):
        """Atualiza Gloss Fill"""
        enabled = self.gloss_override_var.get()
        self.settings['gloss_override_enabled'] = enabled
        
        slider = getattr(self, "gloss_override_slider", None)
        if slider:
            slider.configure(state="normal" if enabled else "disabled")
        
        if self.real_time_preview.get():
            self.generate_preview()
        # Atualizar RVMAT em tempo real
        self.update_rvmat_preview()
    
    def update_gloss_fill_value(self, value: float):
        """Atualiza valor do Gloss Fill"""
        self.settings['gloss_override_value'] = int(value)
        if self.real_time_preview.get():
            self.generate_preview()
        # Atualizar RVMAT em tempo real
        self.update_rvmat_preview()
    
    def update_opacity_value(self, value: float):
        """Atualiza valor da opacidade SMDI"""
        self.settings['opacity_value'] = int(value)
        # Atualizar RVMAT em tempo real
        self.update_rvmat_preview()
    
    def on_preset_changed(self, preset_name: str):
        """Callback quando preset muda"""
        preset_key = self.material_presets.get_preset_key_by_name(preset_name)
        self.settings = self.material_presets.apply_preset_to_settings(self.settings, preset_key)
        
        # Atualizar interface com os novos valores
        self.update_ui_from_settings()
        
        # Atualizar preview do RVMAT
        self.update_rvmat_preview()
        
        # Atualizar preview das texturas se ativo
        if self.real_time_preview.get():
            self.generate_preview()
    
    def update_ui_from_settings(self):
        """Atualiza interface baseado nas configurações atuais"""
        try:
            # Atualizar sliders RGB
            rgb = self.settings['base_color_rgb']
            if hasattr(self, 'rgb_r_slider'):
                self.rgb_r_slider.set(rgb['r'])
                self.rgb_r_value_label.configure(text=f"{rgb['r']:.2f}")
            if hasattr(self, 'rgb_g_slider'):
                self.rgb_g_slider.set(rgb['g'])
                self.rgb_g_value_label.configure(text=f"{rgb['g']:.2f}")
            if hasattr(self, 'rgb_b_slider'):
                self.rgb_b_slider.set(rgb['b'])
                self.rgb_b_value_label.configure(text=f"{rgb['b']:.2f}")
            
            # Atualizar opacidades
            if hasattr(self, 'metalness_opacity_slider'):
                self.metalness_opacity_slider.set(self.settings['metalness_opacity'])
                self.metalness_opacity_value_label.configure(text=f"{int(self.settings['metalness_opacity'])}%")
            
            if hasattr(self, 'roughness_opacity_slider'):
                self.roughness_opacity_slider.set(self.settings['roughness_opacity'])
                self.roughness_opacity_value_label.configure(text=f"{int(self.settings['roughness_opacity'])}%")
            
            # Atualizar valor de opacity SMDI
            if hasattr(self, 'opacity_slider'):
                self.opacity_slider.set(self.settings['opacity_value'])
                self.opacity_value_label.configure(text=f"{int(self.settings['opacity_value'])}")
                
        except Exception as e:
            print(f"Erro ao atualizar UI: {e}")
    
    def update_paa_setting(self):
        """Atualiza configuração PAA"""
        self.settings['convert_to_paa'] = self.convert_paa_var.get()
        # Atualizar RVMAT em tempo real
        self.update_rvmat_preview()
    
    def browse_output_directory(self):
        """Seleciona pasta de destino"""
        directory = filedialog.askdirectory(
            title="Selecionar Pasta de Destino",
            initialdir="P:\\" if Path("P:\\").exists() else str(Path.home())
        )
        
        if directory:
            self.dest_entry.delete(0, "end")
            self.dest_entry.insert(0, directory)
            self.settings['output_directory'] = directory
            # Atualizar RVMAT em tempo real com novo caminho
            self.update_rvmat_preview()
    
    def generate_preview(self):
        """Gera preview das texturas"""
        def preview_thread():
            try:
                previews = self.preview_generator.generate_previews(
                    self.textures, 
                    self.settings,
                    preview_size=150
                )
                self.root.after(0, lambda: self.update_preview_ui(previews))
            except Exception as e:
                print(f"Erro no preview: {e}")
        
        threading.Thread(target=preview_thread, daemon=True).start()
    
    def update_preview_ui(self, previews: Dict):
        """Atualiza UI com previews"""
        for preview_type, img_array in previews.items():
            if img_array is not None:
                try:
                    img = Image.fromarray(img_array)
                    photo = ImageTk.PhotoImage(img)
                    
                    canvas = getattr(self, f"{preview_type}_canvas", None)
                    if canvas:
                        canvas.delete("all")
                        canvas.create_image(75, 75, image=photo, anchor="center")
                        setattr(self, f"{preview_type}_photo", photo)
                except Exception as e:
                    print(f"Erro ao atualizar preview {preview_type}: {e}")
    
    def convert_textures(self):
        """Converte as texturas"""
        # Verificar texturas
        required = ['base_color', 'normal_map', 'metalness', 'roughness']
        missing = [t for t in required if not self.textures.get(t)]
        
        if missing:
            messagebox.showwarning(
                "Texturas Faltando", 
                f"Carregue as texturas:\n{', '.join(missing)}"
            )
            return
        
        # Verificar/criar pasta de destino
        output_dir = self.dest_entry.get().strip()
        if output_dir:
            if not Path(output_dir).exists():
                try:
                    Path(output_dir).mkdir(parents=True, exist_ok=True)
                except Exception as e:
                    messagebox.showerror("Erro", f"Não foi possível criar pasta:\n{e}")
                    return
            self.settings['output_directory'] = output_dir
        else:
            first_texture = next(iter(self.textures.values()))
            self.settings['output_directory'] = str(Path(first_texture).parent)
        
        # Configurações
        self.settings['convert_to_paa'] = self.convert_paa_var.get()
        self.settings['remove_png_after_paa'] = self.remove_png_var.get()
        self.settings['generate_rvmat'] = self.generate_rvmat_var.get()
        self.settings['output_resolution'] = int(self.resolution_var.get().split('x')[0])
        
        # Verificar PAA
        if self.settings['convert_to_paa'] and not self.processor.is_paa_conversion_available():
            result = messagebox.askyesno(
                "ImageToPAA não encontrado",
                "Conversão PAA solicitada mas ImageToPAA não encontrado.\n\nContinuar gerando apenas .png?"
            )
            if not result:
                return
            self.settings['convert_to_paa'] = False
        
        # Desabilitar botão
        self.convert_btn.configure(state="disabled", text="⏳ Convertendo...")
        
        def convert_thread():
            try:
                output_files = self.processor.process_textures(self.textures, self.settings)
                self.root.after(0, lambda: self.show_result(output_files))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Erro", f"Erro na conversão:\n{e}"))
            finally:
                self.root.after(0, lambda: self.convert_btn.configure(
                    state="normal", text="🚀 CONVERTER TEXTURAS"))
        
        threading.Thread(target=convert_thread, daemon=True).start()
    
    def show_result(self, output_files: list):
        """Mostra resultado da conversão"""
        if output_files:
            files_list = '\n'.join([f"• {Path(f).name}" for f in output_files])
            output_dir = self.settings.get('output_directory', '')
            
            message = f"✅ Texturas convertidas!\n\nArquivos:\n{files_list}"
            if output_dir:
                message += f"\n\nPasta: {output_dir}"
            
            messagebox.showinfo("Sucesso", message)
        else:
            messagebox.showerror("Erro", "Nenhum arquivo gerado.")
    
    def run(self):
        """Executa a aplicação"""
        self.root.mainloop()
