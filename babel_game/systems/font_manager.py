"""
フォント管理システム
Font Management System
"""

import os
import pyxel
from typing import Optional, Dict


class FontManager:
    """フォント管理クラス"""
    
    def __init__(self):
        self.fonts: Dict[str, pyxel.Font] = {}
        self.default_font: Optional[pyxel.Font] = None
        self.current_font: Optional[pyxel.Font] = None
        
    def load_font(self, name: str, filepath: str) -> bool:
        """BDFフォントを読み込み"""
        try:
            # ファイルパスの解決
            if not os.path.isabs(filepath):
                base_dir = os.path.dirname(os.path.dirname(__file__))
                filepath = os.path.join(base_dir, filepath)
            
            if not os.path.exists(filepath):
                print(f"Font file not found: {filepath}")
                return False
            
            # Pyxel 2.xのFont機能を使用
            font = pyxel.Font(filepath)
            self.fonts[name] = font
            
            # デフォルトフォントとして設定
            if self.default_font is None:
                self.default_font = font
                self.current_font = font
            
            print(f"Loaded font: {name} from {filepath}")
            return True
            
        except Exception as e:
            print(f"Failed to load font {name}: {e}")
            return False
    
    def set_current_font(self, name: str) -> bool:
        """現在使用するフォントを設定"""
        if name in self.fonts:
            self.current_font = self.fonts[name]
            return True
        return False
    
    def get_font(self, name: str = None) -> Optional[pyxel.Font]:
        """指定された名前のフォントを取得"""
        if name and name in self.fonts:
            return self.fonts[name]
        return self.current_font
    
    def draw_text(self, x: int, y: int, text: str, color: int, font_name: str = None):
        """フォントを使用してテキストを描画"""
        font = self.get_font(font_name)
        if font:
            pyxel.text(x, y, text, color, font)
        else:
            # フォールバック：標準フォント
            pyxel.text(x, y, text, color)
    
    def load_default_fonts(self):
        """デフォルトのフォントを読み込み"""
        # 日本語フォント
        self.load_font("japanese", "assets/fonts/umplus_j10r.bdf")
        
        # 他のフォントがあれば追加
        # self.load_font("english", "assets/fonts/english.bdf")
    
    def get_text_width(self, text: str, font_name: str = None) -> int:
        """テキストの幅を取得"""
        font = self.get_font(font_name)
        if font:
            # BDFフォントの場合、文字幅は固定（10ピクセル）と仮定
            # 実際のフォントメトリクスに基づいて調整が必要
            return len(text) * 10
        else:
            # 標準フォント（4ピクセル幅）
            return len(text) * 4
    
    def get_text_height(self, font_name: str = None) -> int:
        """テキストの高さを取得"""
        font = self.get_font(font_name)
        if font:
            # BDFフォントの場合、高さは10ピクセルと仮定
            return 10
        else:
            # 標準フォント
            return 6


# グローバルフォントマネージャーインスタンス
font_manager = FontManager()