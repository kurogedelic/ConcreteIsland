"""
技術進歩管理システム
Technology Progression Management System
"""

from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from enum import Enum
from core.event_manager import event_manager
from config.game_config import GameConfig


class TechnologyEra(Enum):
    """技術時代"""
    POST_WAR_RECOVERY = "post_war_recovery"      # 戦後復興期 (1945-1950)
    KOREAN_WAR_BOOM = "korean_war_boom"          # 朝鮮戦争特需期 (1950-1955)
    HIGH_GROWTH_EARLY = "high_growth_early"      # 高度成長期前期 (1955-1965)
    HIGH_GROWTH_LATE = "high_growth_late"        # 高度成長期後期 (1965-1970)


@dataclass
class TechnologyEvent:
    """技術イベント"""
    name_jp: str
    name_en: str
    description_jp: str
    year: int
    era: TechnologyEra
    effects: Dict[str, any]  # 経済効果、建物アンロック等
    
    def __post_init__(self):
        """イベント後処理"""
        if not self.effects:
            self.effects = {}


@dataclass
class HistoricalPeriod:
    """歴史的時期"""
    name_jp: str
    name_en: str
    start_year: int
    end_year: int
    era: TechnologyEra
    description_jp: str
    characteristic_buildings: List[str]  # この時期の特徴的建物
    economic_modifiers: Dict[str, float]  # 経済効果


