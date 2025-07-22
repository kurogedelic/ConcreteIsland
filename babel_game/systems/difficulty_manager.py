"""
難易度管理システム
Difficulty Management System
"""

from config.balance_config import DifficultyLevel, BalanceConfig
from core.event_manager import event_manager


class DifficultyManager:
    """難易度を管理するクラス"""
    
    def __init__(self):
        self.current_difficulty = DifficultyLevel.NORMAL
        self.settings = BalanceConfig.get_difficulty_settings(self.current_difficulty)
        
        # イベントリスナー登録
        self._register_event_listeners()
    
    def _register_event_listeners(self):
        """イベントリスナーを登録"""
        event_manager.register_listener("difficulty_changed", self._on_difficulty_changed)
    
    def set_difficulty(self, difficulty: DifficultyLevel):
        """難易度を設定"""
        if difficulty != self.current_difficulty:
            self.current_difficulty = difficulty
            self.settings = BalanceConfig.get_difficulty_settings(difficulty)
            
            # 難易度変更イベント発火
            event_manager.emit_event("difficulty_changed", {
                "difficulty": difficulty,
                "settings": self.settings
            })
            
            print(f"難易度を{self.get_difficulty_name_jp()}に変更しました")
    
    def get_difficulty_name_jp(self) -> str:
        """現在の難易度の日本語名を取得"""
        names = {
            DifficultyLevel.EASY: "イージー",
            DifficultyLevel.NORMAL: "ノーマル",
            DifficultyLevel.HARD: "ハード"
        }
        return names.get(self.current_difficulty, "ノーマル")
    
    def get_adjusted_cost(self, base_cost: int, year: int) -> int:
        """調整済みコストを取得"""
        return BalanceConfig.calculate_adjusted_cost(base_cost, self.current_difficulty, year)
    
    def get_adjusted_income(self, base_income: int, year: int) -> int:
        """調整済み収入を取得"""
        return BalanceConfig.calculate_adjusted_income(base_income, self.current_difficulty, year)
    
    def get_maintenance_cost(self, building_cost: int, category: str) -> int:
        """維持費を計算"""
        return BalanceConfig.calculate_maintenance_cost(building_cost, category, self.current_difficulty)
    
    def get_starting_money(self) -> int:
        """初期資金を取得"""
        return self.settings["starting_money"]
    
    def get_disaster_frequency(self) -> float:
        """災害頻度を取得"""
        return self.settings["disaster_frequency"]
    
    def get_population_growth_rate(self) -> float:
        """人口増加率を取得"""
        return self.settings["population_growth_rate"]
    
    def get_happiness_decay_rate(self) -> float:
        """幸福度減衰率を取得"""
        return self.settings["happiness_decay_rate"]
    
    def _on_difficulty_changed(self, data: dict):
        """難易度変更イベントハンドラ"""
        print(f"Difficulty changed to: {data['difficulty'].value}")
        # 必要に応じて他のシステムに通知


# シングルトンインスタンス
difficulty_manager = DifficultyManager()