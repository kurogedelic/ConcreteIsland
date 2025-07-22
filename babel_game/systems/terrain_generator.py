"""
地形自動生成システム
Procedural Terrain Generation System

パーリンノイズを使用した自然な地形生成
"""

import random
import math
from typing import Dict, List, Tuple, Optional, Any
from enum import Enum
from dataclasses import dataclass

from config.game_config import GameConfig


class TerrainType(Enum):
    """地形タイプ"""
    WATER = 0           # 水
    SAND = 1            # 砂浜
    GRASS = 2           # 草地（デフォルト）
    FOREST = 3          # 森林
    MOUNTAIN = 4        # 山地
    WASTELAND = 5       # 戦災荒廃地（戦後特有）


class MapType(Enum):
    """マップタイプ"""
    ISLAND = "island"           # 島
    COASTAL = "coastal"         # 海岸地域
    INLAND = "inland"          # 内陸
    PENINSULA = "peninsula"     # 半島
    RIVER_VALLEY = "river_valley"  # 河川流域


@dataclass
class TerrainGenConfig:
    """地形生成設定"""
    map_type: MapType = MapType.COASTAL
    seed: int = None
    
    # ノイズパラメータ
    base_frequency: float = 0.05
    octaves: int = 4
    persistence: float = 0.5
    lacunarity: float = 2.0
    
    # 地形閾値
    water_threshold: float = 0.3
    sand_threshold: float = 0.4
    forest_threshold: float = 0.6
    mountain_threshold: float = 0.8
    
    # 戦災荒廃地の生成率（戦後らしさのため）
    wasteland_probability: float = 0.15
    
    # 河川生成
    river_count: int = 2
    river_width: int = 2
    
    # スムージング
    smoothing_passes: int = 2


class PerlinNoise:
    """パーリンノイズ実装"""
    
    def __init__(self, seed: int = None):
        if seed is None:
            seed = random.randint(0, 2**31)
        random.seed(seed)
        
        # 順列テーブル
        self.p = list(range(256))
        random.shuffle(self.p)
        self.p += self.p  # 重複して512要素にする
    
    def fade(self, t: float) -> float:
        """フェード関数"""
        return t * t * t * (t * (t * 6 - 15) + 10)
    
    def lerp(self, t: float, a: float, b: float) -> float:
        """線形補間"""
        return a + t * (b - a)
    
    def grad(self, hash_val: int, x: float, y: float) -> float:
        """勾配関数"""
        h = hash_val & 3
        u = x if h < 2 else y
        v = y if h < 2 else x
        return (u if (h & 1) == 0 else -u) + (v if (h & 2) == 0 else -v)
    
    def noise(self, x: float, y: float) -> float:
        """2Dパーリンノイズ"""
        # 整数部分
        X = int(x) & 255
        Y = int(y) & 255
        
        # 小数部分
        x -= int(x)
        y -= int(y)
        
        # フェード
        u = self.fade(x)
        v = self.fade(y)
        
        # ハッシュ座標
        A = self.p[X] + Y
        B = self.p[X + 1] + Y
        
        # 補間
        return self.lerp(v,
            self.lerp(u, self.grad(self.p[A], x, y), self.grad(self.p[B], x - 1, y)),
            self.lerp(u, self.grad(self.p[A + 1], x, y - 1), self.grad(self.p[B + 1], x - 1, y - 1))
        )
    
    def octave_noise(self, x: float, y: float, octaves: int, persistence: float, lacunarity: float) -> float:
        """オクターブノイズ"""
        value = 0.0
        amplitude = 1.0
        frequency = 1.0
        max_amplitude = 0.0
        
        for _ in range(octaves):
            value += self.noise(x * frequency, y * frequency) * amplitude
            max_amplitude += amplitude
            amplitude *= persistence
            frequency *= lacunarity
        
        return value / max_amplitude