class TechnologyManager:
    """技術進歩管理クラス"""
    
    def __init__(self):
        self.current_era = TechnologyEra.POST_WAR_RECOVERY
        self.current_period: Optional[HistoricalPeriod] = None
        self.triggered_events: List[TechnologyEvent] = []
        
        # 技術進歩イベントの定義
        self.technology_events = self._define_technology_events()
        
        # 歴史的時期の定義
        self.historical_periods = self._define_historical_periods()
        
        # 技術研究の進捗
        self.research_progress: Dict[str, int] = {}
        
        # イベントリスナー登録
        self._register_event_listeners()
    
    def _register_event_listeners(self):
        """イベントリスナーを登録"""
        event_manager.register_listener("year_changed", self._on_year_changed)
        event_manager.register_listener("month_changed", self._on_month_changed)
        event_manager.register_listener("building_placed", self._on_building_placed)
    
    def _define_technology_events(self) -> List[TechnologyEvent]:
        """技術進歩イベントを定義"""
        return [
            # 戦後復興期 (1945-1950)
            TechnologyEvent(
                name_jp="戦後復興開始",
                name_en="Post-war Recovery Begins",
                description_jp="戦争の傷跡から立ち上がり、復興が始まる",
                year=1945,
                era=TechnologyEra.POST_WAR_RECOVERY,
                effects={
                    "building_cost_modifier": 0.8,  # 建設費20%安
                    "unlock_buildings": ["barrack_house", "road", "small_shop", "small_factory"]
                }
            ),
            TechnologyEvent(
                name_jp="教育制度改革",
                name_en="Educational Reform",
                description_jp="新しい教育制度により人材育成が加速",
                year=1947,
                era=TechnologyEra.POST_WAR_RECOVERY,
                effects={
                    "happiness_bonus": 5,
                    "unlock_buildings": ["elementary_school"]
                }
            ),
            TechnologyEvent(
                name_jp="復興院設立",
                name_en="Reconstruction Agency Established",
                description_jp="政府主導の復興事業により建設が促進",
                year=1948,
                era=TechnologyEra.POST_WAR_RECOVERY,
                effects={
                    "construction_speed": 1.2,
                    "unlock_buildings": ["market_street", "clinic"]
                }
            ),
            
            # 朝鮮戦争特需期 (1950-1955)
            TechnologyEvent(
                name_jp="朝鮮戦争特需開始",
                name_en="Korean War Boom Begins",
                description_jp="朝鮮戦争により特需景気が始まる",
                year=1950,
                era=TechnologyEra.KOREAN_WAR_BOOM,
                effects={
                    "industrial_income_multiplier": 1.5,
                    "unlock_buildings": ["textile_factory", "public_housing", "train_station"]
                }
            ),
            TechnologyEvent(
                name_jp="電力復旧事業",
                name_en="Power Recovery Project",
                description_jp="電力供給網の復旧により産業が活性化",
                year=1950,
                era=TechnologyEra.KOREAN_WAR_BOOM,
                effects={
                    "power_efficiency": 1.3,
                    "unlock_buildings": ["coal_power_plant"]
                }
            ),
            TechnologyEvent(
                name_jp="住宅金融公庫設立",
                name_en="Housing Finance Corporation Established",
                description_jp="住宅建設資金の提供により住宅不足が解消",
                year=1950,
                era=TechnologyEra.KOREAN_WAR_BOOM,
                effects={
                    "housing_cost_modifier": 0.9,
                    "unlock_buildings": ["concrete_tech"]
                }
            ),
            TechnologyEvent(
                name_jp="上水道整備事業",
                name_en="Water Supply Development",
                description_jp="上水道の整備により都市環境が改善",
                year=1952,
                era=TechnologyEra.KOREAN_WAR_BOOM,
                effects={
                    "health_bonus": 10,
                    "unlock_buildings": ["water_plant"]
                }
            ),
            TechnologyEvent(
                name_jp="娯楽産業発展",
                name_en="Entertainment Industry Growth",
                description_jp="映画や娯楽産業の発展により文化が豊かに",
                year=1952,
                era=TechnologyEra.KOREAN_WAR_BOOM,
                effects={
                    "happiness_bonus": 10,
                    "unlock_buildings": ["movie_theater"]
                }
            ),
            
            # 高度成長期前期 (1955-1965)
            TechnologyEvent(
                name_jp="高度成長期開始",
                name_en="High Growth Period Begins",
                description_jp="神武景気により高度成長期が始まる",
                year=1955,
                era=TechnologyEra.HIGH_GROWTH_EARLY,
                effects={
                    "economic_growth_rate": 1.8,
                    "unlock_buildings": ["steel_mill", "apartment_building", "hospital"]
                }
            ),
            TechnologyEvent(
                name_jp="新三種の神器普及",
                name_en="New Three Sacred Treasures",
                description_jp="テレビ、洗濯機、冷蔵庫の普及により生活が豊かに",
                year=1958,
                era=TechnologyEra.HIGH_GROWTH_EARLY,
                effects={
                    "happiness_bonus": 15,
                    "power_consumption_increase": 1.2,
                    "unlock_buildings": ["tv_tower"]
                }
            ),
            TechnologyEvent(
                name_jp="モータリゼーション",
                name_en="Motorization",
                description_jp="自動車の普及により産業構造が変化",
                year=1960,
                era=TechnologyEra.HIGH_GROWTH_EARLY,
                effects={
                    "transport_efficiency": 1.5,
                    "unlock_buildings": ["auto_factory"]
                }
            ),
            TechnologyEvent(
                name_jp="所得倍増計画",
                name_en="Income Doubling Plan",
                description_jp="政府の所得倍増計画により経済が急成長",
                year=1960,
                era=TechnologyEra.HIGH_GROWTH_EARLY,
                effects={
                    "income_multiplier": 1.4,
                    "population_growth_rate": 1.3
                }
            ),
            
            # 高度成長期後期 (1965-1970)
            TechnologyEvent(
                name_jp="東京オリンピック開催",
                name_en="Tokyo Olympics",
                description_jp="東京オリンピックにより国際化が進む",
                year=1964,
                era=TechnologyEra.HIGH_GROWTH_LATE,
                effects={
                    "international_prestige": 50,
                    "tourism_bonus": 1.5,
                    "unlock_buildings": ["airport"]
                }
            ),
            TechnologyEvent(
                name_jp="原子力発電開始",
                name_en="Nuclear Power Introduction",
                description_jp="原子力発電により電力不足が解消",
                year=1965,
                era=TechnologyEra.HIGH_GROWTH_LATE,
                effects={
                    "power_production_boost": 2.0,
                    "unlock_buildings": ["nuclear_power_plant"]
                }
            ),
            TechnologyEvent(
                name_jp="新幹線開通",
                name_en="Shinkansen Opening",
                description_jp="新幹線の開通により高速交通時代が到来",
                year=1964,
                era=TechnologyEra.HIGH_GROWTH_LATE,
                effects={
                    "transport_revolution": 2.0,
                    "economic_connectivity": 1.5
                }
            ),
            TechnologyEvent(
                name_jp="大阪万博決定",
                name_en="Osaka Expo Announcement",
                description_jp="1970年大阪万博開催決定により建設ブーム",
                year=1965,
                era=TechnologyEra.HIGH_GROWTH_LATE,
                effects={
                    "construction_boom": 1.3,
                    "technology_advancement": 1.4
                }
            ),
            TechnologyEvent(
                name_jp="公害問題顕在化",
                name_en="Pollution Problem Emergence",
                description_jp="高度成長の代償として公害問題が深刻化",
                year=1967,
                era=TechnologyEra.HIGH_GROWTH_LATE,
                effects={
                    "environmental_concern": 1.0,
                    "pollution_awareness": 1.5,
                    "industrial_regulation": 1.2
                }
            )
        ]
    
    def _define_historical_periods(self) -> List[HistoricalPeriod]:
        """歴史的時期を定義"""
        return [
            HistoricalPeriod(
                name_jp="戦後復興期",
                name_en="Post-war Recovery Period",
                start_year=1945,
                end_year=1950,
                era=TechnologyEra.POST_WAR_RECOVERY,
                description_jp="戦争の傷跡から立ち上がり、基本的な都市インフラを整備する時期",
                characteristic_buildings=[
                    "barrack_house", "wooden_house", "small_shop", "small_factory", 
                    "police_box", "elementary_school", "road"
                ],
                economic_modifiers={
                    "construction_cost": 0.8,
                    "maintenance_cost": 0.9,
                    "population_growth": 0.7
                }
            ),
            HistoricalPeriod(
                name_jp="朝鮮戦争特需期",
                name_en="Korean War Boom Period",
                start_year=1950,
                end_year=1955,
                era=TechnologyEra.KOREAN_WAR_BOOM,
                description_jp="朝鮮戦争特需により工業化が進み、都市基盤が拡充される時期",
                characteristic_buildings=[
                    "textile_factory", "public_housing", "train_station", "coal_power_plant", 
                    "water_plant", "fire_station", "market_street", "movie_theater"
                ],
                economic_modifiers={
                    "industrial_income": 1.5,
                    "construction_speed": 1.2,
                    "power_efficiency": 1.3
                }
            ),
            HistoricalPeriod(
                name_jp="高度成長期前期",
                name_en="Early High Growth Period",
                start_year=1955,
                end_year=1965,
                era=TechnologyEra.HIGH_GROWTH_EARLY,
                description_jp="重化学工業化により急速な経済成長を遂げる時期",
                characteristic_buildings=[
                    "steel_mill", "apartment_building", "hospital", "department_store", 
                    "tv_tower", "auto_factory", "concrete_tech"
                ],
                economic_modifiers={
                    "economic_growth": 1.8,
                    "income_multiplier": 1.4,
                    "technology_advancement": 1.3
                }
            ),
            HistoricalPeriod(
                name_jp="高度成長期後期",
                name_en="Late High Growth Period",
                start_year=1965,
                end_year=1970,
                era=TechnologyEra.HIGH_GROWTH_LATE,
                description_jp="国際化と技術革新により世界有数の経済大国となる時期",
                characteristic_buildings=[
                    "nuclear_power_plant", "airport", "tv_tower"
                ],
                economic_modifiers={
                    "international_trade": 1.6,
                    "technology_level": 1.5,
                    "environmental_concern": 1.2
                }
            )
        ]
    
    def update(self, current_year: int, current_month: int):
        """技術進歩システムを更新"""
        # 現在の時期を更新
        self._update_current_period(current_year)
        
        # 技術イベントの処理
        self._process_technology_events(current_year)
        
        # 研究進捗の更新
        self._update_research_progress(current_year, current_month)
    
    def _update_current_period(self, current_year: int):
        """現在の歴史的時期を更新"""
        new_period = None
        for period in self.historical_periods:
            if period.start_year <= current_year <= period.end_year:
                new_period = period
                break
        
        if new_period and new_period != self.current_period:
            old_period = self.current_period
            self.current_period = new_period
            self.current_era = new_period.era
            
            # 時期変更イベントを発行
            event_manager.emit_event("historical_period_changed", {
                "old_period": old_period,
                "new_period": new_period,
                "year": current_year
            })
            
            print(f"時代が変わりました: {new_period.name_jp} ({current_year}年)")
    
    def _process_technology_events(self, current_year: int):
        """技術イベントを処理"""
        for event in self.technology_events:
            if event.year == current_year and event not in self.triggered_events:
                self._trigger_technology_event(event)
    
    def _trigger_technology_event(self, event: TechnologyEvent):
        """技術イベントを発動"""
        self.triggered_events.append(event)
        
        # イベント効果を適用
        if "unlock_buildings" in event.effects:
            for building_id in event.effects["unlock_buildings"]:
                event_manager.emit_event("technology_unlock", {
                    "building_id": building_id,
                    "event": event
                })
        
        # 技術イベント発生を通知
        event_manager.emit_event("technology_event_triggered", event)
        
        print(f"技術イベント発生: {event.name_jp} ({event.year}年)")
        print(f"  効果: {event.description_jp}")
    
    def _update_research_progress(self, current_year: int, current_month: int):
        """研究進捗を更新"""
        # 月次の研究進捗処理
        research_facilities = self._count_research_facilities()
        
        # 研究施設数に応じて技術進歩速度を調整
        if research_facilities > 0:
            research_speed = min(2.0, 1.0 + (research_facilities * 0.1))
            
            # 各技術分野の研究進捗を更新
            for tech_field in ["construction", "industrial", "energy", "transport"]:
                if tech_field not in self.research_progress:
                    self.research_progress[tech_field] = 0
                
                self.research_progress[tech_field] += research_speed
    
    def _count_research_facilities(self) -> int:
        """研究施設数をカウント"""
        # 将来的にはbuilding_managerから研究施設数を取得
        # 現在は技術関連建物を代用
        return 1  # 仮の値
    
    def get_current_era_info(self) -> Dict[str, any]:
        """現在の時代情報を取得"""
        return {
            "era": self.current_era,
            "period": self.current_period,
            "triggered_events": len(self.triggered_events),
            "research_progress": self.research_progress.copy()
        }
    
    def get_progress(self) -> float:
        """技術進歩率を取得（0.0-1.0）"""
        total_events = len(self.technology_events)
        if total_events == 0:
            return 0.0
        
        completed_events = sum(1 for event in self.technology_events if event.year <= self.current_year)
        return completed_events / total_events
    
    def get_available_technologies(self, current_year: int) -> List[str]:
        """利用可能な技術のリストを取得"""
        available = []
        for event in self.technology_events:
            if event.year <= current_year:
                if "unlock_buildings" in event.effects:
                    available.extend(event.effects["unlock_buildings"])
        return list(set(available))
    
    def get_era_modifiers(self) -> Dict[str, float]:
        """現在の時代の経済修正値を取得"""
        if self.current_period:
            return self.current_period.economic_modifiers.copy()
        return {}
    
    def get_next_major_event(self, current_year: int) -> Optional[TechnologyEvent]:
        """次の主要技術イベントを取得"""
        upcoming_events = [
            event for event in self.technology_events
            if event.year > current_year and event not in self.triggered_events
        ]
        
        if upcoming_events:
            return min(upcoming_events, key=lambda x: x.year)
        return None
    
    def _on_year_changed(self, new_year: int):
        """年変更イベントハンドラ"""
        self.update(new_year, 1)
    
    def _on_month_changed(self, year: int, month: int):
        """月変更イベントハンドラ"""
        self.update(year, month)
    
    def _on_building_placed(self, building):
        """建物配置イベントハンドラ"""
        # 特定の建物配置により技術進歩を促進
        if building.definition.id in ["concrete_tech", "steel_mill", "nuclear_power_plant"]:
            for tech_field in self.research_progress:
                self.research_progress[tech_field] += 5
    
    def _restore_from_save_data(self, tech_data: Dict[str, Any]):
        """セーブデータから技術システムを復元"""
        try:
            # 現在の時代を復元
            if 'current_era' in tech_data:
                era_value = tech_data['current_era']
                for era in TechnologyEra:
                    if era.value == era_value:
                        self.current_era = era
                        break
            
            # アンロック済み建物リストを復元
            if 'unlocked_buildings' in tech_data:
                self.unlocked_buildings = set(tech_data['unlocked_buildings'])
            
            # 研究進捗を復元
            if 'research_progress' in tech_data:
                saved_progress = tech_data['research_progress']
                for field, progress in saved_progress.items():
                    if field in self.research_progress:
                        self.research_progress[field] = progress
            
            # 完了済み時代を復元
            if 'completed_eras' in tech_data:
                self.completed_eras = set()
                for era_value in tech_data['completed_eras']:
                    for era in TechnologyEra:
                        if era.value == era_value:
                            self.completed_eras.add(era)
                            break
            
            # 現在の時代に合わせて時代設定を更新
            self._update_current_period()
            
            print(f"Technology system restored: Era {self.current_era.value}, {len(self.unlocked_buildings)} buildings unlocked")
            
        except Exception as e:
            print(f"Error restoring technology system: {e}")