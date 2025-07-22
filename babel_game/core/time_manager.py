"""
時間・年代管理システム
Time and Era Management System
"""

from config.game_config import GameConfig
from core.event_manager import event_manager


class TimeManager:
    """ゲーム内時間と年代を管理するクラス"""
    
    def __init__(self):
        self.current_year = GameConfig.START_YEAR
        self.current_month = 1
        self.current_day = 1
        self.game_speed = 1.0  # ゲーム速度倍率
        self.paused = False
        self._day_counter = 0
        self._days_per_frame = 0.005  # フレームあたりの日数進行（60FPSで約33秒で1日）
    
    def update(self):
        """時間を進める"""
        if self.paused:
            return
        
        self._day_counter += self._days_per_frame * self.game_speed
        
        if self._day_counter >= 1.0:
            days_to_advance = int(self._day_counter)
            self._day_counter -= days_to_advance
            self._advance_days(days_to_advance)
    
    def _advance_days(self, days: int):
        """指定日数だけ日付を進める"""
        for _ in range(days):
            self.current_day += 1
            
            # 月末チェック
            days_in_month = self._get_days_in_month(self.current_year, self.current_month)
            if self.current_day > days_in_month:
                self.current_day = 1
                self.current_month += 1
                
                # 年末チェック
                if self.current_month > 12:
                    self.current_month = 1
                    self.current_year += 1
                    
                    # 年変更イベント
                    event_manager.emit_event("year_changed", self.current_year)
                    
                # 月変更イベント
                event_manager.emit_event("month_changed", self.current_year, self.current_month)
            
            # 日変更イベント
            event_manager.emit_event("day_changed", self.current_year, self.current_month, self.current_day)
    
    def _get_days_in_month(self, year: int, month: int) -> int:
        """指定された年月の日数を取得"""
        if month in [1, 3, 5, 7, 8, 10, 12]:
            return 31
        elif month in [4, 6, 9, 11]:
            return 30
        elif month == 2:
            # うるう年チェック
            if year % 4 == 0 and (year % 100 != 0 or year % 400 == 0):
                return 29
            else:
                return 28
        return 30
    
    def set_speed(self, speed: float):
        """ゲーム速度を設定"""
        self.game_speed = max(0.1, min(10.0, speed))
        event_manager.emit_event("speed_changed", self.game_speed)
    
    def pause(self):
        """ゲームを一時停止"""
        self.paused = True
        event_manager.emit_event("game_paused")
    
    def resume(self):
        """ゲームを再開"""
        self.paused = False
        event_manager.emit_event("game_resumed")
    
    def toggle_pause(self):
        """一時停止状態を切り替え"""
        if self.paused:
            self.resume()
        else:
            self.pause()
    
    def get_date_string(self) -> str:
        """現在の日付を文字列で取得"""
        return f"{self.current_year}年{self.current_month}月{self.current_day}日"
    
    def get_progress_ratio(self) -> float:
        """ゲーム開始から終了までの進行率（0.0-1.0）"""
        total_years = GameConfig.END_YEAR - GameConfig.START_YEAR
        current_progress = self.current_year - GameConfig.START_YEAR
        return min(1.0, max(0.0, current_progress / total_years))
    
    def is_game_ended(self) -> bool:
        """ゲーム終了年に達したかチェック"""
        return self.current_year >= GameConfig.END_YEAR