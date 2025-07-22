"""
ゲームエンジン
Main Game Engine
"""

import pyxel
from config.game_config import GameConfig
from core.event_manager import event_manager
from core.time_manager import TimeManager
from systems.grid_system import GridSystem
from systems.cursor_system import CursorSystem
from systems.asset_manager import asset_manager
from systems.ui_manager import UIManager
from systems.building_manager import BuildingManager
from systems.population_manager import PopulationManager
from systems.economy_manager import EconomyManager
from systems.technology_manager import TechnologyManager
from systems.event_system import EventSystem
from systems.font_manager import font_manager
from systems.animation_manager import animation_manager
from systems.difficulty_manager import difficulty_manager
from systems.game_completion import GameCompletionSystem


class GameEngine:
    """メインゲームエンジンクラス"""
    
    def __init__(self):
        self.time_manager = TimeManager()
        self.grid_system = GridSystem()
        self.cursor_system = CursorSystem()
        self.ui_manager = UIManager()
        self.building_manager = BuildingManager()
        self.population_manager = PopulationManager()
        self.economy_manager = EconomyManager()
        self.technology_manager = TechnologyManager()
        self.event_system = EventSystem()
        self.game_completion = GameCompletionSystem()
        
        # ゲーム状態
        self.running = True
        self.debug_mode = False
        self.game_completed = False
        
        # イベントリスナーを登録
        self._register_event_listeners()
        
        # システムを初期化
        self._initialize_systems()
        
        # システム間の参照を設定
        self.cursor_system.set_grid_system(self.grid_system)
    
    def _register_event_listeners(self):
        """イベントリスナーを登録"""
        event_manager.register_listener("year_changed", self._on_year_changed)
        event_manager.register_listener("game_paused", self._on_game_paused)
        event_manager.register_listener("game_resumed", self._on_game_resumed)
        event_manager.register_listener("build_requested", self._on_build_requested)
        event_manager.register_listener("game_completed", self._on_game_completed)
    
    def _initialize_systems(self):
        """各システムを初期化"""
        self.grid_system.initialize()
        self.cursor_system.initialize()
        
        # フォントを読み込み
        font_manager.load_default_fonts()
        
        # アセットを読み込み
        asset_manager.load_all_assets()
        self.building_manager.load_building_definitions()
        
        # 初期人口設定（建物配置後）
        self._setup_initial_population()
    
    def update(self):
        """メインアップデートループ"""
        if not self.running:
            return
        
        # 入力処理
        self._handle_input()
        
        # システム更新
        self.time_manager.update()
        self.cursor_system.update()
        self.grid_system.update()
        self.ui_manager.update(self.building_manager)
        self.building_manager.update(self.time_manager.current_year)
        self.population_manager.update(
            self.time_manager.current_year, 
            self.time_manager.current_month,
            self.building_manager
        )
        self.economy_manager.update(
            self.time_manager.current_year,
            self.time_manager.current_month,
            self.building_manager,
            self.population_manager
        )
        self.technology_manager.update(
            self.time_manager.current_year,
            self.time_manager.current_month
        )
        
        # イベントシステム更新
        game_state_for_events = {
            'population': int(self.population_manager.get_statistics()['total_population']),
            'money': self.economy_manager.get_economic_summary()['money'],
            'year': self.time_manager.current_year,
            'month': self.time_manager.current_month
        }
        self.event_system.update(
            self.time_manager.current_year,
            self.time_manager.current_month,
            game_state_for_events
        )
        
        # 選択中の建物をカーソルシステムに設定
        selected_building = self.ui_manager.get_selected_building()
        if selected_building:
            # 建物のサイズ情報を取得
            building_def = self.building_manager.get_building_definition(selected_building)
            if building_def:
                building_size = (building_def.size_width, building_def.size_height)
                self.cursor_system.set_selected_building(selected_building, building_size)
            else:
                self.cursor_system.set_selected_building(selected_building)
        
        # イベント処理
        event_manager.process_events()
        
        # ゲーム完了チェック
        if self.time_manager.current_year >= GameConfig.END_YEAR and not self.game_completed:
            self._prepare_game_completion()
    
    def draw(self):
        """メイン描画ループ"""
        pyxel.cls(GameConfig.COLOR_GRASS)
        
        # グリッド描画
        self.grid_system.draw()
        
        # 建物描画
        self._draw_buildings()
        
        # 住民描画
        self._draw_citizens()
        
        # カーソル描画
        self.cursor_system.draw()
        
        # UI描画
        self._draw_ui()
    
    def _handle_input(self):
        """入力処理"""
        # デバッグモード切り替え
        if pyxel.btnp(pyxel.KEY_F1):
            self.debug_mode = not self.debug_mode
            self.ui_manager.set_debug_mode(self.debug_mode)
        
        # ポーズ切り替え
        if pyxel.btnp(pyxel.KEY_SPACE):
            self.time_manager.toggle_pause()
        
        # ゲーム速度調整（Shift+数字キー）
        if pyxel.btn(pyxel.KEY_SHIFT):
            if pyxel.btnp(pyxel.KEY_1):
                self.time_manager.set_speed(0.5)
            elif pyxel.btnp(pyxel.KEY_2):
                self.time_manager.set_speed(1.0)
            elif pyxel.btnp(pyxel.KEY_3):
                self.time_manager.set_speed(2.0)
            elif pyxel.btnp(pyxel.KEY_4):
                self.time_manager.set_speed(5.0)
        
        # カーソルシステムに入力を渡す
        self.cursor_system.handle_input()
    
    def _draw_ui(self):
        """UI描画"""
        # 統計情報を取得
        pop_stats = self.population_manager.get_statistics()
        building_stats = self.building_manager.get_statistics()
        economy_stats = self.economy_manager.get_economic_summary()
        tech_stats = self.technology_manager.get_current_era_info()
        event_stats = self.event_system.get_event_summary()
        
        # ゲーム状態を準備
        game_state = {
            'date': self.time_manager.get_date_string(),
            'year': self.time_manager.current_year,
            'money': economy_stats['money'],
            'population': int(pop_stats['total_population']),
            'happiness': int(pop_stats['average_happiness']),
            'speed': self.time_manager.game_speed,
            'paused': self.time_manager.paused,
            'progress': self.time_manager.get_progress_ratio(),
            'cursor_pos': self.cursor_system.get_cursor_position(),
            'grid_pos': self.cursor_system.get_grid_position(),
            'selected_tool': self.cursor_system.get_selected_tool(),
            'r_demand': max(0, 50 - int(pop_stats['available_housing'])),  # 住宅需要
            'c_demand': min(100, int(pop_stats['total_population'] / 10)),  # 商業需要
            'i_demand': min(100, int(pop_stats['unemployed_population'])),  # 工業需要
            'power_usage': building_stats.get('power_consumption', 0),
            'power_capacity': building_stats.get('power_production', 0),
            'water_usage': building_stats.get('water_consumption', 0),
            'water_capacity': building_stats.get('water_production', 0),
            # 経済データ
            'rice': economy_stats['rice'],
            'iron': economy_stats['iron'],
            'wood': economy_stats['wood'],
            'coal': economy_stats['coal'],
            'electricity': economy_stats['electricity'],
            'monthly_income': economy_stats['monthly_income'],
            'monthly_expenses': economy_stats['monthly_expenses'],
            'net_income': economy_stats['net_income'],
            'market_condition': economy_stats['market_condition'],
            'era_info': tech_stats,
            'event_info': event_stats,
            'current_season': event_stats['current_season'],
            'active_events': self.event_system.get_active_events(),
            # パフォーマンス統計（デバッグモード用）
            'culling_stats': self.grid_system.get_culling_stats() if self.debug_mode else {},
            'memory_stats': self.grid_system.get_memory_stats() if self.debug_mode else {},
            'elapsed_time': pyxel.frame_count / 60.0  # FPS計算用
        }
        
        # UIManager経由で描画
        self.ui_manager.draw(game_state, self.building_manager)
    
    def _draw_buildings(self):
        """建物を描画（視界カリング対応）"""
        # 建物リストを視界カリングでフィルタリング
        visible_buildings = self.grid_system.viewport_culling.cull_objects(
            self.building_manager.buildings, 
            lambda building: (building.x, building.y)
        )
        
        for building in visible_buildings:
            screen_x, screen_y = self.grid_system.grid_to_screen(building.x, building.y)
            screen_x += self.grid_system.camera_x
            screen_y += self.grid_system.camera_y
            
            # アニメーションスプライトを優先して使用
            animated_sprite = animation_manager.get_tile_sprite(building.x, building.y)
            if animated_sprite and asset_manager.has_sprite(animated_sprite):
                # アセットを1タイルに合わせて描画
                asset_manager.draw_sprite(animated_sprite, 
                                        screen_x - 16 + GameConfig.ASSET_OFFSET_X, 
                                        screen_y - 16 + GameConfig.ASSET_OFFSET_Y)
            else:
                # 通常のスプライト描画
                asset_manager.draw_sprite(building.definition.sprite_name, 
                                        screen_x - 16 + GameConfig.ASSET_OFFSET_X, 
                                        screen_y - 16 + GameConfig.ASSET_OFFSET_Y)
    
    def _draw_citizens(self):
        """住民を描画（視界カリング対応）"""
        # 住民リストを視界カリングでフィルタリング
        visible_citizens = self.grid_system.viewport_culling.cull_objects(
            self.population_manager.citizens,
            lambda citizen: (citizen.x, citizen.y)
        )
        
        for citizen in visible_citizens:
            screen_x, screen_y = self.grid_system.grid_to_screen(citizen.x, citizen.y)
            screen_x += self.grid_system.camera_x
            screen_y += self.grid_system.camera_y
            
            # 小さなドットで住民を表示
            citizen_color = GameConfig.COLOR_TEXT
            if citizen.moving:
                citizen_color = GameConfig.COLOR_HIGHLIGHT
            
            pyxel.pset(screen_x, screen_y, citizen_color)
    
    def _setup_initial_population(self):
        """初期人口を設定"""
        # いくつかの初期建物を配置
        initial_buildings = [
            ("barrack_house", 5, 5),
            ("barrack_house", 7, 5),
            ("small_shop", 6, 7),
            ("road", 5, 6),
            ("road", 6, 6),
            ("road", 7, 6)
        ]
        
        for building_id, x, y in initial_buildings:
            self.building_manager.place_building(
                building_id, x, y, self.time_manager.current_year, self.grid_system
            )
        
        # 初期人口を設定
        self.population_manager.initialize_population(self.building_manager)
    
    
    def _on_year_changed(self, new_year):
        """年変更イベントハンドラ"""
        print(f"Year changed to: {new_year}")
        # 技術アンロック等の処理（将来実装）
    
    def _on_game_paused(self):
        """ゲーム一時停止イベントハンドラ"""
        print("Game paused")
    
    def _on_game_resumed(self):
        """ゲーム再開イベントハンドラ"""
        print("Game resumed")
    
    def _on_build_requested(self, x: int, y: int, building_id: str):
        """建設要求イベントハンドラ"""
        if building_id:
            building_definition = self.building_manager.get_building_definition(building_id)
            current_year = self.time_manager.current_year
            
            if building_definition and self.economy_manager.can_afford_building(building_definition, current_year):
                if self.economy_manager.purchase_building(building_definition, current_year):
                    building = self.building_manager.place_building(
                        building_id, x, y, current_year, self.grid_system
                    )
                    if building:
                        print(f"Successfully placed {building.name_jp}")
                else:
                    print(f"Cannot afford {building_definition.name_jp}")
            else:
                print(f"建設費用が不足しています")
    
    def _prepare_game_completion(self):
        """ゲーム完了の準備"""
        # 統計情報を収集
        pop_stats = self.population_manager.get_statistics()
        building_stats = self.building_manager.get_statistics()
        economy_stats = self.economy_manager.get_economic_summary()
        
        # 建物の内訳を取得
        building_breakdown = {}
        for building in self.building_manager.buildings:
            building_id = building.definition.id
            building_breakdown[building_id] = building_breakdown.get(building_id, 0) + 1
        
        # ゲーム状態をまとめる
        game_state = {
            "year": self.time_manager.current_year,
            "population": int(pop_stats['total_population']),
            "money": economy_stats['money'],
            "happiness": int(pop_stats['average_happiness']),
            "total_buildings": len(self.building_manager.buildings),
            "building_breakdown": building_breakdown,
            "total_income": economy_stats.get('total_income', 0),
            "total_expenses": economy_stats.get('total_expenses', 0),
            "economic_growth": economy_stats.get('economic_growth', 0),
            "tech_progress": self.technology_manager.get_progress(),
            "no_disasters": not self.event_system.has_disasters_occurred(),
            "full_employment": pop_stats.get('unemployed_population', 0) < pop_stats['total_population'] * 0.05
        }
        
        # 完了統計を計算
        self.game_completion.calculate_completion_stats(game_state)
    
    def _on_game_completed(self, stats: dict):
        """ゲーム完了イベントハンドラ"""
        self.game_completed = True
        print("\n" + "="*50)
        print("ゲーム完了！")
        print("="*50)
        
        # 完了メッセージを表示
        messages = self.game_completion.format_completion_message()
        for message in messages:
            print(message)
        
        # UIに完了画面を表示
        self.ui_manager.show_game_completion(stats)
        
        # ゲームを一時停止
        self.time_manager.pause()
    
    def shutdown(self):
        """ゲーム終了処理"""
        self.running = False
        event_manager.clear_all_listeners()