class TerrainGenerator:
    """地形生成クラス"""
    
    def __init__(self):
        self.noise_generator = None
        self.config = TerrainGenConfig()
        self.grid_width = getattr(GameConfig, 'GRID_SIZE', 32)
        self.grid_height = getattr(GameConfig, 'GRID_SIZE', 32)
    
    def generate_terrain(self, config: TerrainGenConfig = None) -> List[List[int]]:
        """地形を生成"""
        if config:
            self.config = config
        
        # シード設定
        if self.config.seed is None:
            self.config.seed = random.randint(0, 2**31)
        
        self.noise_generator = PerlinNoise(self.config.seed)
        
        print(f"Generating terrain: {self.config.map_type.value}, seed: {self.config.seed}")
        
        # 基本地形生成
        terrain_grid = self._generate_base_terrain()
        
        # マップタイプ別処理
        if self.config.map_type == MapType.ISLAND:
            terrain_grid = self._apply_island_mask(terrain_grid)
        elif self.config.map_type == MapType.COASTAL:
            terrain_grid = self._apply_coastal_features(terrain_grid)
        elif self.config.map_type == MapType.PENINSULA:
            terrain_grid = self._apply_peninsula_mask(terrain_grid)
        elif self.config.map_type == MapType.RIVER_VALLEY:
            terrain_grid = self._add_rivers(terrain_grid)
        
        # 戦災荒廃地の追加（戦後らしさ）
        terrain_grid = self._add_wasteland(terrain_grid)
        
        # スムージング
        for _ in range(self.config.smoothing_passes):
            terrain_grid = self._smooth_terrain(terrain_grid)
        
        # 海岸線の調整
        terrain_grid = self._adjust_coastlines(terrain_grid)
        
        print(f"Terrain generated: {self.grid_width}x{self.grid_height}")
        return terrain_grid
    
    def _generate_base_terrain(self) -> List[List[int]]:
        """基本地形生成"""
        terrain = []
        
        for y in range(self.grid_height):
            row = []
            for x in range(self.grid_width):
                # ノイズ値計算
                noise_val = self.noise_generator.octave_noise(
                    x * self.config.base_frequency,
                    y * self.config.base_frequency,
                    self.config.octaves,
                    self.config.persistence,
                    self.config.lacunarity
                )
                
                # 正規化 (-1, 1) -> (0, 1)
                noise_val = (noise_val + 1) * 0.5
                
                # 地形タイプ決定
                terrain_type = self._noise_to_terrain(noise_val)
                row.append(terrain_type.value)
            
            terrain.append(row)
        
        return terrain
    
    def _noise_to_terrain(self, noise_val: float) -> TerrainType:
        """ノイズ値から地形タイプを決定"""
        if noise_val < self.config.water_threshold:
            return TerrainType.WATER
        elif noise_val < self.config.sand_threshold:
            return TerrainType.SAND
        elif noise_val < self.config.forest_threshold:
            return TerrainType.GRASS
        elif noise_val < self.config.mountain_threshold:
            return TerrainType.FOREST
        else:
            return TerrainType.MOUNTAIN
    
    def _apply_island_mask(self, terrain: List[List[int]]) -> List[List[int]]:
        """島マスクを適用"""
        center_x = self.grid_width // 2
        center_y = self.grid_height // 2
        max_radius = min(self.grid_width, self.grid_height) * 0.4
        
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                # 中心からの距離
                distance = math.sqrt((x - center_x)**2 + (y - center_y)**2)
                
                # 距離に基づく減衰
                if distance > max_radius:
                    terrain[y][x] = TerrainType.WATER.value
                elif distance > max_radius * 0.9:
                    # 海岸線エリア
                    if terrain[y][x] == TerrainType.GRASS.value:
                        terrain[y][x] = TerrainType.SAND.value
        
        return terrain
    
    def _apply_coastal_features(self, terrain: List[List[int]]) -> List[List[int]]:
        """海岸地域の特徴を適用"""
        # 上端と下端を水域にする
        for y in [0, 1, self.grid_height-2, self.grid_height-1]:
            for x in range(self.grid_width):
                if random.random() < 0.7:  # 70%の確率で水域
                    terrain[y][x] = TerrainType.WATER.value
        
        # 左端を一部水域に
        for y in range(self.grid_height):
            for x in range(3):
                if random.random() < 0.5:  # 50%の確率で水域
                    terrain[y][x] = TerrainType.WATER.value
        
        return terrain
    
    def _apply_peninsula_mask(self, terrain: List[List[int]]) -> List[List[int]]:
        """半島マスクを適用"""
        # 左側を海に、右側を陸地に
        for y in range(self.grid_height):
            for x in range(self.grid_width // 3):
                terrain[y][x] = TerrainType.WATER.value
        
        # 接続部分の狭め
        neck_width = self.grid_width // 6
        neck_start = self.grid_height // 3
        neck_end = neck_start + self.grid_height // 3
        
        for y in range(neck_start, neck_end):
            for x in range(neck_width):
                terrain[y][x] = TerrainType.WATER.value
        
        return terrain
    
    def _add_rivers(self, terrain: List[List[int]]) -> List[List[int]]:
        """河川を追加"""
        # 主河川を追加（横断）
        main_river_y = self.grid_height // 2
        for x in range(self.grid_width):
            for dy in range(-self.config.river_width//2, self.config.river_width//2 + 1):
                ny = main_river_y + dy
                if 0 <= ny < self.grid_height:
                    terrain[ny][x] = TerrainType.WATER.value
        
        # 支流を追加
        for _ in range(self.config.river_count):
            # 河川のスタート地点（端から）
            if random.random() < 0.5:
                # 上端から
                start_x = random.randint(0, self.grid_width - 1)
                start_y = 0
                target_y = main_river_y
            else:
                # 下端から
                start_x = random.randint(0, self.grid_width - 1)
                start_y = self.grid_height - 1
                target_y = main_river_y
            
            # 河川のパス生成（主河川に向かって流れる）
            current_x, current_y = start_x, start_y
            
            for _ in range(self.grid_height):
                # 河川の幅
                for dy in range(-self.config.river_width//2, self.config.river_width//2 + 1):
                    for dx in range(-1, 2):
                        nx, ny = current_x + dx, current_y + dy
                        if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                            terrain[ny][nx] = TerrainType.WATER.value
                
                # 主河川に近づく
                if current_y < target_y:
                    current_y += 1
                elif current_y > target_y:
                    current_y -= 1
                
                # 少し横にも移動
                if random.random() < 0.3:
                    current_x += random.choice([-1, 1])
                    current_x = max(0, min(self.grid_width - 1, current_x))
                
                # 主河川に到達したら終了
                if abs(current_y - target_y) <= self.config.river_width//2:
                    break
        
        return terrain
    
    def _add_wasteland(self, terrain: List[List[int]]) -> List[List[int]]:
        """戦災荒廃地を追加（戦後らしさ）"""
        wasteland_count = int(self.grid_width * self.grid_height * self.config.wasteland_probability)
        
        for _ in range(wasteland_count):
            x = random.randint(0, self.grid_width - 1)
            y = random.randint(0, self.grid_height - 1)
            
            # 既存の陸地のみを荒廃地に変換
            if terrain[y][x] in [TerrainType.GRASS.value, TerrainType.FOREST.value]:
                # 荒廃地エリアを生成（3x3程度のクラスター）
                for dy in range(-1, 2):
                    for dx in range(-1, 2):
                        nx, ny = x + dx, y + dy
                        if (0 <= nx < self.grid_width and 0 <= ny < self.grid_height and
                            terrain[ny][nx] in [TerrainType.GRASS.value, TerrainType.FOREST.value] and
                            random.random() < 0.6):
                            terrain[ny][nx] = TerrainType.WASTELAND.value
        
        return terrain
    
    def _smooth_terrain(self, terrain: List[List[int]]) -> List[List[int]]:
        """地形をスムージング"""
        smoothed = [[terrain[y][x] for x in range(self.grid_width)] for y in range(self.grid_height)]
        
        for y in range(1, self.grid_height - 1):
            for x in range(1, self.grid_width - 1):
                # 周囲8マスの地形タイプをカウント
                neighbors = {}
                for dy in [-1, 0, 1]:
                    for dx in [-1, 0, 1]:
                        terrain_type = terrain[y + dy][x + dx]
                        neighbors[terrain_type] = neighbors.get(terrain_type, 0) + 1
                
                # 最多の地形タイプを選択（ただし水域は保護）
                if terrain[y][x] != TerrainType.WATER.value:
                    most_common = max(neighbors.items(), key=lambda item: item[1])
                    if most_common[1] >= 5:  # 9マス中5マス以上が同じ地形なら変更
                        smoothed[y][x] = most_common[0]
        
        return smoothed
    
    def _adjust_coastlines(self, terrain: List[List[int]]) -> List[List[int]]:
        """海岸線を調整"""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if terrain[y][x] == TerrainType.WATER.value:
                    # 水域の隣接する陸地を砂浜にする
                    for dy in [-1, 0, 1]:
                        for dx in [-1, 0, 1]:
                            if dx == 0 and dy == 0:
                                continue
                            
                            nx, ny = x + dx, y + dy
                            if (0 <= nx < self.grid_width and 0 <= ny < self.grid_height and
                                terrain[ny][nx] == TerrainType.GRASS.value):
                                terrain[ny][nx] = TerrainType.SAND.value
        
        return terrain
    
    def get_terrain_info(self, terrain: List[List[int]]) -> Dict[str, Any]:
        """地形情報を取得"""
        terrain_counts = {}
        total_tiles = self.grid_width * self.grid_height
        
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                terrain_type = terrain[y][x]
                terrain_counts[terrain_type] = terrain_counts.get(terrain_type, 0) + 1
        
        # パーセンテージ計算
        terrain_percentages = {}
        terrain_names = {
            TerrainType.WATER.value: "水域",
            TerrainType.SAND.value: "砂浜",
            TerrainType.GRASS.value: "草地",
            TerrainType.FOREST.value: "森林",
            TerrainType.MOUNTAIN.value: "山地",
            TerrainType.WASTELAND.value: "荒廃地"
        }
        
        for terrain_type, count in terrain_counts.items():
            percentage = (count / total_tiles) * 100
            name = terrain_names.get(terrain_type, f"Unknown({terrain_type})")
            terrain_percentages[name] = {
                'count': count,
                'percentage': percentage
            }
        
        return {
            'total_tiles': total_tiles,
            'terrain_distribution': terrain_percentages,
            'seed': self.config.seed,
            'map_type': self.config.map_type.value
        }
    
    def save_terrain_config(self, filepath: str):
        """地形設定を保存"""
        import json
        config_data = {
            'map_type': self.config.map_type.value,
            'seed': self.config.seed,
            'base_frequency': self.config.base_frequency,
            'octaves': self.config.octaves,
            'persistence': self.config.persistence,
            'lacunarity': self.config.lacunarity,
            'water_threshold': self.config.water_threshold,
            'sand_threshold': self.config.sand_threshold,
            'forest_threshold': self.config.forest_threshold,
            'mountain_threshold': self.config.mountain_threshold,
            'wasteland_probability': self.config.wasteland_probability,
            'river_count': self.config.river_count,
            'river_width': self.config.river_width,
            'smoothing_passes': self.config.smoothing_passes
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
    
    def load_terrain_config(self, filepath: str) -> TerrainGenConfig:
        """地形設定を読み込み"""
        import json
        with open(filepath, 'r', encoding='utf-8') as f:
            config_data = json.load(f)
        
        config = TerrainGenConfig()
        config.map_type = MapType(config_data['map_type'])
        config.seed = config_data['seed']
        config.base_frequency = config_data['base_frequency']
        config.octaves = config_data['octaves']
        config.persistence = config_data['persistence']
        config.lacunarity = config_data['lacunarity']
        config.water_threshold = config_data['water_threshold']
        config.sand_threshold = config_data['sand_threshold']
        config.forest_threshold = config_data['forest_threshold']
        config.mountain_threshold = config_data['mountain_threshold']
        config.wasteland_probability = config_data['wasteland_probability']
        config.river_count = config_data['river_count']
        config.river_width = config_data['river_width']
        config.smoothing_passes = config_data['smoothing_passes']
        
        return config


# グローバルインスタンス
terrain_generator = TerrainGenerator()