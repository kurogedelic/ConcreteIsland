"""
UI管理システム
UI Management System
"""

import pyxel
from config.game_config import GameConfig
from systems.asset_manager import asset_manager
from systems.font_manager import font_manager
from systems.difficulty_manager import difficulty_manager
from config.balance_config import DifficultyLevel


class UIManager:
    """UI管理クラス"""
    
    def __init__(self):
        # UI要素の配置
        self.status_bar_height = 30
        self.info_panel_width = 200
        self.build_palette_height = 150
        
        # UI状態
        self.show_info_panel = True
        self.show_build_palette = True
        self.show_debug_info = False
        self.show_completion_screen = False
        self.completion_stats = None
        self.show_help_screen = False
        self.show_terrain_generator = False
        
        # 地形生成UI状態
        self.terrain_map_type = "coastal"
        self.terrain_seed = ""
        self.terrain_editing_seed = False
        
        # シムシティ風パレット
        self.selected_category = "residential"  # 選択中のカテゴリ
        self.selected_building_index = 0
        self.building_categories = {
            "residential": {"name": "住宅", "icon": "🏠", "buildings": []},
            "commercial": {"name": "商業", "icon": "🏪", "buildings": []},
            "industrial": {"name": "工業", "icon": "🏭", "buildings": []},
            "civic": {"name": "公共", "icon": "🏛️", "buildings": []},
            "infra": {"name": "インフラ", "icon": "🛣️", "buildings": []},
            "recreation": {"name": "娯楽", "icon": "🎪", "buildings": []},
            "special": {"name": "特殊", "icon": "⭐", "buildings": []}
        }
        self.category_keys = list(self.building_categories.keys())
        
        # UI色設定
        self.bg_color = GameConfig.COLOR_UI_BG
        self.text_color = GameConfig.COLOR_TEXT
        self.highlight_color = GameConfig.COLOR_HIGHLIGHT
        self.border_color = GameConfig.COLOR_UI_BORDER
    
    def update(self, building_manager=None):
        """UI状態を更新"""
        # UI切り替え
        if pyxel.btnp(pyxel.KEY_TAB):
            self.show_info_panel = not self.show_info_panel
        
        if pyxel.btnp(pyxel.KEY_P):
            self.show_build_palette = not self.show_build_palette
        
        # 建物カテゴリを更新
        if building_manager:
            self._update_building_categories(building_manager)
        
        # カテゴリ選択（数字キー 1-7）
        for i, category_key in enumerate(self.category_keys):
            if pyxel.btnp(pyxel.KEY_1 + i):
                self.selected_category = category_key
                self.selected_building_index = 0
        
        # デバッグ情報切り替え（F1キー）
        if pyxel.btnp(pyxel.KEY_F1):
            self.show_debug_info = not self.show_debug_info

        # 難易度変更（F5, F6, F7キー）
        if pyxel.btnp(pyxel.KEY_F5):
            difficulty_manager.set_difficulty(DifficultyLevel.EASY)
        elif pyxel.btnp(pyxel.KEY_F6):
            difficulty_manager.set_difficulty(DifficultyLevel.NORMAL)
        elif pyxel.btnp(pyxel.KEY_F7):
            difficulty_manager.set_difficulty(DifficultyLevel.HARD)

        # ヘルプ画面切り替え（F2キー）
        if pyxel.btnp(pyxel.KEY_F2):
            self.show_help_screen = not self.show_help_screen
        
        # 地形生成画面切り替え（F3キー）
        if pyxel.btnp(pyxel.KEY_F3):
            self.show_terrain_generator = not self.show_terrain_generator
            
        # 地形生成UI操作
        if self.show_terrain_generator:
            self._handle_terrain_generator_input()
        
        # 建物選択（現在のカテゴリ内）- グリッドナビゲーション対応
        current_buildings = self.building_categories[self.selected_category]["buildings"]
        if len(current_buildings) > 0:
            grid_cols = 6  # グリッドの列数
            grid_rows = 3  # グリッドの行数
            max_items = min(len(current_buildings), grid_cols * grid_rows)
            
            # 左移動 (Q/左矢印)
            if pyxel.btnp(pyxel.KEY_Q) or pyxel.btnp(pyxel.KEY_LEFT):
                if self.selected_building_index > 0:
                    self.selected_building_index -= 1
            
            # 右移動 (E/右矢印)
            if pyxel.btnp(pyxel.KEY_E) or pyxel.btnp(pyxel.KEY_RIGHT):
                if self.selected_building_index < max_items - 1:
                    self.selected_building_index += 1
            
            # 上移動 (上矢印)
            if pyxel.btnp(pyxel.KEY_UP):
                new_index = self.selected_building_index - grid_cols
                if new_index >= 0:
                    self.selected_building_index = new_index
            
            # 下移動 (下矢印)
            if pyxel.btnp(pyxel.KEY_DOWN):
                new_index = self.selected_building_index + grid_cols
                if new_index < max_items:
                    self.selected_building_index = new_index
    
    def draw(self, game_state: dict, building_manager=None):
        """UI全体を描画"""
        # ゲーム完了画面
        if self.show_completion_screen and self.completion_stats:
            self.draw_completion_screen()
            return
        
        # ヘルプ画面
        if self.show_help_screen:
            self.draw_help_screen()
            return
        
        # 地形生成画面
        if self.show_terrain_generator:
            self.draw_terrain_generator()
            return
        
        # ステータスバー
        self.draw_status_bar(game_state)
        
        # 情報パネル
        if self.show_info_panel:
            self.draw_info_panel(game_state)
        
        # 建設パレット
        if self.show_build_palette:
            self.draw_build_palette(building_manager)
        
        # デバッグ情報
        if self.show_debug_info:
            self.draw_debug_info(game_state)
    
    def draw_status_bar(self, game_state: dict):
        """ステータスバーを描画"""
        # 背景
        pyxel.rect(0, 0, GameConfig.SCREEN_WIDTH, self.status_bar_height, self.bg_color)
        pyxel.line(0, self.status_bar_height, GameConfig.SCREEN_WIDTH, self.status_bar_height, self.border_color)
        
        # 日付
        date_str = game_state.get('date', '1945年1月1日')
        font_manager.draw_text(10, 8, date_str, self.text_color)
        
        # 資金
        money = game_state.get('money', 10000)
        money_str = f"資金: ¥{money:,}"
        font_manager.draw_text(140, 8, money_str, self.text_color)
        
        # 人口
        population = game_state.get('population', 0)
        pop_str = f"人口: {population:,}人"
        font_manager.draw_text(280, 8, pop_str, self.text_color)
        
        # ゲーム速度・一時停止
        speed = game_state.get('speed', 1.0)
        paused = game_state.get('paused', False)
        if paused:
            font_manager.draw_text(450, 8, "一時停止", self.highlight_color)
        else:
            font_manager.draw_text(450, 8, f"速度: x{speed}", self.text_color)
        
        # 進行度
        progress = game_state.get('progress', 0.0)
        progress_str = f"進行: {progress*100:.1f}%"
        font_manager.draw_text(550, 8, progress_str, self.text_color)
        
        # 年代表示
        year = game_state.get('year', 1945)
        era = self._get_era_name(year)
        era_info = game_state.get('era_info', {})
        if era_info and era_info.get('period'):
            era = era_info['period'].name_jp
        font_manager.draw_text(10, 18, era, self.text_color)
    
    def draw_info_panel(self, game_state: dict):
        """情報パネルを描画"""
        x = GameConfig.SCREEN_WIDTH - self.info_panel_width
        y = self.status_bar_height
        width = self.info_panel_width
        height = GameConfig.SCREEN_HEIGHT - self.status_bar_height - self.build_palette_height
        
        # 背景
        pyxel.rect(x, y, width, height, self.bg_color)
        pyxel.rectb(x, y, width, height, self.border_color)
        
        # タイトル
        font_manager.draw_text(x + 5, y + 5, "都市情報", self.text_color)
        
        # タイル情報セクション
        stats_y = y + 25
        tile_info = game_state.get('tile_info')
        if tile_info:
            self._draw_section_header(x, stats_y, width, "タイル情報")
            stats_y += 20
            
            pos_x, pos_y = tile_info['position']
            font_manager.draw_text(x + 10, stats_y, f"位置: ({pos_x}, {pos_y})", self.text_color)
            stats_y += 14
            
            terrain_name = tile_info['terrain_name']
            font_manager.draw_text(x + 10, stats_y, f"地形: {terrain_name}", self.text_color)
            stats_y += 14
            
            # 建物情報があれば表示
            if tile_info.get('building'):
                building = tile_info['building']
                font_manager.draw_text(x + 10, stats_y, f"建物: {building}", self.text_color)
                stats_y += 14
            
            stats_y += 10  # セクション間のスペース
        else:
            stats_y += 25  # タイル情報がない場合のスペース
        
        # 統計情報
        
        # 基本統計セクション
        self._draw_section_header(x, stats_y, width, "基本データ")
        stats_y += 20
        
        money = game_state.get('money', 0)
        font_manager.draw_text(x + 10, stats_y, f"予算: ¥{money:,}", self.text_color)
        stats_y += 14
        
        population = game_state.get('population', 0)
        font_manager.draw_text(x + 10, stats_y, f"人口: {population:,}人", self.text_color)
        stats_y += 14
        
        happiness = game_state.get('happiness', 50)
        font_manager.draw_text(x + 10, stats_y, f"満足度: {happiness}%", self.text_color)
        stats_y += 25
        
        # RCI需要セクション
        self._draw_section_header(x, stats_y, width, "需要状況")
        stats_y += 20
        
        r_demand = game_state.get('r_demand', 0)
        c_demand = game_state.get('c_demand', 0)
        i_demand = game_state.get('i_demand', 0)
        
        font_manager.draw_text(x + 10, stats_y, f"住宅: {r_demand}", self.text_color)
        stats_y += 14
        font_manager.draw_text(x + 10, stats_y, f"商業: {c_demand}", self.text_color)
        stats_y += 14
        font_manager.draw_text(x + 10, stats_y, f"工業: {i_demand}", self.text_color)
        stats_y += 25
        
        # インフラセクション
        self._draw_section_header(x, stats_y, width, "インフラ")
        stats_y += 20
        
        power = game_state.get('power_usage', 0)
        power_cap = game_state.get('power_capacity', 0)
        font_manager.draw_text(x + 10, stats_y, f"電力: {power}/{power_cap}", self.text_color)
        stats_y += 14
        
        water = game_state.get('water_usage', 0)
        water_cap = game_state.get('water_capacity', 0)
        font_manager.draw_text(x + 10, stats_y, f"上水: {water}/{water_cap}", self.text_color)
        stats_y += 25
        
        # 経済情報セクション
        self._draw_section_header(x, stats_y, width, "経済状況")
        stats_y += 20
        
        rice = game_state.get('rice', 0)
        font_manager.draw_text(x + 10, stats_y, f"米: {rice}kg", self.text_color)
        stats_y += 14
        
        iron = game_state.get('iron', 0)
        font_manager.draw_text(x + 10, stats_y, f"鉄: {iron}kg", self.text_color)
        stats_y += 14
        
        wood = game_state.get('wood', 0)
        font_manager.draw_text(x + 10, stats_y, f"木材: {wood}kg", self.text_color)
        stats_y += 14
        
        coal = game_state.get('coal', 0)
        font_manager.draw_text(x + 10, stats_y, f"石炭: {coal}kg", self.text_color)
        stats_y += 20
        
        # 収支情報
        net_income = game_state.get('net_income', 0)
        income_color = self.text_color if net_income >= 0 else self.highlight_color
        font_manager.draw_text(x + 10, stats_y, f"収支: ¥{net_income:+}", income_color)
        stats_y += 14
        
        # 市場状況
        market = game_state.get('market_condition', '安定')
        font_manager.draw_text(x + 10, stats_y, f"市場: {market}", self.text_color)
        stats_y += 25
        
        # イベント情報セクション
        self._draw_section_header(x, stats_y, width, "イベント")
        stats_y += 20
        
        # 現在の季節
        current_season = game_state.get('current_season', 'spring')
        season_names = {
            'spring': '春', 'summer': '夏', 'autumn': '秋', 'winter': '冬'
        }
        season_jp = season_names.get(current_season, '春')
        font_manager.draw_text(x + 10, stats_y, f"季節: {season_jp}", self.text_color)
        stats_y += 14
        
        # アクティブイベント
        active_events = game_state.get('active_events', [])
        if active_events:
            font_manager.draw_text(x + 10, stats_y, "発生中:", self.text_color)
            stats_y += 14
            for event in active_events[:3]:  # 最大3つまで表示
                event_name = event.name_jp[:8]  # 8文字に制限
                event_color = self.highlight_color if event.severity >= 3 else self.text_color
                font_manager.draw_text(x + 15, stats_y, f"・{event_name}", event_color)
                stats_y += 14
        else:
            font_manager.draw_text(x + 10, stats_y, "平穏", self.text_color)
    
    def draw_build_palette(self, building_manager=None):
        """アイコングリッド式建設パレットを描画"""
        # アイコングリッド設定
        grid_cols = 6  # グリッドの列数
        grid_rows = 3  # グリッドの行数
        icon_size = 32  # アイコンサイズ
        padding = 4    # アイコン間の余白
        
        palette_width = grid_cols * (icon_size + padding) + padding + 10
        palette_height = grid_rows * (icon_size + padding) + padding + 60  # タイトルとタブ分追加
        x = GameConfig.SCREEN_WIDTH - palette_width - 10
        y = GameConfig.SCREEN_HEIGHT - palette_height - 10
        
        # 背景
        pyxel.rect(x, y, palette_width, palette_height, self.bg_color)
        pyxel.rectb(x, y, palette_width, palette_height, self.border_color)
        
        # タイトル
        font_manager.draw_text(x + 5, y + 5, "建設パレット", self.text_color)
        
        # カテゴリタブ描画
        tab_y = y + 18
        tab_width = palette_width // len(self.category_keys[:7])
        for i, category_key in enumerate(self.category_keys[:7]):
            category_data = self.building_categories[category_key]
            tab_x = x + i * tab_width
            
            # タブの背景色（選択中は明るく）
            if category_key == self.selected_category:
                pyxel.rect(tab_x, tab_y, tab_width - 1, 14, self.highlight_color)
                color = self.text_color
            else:
                pyxel.rect(tab_x, tab_y, tab_width - 1, 14, self.border_color)
                color = self.text_color
            
            # カテゴリ番号と名前（短縮）
            text = category_data['name'][:3]
            font_manager.draw_text(tab_x + 2, tab_y + 3, text, color)
        
        # 選択中カテゴリ名表示
        current_category = self.building_categories[self.selected_category]
        category_text = f"{current_category['name']}カテゴリ"
        font_manager.draw_text(x + 5, y + 35, category_text, self.text_color)
        
        # アイコングリッド描画
        grid_start_x = x + padding
        grid_start_y = y + 50
        current_buildings = current_category["buildings"]
        
        if not current_buildings:
            font_manager.draw_text(x + 5, grid_start_y + 20, "利用可能な建物なし", self.text_color)
            return
        
        # アイコングリッドで建物を表示
        for idx, building_id in enumerate(current_buildings[:grid_rows * grid_cols]):
            row = idx // grid_cols
            col = idx % grid_cols
            
            icon_x = grid_start_x + col * (icon_size + padding)
            icon_y = grid_start_y + row * (icon_size + padding)
            
            # 建物定義を取得
            building_def = building_manager.get_building_definition(building_id) if building_manager else None
            
            # 選択中の建物をハイライト
            if idx == self.selected_building_index:
                pyxel.rectb(icon_x - 2, icon_y - 2, icon_size + 4, icon_size + 4, self.highlight_color)
                pyxel.rect(icon_x - 1, icon_y - 1, icon_size + 2, icon_size + 2, 1)  # 黒い内枠
            
            # アイコン描画
            if building_def and asset_manager.has_sprite(building_def.icon_name):
                asset_manager.draw_sprite(building_def.icon_name, icon_x, icon_y)
            else:
                # フォールバック：色付きの四角
                pyxel.rect(icon_x, icon_y, icon_size, icon_size, self.border_color)
                pyxel.rectb(icon_x, icon_y, icon_size, icon_size, self.text_color)
                
                # 建物名の頭文字を表示
                if building_def:
                    initial = building_def.name_jp[0] if building_def.name_jp else "?"
                    font_manager.draw_text(icon_x + 12, icon_y + 12, initial, self.text_color)
        
        # 選択中の建物情報
        if 0 <= self.selected_building_index < len(current_buildings):
            building_id = current_buildings[self.selected_building_index]
            building_def = building_manager.get_building_definition(building_id) if building_manager else None
            if building_def:
                info_y = y + palette_height - 25
                info_text = f"{building_def.name_jp} ¥{building_def.cost}"
                font_manager.draw_text(x + 5, info_y, info_text, self.text_color)
                
                # サイズ情報
                size_text = f"サイズ: {building_def.size_width}x{building_def.size_height}"
                font_manager.draw_text(x + 5, info_y + 10, size_text, self.text_color)
    
    def draw_debug_info(self, game_state: dict):
        """デバッグ情報を描画"""
        debug_x = 10
        debug_y = 50

        # FPS
        fps = game_state.get('fps', 60)
        font_manager.draw_text(debug_x, debug_y, f"FPS: {fps}", self.text_color)
        debug_y += 10
        
        # カーソル位置
        cursor_pos = game_state.get('cursor_pos', (0, 0))
        font_manager.draw_text(debug_x, debug_y, f"カーソル: {cursor_pos}", self.text_color)
        debug_y += 10
        
        # グリッド位置
        grid_pos = game_state.get('grid_pos', (0, 0))
        font_manager.draw_text(debug_x, debug_y, f"グリッド: {grid_pos}", self.text_color)
        debug_y += 10
        
        # 選択ツール
        tool = game_state.get('selected_tool', 'cursor')
        tool_names = {"cursor": "選択", "build": "建設", "destroy": "破壊"}
        tool_jp = tool_names.get(tool, tool)
        font_manager.draw_text(debug_x, debug_y, f"ツール: {tool_jp}", self.text_color)
        debug_y += 15
        
        # 視界カリング統計
        culling_stats = game_state.get('culling_stats', {})
        if culling_stats:
            font_manager.draw_text(debug_x, debug_y, "視界カリング:", self.text_color)
            debug_y += 10
            
            visible = culling_stats.get('visible_cells', 0)
            total = culling_stats.get('total_cells', 0)
            rate = culling_stats.get('culling_rate', 0)
            font_manager.draw_text(debug_x, debug_y, f"描画: {visible}/{total}", self.text_color)
            debug_y += 10
            font_manager.draw_text(debug_x, debug_y, f"カリング率: {rate:.1f}%", self.text_color)
            debug_y += 10
        
        # メモリ統計
        memory_stats = game_state.get('memory_stats', {})
        if memory_stats:
            saved_mb = memory_stats.get('saved_memory_mb', 0)
            font_manager.draw_text(debug_x, debug_y, f"節約: {saved_mb:.1f}MB", self.text_color)
            debug_y += 15
        
        # キー操作ヘルプ
        font_manager.draw_text(debug_x, debug_y, "F1:デバッグ | Space:一時停止", self.text_color)
        debug_y += 10
        font_manager.draw_text(debug_x, debug_y, "WASD:カメラ | Z/X:ズーム", self.text_color)
        debug_y += 10
        font_manager.draw_text(debug_x, debug_y, "Tab:情報 | P:パレット", self.text_color)
    
    def _get_era_name(self, year: int) -> str:
        """年代に応じた時代名を取得"""
        if year < 1950:
            return "戦後復興期 (Post-war Recovery)"
        elif year < 1955:
            return "朝鮮戦争特需期 (Korean War Boom)"
        elif year < 1965:
            return "高度成長期前期 (Early High Growth)"
        else:
            return "高度成長期後期 (Late High Growth)"
    
    def _get_building_icon_by_category(self, category: str) -> str:
        """カテゴリに応じたアイコンを取得"""
        return self.building_categories[category]["icon"]
    
    def _get_building_icon(self, building_type: str) -> str:
        """建物タイプに応じたアイコンを取得"""
        icons = {
            "barracks": "🏚️",
            "small_factory": "🏭", 
            "personal_shop": "🏪",
            "road": "🛤️"
        }
        return icons.get(building_type, "🏗️")
    
    def _get_building_price(self, building_type: str) -> int:
        """建物タイプに応じた価格を取得"""
        prices = {
            "barracks": 100,
            "small_factory": 500,
            "personal_shop": 300,
            "road": 10
        }
        return prices.get(building_type, 1000)
    
    def set_debug_mode(self, enabled: bool):
        """デバッグモードを設定"""
        self.show_debug_info = enabled
    
    def _update_building_categories(self, building_manager):
        """建物カテゴリを更新"""
        # 各カテゴリの建物リストをクリア
        for category_data in self.building_categories.values():
            category_data["buildings"] = []
        
        # アンロック済み建物を各カテゴリに分類
        unlocked_buildings = building_manager.get_unlocked_buildings()
        for building in unlocked_buildings:
            category_key = building.category.value  # EnumのValueを取得
            if category_key in self.building_categories:
                self.building_categories[category_key]["buildings"].append(building.id)
    
    def get_selected_building(self) -> str:
        """選択中の建物タイプを取得"""
        current_buildings = self.building_categories[self.selected_category]["buildings"]
        if current_buildings and 0 <= self.selected_building_index < len(current_buildings):
            return current_buildings[self.selected_building_index]
        return None
    
    def show_game_completion(self, stats: dict):
        """ゲーム完了画面を表示"""
        self.show_completion_screen = True
        self.completion_stats = stats
    
    def draw_completion_screen(self):
        """ゲーム完了画面を描画"""
        # 背景を暗くする
        pyxel.rect(0, 0, GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT, 0)
        
        # 半透明の背景パネル
        panel_width = 600
        panel_height = 400
        panel_x = (GameConfig.SCREEN_WIDTH - panel_width) // 2
        panel_y = (GameConfig.SCREEN_HEIGHT - panel_height) // 2
        
        # パネル背景
        pyxel.rect(panel_x, panel_y, panel_width, panel_height, self.bg_color)
        pyxel.rectb(panel_x, panel_y, panel_width, panel_height, self.border_color)
        
        # タイトル
        title = "ゲーム完了"
        font_manager.draw_text(panel_x + panel_width // 2 - 40, panel_y + 20, title, self.text_color)
        
        # 統計情報
        y_offset = panel_y + 60
        line_height = 20
        
        # 基本情報
        font_manager.draw_text(panel_x + 30, y_offset, f"最終年: {self.completion_stats.get('final_year', 1970)}年", self.text_color)
        y_offset += line_height
        
        font_manager.draw_text(panel_x + 30, y_offset, f"最終人口: {self.completion_stats.get('final_population', 0):,}人", self.text_color)
        y_offset += line_height
        
        font_manager.draw_text(panel_x + 30, y_offset, f"最終資金: ¥{self.completion_stats.get('final_money', 0):,}", self.text_color)
        y_offset += line_height
        
        font_manager.draw_text(panel_x + 30, y_offset, f"市民幸福度: {self.completion_stats.get('final_happiness', 0)}%", self.text_color)
        y_offset += line_height * 2
        
        # スコアと評価
        score = self.completion_stats.get('score', 0)
        rating = self.completion_stats.get('rating', 'C')
        font_manager.draw_text(panel_x + 30, y_offset, f"総スコア: {score:,}点", self.text_color)
        y_offset += line_height
        
        # 評価ランクを大きく表示
        font_manager.draw_text(panel_x + 30, y_offset, f"評価ランク: ", self.text_color)
        font_manager.draw_text(panel_x + 130, y_offset, rating, self.highlight_color)
        y_offset += line_height * 2
        
        # 達成項目
        achievements = self.completion_stats.get('achievements', [])
        if achievements:
            font_manager.draw_text(panel_x + 30, y_offset, "達成項目:", self.text_color)
            y_offset += line_height
            
            for achievement in achievements[:5]:  # 最大5個まで表示
                font_manager.draw_text(panel_x + 50, y_offset, f"・{achievement}", self.text_color)
                y_offset += line_height
        
        # 操作説明
        font_manager.draw_text(panel_x + panel_width // 2 - 100, panel_y + panel_height - 40, 
                             "Spaceキーで続行 / Qキーで終了", self.text_color)
    
    def draw_help_screen(self):
        """ヘルプ画面を描画"""
        # 背景を暗くする
        pyxel.rect(0, 0, GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT, 0)
        
        # ヘルプパネル
        panel_width = 700
        panel_height = 500
        panel_x = (GameConfig.SCREEN_WIDTH - panel_width) // 2
        panel_y = (GameConfig.SCREEN_HEIGHT - panel_height) // 2
        
        # パネル背景
        pyxel.rect(panel_x, panel_y, panel_width, panel_height, self.bg_color)
        pyxel.rectb(panel_x, panel_y, panel_width, panel_height, self.border_color)
        
        # タイトル
        title = "操作方法"
        font_manager.draw_text(panel_x + panel_width // 2 - 30, panel_y + 20, title, self.text_color)
        
        # ヘルプ内容
        y_offset = panel_y + 60
        line_height = 20
        
        help_items = [
            ("カメラ操作", [
                "W/A/S/D or 矢印キー: カメラ移動",
                "Z/X: ズームイン/アウト",
                "マウス: カーソル移動"
            ]),
            ("建設操作", [
                "左クリック: 建物配置/選択",
                "右クリック: 建物削除",
                "1-7キー: 建物カテゴリ選択",
                "マウスクリック: パレットから建物選択"
            ]),
            ("UI操作", [
                "Tab: 情報パネル切り替え",
                "P: 建設パレット切り替え",
                "G: グリッド表示切り替え",
                "Space: 一時停止/再開"
            ]),
            ("時間操作", [
                "Shift+1: 速度0.5倍",
                "Shift+2: 速度1.0倍（標準）",
                "Shift+3: 速度2.0倍",
                "Shift+4: 速度5.0倍"
            ]),
            ("その他", [
                "F1: デバッグ情報表示",
                "F2: このヘルプ画面",
                "F3: 地形生成画面",
                "F5/F6/F7: 難易度変更",
                "Q: ゲーム終了"
            ])
        ]
        
        # 左右2列で表示
        column_width = panel_width // 2 - 40
        
        for i, (category, keys) in enumerate(help_items):
            # カテゴリの位置を決定（左列か右列か）
            if i < 3:
                x = panel_x + 30
                y = y_offset + i * 100
            else:
                x = panel_x + panel_width // 2 + 10
                y = y_offset + (i - 3) * 100
            
            # カテゴリ名
            font_manager.draw_text(x, y, category, self.highlight_color)
            
            # キー説明
            for j, key_desc in enumerate(keys):
                font_manager.draw_text(x + 10, y + (j + 1) * line_height, key_desc, self.text_color)
        
        # 閉じる説明
        font_manager.draw_text(panel_x + panel_width // 2 - 60, panel_y + panel_height - 40, 
                             "F2キーで閉じる", self.text_color)
    
    def _handle_terrain_generator_input(self):
        """地形生成画面の入力処理"""
        from core.event_manager import event_manager
        
        # 地形タイプ選択（1-5キー）
        terrain_types = ["island", "coastal", "inland", "peninsula", "river_valley"]
        for i, terrain_type in enumerate(terrain_types):
            if pyxel.btnp(pyxel.KEY_1 + i):
                self.terrain_map_type = terrain_type
        
        # シード値編集モード切り替え（Sキー）
        if pyxel.btnp(pyxel.KEY_S):
            self.terrain_editing_seed = not self.terrain_editing_seed
            if not self.terrain_editing_seed:
                # 編集終了時に数値チェック
                try:
                    if self.terrain_seed:
                        int(self.terrain_seed)
                except ValueError:
                    self.terrain_seed = ""
        
        # シード値編集中の文字入力
        if self.terrain_editing_seed:
            # 数字キー入力
            for i in range(10):
                if pyxel.btnp(pyxel.KEY_0 + i):
                    if len(self.terrain_seed) < 10:  # 最大10桁
                        self.terrain_seed += str(i)
            
            # バックスペース
            if pyxel.btnp(pyxel.KEY_BACKSPACE):
                if self.terrain_seed:
                    self.terrain_seed = self.terrain_seed[:-1]
        
        # 地形生成実行（Enterキー）
        if pyxel.btnp(pyxel.KEY_RETURN):
            seed = None
            if self.terrain_seed:
                try:
                    seed = int(self.terrain_seed)
                except ValueError:
                    seed = None
            
            # 地形生成イベントを発火
            event_manager.emit_event("developer_generate_terrain", {
                "map_type": self.terrain_map_type,
                "seed": seed
            })
            
            # 画面を閉じる
            self.show_terrain_generator = False
        
        # ランダムシード生成（Rキー）
        if pyxel.btnp(pyxel.KEY_R):
            import random
            self.terrain_seed = str(random.randint(1, 999999))
    
    def draw_terrain_generator(self):
        """地形生成画面を描画"""
        # 背景を暗くする
        pyxel.rect(0, 0, GameConfig.SCREEN_WIDTH, GameConfig.SCREEN_HEIGHT, 0)
        
        # パネル設定
        panel_width = 500
        panel_height = 400
        panel_x = (GameConfig.SCREEN_WIDTH - panel_width) // 2
        panel_y = (GameConfig.SCREEN_HEIGHT - panel_height) // 2
        
        # パネル背景
        pyxel.rect(panel_x, panel_y, panel_width, panel_height, self.bg_color)
        pyxel.rectb(panel_x, panel_y, panel_width, panel_height, self.border_color)
        
        # タイトル
        title = "地形生成"
        font_manager.draw_text(panel_x + panel_width // 2 - 30, panel_y + 20, title, self.text_color)
        
        y_offset = panel_y + 60
        line_height = 25
        
        # 地形タイプ選択
        font_manager.draw_text(panel_x + 30, y_offset, "地形タイプ:", self.text_color)
        y_offset += line_height
        
        terrain_types = [
            ("island", "島", "1"),
            ("coastal", "海岸", "2"),
            ("inland", "内陸", "3"),
            ("peninsula", "半島", "4"),
            ("river_valley", "河川流域", "5")
        ]
        
        for terrain_type, name_jp, key in terrain_types:
            color = self.highlight_color if terrain_type == self.terrain_map_type else self.text_color
            text = f"[{key}] {name_jp}"
            if terrain_type == self.terrain_map_type:
                text = f"► {text}"
            font_manager.draw_text(panel_x + 50, y_offset, text, color)
            y_offset += 20
        
        y_offset += 10
        
        # シード値設定
        font_manager.draw_text(panel_x + 30, y_offset, "シード値:", self.text_color)
        y_offset += line_height
        
        # シード入力欄
        seed_box_x = panel_x + 50
        seed_box_y = y_offset - 5
        seed_box_width = 200
        seed_box_height = 20
        
        # 入力欄の背景
        input_bg_color = 1 if self.terrain_editing_seed else 5
        pyxel.rect(seed_box_x, seed_box_y, seed_box_width, seed_box_height, input_bg_color)
        pyxel.rectb(seed_box_x, seed_box_y, seed_box_width, seed_box_height, self.border_color)
        
        # シード値表示
        display_seed = self.terrain_seed if self.terrain_seed else "ランダム"
        if self.terrain_editing_seed and len(self.terrain_seed) < 10:
            display_seed += "_"  # カーソル表示
        
        font_manager.draw_text(seed_box_x + 5, seed_box_y + 5, display_seed, self.text_color)
        
        y_offset += 35
        
        # シード編集説明
        edit_text = "[S] シード編集" if not self.terrain_editing_seed else "[S] 編集終了"
        font_manager.draw_text(panel_x + 50, y_offset, edit_text, self.text_color)
        y_offset += 20
        
        font_manager.draw_text(panel_x + 50, y_offset, "[R] ランダム生成", self.text_color)
        y_offset += 30
        
        # 操作説明
        font_manager.draw_text(panel_x + 30, y_offset, "操作:", self.highlight_color)
        y_offset += 20
        
        font_manager.draw_text(panel_x + 50, y_offset, "[Enter] 地形生成実行", self.text_color)
        y_offset += 20
        
        font_manager.draw_text(panel_x + 50, y_offset, "[F3] キャンセル", self.text_color)
        
        # 注意事項
        y_offset += 30
        font_manager.draw_text(panel_x + 30, y_offset, "※現在の地形は失われます", 8)  # 警告色
    
    def _draw_section_header(self, x: int, y: int, width: int, title: str):
        """情報パネルのセクションヘッダーを描画"""
        # ヘッダー背景
        header_width = width - 10
        pyxel.rect(x + 5, y - 2, header_width, 16, self.border_color)
        
        # ヘッダーテキスト
        font_manager.draw_text(x + 8, y + 2, title, 0)  # 黒文字でコントラスト