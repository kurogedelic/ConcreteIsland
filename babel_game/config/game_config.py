"""
ゲーム設定管理
Game Configuration Management
"""

class GameConfig:
    """ゲーム設定を管理するクラス"""
    
    # 画面設定
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    
    # グリッド設定
    GRID_WIDTH = 32
    GRID_HEIGHT = 32
    CELL_SIZE = 32
    
    # 等角投影設定
    ISO_OFFSET_X = SCREEN_WIDTH // 2
    ISO_OFFSET_Y = SCREEN_HEIGHT // 2
    
    # アセット描画オフセット (1タイルに合わせる)
    ASSET_OFFSET_X = -16  # アセットの中心調整（半タイル左へ）
    ASSET_OFFSET_Y = -8   # アセットの高さ調整（半タイル上へ）
    
    # ゲーム設定
    START_YEAR = 1945
    END_YEAR = 1970
    START_MONEY = 10000  # 初期資金（円）
    
    # UI設定
    INFO_PANEL_WIDTH = 200
    BUILD_PALETTE_HEIGHT = 150
    
    # パフォーマンス設定
    TARGET_FPS = 60
    MAX_CITIZENS = 10000
    
    # ファイルパス
    BUILDINGS_JSON = "data/buildings.json"
    ASSETS_PATH = "../assets/"
    FONTS_PATH = "../fonts/"
    
    # 色設定（Pyxel色番号）
    COLOR_GRASS = 3     # 緑
    COLOR_DIRT = 4      # 茶色
    COLOR_WATER = 12    # 青
    COLOR_ROAD = 6      # グレー
    COLOR_UI_BG = 5     # 暗灰色
    COLOR_UI_BORDER = 6 # 明灰色
    COLOR_TEXT = 7      # 白
    COLOR_HIGHLIGHT = 8 # 赤
    
    @classmethod
    def load_from_file(cls, filepath):
        """設定ファイルから設定を読み込み（将来実装）"""
        pass
    
    @classmethod
    def save_to_file(cls, filepath):
        """設定をファイルに保存（将来実装）"""
        pass