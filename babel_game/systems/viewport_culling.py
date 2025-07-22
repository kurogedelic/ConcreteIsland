"""
視界カリングシステム
Viewport Culling System
"""

from typing import Tuple, List, Set
from config.game_config import GameConfig


class ViewportCulling:
    """視界カリング管理クラス"""
    
    def __init__(self):
        self.screen_width = GameConfig.SCREEN_WIDTH
        self.screen_height = GameConfig.SCREEN_HEIGHT
        self.cell_size = GameConfig.CELL_SIZE
        
        # カリング用のマージン（画面外でも少し余分に描画）
        self.margin = 5  # セル数（より大きなマージンで安全に）
        
        # 視界内のセル範囲
        self.visible_min_x = 0
        self.visible_max_x = 0
        self.visible_min_y = 0
        self.visible_max_y = 0
        
        # 統計情報
        self.total_cells = 0
        self.visible_cells = 0
        self.culled_cells = 0
    
    def update_viewport(self, camera_x: int, camera_y: int, zoom: float, 
                       grid_width: int, grid_height: int):
        """視界範囲を更新"""
        # スクリーン座標からグリッド座標への変換
        # 画面の四隅のグリッド座標を計算
        corners = [
            (0, 0),                                    # 左上
            (self.screen_width, 0),                    # 右上
            (0, self.screen_height),                   # 左下
            (self.screen_width, self.screen_height)    # 右下
        ]
        
        min_x, max_x = grid_width, 0
        min_y, max_y = grid_height, 0
        
        for screen_x, screen_y in corners:
            # カメラオフセットを考慮
            world_x = screen_x - camera_x
            world_y = screen_y - camera_y
            
            # ズームを考慮
            world_x /= zoom
            world_y /= zoom
            
            # グリッド座標に変換（GridSystemのscreen_to_gridと同じ計算）
            # 画面中央オフセットを除去
            world_x -= GameConfig.ISO_OFFSET_X
            world_y -= GameConfig.ISO_OFFSET_Y
            
            # 等角投影逆変換
            grid_x = int((world_x / (self.cell_size // 2) + world_y / (self.cell_size // 4)) / 2)
            grid_y = int((world_y / (self.cell_size // 4) - world_x / (self.cell_size // 2)) / 2)
            
            # 範囲を更新
            min_x = min(min_x, grid_x)
            max_x = max(max_x, grid_x)
            min_y = min(min_y, grid_y)
            max_y = max(max_y, grid_y)
        
        # マージンを追加
        self.visible_min_x = max(0, min_x - self.margin)
        self.visible_max_x = min(grid_width - 1, max_x + self.margin)
        self.visible_min_y = max(0, min_y - self.margin)
        self.visible_max_y = min(grid_height - 1, max_y + self.margin)
        
        # 統計情報を更新
        self.total_cells = grid_width * grid_height
        self.visible_cells = (self.visible_max_x - self.visible_min_x + 1) * \
                           (self.visible_max_y - self.visible_min_y + 1)
        self.culled_cells = self.total_cells - self.visible_cells
    
    def is_cell_visible(self, grid_x: int, grid_y: int) -> bool:
        """セルが視界内にあるかチェック"""
        return (self.visible_min_x <= grid_x <= self.visible_max_x and
                self.visible_min_y <= grid_y <= self.visible_max_y)
    
    def get_visible_range(self) -> Tuple[int, int, int, int]:
        """視界内のセル範囲を取得"""
        return (self.visible_min_x, self.visible_min_y, 
                self.visible_max_x, self.visible_max_y)
    
    def get_visible_cells(self, grid_width: int, grid_height: int) -> List[Tuple[int, int]]:
        """視界内のセル座標リストを取得"""
        visible_cells = []
        for y in range(self.visible_min_y, min(self.visible_max_y + 1, grid_height)):
            for x in range(self.visible_min_x, min(self.visible_max_x + 1, grid_width)):
                visible_cells.append((x, y))
        return visible_cells
    
    def cull_objects(self, objects: List[any], get_position_func) -> List[any]:
        """オブジェクトリストから視界外のものをカリング"""
        visible_objects = []
        for obj in objects:
            x, y = get_position_func(obj)
            if self.is_cell_visible(x, y):
                visible_objects.append(obj)
        return visible_objects
    
    def get_culling_stats(self) -> dict:
        """カリング統計情報を取得"""
        culling_rate = (self.culled_cells / self.total_cells * 100) if self.total_cells > 0 else 0
        return {
            'total_cells': self.total_cells,
            'visible_cells': self.visible_cells,
            'culled_cells': self.culled_cells,
            'culling_rate': culling_rate,
            'visible_range': {
                'min_x': self.visible_min_x,
                'max_x': self.visible_max_x,
                'min_y': self.visible_min_y,
                'max_y': self.visible_max_y
            }
        }
    
    def optimize_draw_order(self, visible_cells: List[Tuple[int, int]]) -> List[Tuple[int, int]]:
        """描画順序を最適化（後ろから前へ）"""
        # 等角投影では、y座標が小さい（画面上部）ものから描画
        # 同じy座標の場合、x座標が小さいものから描画
        return sorted(visible_cells, key=lambda cell: (cell[1], cell[0]))
    
    def estimate_memory_usage(self) -> dict:
        """メモリ使用量を推定"""
        # 各セルのメモリ使用量を推定（バイト）
        cell_memory = 32  # 地形データ、建物参照など
        sprite_memory = 4096  # スプライトデータ（32x32 RGBA）
        
        total_memory = self.total_cells * cell_memory
        visible_memory = self.visible_cells * (cell_memory + sprite_memory)
        saved_memory = (self.culled_cells * sprite_memory) / 1024 / 1024  # MB
        
        return {
            'total_memory_mb': total_memory / 1024 / 1024,
            'visible_memory_mb': visible_memory / 1024 / 1024,
            'saved_memory_mb': saved_memory
        }