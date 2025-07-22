"""
経済データモデル
Economy Data Model
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random


class ResourceType(Enum):
    """資源タイプ"""
    MONEY = "money"      # 円
    RICE = "rice"        # 米
    IRON = "iron"        # 鉄
    WOOD = "wood"        # 木材
    COAL = "coal"        # 石炭
    ELECTRICITY = "electricity"  # 電力


@dataclass
class EconomicData:
    """経済データ"""
    money: int = 10000000        # デバッグ用潤沢資金: ¥10,000,000
    rice: int = 1000             # 米 (kg)
    iron: int = 500              # 鉄 (kg)
    wood: int = 2000             # 木材 (kg)
    coal: int = 800              # 石炭 (kg)
    electricity: int = 0         # 電力 (kW)
    
    # 月間収支
    monthly_income: int = 0
    monthly_expenses: int = 0
    
    # 税収
    tax_rate: float = 0.1        # 税率 10%
    
    # 物価・相場
    rice_price: int = 50         # 米1kgの価格
    iron_price: int = 100        # 鉄1kgの価格
    wood_price: int = 30         # 木材1kgの価格
    coal_price: int = 80         # 石炭1kgの価格
    
    def get_resource(self, resource_type: ResourceType) -> int:
        """資源を取得"""
        return getattr(self, resource_type.value, 0)
    
    def set_resource(self, resource_type: ResourceType, amount: int):
        """資源を設定"""
        setattr(self, resource_type.value, max(0, amount))
    
    def add_resource(self, resource_type: ResourceType, amount: int):
        """資源を追加"""
        current = self.get_resource(resource_type)
        self.set_resource(resource_type, current + amount)
    
    def spend_resource(self, resource_type: ResourceType, amount: int) -> bool:
        """資源を消費（成功/失敗を返す）"""
        current = self.get_resource(resource_type)
        if current >= amount:
            self.set_resource(resource_type, current - amount)
            return True
        return False
    
    def can_afford(self, costs: Dict[ResourceType, int]) -> bool:
        """コストを支払えるかチェック"""
        for resource_type, amount in costs.items():
            if self.get_resource(resource_type) < amount:
                return False
        return True
    
    def pay_costs(self, costs: Dict[ResourceType, int]) -> bool:
        """コストを支払う"""
        if not self.can_afford(costs):
            return False
        
        for resource_type, amount in costs.items():
            self.spend_resource(resource_type, amount)
        return True
    
    def get_total_value(self) -> int:
        """総資産価値を取得（円換算）"""
        return (self.money + 
                self.rice * self.rice_price +
                self.iron * self.iron_price +
                self.wood * self.wood_price +
                self.coal * self.coal_price)
    
    def calculate_net_worth(self) -> int:
        """純資産を計算"""
        return self.get_total_value()


class TradeEvent:
    """貿易イベント"""
    
    def __init__(self, resource_type: ResourceType, amount: int, price_per_unit: int, 
                 event_type: str = "import"):
        self.resource_type = resource_type
        self.amount = amount
        self.price_per_unit = price_per_unit
        self.event_type = event_type  # "import", "export", "gift"
        self.total_cost = amount * price_per_unit
        self.description = self._generate_description()
    
    def _generate_description(self) -> str:
        """説明文を生成"""
        resource_names = {
            ResourceType.RICE: "米",
            ResourceType.IRON: "鉄",
            ResourceType.WOOD: "木材",
            ResourceType.COAL: "石炭"
        }
        
        resource_name = resource_names.get(self.resource_type, self.resource_type.value)
        
        if self.event_type == "import":
            return f"外国から{resource_name}{self.amount}kgを輸入 (¥{self.total_cost})"
        elif self.event_type == "export":
            return f"{resource_name}{self.amount}kgを輸出 (+¥{self.total_cost})"
        elif self.event_type == "gift":
            return f"援助物資: {resource_name}{self.amount}kgを受領"
        else:
            return f"{resource_name}の取引"


class EconomicEvent:
    """経済イベント"""
    
    def __init__(self, event_type: str, description: str, effects: Dict[str, int]):
        self.event_type = event_type
        self.description = description
        self.effects = effects  # {"money": 1000, "rice": -500} など
        self.year = 1945
    
    @staticmethod
    def create_korean_war_boom(year: int) -> 'EconomicEvent':
        """朝鮮戦争特需イベント"""
        return EconomicEvent(
            "korean_war_boom",
            f"{year}年: 朝鮮戦争特需により工業生産が活発化",
            {"money": 5000, "iron": 1000, "coal": 500}
        )
    
    @staticmethod
    def create_rice_shortage(year: int) -> 'EconomicEvent':
        """米不足イベント"""
        return EconomicEvent(
            "rice_shortage",
            f"{year}年: 冷害により米が不足",
            {"rice": -800, "money": -2000}
        )
    
    @staticmethod
    def create_infrastructure_investment(year: int) -> 'EconomicEvent':
        """インフラ投資イベント"""
        return EconomicEvent(
            "infrastructure_investment",
            f"{year}年: 政府のインフラ投資により建設資材が豊富に",
            {"wood": 1500, "iron": 800, "money": 3000}
        )
    
    @staticmethod
    def create_technology_advancement(year: int) -> 'EconomicEvent':
        """技術進歩イベント"""
        return EconomicEvent(
            "technology_advancement",
            f"{year}年: 技術進歩により生産効率が向上",
            {"money": 4000, "electricity": 500}
        )


class MarketCondition:
    """市場状況"""
    
    def __init__(self):
        self.demand_rice = 50      # 米の需要 (0-100)
        self.demand_iron = 30      # 鉄の需要
        self.demand_wood = 40      # 木材の需要
        self.demand_coal = 35      # 石炭の需要
        
        self.supply_rice = 60      # 米の供給
        self.supply_iron = 40      # 鉄の供給
        self.supply_wood = 70      # 木材の供給
        self.supply_coal = 50      # 石炭の供給
        
        self.inflation_rate = 0.02 # インフレ率
    
    def update_market(self, economic_data: EconomicData):
        """市場状況を更新"""
        # 需要と供給の変動
        self.demand_rice += random.randint(-5, 5)
        self.demand_iron += random.randint(-3, 8)  # 工業化で需要増
        self.demand_wood += random.randint(-3, 5)
        self.demand_coal += random.randint(-2, 6)
        
        self.supply_rice += random.randint(-3, 3)
        self.supply_iron += random.randint(-2, 4)
        self.supply_wood += random.randint(-2, 6)
        self.supply_coal += random.randint(-2, 4)
        
        # 0-100の範囲に制限
        self.demand_rice = max(0, min(100, self.demand_rice))
        self.demand_iron = max(0, min(100, self.demand_iron))
        self.demand_wood = max(0, min(100, self.demand_wood))
        self.demand_coal = max(0, min(100, self.demand_coal))
        
        self.supply_rice = max(0, min(100, self.supply_rice))
        self.supply_iron = max(0, min(100, self.supply_iron))
        self.supply_wood = max(0, min(100, self.supply_wood))
        self.supply_coal = max(0, min(100, self.supply_coal))
        
        # 価格調整
        self._adjust_prices(economic_data)
    
    def _adjust_prices(self, economic_data: EconomicData):
        """需給バランスに基づいて価格を調整"""
        # 需要 > 供給なら価格上昇
        rice_balance = (self.demand_rice - self.supply_rice) / 100
        iron_balance = (self.demand_iron - self.supply_iron) / 100
        wood_balance = (self.demand_wood - self.supply_wood) / 100
        coal_balance = (self.demand_coal - self.supply_coal) / 100
        
        # 価格調整（基準価格の±30%以内）
        base_rice_price = 50
        base_iron_price = 100
        base_wood_price = 30
        base_coal_price = 80
        
        economic_data.rice_price = int(base_rice_price * (1 + rice_balance * 0.3))
        economic_data.iron_price = int(base_iron_price * (1 + iron_balance * 0.3))
        economic_data.wood_price = int(base_wood_price * (1 + wood_balance * 0.3))
        economic_data.coal_price = int(base_coal_price * (1 + coal_balance * 0.3))
    
    def get_market_report(self) -> str:
        """市場レポートを取得"""
        conditions = []
        
        if self.demand_rice > self.supply_rice + 20:
            conditions.append("米不足深刻")
        elif self.demand_rice < self.supply_rice - 20:
            conditions.append("米余り")
        
        if self.demand_iron > self.supply_iron + 15:
            conditions.append("鉄鋼需要旺盛")
        elif self.demand_iron < self.supply_iron - 15:
            conditions.append("鉄鋼需要低迷")
        
        if self.demand_wood > self.supply_wood + 15:
            conditions.append("建材不足")
        elif self.demand_wood < self.supply_wood - 15:
            conditions.append("建材余り")
        
        if not conditions:
            conditions.append("市場安定")
        
        return "、".join(conditions)