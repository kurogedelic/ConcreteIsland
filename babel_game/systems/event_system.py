"""
イベントシステム
Event System for disasters, economic cycles, and seasonal changes
"""

import random
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from core.event_manager import event_manager
from config.game_config import GameConfig


class EventType(Enum):
    """イベントタイプ"""
    DISASTER = "disaster"           # 災害
    ECONOMIC = "economic"           # 経済イベント
    SEASONAL = "seasonal"           # 季節イベント
    POLITICAL = "political"         # 政治イベント
    SOCIAL = "social"              # 社会イベント


class DisasterType(Enum):
    """災害タイプ"""
    EARTHQUAKE = "earthquake"       # 地震
    TYPHOON = "typhoon"            # 台風
    FIRE = "fire"                  # 火災
    FLOOD = "flood"                # 洪水
    DROUGHT = "drought"            # 干ばつ
    VOLCANIC = "volcanic"          # 火山噴火


class SeasonType(Enum):
    """季節タイプ"""
    SPRING = "spring"              # 春
    SUMMER = "summer"              # 夏
    AUTUMN = "autumn"              # 秋
    WINTER = "winter"              # 冬


@dataclass
class GameEvent:
    """ゲームイベント"""
    event_id: str
    name_jp: str
    name_en: str
    description_jp: str
    description_en: str
    event_type: EventType
    year: int
    month: int
    duration_months: int = 1
    severity: int = 1  # 1-5 (1=軽微, 5=甚大)
    
    # 効果
    effects: Dict[str, Any] = None
    
    # 発生条件
    prerequisites: List[str] = None
    population_min: int = 0
    population_max: int = 999999
    
    # 発生確率
    probability: float = 1.0
    
    def __post_init__(self):
        if self.effects is None:
            self.effects = {}
        if self.prerequisites is None:
            self.prerequisites = []


