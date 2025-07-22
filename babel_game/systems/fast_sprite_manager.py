"""
高速スプライト管理システム
Fast Sprite Management System

既存のasset_managerと並行動作し、段階的に移行可能
"""

import os
import json
import time
import gzip
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from PIL import Image
import pyxel
from config.game_config import GameConfig


class SpriteAtlas:
    """スプライトアトラス（スプライトシート）管理"""
    
    def __init__(self, atlas_size: int = 1024):
        self.atlas_size = atlas_size
        self.atlas_data = [[0 for _ in range(atlas_size)] for _ in range(atlas_size)]
        self.sprite_map: Dict[str, Dict[str, Any]] = {}
        self.current_x = 0
        self.current_y = 0
        self.row_height = 0
        
        # Pyxel標準16色パレット
        self.pyxel_palette = [
            (0, 0, 0), (29, 43, 83), (126, 37, 83), (0, 135, 81),
            (171, 82, 54), (95, 87, 79), (194, 195, 199), (255, 241, 232),
            (255, 0, 77), (255, 163, 0), (255, 236, 39), (0, 228, 54),
            (41, 173, 255), (131, 118, 156), (255, 119, 168), (255, 204, 170)
        ]
        
        # 色変換キャッシュ
        self.color_cache: Dict[Tuple[int, int, int], int] = {}
        for i, color in enumerate(self.pyxel_palette):
            self.color_cache[color] = i
    
    def add_sprite(self, name: str, image_data: List[List[int]], width: int, height: int) -> bool:
        """スプライトをアトラスに追加"""
        # アトラスに収まるかチェック
        if self.current_x + width > self.atlas_size:
            # 次の行に移動
            self.current_x = 0
            self.current_y += self.row_height
            self.row_height = 0
        
        if self.current_y + height > self.atlas_size:
            print(f"Atlas full, cannot add sprite {name}")
            return False
        
        # スプライトデータをアトラスにコピー
        for y in range(height):
            for x in range(width):
                if y < len(image_data) and x < len(image_data[y]):
                    self.atlas_data[self.current_y + y][self.current_x + x] = image_data[y][x]
        
        # スプライト位置を記録
        self.sprite_map[name] = {
            'x': self.current_x,
            'y': self.current_y,
            'width': width,
            'height': height
        }
        
        # 次のスプライト位置を更新
        self.current_x += width
        self.row_height = max(self.row_height, height)
        
        return True
    
    def get_sprite_info(self, name: str) -> Optional[Dict[str, Any]]:
        """スプライト情報を取得"""
        return self.sprite_map.get(name)
    
    def save_atlas(self, filepath: str):
        """アトラスをファイルに保存（圧縮）"""
        atlas_data = {
            'atlas_size': self.atlas_size,
            'atlas_data': self.atlas_data,
            'sprite_map': self.sprite_map,
            'palette': self.pyxel_palette
        }
        
        # JSON → gzip圧縮で保存
        json_data = json.dumps(atlas_data).encode('utf-8')
        compressed_data = gzip.compress(json_data)
        
        with open(filepath, 'wb') as f:
            f.write(compressed_data)
        
        print(f"Atlas saved: {filepath} ({len(compressed_data)} bytes)")
    
    def load_atlas(self, filepath: str) -> bool:
        """圧縮されたアトラスを読み込み"""
        try:
            with open(filepath, 'rb') as f:
                compressed_data = f.read()
            
            json_data = gzip.decompress(compressed_data).decode('utf-8')
            atlas_data = json.loads(json_data)
            
            self.atlas_size = atlas_data['atlas_size']
            self.atlas_data = atlas_data['atlas_data']
            self.sprite_map = atlas_data['sprite_map']
            self.pyxel_palette = atlas_data['palette']
            
            print(f"Atlas loaded: {filepath} ({len(self.sprite_map)} sprites)")
            return True
            
        except Exception as e:
            print(f"Failed to load atlas: {e}")
            return False


