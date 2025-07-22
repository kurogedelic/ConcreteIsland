"""
建物データモデル
Building Data Model
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum


class BuildingCategory(Enum):
    """建物カテゴリ"""
    RESIDENTIAL = "residential"
    COMMERCIAL = "commercial"
    INDUSTRIAL = "industrial"
    CIVIC = "civic"
    INFRA = "infra"
    RECREATION = "recreation"
    SPECIAL = "special"


@dataclass
class BuildingUnlockCondition:
    """建物アンロック条件"""
    year: int = 1945
    population: int = 0
    prerequisites: List[str] = None
    
    def __post_init__(self):
        if self.prerequisites is None:
            self.prerequisites = []


@dataclass
class BuildingStats:
    """建物統計"""
    population_capacity: int = 0
    jobs_provided: int = 0
    power_consumption: int = 0
    water_consumption: int = 0
    power_production: int = 0
    water_production: int = 0
    happiness_effect: int = 0
    pollution: int = 0
    fire_risk: int = 0


@dataclass
class BuildingDefinition:
    """建物定義"""
    id: str
    name_jp: str
    name_en: str
    category: BuildingCategory
    cost: int
    maintenance_cost: int
    unlock_condition: BuildingUnlockCondition
    stats: BuildingStats
    sprite_name: str
    icon_name: str
    size_width: int = 1
    size_height: int = 1
    description_jp: str = ""
    description_en: str = ""
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BuildingDefinition':
        """辞書から建物定義を作成"""
        # アンロック条件
        unlock_data = data.get('unlock_condition', {})
        unlock_condition = BuildingUnlockCondition(
            year=unlock_data.get('year', 1945),
            population=unlock_data.get('population', 0),
            prerequisites=unlock_data.get('prerequisites', [])
        )
        
        # 統計データ
        stats_data = data.get('stats', {})
        stats = BuildingStats(
            population_capacity=stats_data.get('population_capacity', 0),
            jobs_provided=stats_data.get('jobs_provided', 0),
            power_consumption=stats_data.get('power_consumption', 0),
            water_consumption=stats_data.get('water_consumption', 0),
            power_production=stats_data.get('power_production', 0),
            water_production=stats_data.get('water_production', 0),
            happiness_effect=stats_data.get('happiness_effect', 0),
            pollution=stats_data.get('pollution', 0),
            fire_risk=stats_data.get('fire_risk', 0)
        )
        
        return cls(
            id=data['id'],
            name_jp=data['name_jp'],
            name_en=data['name_en'],
            category=BuildingCategory(data['category']),
            cost=data['cost'],
            maintenance_cost=data.get('maintenance_cost', 0),
            unlock_condition=unlock_condition,
            stats=stats,
            sprite_name=data.get('sprite_name', data['id']),
            icon_name=data.get('icon_name', data['id']),
            size_width=data.get('size_width', 1),
            size_height=data.get('size_height', 1),
            description_jp=data.get('description_jp', ''),
            description_en=data.get('description_en', '')
        )


class Building:
    """配置された建物インスタンス"""
    
    def __init__(self, definition: BuildingDefinition, x: int, y: int):
        self.definition = definition
        self.x = x
        self.y = y
        self.placed_year = 1945
        self.condition = 100  # 建物の状態（0-100%）
        self.active = True
        self.upgrade_level = 0
        
        # 難易度調整されたコスト（後で設定）
        self.adjusted_cost = definition.cost
        self.adjusted_maintenance_cost = definition.maintenance_cost
        self.data = {}  # カスタムデータ
    
    @property
    def id(self) -> str:
        return self.definition.id
    
    @property
    def name_jp(self) -> str:
        return self.definition.name_jp
    
    @property
    def category(self) -> BuildingCategory:
        return self.definition.category
    
    @property
    def size(self) -> tuple:
        return (self.definition.size_width, self.definition.size_height)
    
    def get_effective_stats(self) -> BuildingStats:
        """現在の状態を反映した効果的な統計を取得"""
        base_stats = self.definition.stats
        condition_factor = self.condition / 100.0
        active_factor = 1.0 if self.active else 0.0
        
        # 状態に基づいて統計を調整
        return BuildingStats(
            population_capacity=int(base_stats.population_capacity * condition_factor * active_factor),
            jobs_provided=int(base_stats.jobs_provided * condition_factor * active_factor),
            power_consumption=int(base_stats.power_consumption * active_factor),
            water_consumption=int(base_stats.water_consumption * active_factor),
            power_production=int(base_stats.power_production * condition_factor * active_factor),
            water_production=int(base_stats.water_production * condition_factor * active_factor),
            happiness_effect=int(base_stats.happiness_effect * condition_factor),
            pollution=int(base_stats.pollution * active_factor),
            fire_risk=int(base_stats.fire_risk * (2.0 - condition_factor))  # 状態が悪いほど火災リスク増加
        )
    
    def update(self, current_year: int):
        """建物状態を更新"""
        # 経年劣化
        age = current_year - self.placed_year
        degradation_rate = 0.5  # 年あたりの劣化率
        self.condition = max(0, 100 - age * degradation_rate)
        
        # 維持費未払いの場合は非活性化（将来実装）
        # if not paid_maintenance:
        #     self.active = False
    
    def repair(self, amount: int = 50):
        """建物を修理"""
        self.condition = min(100, self.condition + amount)
    
    def demolish(self):
        """建物を解体準備"""
        self.active = False
        self.condition = 0
    
    def get_occupying_cells(self) -> List[tuple]:
        """建物が占有するセル座標のリストを取得"""
        cells = []
        for dy in range(self.definition.size_height):
            for dx in range(self.definition.size_width):
                cells.append((self.x + dx, self.y + dy))
        return cells
    
    def to_dict(self) -> Dict[str, Any]:
        """建物データを辞書に変換（セーブ用）"""
        return {
            'definition_id': self.definition.id,
            'x': self.x,
            'y': self.y,
            'placed_year': self.placed_year,
            'condition': self.condition,
            'active': self.active,
            'upgrade_level': self.upgrade_level,
            'data': self.data
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any], definitions: Dict[str, BuildingDefinition]) -> 'Building':
        """辞書から建物インスタンスを復元（ロード用）"""
        definition = definitions[data['definition_id']]
        building = cls(definition, data['x'], data['y'])
        building.placed_year = data.get('placed_year', 1945)
        building.condition = data.get('condition', 100)
        building.active = data.get('active', True)
        building.upgrade_level = data.get('upgrade_level', 0)
        building.data = data.get('data', {})
        return building