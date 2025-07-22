"""
ゲーム完了システム
Game Completion System
"""

from typing import Dict, Any
from core.event_manager import event_manager
from config.game_config import GameConfig


class GameCompletionSystem:
    """ゲーム完了と結果表示を管理するクラス"""
    
    def __init__(self):
        self.game_completed = False
        self.completion_stats = {}
        
        # イベントリスナー登録
        self._register_event_listeners()
    
    def _register_event_listeners(self):
        """イベントリスナーを登録"""
        event_manager.register_listener("year_changed", self._on_year_changed)
    
    def _on_year_changed(self, year: int):
        """年変更イベントハンドラ"""
        if year >= GameConfig.END_YEAR and not self.game_completed:
            self._trigger_game_completion()
    
    def _trigger_game_completion(self):
        """ゲーム完了を発動"""
        self.game_completed = True
        event_manager.emit_event("game_completed", self.completion_stats)
    
    def calculate_completion_stats(self, game_state: Dict[str, Any]) -> Dict[str, Any]:
        """ゲーム完了時の統計を計算"""
        stats = {
            # 基本統計
            "final_year": game_state.get("year", 1970),
            "final_population": game_state.get("population", 0),
            "final_money": game_state.get("money", 0),
            "final_happiness": game_state.get("happiness", 0),
            
            # 建物統計
            "total_buildings": game_state.get("total_buildings", 0),
            "building_breakdown": game_state.get("building_breakdown", {}),
            
            # 経済統計
            "total_income": game_state.get("total_income", 0),
            "total_expenses": game_state.get("total_expenses", 0),
            "economic_growth": game_state.get("economic_growth", 0),
            
            # 達成度評価
            "score": self._calculate_score(game_state),
            "rating": self._calculate_rating(game_state),
            "achievements": self._check_achievements(game_state)
        }
        
        self.completion_stats = stats
        return stats
    
    def _calculate_score(self, game_state: Dict[str, Any]) -> int:
        """スコアを計算"""
        score = 0
        
        # 人口スコア（最大30,000点）
        population = game_state.get("population", 0)
        score += min(30000, population * 3)
        
        # 経済スコア（最大20,000点）
        money = game_state.get("money", 0)
        score += min(20000, money // 100)
        
        # 幸福度スコア（最大20,000点）
        happiness = game_state.get("happiness", 50)
        score += happiness * 200
        
        # 建物スコア（最大20,000点）
        total_buildings = game_state.get("total_buildings", 0)
        score += min(20000, total_buildings * 200)
        
        # 時代進歩スコア（最大10,000点）
        tech_progress = game_state.get("tech_progress", 0)
        score += int(tech_progress * 10000)
        
        return score
    
    def _calculate_rating(self, game_state: Dict[str, Any]) -> str:
        """評価ランクを計算"""
        score = self._calculate_score(game_state)
        
        if score >= 90000:
            return "S"  # 奇跡の復興
        elif score >= 75000:
            return "A"  # 素晴らしい復興
        elif score >= 60000:
            return "B"  # 良好な復興
        elif score >= 40000:
            return "C"  # 標準的な復興
        elif score >= 20000:
            return "D"  # 苦難の復興
        else:
            return "E"  # 困難な時代
    
    def _check_achievements(self, game_state: Dict[str, Any]) -> list:
        """達成項目をチェック"""
        achievements = []
        
        # 人口達成
        population = game_state.get("population", 0)
        if population >= 10000:
            achievements.append("人口1万人達成")
        if population >= 50000:
            achievements.append("人口5万人達成")
        if population >= 100000:
            achievements.append("大都市への成長")
        
        # 経済達成
        money = game_state.get("money", 0)
        if money >= 1000000:
            achievements.append("百万長者")
        if money >= 10000000:
            achievements.append("経済大国")
        
        # 建物達成
        building_breakdown = game_state.get("building_breakdown", {})
        if building_breakdown.get("nuclear_plant", 0) > 0:
            achievements.append("原子力時代")
        if building_breakdown.get("airport", 0) > 0:
            achievements.append("国際都市")
        if building_breakdown.get("tv_tower", 0) > 0:
            achievements.append("情報化社会")
        
        # 特殊達成
        if game_state.get("no_disasters", False):
            achievements.append("災害ゼロ")
        if game_state.get("happiness", 50) >= 80:
            achievements.append("幸福な市民")
        if game_state.get("full_employment", False):
            achievements.append("完全雇用")
        
        return achievements
    
    def get_rating_description(self, rating: str) -> str:
        """評価の説明文を取得"""
        descriptions = {
            "S": "奇跡の復興！戦後の焼け野原から世界に誇る都市を築き上げました。",
            "A": "素晴らしい復興！高度成長期の波に乗り、繁栄する都市を作り上げました。",
            "B": "良好な復興。着実な発展により、市民が安心して暮らせる都市になりました。",
            "C": "標準的な復興。困難を乗り越え、基本的な都市機能を回復しました。",
            "D": "苦難の復興。多くの困難に直面しましたが、諦めずに前進しました。",
            "E": "困難な時代でした。しかし、復興への第一歩を踏み出しました。"
        }
        return descriptions.get(rating, "")
    
    def format_completion_message(self) -> list:
        """完了メッセージをフォーマット"""
        stats = self.completion_stats
        messages = []
        
        messages.append("＝＝＝ ゲーム完了 ＝＝＝")
        messages.append(f"1945年から{stats['final_year']}年まで、{stats['final_year'] - 1945}年間の復興")
        messages.append("")
        
        messages.append(f"最終人口: {stats['final_population']:,}人")
        messages.append(f"最終資金: ¥{stats['final_money']:,}")
        messages.append(f"市民幸福度: {stats['final_happiness']}%")
        messages.append("")
        
        messages.append(f"総スコア: {stats['score']:,}点")
        messages.append(f"評価ランク: {stats['rating']}")
        messages.append(self.get_rating_description(stats['rating']))
        messages.append("")
        
        if stats['achievements']:
            messages.append("達成項目:")
            for achievement in stats['achievements']:
                messages.append(f"  ・{achievement}")
        
        return messages