class FastSpriteManager:
    """高速スプライト管理クラス"""
    
    def __init__(self):
        self.atlas = SpriteAtlas()
        self.atlas_file = "babel_game/assets/sprites.atlas"
        self.atlas_loaded = False
        
        # 従来システムとの互換性フラグ
        self.use_fast_sprites = True
        self.fallback_manager = None  # asset_managerの参照（後で設定）
    
    def set_fallback_manager(self, asset_manager):
        """既存asset_managerをフォールバックとして設定"""
        self.fallback_manager = asset_manager
    
    def build_atlas_from_assets(self, assets_dir: str = "babel_game/assets"):
        """アセットディレクトリからアトラスを構築"""
        print("Building sprite atlas...")
        start_time = time.time()
        
        # タイルとUIアイコンを処理
        tile_dir = Path(assets_dir) / "tiles"
        ui_dir = Path(assets_dir) / "ui"
        
        sprite_count = 0
        
        # タイルスプライト
        if tile_dir.exists():
            for png_file in tile_dir.glob("*.png"):
                if self._process_png_file(png_file, "tile"):
                    sprite_count += 1
        
        # UIアイコン
        if ui_dir.exists():
            for png_file in ui_dir.glob("*.png"):
                if self._process_png_file(png_file, "ui"):
                    sprite_count += 1
        
        # アトラスを保存
        self.atlas.save_atlas(self.atlas_file)
        
        build_time = time.time() - start_time
        print(f"Atlas built: {sprite_count} sprites in {build_time:.2f}s")
        
        return True
    
    def _process_png_file(self, png_file: Path, category: str) -> bool:
        """PNGファイルを処理してアトラスに追加"""
        try:
            # PIL で画像読み込み
            img = Image.open(png_file).convert('RGBA')
            
            # Pyxelデータに変換（64色→16色ディザリング）
            pyxel_data = self._convert_with_dithering(img)
            
            # スプライト名を生成
            sprite_name = f"{category}_{png_file.stem}"
            
            # アトラスに追加
            return self.atlas.add_sprite(sprite_name, pyxel_data, img.width, img.height)
            
        except Exception as e:
            print(f"Failed to process {png_file}: {e}")
            return False
    
    def _convert_with_dithering(self, img: Image.Image) -> List[List[int]]:
        """64色画像を16色にディザリング変換"""
        width, height = img.size
        result = []
        
        # Floyd-Steinberg ディザリング
        error_buffer = [[0, 0, 0] for _ in range(width + 2)]
        
        for y in range(height):
            row = []
            next_error = [0, 0, 0]
            
            for x in range(width):
                r, g, b, a = img.getpixel((x, y))
                
                # 透明度処理
                if a < 128:
                    row.append(14)  # 透過色
                    continue
                
                # 誤差を加算
                r = max(0, min(255, r + error_buffer[x][0]))
                g = max(0, min(255, g + error_buffer[x][1]))
                b = max(0, min(255, b + error_buffer[x][2]))
                
                # 最近傍色を探す
                color_index = self._find_nearest_pyxel_color((r, g, b))
                row.append(color_index)
                
                # 誤差を計算
                actual_color = self.atlas.pyxel_palette[color_index]
                error_r = r - actual_color[0]
                error_g = g - actual_color[1]
                error_b = b - actual_color[2]
                
                # 誤差拡散（Floyd-Steinberg）
                if x < width - 1:
                    error_buffer[x + 1][0] += error_r * 7 // 16
                    error_buffer[x + 1][1] += error_g * 7 // 16
                    error_buffer[x + 1][2] += error_b * 7 // 16
                
                next_error[0] += error_r * 5 // 16
                next_error[1] += error_g * 5 // 16
                next_error[2] += error_b * 5 // 16
                
                if x > 0:
                    next_error[0] += error_r * 3 // 16
                    next_error[1] += error_g * 3 // 16
                    next_error[2] += error_b * 3 // 16
                
                if x < width - 1:
                    next_error[0] += error_r * 1 // 16
                    next_error[1] += error_g * 1 // 16
                    next_error[2] += error_b * 1 // 16
            
            result.append(row)
            error_buffer = [[0, 0, 0] for _ in range(width + 2)]
            error_buffer[0] = next_error[:]
        
        return result
    
    def _find_nearest_pyxel_color(self, rgb: Tuple[int, int, int]) -> int:
        """最近傍Pyxel色を探す（キャッシュ付き）"""
        if rgb in self.atlas.color_cache:
            return self.atlas.color_cache[rgb]
        
        min_distance = float('inf')
        nearest_index = 0
        
        for i, palette_color in enumerate(self.atlas.pyxel_palette):
            # ユークリッド距離
            distance = sum((a - b) ** 2 for a, b in zip(rgb, palette_color))
            if distance < min_distance:
                min_distance = distance
                nearest_index = i
        
        # キャッシュに保存
        self.atlas.color_cache[rgb] = nearest_index
        return nearest_index
    
    def load_sprites(self) -> bool:
        """スプライトを読み込み（アトラス優先、フォールバック対応）"""
        # アトラスが存在するかチェック
        if Path(self.atlas_file).exists():
            print("Loading sprite atlas...")
            start_time = time.time()
            
            if self.atlas.load_atlas(self.atlas_file):
                self.atlas_loaded = True
                load_time = time.time() - start_time
                print(f"Atlas loaded in {load_time:.2f}s")
                return True
        
        # アトラスが無い場合は構築
        print("Sprite atlas not found, building...")
        return self.build_atlas_from_assets()
    
    def has_sprite(self, sprite_name: str) -> bool:
        """スプライトが存在するかチェック"""
        if self.use_fast_sprites and self.atlas_loaded:
            return sprite_name in self.atlas.sprite_map
        elif self.fallback_manager:
            return self.fallback_manager.has_sprite(sprite_name)
        return False
    
    def draw_sprite(self, sprite_name: str, x: int, y: int):
        """スプライトを描画"""
        if self.use_fast_sprites and self.atlas_loaded:
            self._draw_from_atlas(sprite_name, x, y)
        elif self.fallback_manager:
            # 既存システムにフォールバック
            self.fallback_manager.draw_sprite(sprite_name, x, y)
    
    def _draw_from_atlas(self, sprite_name: str, x: int, y: int):
        """アトラスからスプライトを描画"""
        sprite_info = self.atlas.get_sprite_info(sprite_name)
        if not sprite_info:
            return
        
        # アトラスからピクセル単位で描画
        atlas_x = sprite_info['x']
        atlas_y = sprite_info['y']
        width = sprite_info['width']
        height = sprite_info['height']
        
        for dy in range(height):
            for dx in range(width):
                color = self.atlas.atlas_data[atlas_y + dy][atlas_x + dx]
                if color != 14:  # 透過色以外
                    pyxel.pset(x + dx, y + dy, color)
    
    def get_sprite_info(self, sprite_name: str) -> Optional[Dict[str, Any]]:
        """スプライト情報を取得"""
        if self.use_fast_sprites and self.atlas_loaded:
            return self.atlas.get_sprite_info(sprite_name)
        return None
    
    def is_atlas_outdated(self, assets_dir: str = "babel_game/assets") -> bool:
        """アトラスが古くなっているかチェック"""
        if not Path(self.atlas_file).exists():
            return True
        
        atlas_mtime = Path(self.atlas_file).stat().st_mtime
        
        # アセットファイルの最新更新時刻をチェック
        for asset_path in [Path(assets_dir) / "tiles", Path(assets_dir) / "ui"]:
            if asset_path.exists():
                for png_file in asset_path.glob("*.png"):
                    if png_file.stat().st_mtime > atlas_mtime:
                        return True
        
        return False
    
    def rebuild_if_needed(self, assets_dir: str = "babel_game/assets") -> bool:
        """必要に応じてアトラスを再構築"""
        if self.is_atlas_outdated(assets_dir):
            print("Assets updated, rebuilding atlas...")
            return self.build_atlas_from_assets(assets_dir)
        return True


# グローバルインスタンス
fast_sprite_manager = FastSpriteManager()