"""
ゲームバランス設定
Game Balance Configuration
"""

from enum import Enum


class DifficultyLevel(Enum):
    """難易度レベル"""
    EASY = "easy"
    NORMAL = "normal"
    HARD = "hard"


class BalanceConfig:
    """ゲームバランス設定クラス"""
    
    # 難易度別の設定
    DIFFICULTY_SETTINGS = {
        DifficultyLevel.EASY: {
            "starting_money": 15000,      # 初期資金
            "cost_multiplier": 0.8,        # 建設コスト倍率
            "income_multiplier": 1.2,      # 収入倍率
            "maintenance_multiplier": 0.7, # 維持費倍率
            "disaster_frequency": 0.5,     # 災害頻度
            "population_growth_rate": 1.3, # 人口増加率
            "happiness_decay_rate": 0.7,   # 幸福度減衰率
        },
        DifficultyLevel.NORMAL: {
            "starting_money": 10000,
            "cost_multiplier": 1.0,
            "income_multiplier": 1.0,
            "maintenance_multiplier": 1.0,
            "disaster_frequency": 1.0,
            "population_growth_rate": 1.0,
            "happiness_decay_rate": 1.0,
        },
        DifficultyLevel.HARD: {
            "starting_money": 5000,
            "cost_multiplier": 1.3,
            "income_multiplier": 0.8,
            "maintenance_multiplier": 1.5,
            "disaster_frequency": 1.5,
            "population_growth_rate": 0.8,
            "happiness_decay_rate": 1.3,
        }
    }
    
    # 建物カテゴリ別の基本維持費率（建設コストに対する％）
    MAINTENANCE_COST_RATES = {
        "residential": 0.03,    # 住宅: 3%
        "commercial": 0.05,     # 商業: 5%
        "industrial": 0.06,     # 工業: 6%
        "civic": 0.04,          # 公共: 4%
        "infra": 0.02,          # インフラ: 2%
        "recreation": 0.03,     # 娯楽: 3%
        "special": 0.08         # 特殊: 8%
    }
    
    # 税収の基本設定
    TAX_SETTINGS = {
        "income_tax_per_worker": 150,      # 労働者1人あたりの所得税
        "corporate_tax_commercial": 100,    # 商業施設の法人税
        "corporate_tax_industrial": 200,    # 工業施設の法人税
        "property_tax_rate": 0.01,          # 固定資産税率
    }
    
    # 資源生産の基本設定
    RESOURCE_PRODUCTION = {
        "small_factory": {
            "money": 200,      # 日次売上
            "iron": 5,         # 鉄生産
            "coal_consume": 3  # 石炭消費
        },
        "auto_factory": {
            "money": 500,
            "iron": 15,
            "coal_consume": 10
        },
        "power_plant_coal": {
            "electricity": 100,
            "coal_consume": 20
        },
        "nuclear_plant": {
            "electricity": 300,
            "maintenance_special": 500  # 特別維持費
        }
    }
    
    # 年代別の経済修正
    ERA_MODIFIERS = {
        1945: {"income": 0.5, "cost": 0.8},      # 終戦直後
        1950: {"income": 1.2, "cost": 1.0},      # 朝鮮戦争特需
        1955: {"income": 1.5, "cost": 1.1},      # 高度成長期開始
        1960: {"income": 2.0, "cost": 1.3},      # 高度成長期
        1965: {"income": 2.5, "cost": 1.5},      # オリンピック景気
        1970: {"income": 3.0, "cost": 2.0}       # 万博景気
    }
    
    # 人口に基づく需要計算
    DEMAND_CALCULATION = {
        "residential_base": 50,              # 基本住宅需要
        "commercial_per_100_pop": 10,       # 100人あたりの商業需要
        "industrial_unemployment_rate": 0.2, # 失業率から工業需要を計算
        "civic_per_1000_pop": 5,           # 1000人あたりの公共施設需要
    }
    
    # イベントの影響
    EVENT_IMPACTS = {
        "earthquake": {
            "building_damage_rate": 0.3,    # 建物損壊率
            "population_loss_rate": 0.1,    # 人口減少率
            "reconstruction_cost": 5000     # 復興費用
        },
        "typhoon": {
            "building_damage_rate": 0.2,
            "population_loss_rate": 0.05,
            "reconstruction_cost": 3000
        },
        "fire": {
            "building_damage_rate": 0.4,
            "population_loss_rate": 0.15,
            "reconstruction_cost": 2000
        }
    }
    
    @classmethod
    def get_difficulty_settings(cls, difficulty: DifficultyLevel) -> dict:
        """指定難易度の設定を取得"""
        return cls.DIFFICULTY_SETTINGS.get(difficulty, cls.DIFFICULTY_SETTINGS[DifficultyLevel.NORMAL])
    
    @classmethod
    def calculate_adjusted_cost(cls, base_cost: int, difficulty: DifficultyLevel, year: int) -> int:
        """難易度と年代を考慮した調整済みコストを計算"""
        settings = cls.get_difficulty_settings(difficulty)
        era_modifier = cls.get_era_modifier(year)
        
        adjusted_cost = base_cost * settings["cost_multiplier"] * era_modifier["cost"]
        return int(adjusted_cost)
    
    @classmethod
    def calculate_adjusted_income(cls, base_income: int, difficulty: DifficultyLevel, year: int) -> int:
        """難易度と年代を考慮した調整済み収入を計算"""
        settings = cls.get_difficulty_settings(difficulty)
        era_modifier = cls.get_era_modifier(year)
        
        adjusted_income = base_income * settings["income_multiplier"] * era_modifier["income"]
        return int(adjusted_income)
    
    @classmethod
    def get_era_modifier(cls, year: int) -> dict:
        """年代に応じた修正値を取得"""
        # 最も近い年代の修正値を使用
        closest_year = min(cls.ERA_MODIFIERS.keys(), key=lambda y: abs(y - year) if y <= year else float('inf'))
        return cls.ERA_MODIFIERS.get(closest_year, {"income": 1.0, "cost": 1.0})
    
    @classmethod
    def calculate_maintenance_cost(cls, building_cost: int, category: str, difficulty: DifficultyLevel) -> int:
        """建物の維持費を計算"""
        base_rate = cls.MAINTENANCE_COST_RATES.get(category, 0.05)
        settings = cls.get_difficulty_settings(difficulty)
        
        maintenance_cost = building_cost * base_rate * settings["maintenance_multiplier"]
        return max(1, int(maintenance_cost))  # 最低1円