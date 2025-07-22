"""
開発者モード・神モード
Developer Mode & God Mode for development support
"""

import pyxel
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum
from core.event_manager import event_manager
from config.game_config import GameConfig


class DevModeType(Enum):
    """開発モードタイプ"""
    NORMAL = "normal"          # 通常モード
    DEBUG = "debug"            # デバッグモード  
    GOD = "god"               # 神モード
    CREATIVE = "creative"      # クリエイティブモード


@dataclass
class DevCommand:
    """開発者コマンド"""
    command: str
    description: str
    action: callable
    enabled: bool = True


class DeveloperMode:
    """開発者モード管理クラス"""
    
    def __init__(self):
        self.current_mode = DevModeType.NORMAL
        self.god_mode_enabled = False
        self.infinite_money = False
        self.no_building_restrictions = False
        self.no_resource_requirements = False
        self.time_frozen = False
        self.unlock_all_buildings = False
        self.invincible_buildings = False
        
        # コンソール機能
        self.show_dev_console = False
        self.console_commands: List[DevCommand] = []
        self.console_log: List[str] = []
        self.max_log_entries = 20
        
        # 統計表示
        self.show_performance_stats = False
        self.show_memory_stats = False
        self.show_building_stats = False
        
        # チート機能
        self.fast_construction = False
        self.instant_population_growth = False
        self.no_disasters = False
        
        # 開発者コマンドを登録
        self._register_dev_commands()
        
        # イベントリスナー登録
        self._register_event_listeners()
    
    def _register_dev_commands(self):
        """開発者コマンドを登録"""
        self.console_commands = [
            DevCommand("god", "神モード切り替え", self.toggle_god_mode),
            DevCommand("money <amount>", "資金設定", self.set_money),
            DevCommand("addmoney <amount>", "資金追加", self.add_money),
            DevCommand("unlock", "全建物アンロック", self.unlock_all),
            DevCommand("build <building> <x> <y>", "建物配置", self.force_build),
            DevCommand("clear", "マップクリア", self.clear_map),
            DevCommand("time <year> <month>", "時間設定", self.set_time),
            DevCommand("freeze", "時間停止切り替え", self.toggle_time_freeze),
            DevCommand("speed <multiplier>", "ゲーム速度設定", self.set_game_speed),
            DevCommand("population <amount>", "人口設定", self.set_population),
            DevCommand("stats", "統計表示切り替え", self.toggle_stats),
            DevCommand("noevent", "イベント無効化", self.toggle_no_events),
            DevCommand("invincible", "建物無敵化", self.toggle_invincible),
            DevCommand("help", "コマンド一覧", self.show_help)
        ]
    
    def _register_event_listeners(self):
        """イベントリスナーを登録"""
        event_manager.register_listener("key_pressed", self._on_key_pressed)
        event_manager.register_listener("economy_check", self._on_economy_check)
        event_manager.register_listener("building_check", self._on_building_check)
    
    def update(self):
        """開発者モードを更新"""
        # F12で神モード切り替え
        if pyxel.btnp(pyxel.KEY_F12):
            self.toggle_god_mode()
        
        # Ctrl+` で開発者コンソール切り替え
        if pyxel.btn(pyxel.KEY_CTRL) and pyxel.btnp(pyxel.KEY_GRAVE):
            self.toggle_dev_console()
        
        # F11でパフォーマンス統計切り替え
        if pyxel.btnp(pyxel.KEY_F11):
            self.toggle_performance_stats()
        
        # 神モードの効果を適用
        if self.god_mode_enabled:
            self._apply_god_mode_effects()
    
    def toggle_god_mode(self):
        """神モード切り替え"""
        self.god_mode_enabled = not self.god_mode_enabled
        
        if self.god_mode_enabled:
            self.current_mode = DevModeType.GOD
            self.infinite_money = True
            self.no_building_restrictions = True
            self.no_resource_requirements = True
            self.unlock_all_buildings = True
            self.invincible_buildings = True
            self.no_disasters = True
            
            self.log("神モード有効化：全制限解除")
            event_manager.emit_event("god_mode_enabled", {})
        else:
            self.current_mode = DevModeType.NORMAL
            self.infinite_money = False
            self.no_building_restrictions = False
            self.no_resource_requirements = False
            self.unlock_all_buildings = False
            self.invincible_buildings = False
            
            self.log("神モード無効化：通常モード復帰")
            event_manager.emit_event("god_mode_disabled", {})
    
    def toggle_dev_console(self):
        """開発者コンソール切り替え"""
        self.show_dev_console = not self.show_dev_console
        self.log(f"開発者コンソール: {'表示' if self.show_dev_console else '非表示'}")
    
    def toggle_performance_stats(self):
        """パフォーマンス統計表示切り替え"""
        self.show_performance_stats = not self.show_performance_stats
        self.log(f"パフォーマンス統計: {'表示' if self.show_performance_stats else '非表示'}")
    
    def _apply_god_mode_effects(self):
        """神モードの効果を適用"""
        # 経済システムに無限資金設定を通知
        if self.infinite_money:
            event_manager.emit_event("developer_infinite_money", {})
        
        # 建設制限解除を通知
        if self.no_building_restrictions:
            event_manager.emit_event("developer_no_restrictions", {})
    
    def log(self, message: str):
        """コンソールログに追加"""
        self.console_log.append(message)
        if len(self.console_log) > self.max_log_entries:
            self.console_log.pop(0)
        print(f"[DEV] {message}")
    
    def execute_command(self, command: str) -> bool:
        """コマンドを実行"""
        parts = command.strip().split()
        if not parts:
            return False
        
        cmd = parts[0].lower()
        args = parts[1:] if len(parts) > 1 else []
        
        # 基本コマンド処理
        if cmd == "god":
            self.toggle_god_mode()
            return True
        elif cmd == "money" and args:
            try:
                amount = int(args[0])
                self.set_money(amount)
                return True
            except ValueError:
                self.log("エラー: 無効な金額")
                return False
        elif cmd == "addmoney" and args:
            try:
                amount = int(args[0])
                self.add_money(amount)
                return True
            except ValueError:
                self.log("エラー: 無効な金額")
                return False
        elif cmd == "unlock":
            self.unlock_all()
            return True
        elif cmd == "clear":
            self.clear_map()
            return True
        elif cmd == "freeze":
            self.toggle_time_freeze()
            return True
        elif cmd == "stats":
            self.toggle_stats()
            return True
        elif cmd == "help":
            self.show_help()
            return True
        
        self.log(f"不明なコマンド: {cmd}")
        return False
    
    def set_money(self, amount: int):
        """資金設定"""
        event_manager.emit_event("developer_set_money", {"amount": amount})
        self.log(f"資金を {amount:,}円 に設定")
    
    def add_money(self, amount: int):
        """資金追加"""
        event_manager.emit_event("developer_add_money", {"amount": amount})
        self.log(f"資金を {amount:,}円 追加")
    
    def unlock_all(self):
        """全建物アンロック"""
        event_manager.emit_event("developer_unlock_all", {})
        self.log("全建物をアンロックしました")
    
    def force_build(self, building_id: str, x: int, y: int):
        """強制建物配置"""
        event_manager.emit_event("developer_force_build", {
            "building_id": building_id,
            "x": x,
            "y": y
        })
        self.log(f"建物 {building_id} を ({x},{y}) に強制配置")
    
    def clear_map(self):
        """マップクリア"""
        event_manager.emit_event("developer_clear_map", {})
        self.log("マップをクリアしました")
    
    def set_time(self, year: int, month: int):
        """時間設定"""
        event_manager.emit_event("developer_set_time", {
            "year": year,
            "month": month
        })
        self.log(f"時間を {year}年{month}月 に設定")
    
    def toggle_time_freeze(self):
        """時間停止切り替え"""
        self.time_frozen = not self.time_frozen
        event_manager.emit_event("developer_time_freeze", {"frozen": self.time_frozen})
        self.log(f"時間: {'停止' if self.time_frozen else '再開'}")
    
    def set_game_speed(self, multiplier: float):
        """ゲーム速度設定"""
        event_manager.emit_event("developer_set_speed", {"speed": multiplier})
        self.log(f"ゲーム速度を {multiplier}倍 に設定")
    
    def set_population(self, amount: int):
        """人口設定"""
        event_manager.emit_event("developer_set_population", {"population": amount})
        self.log(f"人口を {amount:,}人 に設定")
    
    def toggle_stats(self):
        """統計表示切り替え"""
        self.show_building_stats = not self.show_building_stats
        self.log(f"建物統計: {'表示' if self.show_building_stats else '非表示'}")
    
    def toggle_no_events(self):
        """イベント無効化切り替え"""
        self.no_disasters = not self.no_disasters
        event_manager.emit_event("developer_toggle_events", {"disabled": self.no_disasters})
        self.log(f"イベント: {'無効' if self.no_disasters else '有効'}")
    
    def toggle_invincible(self):
        """建物無敵化切り替え"""
        self.invincible_buildings = not self.invincible_buildings
        event_manager.emit_event("developer_invincible_buildings", {"enabled": self.invincible_buildings})
        self.log(f"建物無敵化: {'有効' if self.invincible_buildings else '無効'}")
    
    def show_help(self):
        """ヘルプ表示"""
        self.log("=== 開発者コマンド一覧 ===")
        for cmd in self.console_commands:
            if cmd.enabled:
                self.log(f"{cmd.command}: {cmd.description}")
    
    def draw_dev_overlay(self, game_state: Dict[str, Any]):
        """開発者オーバーレイを描画"""
        if not (self.god_mode_enabled or self.show_dev_console or self.show_performance_stats):
            return
        
        # 神モード表示
        if self.god_mode_enabled:
            self._draw_god_mode_indicator()
        
        # 開発者コンソール
        if self.show_dev_console:
            self._draw_dev_console()
        
        # パフォーマンス統計
        if self.show_performance_stats:
            self._draw_performance_stats(game_state)
    
    def _draw_god_mode_indicator(self):
        """神モードインジケーターを描画"""
        # 右上に神モード表示
        text = "神モード"
        x = GameConfig.SCREEN_WIDTH - 80
        y = 10
        
        # 背景
        pyxel.rect(x - 5, y - 3, 70, 16, 8)  # 赤背景
        pyxel.rectb(x - 5, y - 3, 70, 16, 7)  # 白枠
        
        # テキスト
        pyxel.text(x, y, text, 7)
        pyxel.text(x, y + 8, "F12:OFF", 7)
    
    def _draw_dev_console(self):
        """開発者コンソールを描画"""
        console_height = 200
        console_y = GameConfig.SCREEN_HEIGHT - console_height
        
        # 背景
        pyxel.rect(0, console_y, GameConfig.SCREEN_WIDTH, console_height, 0)
        pyxel.rectb(0, console_y, GameConfig.SCREEN_WIDTH, console_height, 7)
        
        # タイトル
        pyxel.text(5, console_y + 5, "Developer Console (Ctrl+` to close)", 7)
        
        # ログ表示
        log_y = console_y + 20
        for i, log_entry in enumerate(self.console_log[-10:]):  # 最新10件
            pyxel.text(5, log_y + i * 8, log_entry[:90], 6)  # 90文字制限
        
        # コマンド入力欄
        input_y = console_y + console_height - 20
        pyxel.text(5, input_y, "> ", 7)
        pyxel.text(5, input_y + 8, "Type 'help' for commands", 6)
    
    def _draw_performance_stats(self, game_state: Dict[str, Any]):
        """パフォーマンス統計を描画"""
        stats_x = 10
        stats_y = GameConfig.SCREEN_HEIGHT - 150
        
        # 背景
        pyxel.rect(stats_x - 5, stats_y - 5, 200, 140, 1)
        pyxel.rectb(stats_x - 5, stats_y - 5, 200, 140, 7)
        
        # タイトル
        pyxel.text(stats_x, stats_y, "Performance Stats (F11)", 7)
        
        # FPS
        fps = 60  # 簡易FPS計算
        pyxel.text(stats_x, stats_y + 15, f"FPS: {fps}", 7)
        
        # メモリ使用量（概算）
        memory_mb = len(str(game_state)) / 1024  # 簡易計算
        pyxel.text(stats_x, stats_y + 25, f"Memory: {memory_mb:.1f}KB", 7)
        
        # ゲーム統計
        population = game_state.get('population', 0)
        money = game_state.get('money', 0)
        year = game_state.get('year', 1945)
        
        pyxel.text(stats_x, stats_y + 40, f"Year: {year}", 7)
        pyxel.text(stats_x, stats_y + 50, f"Population: {population:,}", 7)
        pyxel.text(stats_x, stats_y + 60, f"Money: ¥{money:,}", 7)
        
        # システム状態
        pyxel.text(stats_x, stats_y + 75, "System Status:", 7)
        if self.god_mode_enabled:
            pyxel.text(stats_x, stats_y + 85, "God Mode: ON", 8)
        if self.time_frozen:
            pyxel.text(stats_x, stats_y + 95, "Time: FROZEN", 8)
        if self.no_disasters:
            pyxel.text(stats_x, stats_y + 105, "Events: DISABLED", 8)
    
    def get_current_mode(self) -> DevModeType:
        """現在のモードを取得"""
        return self.current_mode
    
    def is_god_mode_enabled(self) -> bool:
        """神モードが有効かチェック"""
        return self.god_mode_enabled
    
    def can_build_anywhere(self) -> bool:
        """どこでも建設可能かチェック"""
        return self.no_building_restrictions
    
    def has_infinite_money(self) -> bool:
        """無限資金かチェック"""
        return self.infinite_money
    
    def _on_key_pressed(self, key_data):
        """キー押下イベントハンドラ"""
        # 将来的にコンソール入力処理を実装
        pass
    
    def _on_economy_check(self, economy_data):
        """経済チェックイベントハンドラ"""
        if self.infinite_money:
            # 無限資金の場合は常にtrueを返すよう修正
            economy_data['force_affordable'] = True
    
    def _on_building_check(self, building_data):
        """建物チェックイベントハンドラ"""
        if self.no_building_restrictions:
            # 建設制限解除
            building_data['force_allowed'] = True
        
        if self.invincible_buildings:
            # 建物無敵化
            building_data['invincible'] = True


# グローバルインスタンス
developer_mode = DeveloperMode()