"""
海岸線自動生成システム
Coastline Generation System
"""

from typing import Dict, List, Tuple, Optional
import math


class CoastlinePattern:
    """海岸線パターン定義"""
    
    def __init__(self, pattern_id: str, name: str, neighbor_mask: int, 
                 sprite_name: str, rotation: int = 0, priority: int = 0):
        self.pattern_id = pattern_id
        self.name = name
        self.neighbor_mask = neighbor_mask  # 8方向の隣接マスク (0=陸地, 1=水)
        self.sprite_name = sprite_name
        self.rotation = rotation  # 0, 90, 180, 270度
        self.priority = priority  # 優先度（高い方が優先）


class CoastlineGenerator:
    """海岸線自動生成クラス"""
    
    def __init__(self):
        self.patterns: List[CoastlinePattern] = []
        self.terrain_water_types = {2}  # 水タイプのテレインID
        self.terrain_land_types = {0, 1, 3, 4, 5}  # 陸地タイプのテレインID
        
        # 8方向の隣接オフセット (N, NE, E, SE, S, SW, W, NW)
        self.neighbor_offsets = [
            (0, -1),  # N
            (1, -1),  # NE
            (1, 0),   # E
            (1, 1),   # SE
            (0, 1),   # S
            (-1, 1),  # SW
            (-1, 0),  # W
            (-1, -1)  # NW
        ]
        
        # 海岸線パターンを初期化
        self._initialize_patterns()
    
    def _initialize_patterns(self):
        """海岸線パターンを初期化"""
        
        # 基本的な海岸線パターン
        # マスクは8bitで表現: bit0=N, bit1=NE, bit2=E, bit3=SE, bit4=S, bit5=SW, bit6=W, bit7=NW
        # 0=陸地, 1=水
        
        patterns = [
            # 直線海岸線
            CoastlinePattern("coast_n", "北海岸", 0b00000001, "coastline_n", 0, 10),
            CoastlinePattern("coast_e", "東海岸", 0b00000100, "coastline_e", 0, 10),
            CoastlinePattern("coast_s", "南海岸", 0b00010000, "coastline_s", 0, 10),
            CoastlinePattern("coast_w", "西海岸", 0b01000000, "coastline_w", 0, 10),
            
            # 角海岸線
            CoastlinePattern("coast_ne", "北東角", 0b00000101, "coastline_ne", 0, 20),
            CoastlinePattern("coast_se", "南東角", 0b00010100, "coastline_se", 0, 20),
            CoastlinePattern("coast_sw", "南西角", 0b01010000, "coastline_sw", 0, 20),
            CoastlinePattern("coast_nw", "北西角", 0b01000001, "coastline_nw", 0, 20),
            
            # 内角海岸線
            CoastlinePattern("coast_inner_ne", "内角北東", 0b11111010, "coastline_inner_ne", 0, 30),
            CoastlinePattern("coast_inner_se", "内角南東", 0b11101011, "coastline_inner_se", 0, 30),
            CoastlinePattern("coast_inner_sw", "内角南西", 0b10101111, "coastline_inner_sw", 0, 30),
            CoastlinePattern("coast_inner_nw", "内角北西", 0b10111110, "coastline_inner_nw", 0, 30),
            
            # 半島パターン
            CoastlinePattern("coast_peninsula_n", "北半島", 0b01010001, "coastline_peninsula_n", 0, 25),
            CoastlinePattern("coast_peninsula_e", "東半島", 0b00010101, "coastline_peninsula_e", 0, 25),
            CoastlinePattern("coast_peninsula_s", "南半島", 0b01010100, "coastline_peninsula_s", 0, 25),
            CoastlinePattern("coast_peninsula_w", "西半島", 0b01000101, "coastline_peninsula_w", 0, 25),
            
            # 湾パターン
            CoastlinePattern("coast_bay_n", "北湾", 0b10111110, "coastline_bay_n", 0, 25),
            CoastlinePattern("coast_bay_e", "東湾", 0b11101011, "coastline_bay_e", 0, 25),
            CoastlinePattern("coast_bay_s", "南湾", 0b11111010, "coastline_bay_s", 0, 25),
            CoastlinePattern("coast_bay_w", "西湾", 0b10101111, "coastline_bay_w", 0, 25),
            
            # 複雑なパターン
            CoastlinePattern("coast_complex_1", "複雑海岸1", 0b10110101, "coastline_complex_1", 0, 15),
            CoastlinePattern("coast_complex_2", "複雑海岸2", 0b01011010, "coastline_complex_2", 0, 15),
            CoastlinePattern("coast_complex_3", "複雑海岸3", 0b11010110, "coastline_complex_3", 0, 15),
            CoastlinePattern("coast_complex_4", "複雑海岸4", 0b01101011, "coastline_complex_4", 0, 15),
            
            # 島パターン
            CoastlinePattern("coast_island_small", "小島", 0b11111111, "coastline_island_small", 0, 40),
            CoastlinePattern("coast_island_large", "大島", 0b11111111, "coastline_island_large", 0, 35),
            
            # 開水面（完全に水に囲まれた水タイル）
            CoastlinePattern("open_water", "開水面", 0b11111111, "terrain_water", 0, 5),
            
            # デフォルトパターン
            CoastlinePattern("default_water", "デフォルト水", 0b00000000, "terrain_water", 0, 1)
        ]
        
        self.patterns = sorted(patterns, key=lambda p: p.priority, reverse=True)
    
    def generate_coastline(self, grid_system, x: int, y: int) -> Optional[str]:
        """指定座標の海岸線スプライトを生成"""
        
        if not self._is_water_tile(grid_system, x, y):
            return None
        
        # 隣接パターンを取得
        neighbor_mask = self._get_neighbor_mask(grid_system, x, y)
        
        # 最適なパターンを検索
        best_pattern = self._find_best_pattern(neighbor_mask)
        
        if best_pattern:
            return best_pattern.sprite_name
        
        return "terrain_water"  # デフォルト
    
    def _is_water_tile(self, grid_system, x: int, y: int) -> bool:
        """水タイルかどうかチェック"""
        if not grid_system.is_valid_grid_position(x, y):
            return False
        
        terrain_type = grid_system.terrain[y][x]
        return terrain_type in self.terrain_water_types
    
    def _is_land_tile(self, grid_system, x: int, y: int) -> bool:
        """陸地タイルかどうかチェック"""
        if not grid_system.is_valid_grid_position(x, y):
            return True  # グリッド外は陸地扱い
        
        terrain_type = grid_system.terrain[y][x]
        return terrain_type in self.terrain_land_types
    
    def _get_neighbor_mask(self, grid_system, x: int, y: int) -> int:
        """隣接マスクを取得"""
        mask = 0
        
        for i, (dx, dy) in enumerate(self.neighbor_offsets):
            neighbor_x = x + dx
            neighbor_y = y + dy
            
            if self._is_water_tile(grid_system, neighbor_x, neighbor_y):
                mask |= (1 << i)
        
        return mask
    
    def _find_best_pattern(self, neighbor_mask: int) -> Optional[CoastlinePattern]:
        """隣接マスクに最適なパターンを検索"""
        
        # 完全一致を優先
        for pattern in self.patterns:
            if pattern.neighbor_mask == neighbor_mask:
                return pattern
        
        # 部分一致（必要な条件を満たすパターン）
        for pattern in self.patterns:
            if self._pattern_matches(pattern.neighbor_mask, neighbor_mask):
                return pattern
        
        return None
    
    def _pattern_matches(self, pattern_mask: int, neighbor_mask: int) -> bool:
        """パターンが隣接マスクにマッチするかチェック"""
        
        # パターンの条件を満たすかチェック
        # パターンマスクで1になっている部分は水である必要がある
        required_water = pattern_mask
        # パターンマスクで0になっている部分は陸地である必要がある
        required_land = ~pattern_mask & 0xFF
        
        # 必要な水の条件をチェック
        if (neighbor_mask & required_water) != required_water:
            return False
        
        # 必要な陸地の条件をチェック
        if (neighbor_mask & required_land) != 0:
            return False
        
        return True
    
    def generate_coastline_for_area(self, grid_system, start_x: int, start_y: int, 
                                   width: int, height: int) -> Dict[Tuple[int, int], str]:
        """指定範囲の海岸線を一括生成"""
        
        coastline_sprites = {}
        
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if grid_system.is_valid_grid_position(x, y):
                    sprite_name = self.generate_coastline(grid_system, x, y)
                    if sprite_name:
                        coastline_sprites[(x, y)] = sprite_name
        
        return coastline_sprites
    
    def update_coastline_around_point(self, grid_system, center_x: int, center_y: int, 
                                     radius: int = 3) -> Dict[Tuple[int, int], str]:
        """指定点の周囲の海岸線を更新"""
        
        coastline_sprites = {}
        
        for y in range(center_y - radius, center_y + radius + 1):
            for x in range(center_x - radius, center_x + radius + 1):
                if grid_system.is_valid_grid_position(x, y):
                    sprite_name = self.generate_coastline(grid_system, x, y)
                    if sprite_name:
                        coastline_sprites[(x, y)] = sprite_name
        
        return coastline_sprites
    
    def analyze_coastline_complexity(self, grid_system, x: int, y: int) -> Dict[str, float]:
        """海岸線の複雑さを分析"""
        
        if not self._is_water_tile(grid_system, x, y):
            return {"complexity": 0.0, "isolation": 0.0, "connectivity": 0.0}
        
        neighbor_mask = self._get_neighbor_mask(grid_system, x, y)
        
        # 複雑さの計算
        water_neighbors = bin(neighbor_mask).count('1')
        land_neighbors = 8 - water_neighbors
        
        # 隣接パターンの複雑さ
        pattern_complexity = self._calculate_pattern_complexity(neighbor_mask)
        
        # 孤立度の計算
        isolation = water_neighbors / 8.0
        
        # 連結性の計算
        connectivity = land_neighbors / 8.0
        
        return {
            "complexity": pattern_complexity,
            "isolation": isolation,
            "connectivity": connectivity,
            "water_neighbors": water_neighbors,
            "land_neighbors": land_neighbors
        }
    
    def _calculate_pattern_complexity(self, neighbor_mask: int) -> float:
        """パターンの複雑さを計算"""
        
        # 隣接する水-陸地の境界数をカウント
        transitions = 0
        
        for i in range(8):
            current_bit = (neighbor_mask >> i) & 1
            next_bit = (neighbor_mask >> ((i + 1) % 8)) & 1
            
            if current_bit != next_bit:
                transitions += 1
        
        # 複雑さは境界数に比例
        return transitions / 8.0
    
    def get_coastline_statistics(self, grid_system, start_x: int, start_y: int, 
                               width: int, height: int) -> Dict[str, int]:
        """海岸線の統計情報を取得"""
        
        stats = {
            "total_water_tiles": 0,
            "coastline_tiles": 0,
            "open_water_tiles": 0,
            "island_tiles": 0,
            "bay_tiles": 0,
            "peninsula_tiles": 0,
            "complex_tiles": 0
        }
        
        for y in range(start_y, start_y + height):
            for x in range(start_x, start_x + width):
                if not grid_system.is_valid_grid_position(x, y):
                    continue
                
                if self._is_water_tile(grid_system, x, y):
                    stats["total_water_tiles"] += 1
                    
                    neighbor_mask = self._get_neighbor_mask(grid_system, x, y)
                    pattern = self._find_best_pattern(neighbor_mask)
                    
                    if pattern:
                        if "coast" in pattern.pattern_id:
                            stats["coastline_tiles"] += 1
                        if "open_water" in pattern.pattern_id:
                            stats["open_water_tiles"] += 1
                        if "island" in pattern.pattern_id:
                            stats["island_tiles"] += 1
                        if "bay" in pattern.pattern_id:
                            stats["bay_tiles"] += 1
                        if "peninsula" in pattern.pattern_id:
                            stats["peninsula_tiles"] += 1
                        if "complex" in pattern.pattern_id:
                            stats["complex_tiles"] += 1
        
        return stats
    
    def create_coastline_sprites(self, asset_manager):
        """海岸線スプライトを作成"""
        
        # 基本的な海岸線スプライトを生成
        coastline_sprites = {
            "coastline_n": self._create_north_coastline_sprite(),
            "coastline_e": self._create_east_coastline_sprite(),
            "coastline_s": self._create_south_coastline_sprite(),
            "coastline_w": self._create_west_coastline_sprite(),
            "coastline_ne": self._create_northeast_corner_sprite(),
            "coastline_se": self._create_southeast_corner_sprite(),
            "coastline_sw": self._create_southwest_corner_sprite(),
            "coastline_nw": self._create_northwest_corner_sprite(),
            "coastline_inner_ne": self._create_inner_northeast_sprite(),
            "coastline_inner_se": self._create_inner_southeast_sprite(),
            "coastline_inner_sw": self._create_inner_southwest_sprite(),
            "coastline_inner_nw": self._create_inner_northwest_sprite(),
        }
        
        # アセットマネージャーに登録
        for sprite_name, sprite_data in coastline_sprites.items():
            asset_manager.create_sprite_from_data(sprite_name, sprite_data)
    
    def _create_north_coastline_sprite(self) -> List[List[int]]:
        """北海岸線スプライトを作成"""
        sprite = [[2 for _ in range(32)] for _ in range(32)]
        
        # 上半分を陸地色、下半分を水色
        for y in range(32):
            for x in range(32):
                if y < 16:
                    sprite[y][x] = 11  # 陸地色
                else:
                    sprite[y][x] = 12  # 水色
        
        # 海岸線を描画
        for x in range(32):
            sprite[15][x] = 1  # 海岸線色
            sprite[16][x] = 1
        
        return sprite
    
    def _create_east_coastline_sprite(self) -> List[List[int]]:
        """東海岸線スプライトを作成"""
        sprite = [[2 for _ in range(32)] for _ in range(32)]
        
        # 右半分を陸地色、左半分を水色
        for y in range(32):
            for x in range(32):
                if x > 16:
                    sprite[y][x] = 11  # 陸地色
                else:
                    sprite[y][x] = 12  # 水色
        
        # 海岸線を描画
        for y in range(32):
            sprite[y][15] = 1  # 海岸線色
            sprite[y][16] = 1
        
        return sprite
    
    def _create_south_coastline_sprite(self) -> List[List[int]]:
        """南海岸線スプライトを作成"""
        sprite = [[2 for _ in range(32)] for _ in range(32)]
        
        # 下半分を陸地色、上半分を水色
        for y in range(32):
            for x in range(32):
                if y > 16:
                    sprite[y][x] = 11  # 陸地色
                else:
                    sprite[y][x] = 12  # 水色
        
        # 海岸線を描画
        for x in range(32):
            sprite[15][x] = 1  # 海岸線色
            sprite[16][x] = 1
        
        return sprite
    
    def _create_west_coastline_sprite(self) -> List[List[int]]:
        """西海岸線スプライトを作成"""
        sprite = [[2 for _ in range(32)] for _ in range(32)]
        
        # 左半分を陸地色、右半分を水色
        for y in range(32):
            for x in range(32):
                if x < 16:
                    sprite[y][x] = 11  # 陸地色
                else:
                    sprite[y][x] = 12  # 水色
        
        # 海岸線を描画
        for y in range(32):
            sprite[y][15] = 1  # 海岸線色
            sprite[y][16] = 1
        
        return sprite
    
    def _create_northeast_corner_sprite(self) -> List[List[int]]:
        """北東角スプライトを作成"""
        sprite = [[12 for _ in range(32)] for _ in range(32)]  # 基本は水色
        
        # 右上を陸地色に
        for y in range(16):
            for x in range(16, 32):
                sprite[y][x] = 11  # 陸地色
        
        # 海岸線を描画
        for i in range(16):
            sprite[15-i][16+i] = 1  # 対角線の海岸線
        
        return sprite
    
    def _create_southeast_corner_sprite(self) -> List[List[int]]:
        """南東角スプライトを作成"""
        sprite = [[12 for _ in range(32)] for _ in range(32)]  # 基本は水色
        
        # 右下を陸地色に
        for y in range(16, 32):
            for x in range(16, 32):
                sprite[y][x] = 11  # 陸地色
        
        # 海岸線を描画
        for i in range(16):
            sprite[16+i][16+i] = 1  # 対角線の海岸線
        
        return sprite
    
    def _create_southwest_corner_sprite(self) -> List[List[int]]:
        """南西角スプライトを作成"""
        sprite = [[12 for _ in range(32)] for _ in range(32)]  # 基本は水色
        
        # 左下を陸地色に
        for y in range(16, 32):
            for x in range(16):
                sprite[y][x] = 11  # 陸地色
        
        # 海岸線を描画
        for i in range(16):
            sprite[16+i][15-i] = 1  # 対角線の海岸線
        
        return sprite
    
    def _create_northwest_corner_sprite(self) -> List[List[int]]:
        """北西角スプライトを作成"""
        sprite = [[12 for _ in range(32)] for _ in range(32)]  # 基本は水色
        
        # 左上を陸地色に
        for y in range(16):
            for x in range(16):
                sprite[y][x] = 11  # 陸地色
        
        # 海岸線を描画
        for i in range(16):
            sprite[15-i][15-i] = 1  # 対角線の海岸線
        
        return sprite
    
    def _create_inner_northeast_sprite(self) -> List[List[int]]:
        """内角北東スプライトを作成"""
        sprite = [[11 for _ in range(32)] for _ in range(32)]  # 基本は陸地色
        
        # 右上を水色に
        for y in range(16):
            for x in range(16, 32):
                sprite[y][x] = 12  # 水色
        
        # 海岸線を描画
        for i in range(16):
            sprite[15-i][16+i] = 1  # 対角線の海岸線
        
        return sprite
    
    def _create_inner_southeast_sprite(self) -> List[List[int]]:
        """内角南東スプライトを作成"""
        sprite = [[11 for _ in range(32)] for _ in range(32)]  # 基本は陸地色
        
        # 右下を水色に
        for y in range(16, 32):
            for x in range(16, 32):
                sprite[y][x] = 12  # 水色
        
        # 海岸線を描画
        for i in range(16):
            sprite[16+i][16+i] = 1  # 対角線の海岸線
        
        return sprite
    
    def _create_inner_southwest_sprite(self) -> List[List[int]]:
        """内角南西スプライトを作成"""
        sprite = [[11 for _ in range(32)] for _ in range(32)]  # 基本は陸地色
        
        # 左下を水色に
        for y in range(16, 32):
            for x in range(16):
                sprite[y][x] = 12  # 水色
        
        # 海岸線を描画
        for i in range(16):
            sprite[16+i][15-i] = 1  # 対角線の海岸線
        
        return sprite
    
    def _create_inner_northwest_sprite(self) -> List[List[int]]:
        """内角北西スプライトを作成"""
        sprite = [[11 for _ in range(32)] for _ in range(32)]  # 基本は陸地色
        
        # 左上を水色に
        for y in range(16):
            for x in range(16):
                sprite[y][x] = 12  # 水色
        
        # 海岸線を描画
        for i in range(16):
            sprite[15-i][15-i] = 1  # 対角線の海岸線
        
        return sprite