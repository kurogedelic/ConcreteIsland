"""
等角投影グリッドシステム
Isometric Grid System
"""

import pyxel
import math
from config.game_config import GameConfig
from systems.coastline_generator import CoastlineGenerator
from systems.animation_manager import animation_manager
from systems.viewport_culling import ViewportCulling
from systems.terrain_generator import terrain_generator, TerrainGenConfig, MapType


class GridSystem:
    """等角投影グリッドを管理するクラス"""
    
    def __init__(self):
        self.grid_width = GameConfig.GRID_WIDTH
        self.grid_height = GameConfig.GRID_HEIGHT
        self.cell_size = GameConfig.CELL_SIZE
        
        # カメラ設定
        self.camera_x = 0
        self.camera_y = 0
        self.zoom = 1.0
        
        # グリッド表示設定
        self.show_grid = True
        self.grid_color = GameConfig.COLOR_ROAD
        
        # 地形データ（テスト用）
        self.terrain = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # 海岸線生成システム
        self.coastline_generator = CoastlineGenerator()
        self.coastline_sprites = {}  # (x, y) -> sprite_name
        
        # 視界カリングシステム
        self.viewport_culling = ViewportCulling()
        
        # 起動時に島を手続き生成（失敗時は従来のデフォルト地形）
        try:
            self.generate_procedural_terrain(MapType.ISLAND)
        except Exception as e:
            print(f"島の生成に失敗、デフォルト地形を使用: {e}")
            self._generate_test_terrain()
        self._generate_coastlines()
        self._setup_terrain_animations()
    
    def initialize(self):
        """グリッドシステムを初期化"""
        pass
    
    def update(self):
        """グリッドシステムを更新"""
        # カメラ操作
        self._handle_camera_input()
        
        # 視界カリング更新
        self.viewport_culling.update_viewport(
            self.camera_x, self.camera_y, self.zoom,
            self.grid_width, self.grid_height
        )
        
        # アニメーション更新
        animation_manager.update()
    
    def draw(self):
        """グリッドを描画"""
        # 地形描画
        self._draw_terrain()
        
        # グリッド線描画
        if self.show_grid:
            self._draw_grid_lines()
    
    def _handle_camera_input(self):
        """カメラ操作を処理"""
        camera_speed = 3
        
        # WASD/矢印キーでカメラ移動（十字キーの向きを修正）
        if pyxel.btn(pyxel.KEY_W) or pyxel.btn(pyxel.KEY_UP):
            self.camera_y += camera_speed  # 上キーで下に移動（画面が上にスクロール）
        if pyxel.btn(pyxel.KEY_S) or pyxel.btn(pyxel.KEY_DOWN):
            self.camera_y -= camera_speed  # 下キーで上に移動（画面が下にスクロール）
        if pyxel.btn(pyxel.KEY_A) or pyxel.btn(pyxel.KEY_LEFT):
            self.camera_x += camera_speed  # 左キーで右に移動（画面が左にスクロール）
        if pyxel.btn(pyxel.KEY_D) or pyxel.btn(pyxel.KEY_RIGHT):
            self.camera_x -= camera_speed  # 右キーで左に移動（画面が右にスクロール）
        
        # ズーム操作（テストキー）
        if pyxel.btnp(pyxel.KEY_Z):
            self.zoom = min(2.0, self.zoom + 0.2)
        if pyxel.btnp(pyxel.KEY_X):
            self.zoom = max(0.5, self.zoom - 0.2)
        
        # グリッド表示切り替え
        if pyxel.btnp(pyxel.KEY_G):
            self.show_grid = not self.show_grid
    
    def _draw_terrain(self):
        """地形を描画（視界カリング対応・高速化）"""
        # 視界内のセルを取得
        visible_cells = self.viewport_culling.get_visible_cells(self.grid_width, self.grid_height)

        # 描画順序を最適化（後ろから前へ）
        optimized_cells = self.viewport_culling.optimize_draw_order(visible_cells)

        for x, y in optimized_cells:
            screen_x, screen_y = self.grid_to_screen(x, y)

            # カメラオフセット適用
            screen_x += self.camera_x
            screen_y += self.camera_y

            terrain_type = self.terrain[y][x]

            # パフォーマンスのため、色付き菱形のみ描画（PNGスプライトはスキップ）
            color = self._get_terrain_color(terrain_type)
            self._draw_isometric_cell(screen_x, screen_y, color)
    
    def _draw_grid_lines(self):
        """グリッド線を描画（視界カリング対応）"""
        # 視界範囲を取得
        min_x, min_y, max_x, max_y = self.viewport_culling.get_visible_range()
        
        # 横線（視界内のみ）
        for y in range(max(0, min_y), min(self.grid_height + 1, max_y + 2)):
            start_x, start_y = self.grid_to_screen(0, y)
            end_x, end_y = self.grid_to_screen(self.grid_width, y)
            
            start_x += self.camera_x
            start_y += self.camera_y
            end_x += self.camera_x
            end_y += self.camera_y
            
            pyxel.line(start_x, start_y, end_x, end_y, self.grid_color)
        
        # 縦線（視界内のみ）
        for x in range(max(0, min_x), min(self.grid_width + 1, max_x + 2)):
            start_x, start_y = self.grid_to_screen(x, 0)
            end_x, end_y = self.grid_to_screen(x, self.grid_height)
            
            start_x += self.camera_x
            start_y += self.camera_y
            end_x += self.camera_x
            end_y += self.camera_y
            
            pyxel.line(start_x, start_y, end_x, end_y, self.grid_color)
    
    def _draw_isometric_cell(self, x, y, color):
        """等角投影セルを描画"""
        half_width = self.cell_size // 2
        half_height = self.cell_size // 4
        
        # 菱形の4つの頂点
        points = [
            (x, y - half_height),           # 上
            (x + half_width, y),            # 右
            (x, y + half_height),           # 下
            (x - half_width, y)             # 左
        ]
        
        # 三角形2つで菱形を描画
        pyxel.tri(points[0][0], points[0][1], points[1][0], points[1][1], 
                 points[2][0], points[2][1], color)
        pyxel.tri(points[0][0], points[0][1], points[2][0], points[2][1], 
                 points[3][0], points[3][1], color)
    
    def grid_to_screen(self, grid_x, grid_y):
        """グリッド座標を画面座標に変換"""
        # 等角投影変換
        screen_x = (grid_x - grid_y) * (self.cell_size // 2) + GameConfig.ISO_OFFSET_X
        screen_y = (grid_x + grid_y) * (self.cell_size // 4) + GameConfig.ISO_OFFSET_Y
        
        # ズーム適用
        screen_x = int(screen_x * self.zoom)
        screen_y = int(screen_y * self.zoom)
        
        return screen_x, screen_y
    
    def screen_to_grid(self, screen_x, screen_y):
        """画面座標をグリッド座標に変換"""
        # カメラオフセットを除去
        screen_x -= self.camera_x
        screen_y -= self.camera_y
        
        # 建物配置位置調整のためのオフセット
        screen_x += 8
        screen_y += -32
        
        # ズーム逆変換
        screen_x /= self.zoom
        screen_y /= self.zoom
        
        # 画面中央オフセットを除去
        screen_x -= GameConfig.ISO_OFFSET_X
        screen_y -= GameConfig.ISO_OFFSET_Y
        
        # 等角投影逆変換
        grid_x = (screen_x / (self.cell_size // 2) + screen_y / (self.cell_size // 4)) / 2
        grid_y = (screen_y / (self.cell_size // 4) - screen_x / (self.cell_size // 2)) / 2
        
        return int(grid_x), int(grid_y)
    
    def is_valid_grid_position(self, grid_x, grid_y):
        """グリッド座標が有効範囲内かチェック"""
        return (0 <= grid_x < self.grid_width and 
                0 <= grid_y < self.grid_height)
    
    def _get_terrain_color(self, terrain_type):
        """地形タイプに応じた色を取得"""
        terrain_colors = {
            0: GameConfig.COLOR_GRASS,  # 草地
            1: GameConfig.COLOR_DIRT,   # 土地
            2: GameConfig.COLOR_WATER,  # 水
            3: GameConfig.COLOR_ROAD    # 道路
        }
        return terrain_colors.get(terrain_type, GameConfig.COLOR_GRASS)
    
    def _get_terrain_sprite_name(self, terrain_type):
        """地形タイプに応じたスプライト名を取得"""
        from config.sprite_mapping import BUILDING_SPRITE_MAPPING
        terrain_sprites = {
            0: BUILDING_SPRITE_MAPPING.get("terrain_grass", "tile_grass-1-1"),    # 草地
            1: BUILDING_SPRITE_MAPPING.get("terrain_dirt", "tile_soil-1-1"),      # 土地
            2: BUILDING_SPRITE_MAPPING.get("terrain_water", "tile_water-1-1"),    # 水
            3: BUILDING_SPRITE_MAPPING.get("terrain_road", "tile_road-1-1"),      # 道路
            4: BUILDING_SPRITE_MAPPING.get("terrain_waste", "tile_waste-1-1"),    # 荒廃地
            5: BUILDING_SPRITE_MAPPING.get("terrain_sand", "tile_sand-1-1")       # 砂地
        }
        return terrain_sprites.get(terrain_type, "tile_grass-1-1")
    
    def generate_procedural_terrain(self, map_type: MapType = MapType.COASTAL, seed: int = None):
        """手続き的地形生成"""
        print(f"Generating procedural terrain: {map_type.value}")
        
        config = TerrainGenConfig()
        config.map_type = map_type
        config.seed = seed
        
        # 戦後復興らしい設定に調整
        config.wasteland_probability = 0.20  # 戦災荒廃地を多めに
        config.base_frequency = 0.06  # より細かい地形
        config.smoothing_passes = 3   # より滑らかに
        
        # 地形生成
        generated_terrain = terrain_generator.generate_terrain(config)
        
        # 既存の地形配列にコピー（既存のフォーマットに合わせて変換）
        for y in range(min(self.grid_height, len(generated_terrain))):
            for x in range(min(self.grid_width, len(generated_terrain[0]))):
                # 新しい地形タイプを既存の形式にマッピング
                new_terrain_type = generated_terrain[y][x]
                if new_terrain_type == 0:  # WATER
                    self.terrain[y][x] = 2
                elif new_terrain_type == 1:  # SAND  
                    self.terrain[y][x] = 1
                elif new_terrain_type == 2:  # GRASS
                    self.terrain[y][x] = 0
                elif new_terrain_type == 3:  # FOREST
                    self.terrain[y][x] = 0  # 森林も草地として扱う
                elif new_terrain_type == 4:  # MOUNTAIN
                    self.terrain[y][x] = 1  # 山地は土地として扱う
                elif new_terrain_type == 5:  # WASTELAND
                    self.terrain[y][x] = 1  # 荒廃地は土地として扱う
                else:
                    self.terrain[y][x] = 0  # デフォルトは草地
        
        # 海岸線生成（既存システムを活用）
        self._generate_coastlines()
        
        # 水タイルのアニメーション設定
        self._setup_water_animations()
        
        # 地形情報を取得・表示
        terrain_info = terrain_generator.get_terrain_info(generated_terrain)
        print(f"Terrain generated: {terrain_info['map_type']}, seed: {terrain_info['seed']}")
        for terrain_name, data in terrain_info['terrain_distribution'].items():
            print(f"  {terrain_name}: {data['percentage']:.1f}%")
    
    def _setup_water_animations(self):
        """水タイルのアニメーション設定"""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.terrain[y][x] == 2:  # 水タイル
                    animation_manager.set_tile_animation(x, y, "water")
    
    def _generate_test_terrain(self):
        """テスト地形を生成（デフォルト地形データを使用）"""
        try:
            from default_terrain import DEFAULT_TERRAIN
            # デフォルト地形データをコピー
            for y in range(min(self.grid_height, len(DEFAULT_TERRAIN))):
                for x in range(min(self.grid_width, len(DEFAULT_TERRAIN[0]))):
                    self.terrain[y][x] = DEFAULT_TERRAIN[y][x]
            print("デフォルト地形データを読み込みました")
        except ImportError:
            print("デフォルト地形データが見つかりません。テスト地形を生成します。")
            # フォールバック: 元のテスト地形生成
            for y in range(self.grid_height):
                for x in range(self.grid_width):
                    if x == 0 or y == 0 or x == self.grid_width-1 or y == self.grid_height-1:
                        self.terrain[y][x] = 2  # 水
                    elif (x + y) % 4 == 0:
                        self.terrain[y][x] = 1  # 土
                    else:
                        self.terrain[y][x] = 0  # 草
    def _generate_coastlines(self):
        """海岸線を生成"""
        self.coastline_sprites = self.coastline_generator.generate_coastline_for_area(
            self, 0, 0, self.grid_width, self.grid_height
        )
        print(f"Generated {len(self.coastline_sprites)} coastline sprites")
    
    def update_coastlines_around_point(self, x: int, y: int):
        """指定点周辺の海岸線を更新"""
        updated_sprites = self.coastline_generator.update_coastline_around_point(self, x, y)
        self.coastline_sprites.update(updated_sprites)
        print(f"Updated {len(updated_sprites)} coastline sprites around ({x}, {y})")
    
    def get_coastline_sprite(self, x: int, y: int) -> str:
        """指定座標の海岸線スプライトを取得"""
        return self.coastline_sprites.get((x, y), "terrain_water")
    
    def _setup_terrain_animations(self):
        """地形アニメーションを設定"""
        # 全水タイルにアニメーションを設定
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.terrain[y][x] == 2:  # 水タイル
                    animation_manager.set_tile_animation(x, y, "water")
        
        print(f"Set up water animations for {sum(1 for row in self.terrain for cell in row if cell == 2)} water tiles")
    
    def get_culling_stats(self) -> dict:
        """カリング統計情報を取得"""
        return self.viewport_culling.get_culling_stats()
    
    def get_memory_stats(self) -> dict:
        """メモリ使用量統計を取得"""
        return self.viewport_culling.estimate_memory_usage()