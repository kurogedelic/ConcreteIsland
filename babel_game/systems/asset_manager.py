"""
アセット管理システム
Asset Management System
"""

import os
from typing import Dict, Optional, Tuple
from PIL import Image
import pyxel
from config.game_config import GameConfig


class AssetManager:
    """アセット管理クラス"""
    
    def __init__(self):
        self.sprites: Dict[str, Dict] = {}
        self.images: Dict[str, Image.Image] = {}
        self.pyxel_colors: Dict[Tuple[int, int, int], int] = {}
        self._initialize_pyxel_palette()
    
    def _initialize_pyxel_palette(self):
        """Pyxel標準パレットを初期化"""
        # Pyxel標準16色パレット
        standard_palette = [
            (0, 0, 0),       # 0: 黒
            (29, 43, 83),    # 1: 暗青
            (126, 37, 83),   # 2: 暗紫
            (0, 135, 81),    # 3: 暗緑
            (171, 82, 54),   # 4: 茶色
            (95, 87, 79),    # 5: 暗灰色
            (194, 195, 199), # 6: 明灰色
            (255, 241, 232), # 7: 白
            (255, 0, 77),    # 8: 赤
            (255, 163, 0),   # 9: オレンジ
            (255, 236, 39),  # 10: 黄色
            (0, 228, 54),    # 11: 緑
            (41, 173, 255),  # 12: 青
            (131, 118, 156), # 13: インディゴ
            (255, 119, 168), # 14: ピンク（透過色として使用）
            (255, 204, 170)  # 15: ベージュ
        ]
        
        for i, color in enumerate(standard_palette):
            self.pyxel_colors[color] = i
    
    def load_png_sprite(self, name: str, filepath: str, transparent_color: Tuple[int, int, int] = (255, 0, 255)) -> bool:
        """PNGスプライトを読み込み"""
        try:
            # PILでPNG読み込み
            img = Image.open(filepath).convert('RGBA')
            self.images[name] = img
            
            # スプライト情報を保存
            sprite_info = {
                'width': img.width,
                'height': img.height,
                'transparent_color': transparent_color,
                'pyxel_data': self._convert_to_pyxel_data(img, transparent_color)
            }
            
            self.sprites[name] = sprite_info
            return True
            
        except Exception as e:
            print(f"Failed to load sprite {name}: {e}")
            return False
    
    def _convert_to_pyxel_data(self, img: Image.Image, transparent_color: Tuple[int, int, int]) -> list:
        """PIL画像をPyxelデータに変換"""
        width, height = img.size
        pyxel_data = []
        
        for y in range(height):
            row = []
            for x in range(width):
                r, g, b, a = img.getpixel((x, y))
                
                # 透明度処理
                if a < 128:  # 半透明以下は透過
                    color_index = 14  # ピンク（透過色）
                else:
                    # 最近傍色を探す
                    color_index = self._find_nearest_color((r, g, b))
                
                row.append(color_index)
            pyxel_data.append(row)
        
        return pyxel_data
    
    def _find_nearest_color(self, rgb: Tuple[int, int, int]) -> int:
        """RGBから最も近いPyxel色を探す"""
        if rgb in self.pyxel_colors:
            return self.pyxel_colors[rgb]
        
        min_distance = float('inf')
        nearest_index = 0
        
        for palette_rgb, index in self.pyxel_colors.items():
            # 色距離計算（簡易版）
            distance = sum((a - b) ** 2 for a, b in zip(rgb, palette_rgb))
            if distance < min_distance:
                min_distance = distance
                nearest_index = index
        
        return nearest_index
    
    def draw_sprite(self, name: str, x: int, y: int, scale: float = 1.0) -> bool:
        """スプライトを描画"""
        if name not in self.sprites:
            return False
        
        sprite = self.sprites[name]
        pyxel_data = sprite['pyxel_data']
        width = sprite['width']
        height = sprite['height']
        
        # スケール適用
        if scale != 1.0:
            self._draw_sprite_scaled(pyxel_data, x, y, width, height, scale)
        else:
            self._draw_sprite_normal(pyxel_data, x, y, width, height)
        
        return True
    
    def _draw_sprite_normal(self, pyxel_data: list, x: int, y: int, width: int, height: int):
        """通常スプライト描画"""
        for py in range(height):
            for px in range(width):
                color = pyxel_data[py][px]
                if color != 14:  # 透過色でなければ描画
                    pyxel.pset(x + px, y + py, color)
    
    def _draw_sprite_scaled(self, pyxel_data: list, x: int, y: int, width: int, height: int, scale: float):
        """スケール適用スプライト描画"""
        scaled_width = int(width * scale)
        scaled_height = int(height * scale)
        
        for py in range(scaled_height):
            for px in range(scaled_width):
                # 元画像での対応ピクセル座標
                orig_x = int(px / scale)
                orig_y = int(py / scale)
                
                if orig_x < width and orig_y < height:
                    color = pyxel_data[orig_y][orig_x]
                    if color != 14:  # 透過色でなければ描画
                        pyxel.pset(x + px, y + py, color)
    
    def create_test_sprite(self, name: str, width: int = 32, height: int = 32, color: int = 3):
        """テスト用スプライト作成"""
        pyxel_data = []
        for y in range(height):
            row = []
            for x in range(width):
                # 簡単なパターン（枠付き四角）
                if x == 0 or x == width-1 or y == 0 or y == height-1:
                    row.append(0)  # 黒枠
                elif x < 4 or x >= width-4 or y < 4 or y >= height-4:
                    row.append(color)  # メイン色
                else:
                    row.append(14)  # 透過
            pyxel_data.append(row)
        
        sprite_info = {
            'width': width,
            'height': height,
            'transparent_color': (255, 0, 255),
            'pyxel_data': pyxel_data
        }
        
        self.sprites[name] = sprite_info
    
    def get_sprite_info(self, name: str) -> Optional[Dict]:
        """スプライト情報を取得"""
        return self.sprites.get(name)
    
    def has_sprite(self, name: str) -> bool:
        """スプライトが存在するかチェック"""
        return name in self.sprites
    
    def load_all_assets(self):
        """全アセットを読み込み"""
        # アセットディレクトリパス
        base_dir = os.path.dirname(os.path.dirname(__file__))
        assets_dir = os.path.join(base_dir, "assets")
        
        # タイルスプライトを読み込み
        tiles_dir = os.path.join(assets_dir, "tiles")
        if os.path.exists(tiles_dir):
            self._load_png_sprites_from_dir(tiles_dir, "tile_")
        
        # UIアイコンを読み込み
        ui_dir = os.path.join(assets_dir, "ui")
        if os.path.exists(ui_dir):
            self._load_png_sprites_from_dir(ui_dir, "icon_")
        
        # フォールバック用スプライト（PNGが見つからない場合）
        if len(self.sprites) == 0:
            self._create_fallback_sprites()
        
        # 海岸線スプライト生成
        self._create_coastline_sprites()
        
        print(f"Loaded {len(self.sprites)} sprites")
    
    def _load_png_sprites_from_dir(self, directory: str, prefix: str = ""):
        """指定ディレクトリからPNGスプライトを一括読み込み"""
        if not os.path.exists(directory):
            print(f"Directory not found: {directory}")
            return
        
        for filename in os.listdir(directory):
            if filename.endswith('.png'):
                sprite_name = prefix + filename[:-4].replace('-', '_')
                filepath = os.path.join(directory, filename)
                if self.load_png_sprite(sprite_name, filepath):
                    print(f"Loaded: {sprite_name}")
    
    def _create_fallback_sprites(self):
        """フォールバック用スプライトを作成"""
        self.create_test_sprite("building_house", 32, 32, GameConfig.COLOR_GRASS)
        self.create_test_sprite("building_factory", 32, 32, GameConfig.COLOR_DIRT)
        self.create_test_sprite("building_shop", 32, 32, GameConfig.COLOR_WATER)
        self.create_test_sprite("terrain_grass", 32, 16, GameConfig.COLOR_GRASS)
        self.create_test_sprite("terrain_dirt", 32, 16, GameConfig.COLOR_DIRT)
        self.create_test_sprite("terrain_water", 32, 16, GameConfig.COLOR_WATER)
    
    def _create_coastline_sprites(self):
        """海岸線スプライトを生成"""
        from systems.coastline_generator import CoastlineGenerator
        
        coastline_gen = CoastlineGenerator()
        coastline_gen.create_coastline_sprites(self)
        print("Created coastline sprites")
    
    def create_sprite_from_data(self, name: str, sprite_data: list):
        """データから直接スプライトを作成"""
        height = len(sprite_data)
        width = len(sprite_data[0]) if height > 0 else 0
        
        if width == 0 or height == 0:
            return
        
        # スプライト情報を保存
        sprite_info = {
            'width': width,
            'height': height,
            'transparent_color': (255, 0, 255),
            'pyxel_data': sprite_data
        }
        
        self.sprites[name] = sprite_info
        print(f"Created sprite from data: {name} ({width}x{height})")
    
    def clear_all_assets(self):
        """全アセットをクリア"""
        self.sprites.clear()
        self.images.clear()


# グローバルアセットマネージャーインスタンス
asset_manager = AssetManager()