class EventSystem:
    """イベントシステム管理クラス"""
    
    def __init__(self):
        self.current_season = SeasonType.SPRING
        self.active_events: List[GameEvent] = []
        self.historical_events: List[GameEvent] = []
        self.event_probabilities: Dict[str, float] = {}
        
        # 季節カウンタ
        self.season_month_counter = 0
        
        # イベント定義
        self.disaster_events = self._define_disaster_events()
        self.economic_events = self._define_economic_events()
        self.seasonal_events = self._define_seasonal_events()
        self.political_events = self._define_political_events()
        
        # デバッグモード：イベントを無効化
        self.debug_disable_events = True
        
        # イベントリスナー登録
        self._register_event_listeners()
    
    def _register_event_listeners(self):
        """イベントリスナーを登録"""
        event_manager.register_listener("year_changed", self._on_year_changed)
        event_manager.register_listener("month_changed", self._on_month_changed)
        event_manager.register_listener("building_placed", self._on_building_placed)
        event_manager.register_listener("population_changed", self._on_population_changed)
    
    def _define_disaster_events(self) -> List[GameEvent]:
        """災害イベントを定義"""
        return [
            # 地震
            GameEvent(
                event_id="small_earthquake",
                name_jp="小地震",
                name_en="Small Earthquake",
                description_jp="軽微な地震が発生しました。建物に若干の被害があります。",
                description_en="A minor earthquake occurred. Some buildings sustained light damage.",
                event_type=EventType.DISASTER,
                year=1945,
                month=1,
                severity=2,
                probability=0.1,
                effects={
                    "building_damage": 0.05,  # 5%の建物に軽微な被害
                    "happiness_loss": 5,
                    "money_loss": 1000,
                    "repair_cost_multiplier": 1.2
                }
            ),
            GameEvent(
                event_id="major_earthquake",
                name_jp="大地震",
                name_en="Major Earthquake",
                description_jp="大きな地震が発生しました。多くの建物が倒壊し、復旧に時間がかかります。",
                description_en="A major earthquake struck. Many buildings collapsed and recovery will take time.",
                event_type=EventType.DISASTER,
                year=1945,
                month=1,
                severity=5,
                probability=0.02,
                duration_months=3,
                effects={
                    "building_damage": 0.3,  # 30%の建物に甚大な被害
                    "building_destroy": 0.1,  # 10%の建物が完全破壊
                    "happiness_loss": 25,
                    "money_loss": 10000,
                    "population_loss": 0.05,  # 5%の人口が流出
                    "construction_speed": 0.5,  # 建設速度半減
                    "repair_cost_multiplier": 2.0
                }
            ),
            
            # 台風
            GameEvent(
                event_id="typhoon",
                name_jp="台風",
                name_en="Typhoon",
                description_jp="強い台風が通過しました。停電や浸水の被害が発生しています。",
                description_en="A strong typhoon passed through. Power outages and flooding occurred.",
                event_type=EventType.DISASTER,
                year=1945,
                month=6,  # 台風シーズン
                severity=3,
                probability=0.3,
                duration_months=1,
                effects={
                    "power_outage": 0.5,  # 50%の電力設備が停止
                    "building_damage": 0.15,
                    "happiness_loss": 10,
                    "money_loss": 3000,
                    "agricultural_damage": 0.3,  # 農業被害
                    "transport_disruption": 0.8  # 交通麻痺
                }
            ),
            
            # 火災
            GameEvent(
                event_id="major_fire",
                name_jp="大火災",
                name_en="Major Fire",
                description_jp="大規模な火災が発生しました。密集した住宅地に延焼の危険があります。",
                description_en="A major fire broke out. There's danger of spreading to densely populated areas.",
                event_type=EventType.DISASTER,
                year=1945,
                month=1,
                severity=4,
                probability=0.05,
                duration_months=1,
                effects={
                    "building_destroy": 0.2,  # 20%の建物が焼失
                    "happiness_loss": 20,
                    "money_loss": 8000,
                    "population_loss": 0.1,
                    "fire_spread_risk": 2.0  # 火災リスク増加
                }
            ),
            
            # 洪水
            GameEvent(
                event_id="flood",
                name_jp="大洪水",
                name_en="Major Flood",
                description_jp="大雨により河川が氾濫しました。低地の建物が浸水しています。",
                description_en="Heavy rains caused rivers to overflow. Buildings in low areas are flooded.",
                event_type=EventType.DISASTER,
                year=1945,
                month=6,
                severity=3,
                probability=0.08,
                duration_months=2,
                effects={
                    "building_damage": 0.25,
                    "happiness_loss": 15,
                    "money_loss": 5000,
                    "disease_risk": 1.5,  # 疫病リスク増加
                    "water_contamination": 0.5  # 水質汚染
                }
            )
        ]
    
    def _define_economic_events(self) -> List[GameEvent]:
        """経済イベントを定義"""
        return [
            # 朝鮮戦争特需
            GameEvent(
                event_id="korean_war_boom",
                name_jp="朝鮮戦争特需",
                name_en="Korean War Economic Boom",
                description_jp="朝鮮戦争により軍需物資の需要が急増しています。工業が活況を呈しています。",
                description_en="The Korean War has greatly increased demand for military supplies. Industry is booming.",
                event_type=EventType.ECONOMIC,
                year=1950,
                month=6,
                duration_months=36,  # 3年間
                severity=4,
                probability=1.0,  # 必ず発生
                effects={
                    "industrial_income": 2.0,  # 工業収入倍増
                    "employment_boost": 1.5,
                    "iron_demand": 3.0,
                    "coal_demand": 2.5,
                    "happiness_bonus": 10,
                    "population_growth": 1.3
                }
            ),
            
            # 神武景気
            GameEvent(
                event_id="jinmu_boom",
                name_jp="神武景気",
                name_en="Jinmu Economic Boom",
                description_jp="神武天皇以来の好景気です。設備投資が活発化しています。",
                description_en="The greatest economic boom since Emperor Jinmu. Capital investment is very active.",
                event_type=EventType.ECONOMIC,
                year=1954,
                month=12,
                duration_months=18,
                severity=3,
                probability=1.0,
                effects={
                    "construction_boom": 1.5,
                    "income_multiplier": 1.3,
                    "happiness_bonus": 15,
                    "technology_advancement": 1.2
                }
            ),
            
            # 岩戸景気
            GameEvent(
                event_id="iwato_boom",
                name_jp="岩戸景気",
                name_en="Iwato Economic Boom",
                description_jp="天の岩戸が開いたような好景気です。消費が活発化しています。",
                description_en="An economic boom as if the heavenly rock cave opened. Consumption is very active.",
                event_type=EventType.ECONOMIC,
                year=1958,
                month=7,
                duration_months=24,
                severity=4,
                probability=1.0,
                effects={
                    "consumer_spending": 1.8,
                    "commercial_income": 1.6,
                    "happiness_bonus": 20,
                    "population_growth": 1.4,
                    "technology_adoption": 1.5
                }
            ),
            
            # 米不足
            GameEvent(
                event_id="rice_shortage",
                name_jp="米不足",
                name_en="Rice Shortage",
                description_jp="冷害により米の収穫が激減しました。食料不足が深刻化しています。",
                description_en="Cold weather damaged rice harvest severely. Food shortage is becoming serious.",
                event_type=EventType.ECONOMIC,
                year=1945,
                month=9,
                severity=4,
                probability=0.15,
                duration_months=6,
                effects={
                    "rice_price": 3.0,  # 米価格3倍
                    "food_shortage": 0.7,
                    "happiness_loss": 20,
                    "health_decline": 0.8,
                    "social_unrest": 1.5
                }
            ),
            
            # 石油ショック
            GameEvent(
                event_id="oil_shock",
                name_jp="石油ショック",
                name_en="Oil Shock",
                description_jp="石油価格の急騰により経済が混乱しています。",
                description_en="Rapid rise in oil prices is causing economic chaos.",
                event_type=EventType.ECONOMIC,
                year=1973,
                month=10,
                severity=5,
                probability=1.0,
                duration_months=12,
                effects={
                    "fuel_cost": 4.0,
                    "construction_cost": 1.5,
                    "transport_cost": 2.0,
                    "inflation": 1.2,
                    "economic_recession": 0.7
                }
            )
        ]
    
    def _define_seasonal_events(self) -> List[GameEvent]:
        """季節イベントを定義"""
        return [
            # 春
            GameEvent(
                event_id="spring_festival",
                name_jp="春祭り",
                name_en="Spring Festival",
                description_jp="桜の季節になりました。お花見で住民の気分が向上しています。",
                description_en="Cherry blossom season has arrived. Citizens' mood improves with hanami.",
                event_type=EventType.SEASONAL,
                year=1945,
                month=3,
                severity=1,
                probability=0.8,
                effects={
                    "happiness_bonus": 10,
                    "tourism_boost": 1.2,
                    "commercial_income": 1.1
                }
            ),
            
            # 夏
            GameEvent(
                event_id="summer_festival",
                name_jp="夏祭り",
                name_en="Summer Festival",
                description_jp="夏祭りの季節です。屋台や花火で賑わっています。",
                description_en="Summer festival season. Food stalls and fireworks create a lively atmosphere.",
                event_type=EventType.SEASONAL,
                year=1945,
                month=7,
                severity=1,
                probability=0.7,
                effects={
                    "happiness_bonus": 8,
                    "commercial_income": 1.2,
                    "electricity_consumption": 1.3  # 夏の電力消費増
                }
            ),
            
            # 秋
            GameEvent(
                event_id="harvest_festival",
                name_jp="収穫祭",
                name_en="Harvest Festival",
                description_jp="実りの秋です。豊作により食料が豊富になっています。",
                description_en="Autumn harvest time. Good harvest makes food abundant.",
                event_type=EventType.SEASONAL,
                year=1945,
                month=10,
                severity=1,
                probability=0.6,
                effects={
                    "food_production": 1.4,
                    "rice_price": 0.8,  # 米価格下落
                    "happiness_bonus": 12,
                    "health_bonus": 5
                }
            ),
            
            # 冬
            GameEvent(
                event_id="winter_hardship",
                name_jp="厳冬",
                name_en="Harsh Winter",
                description_jp="厳しい冬がやってきました。暖房費が増加しています。",
                description_en="A harsh winter has arrived. Heating costs are increasing.",
                event_type=EventType.SEASONAL,
                year=1945,
                month=12,
                severity=2,
                probability=0.5,
                effects={
                    "heating_cost": 1.5,
                    "construction_speed": 0.8,  # 建設速度低下
                    "health_decline": 0.9,
                    "coal_demand": 2.0
                }
            )
        ]
    
    def _define_political_events(self) -> List[GameEvent]:
        """政治イベントを定義"""
        return [
            # 日本国憲法施行
            GameEvent(
                event_id="new_constitution",
                name_jp="日本国憲法施行",
                name_en="New Constitution Enacted",
                description_jp="新しい憲法が施行されました。民主主義の時代が始まります。",
                description_en="The new constitution has been enacted. The era of democracy begins.",
                event_type=EventType.POLITICAL,
                year=1947,
                month=5,
                severity=3,
                probability=1.0,
                effects={
                    "democracy_boost": 1.5,
                    "happiness_bonus": 15,
                    "education_priority": 1.3,
                    "civil_rights": 1.4
                }
            ),
            
            # サンフランシスコ講和条約
            GameEvent(
                event_id="peace_treaty",
                name_jp="サンフランシスコ講和条約",
                name_en="San Francisco Peace Treaty",
                description_jp="講和条約により日本の主権が回復しました。国際社会への復帰です。",
                description_en="Japan's sovereignty restored by peace treaty. Return to international community.",
                event_type=EventType.POLITICAL,
                year=1951,
                month=9,
                severity=4,
                probability=1.0,
                effects={
                    "international_trade": 1.8,
                    "diplomatic_relations": 1.5,
                    "happiness_bonus": 20,
                    "economic_growth": 1.3
                }
            ),
            
            # 安保闘争
            GameEvent(
                event_id="security_protests",
                name_jp="安保闘争",
                name_en="Security Treaty Protests",
                description_jp="安保条約をめぐって大規模な抗議活動が発生しています。",
                description_en="Large-scale protests over the security treaty are occurring.",
                event_type=EventType.POLITICAL,
                year=1960,
                month=5,
                severity=3,
                probability=1.0,
                duration_months=6,
                effects={
                    "social_unrest": 2.0,
                    "happiness_loss": 15,
                    "productivity_decline": 0.9,
                    "political_instability": 1.5
                }
            )
        ]
    
    def update(self, current_year: int, current_month: int, game_state: Dict[str, Any]):
        """イベントシステムを更新"""
        # デバッグモード：イベントを無効化
        if hasattr(self, 'debug_disable_events') and self.debug_disable_events:
            return
        # 季節を更新
        self._update_season(current_month)
        
        # アクティブイベントの期間チェック
        self._update_active_events(current_year, current_month)
        
        # 新しいイベントの発生チェック
        self._check_for_new_events(current_year, current_month, game_state)
        
        # 季節効果の適用
        self._apply_seasonal_effects(current_year, current_month)
    
    def _update_season(self, current_month: int):
        """季節を更新"""
        season_mapping = {
            1: SeasonType.WINTER, 2: SeasonType.WINTER,
            3: SeasonType.SPRING, 4: SeasonType.SPRING, 5: SeasonType.SPRING,
            6: SeasonType.SUMMER, 7: SeasonType.SUMMER, 8: SeasonType.SUMMER,
            9: SeasonType.AUTUMN, 10: SeasonType.AUTUMN, 11: SeasonType.AUTUMN,
            12: SeasonType.WINTER
        }
        
        new_season = season_mapping.get(current_month, SeasonType.SPRING)
        if new_season != self.current_season:
            old_season = self.current_season
            self.current_season = new_season
            
            # 季節変更イベントを発行
            event_manager.emit_event("season_changed", {
                "old_season": old_season,
                "new_season": new_season,
                "month": current_month
            })
            
            print(f"季節が変わりました: {new_season.value}")
    
    def _update_active_events(self, current_year: int, current_month: int):
        """アクティブイベントを更新"""
        events_to_remove = []
        
        for event in self.active_events:
            # イベント期間の計算
            event_end_year = event.year
            event_end_month = event.month + event.duration_months
            
            # 月の正規化
            while event_end_month > 12:
                event_end_month -= 12
                event_end_year += 1
            
            # 期間終了チェック
            if (current_year > event_end_year or 
                (current_year == event_end_year and current_month >= event_end_month)):
                events_to_remove.append(event)
        
        # 期間終了イベントを削除
        for event in events_to_remove:
            self.active_events.remove(event)
            self.historical_events.append(event)
            
            # イベント終了を通知
            event_manager.emit_event("game_event_ended", event)
            print(f"イベント終了: {event.name_jp}")
    
    def _check_for_new_events(self, current_year: int, current_month: int, game_state: Dict[str, Any]):
        """新しいイベントの発生をチェック"""
        population = game_state.get('population', 0)
        
        # 全イベントタイプをチェック
        all_events = (self.disaster_events + self.economic_events + 
                     self.seasonal_events + self.political_events)
        
        for event_template in all_events:
            # 発生条件チェック
            if not self._check_event_conditions(event_template, current_year, current_month, population):
                continue
            
            # 既に発生済みかチェック
            if self._is_event_already_occurred(event_template):
                continue
            
            # 確率チェック
            if random.random() > event_template.probability:
                continue
            
            # イベントを発生させる
            self._trigger_event(event_template, current_year, current_month)
    
    def _check_event_conditions(self, event_template: GameEvent, current_year: int, 
                               current_month: int, population: int) -> bool:
        """イベント発生条件をチェック"""
        # 年チェック
        if current_year < event_template.year:
            return False
        
        # 月チェック（季節イベントの場合）
        if event_template.event_type == EventType.SEASONAL:
            if current_month != event_template.month:
                return False
        
        # 人口チェック
        if population < event_template.population_min or population > event_template.population_max:
            return False
        
        return True
    
    def _is_event_already_occurred(self, event_template: GameEvent) -> bool:
        """イベントが既に発生済みかチェック"""
        # 政治イベントは一度だけ発生
        if event_template.event_type == EventType.POLITICAL:
            return any(e.event_id == event_template.event_id for e in self.historical_events)
        
        # 経済イベントも基本的に一度だけ
        if event_template.event_type == EventType.ECONOMIC:
            return any(e.event_id == event_template.event_id for e in self.historical_events)
        
        # 災害・季節イベントは繰り返し発生可能
        return False
    
    def _trigger_event(self, event_template: GameEvent, current_year: int, current_month: int):
        """イベントを発生させる"""
        # イベントインスタンスを作成
        event = GameEvent(
            event_id=event_template.event_id,
            name_jp=event_template.name_jp,
            name_en=event_template.name_en,
            description_jp=event_template.description_jp,
            description_en=event_template.description_en,
            event_type=event_template.event_type,
            year=current_year,
            month=current_month,
            duration_months=event_template.duration_months,
            severity=event_template.severity,
            effects=event_template.effects.copy()
        )
        
        # アクティブイベントに追加
        self.active_events.append(event)
        
        # イベント発生を通知
        event_manager.emit_event("game_event_triggered", event)
        print(f"イベント発生: {event.name_jp}")
    
    def _apply_seasonal_effects(self, current_year: int, current_month: int):
        """季節効果を適用"""
        # 季節による基本効果
        seasonal_effects = {
            SeasonType.SPRING: {
                "construction_speed": 1.1,
                "happiness_bonus": 5
            },
            SeasonType.SUMMER: {
                "power_consumption": 1.2,
                "productivity": 1.1
            },
            SeasonType.AUTUMN: {
                "food_production": 1.2,
                "happiness_bonus": 3
            },
            SeasonType.WINTER: {
                "heating_cost": 1.3,
                "construction_speed": 0.9
            }
        }
        
        current_effects = seasonal_effects.get(self.current_season, {})
        if current_effects:
            event_manager.emit_event("seasonal_effects_applied", {
                "season": self.current_season,
                "effects": current_effects
            })
    
    def get_active_events(self) -> List[GameEvent]:
        """アクティブイベントを取得"""
        return self.active_events.copy()
    
    def get_historical_events(self) -> List[GameEvent]:
        """過去のイベントを取得"""
        return self.historical_events.copy()
    
    def get_current_season(self) -> SeasonType:
        """現在の季節を取得"""
        return self.current_season
    
    def get_event_summary(self) -> Dict[str, Any]:
        """イベント概要を取得"""
        return {
            "current_season": self.current_season.value,
            "active_events": len(self.active_events),
            "historical_events": len(self.historical_events),
            "disaster_events": len([e for e in self.active_events if e.event_type == EventType.DISASTER]),
            "economic_events": len([e for e in self.active_events if e.event_type == EventType.ECONOMIC]),
            "seasonal_events": len([e for e in self.active_events if e.event_type == EventType.SEASONAL]),
            "political_events": len([e for e in self.active_events if e.event_type == EventType.POLITICAL])
        }
    
    def has_disasters_occurred(self) -> bool:
        """災害が発生したかどうかを返す"""
        # 過去の災害イベントをチェック
        for event in self.historical_events:
            if event.event_type == EventType.DISASTER:
                return True
        return False
    
    def _on_year_changed(self, new_year: int):
        """年変更イベントハンドラ"""
        pass
    
    def _on_month_changed(self, year: int, month: int):
        """月変更イベントハンドラ"""
        pass
    
    def _on_building_placed(self, building):
        """建物配置イベントハンドラ"""
        # 建物配置による災害リスク変更
        if building.definition.category.value == "industrial":
            # 工業建物は火災リスクを増加
            self.event_probabilities["fire"] = self.event_probabilities.get("fire", 0.05) + 0.01
    
    def _on_population_changed(self, new_population: int):
        """人口変更イベントハンドラ"""
        # 人口に応じた災害リスク調整
        if new_population > 5000:
            self.event_probabilities["major_earthquake"] = 0.03
        elif new_population > 1000:
            self.event_probabilities["major_earthquake"] = 0.02
    
    def _restore_from_save_data(self, events_data: Dict[str, Any]):
        """セーブデータからイベントシステムを復元"""
        try:
            # 災害履歴を復元
            if 'disaster_history' in events_data:
                self.disaster_history.clear()
                for disaster_data in events_data['disaster_history']:
                    disaster = DisasterEvent(
                        disaster_type=disaster_data['type'],
                        year=disaster_data['year'],
                        affected_area=disaster_data['affected_area'],
                        damage_amount=disaster_data['damage']
                    )
                    self.disaster_history.append(disaster)
            
            # 現在の季節を復元
            if 'current_season' in events_data:
                season_value = events_data['current_season']
                for season in Season:
                    if season.value == season_value:
                        self.current_season = season
                        break
            
            # イベント有効化状態を復元
            if 'events_enabled' in events_data:
                self.disasters_disabled = not events_data['events_enabled']
            
            print(f"Event system restored: Season {self.current_season.value}, {len(self.disaster_history)} disasters in history")
            
        except Exception as e:
            print(f"Error restoring event system: {e}")