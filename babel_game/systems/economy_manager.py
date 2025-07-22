"""
経済管理システム
Economy Management System
"""

import random
from typing import Dict, List, Optional, Tuple
from models.economy import EconomicData, ResourceType, TradeEvent, EconomicEvent, MarketCondition
from models.building import Building, BuildingCategory
from core.event_manager import event_manager
from config.game_config import GameConfig
from systems.difficulty_manager import difficulty_manager


class EconomyManager:
    """経済管理クラス"""
    
    def __init__(self):
        # 難易度に応じた初期資金を設定
        starting_money = difficulty_manager.get_starting_money()
        self.economic_data = EconomicData()
        self.economic_data.money = starting_money
        self.market_condition = MarketCondition()
        self.trade_events: List[TradeEvent] = []
        self.economic_events: List[EconomicEvent] = []
        
        # 月間収支追跡
        self.monthly_income_sources: Dict[str, int] = {}
        self.monthly_expense_sources: Dict[str, int] = {}
        
        # 経済政策
        self.tax_rate = 0.1
        self.subsidies_enabled = True
        
        # 月次精算フラグ
        self.last_settled_month = 0
        self.last_settled_year = GameConfig.START_YEAR
        
        # イベントリスナー登録
        self._register_event_listeners()
    
    def _register_event_listeners(self):
        """イベントリスナーを登録"""
        event_manager.register_listener("building_placed", self._on_building_placed)
        event_manager.register_listener("building_removed", self._on_building_removed)
        event_manager.register_listener("year_changed", self._on_year_changed)
        event_manager.register_listener("month_changed", self._on_month_changed)
        event_manager.register_listener("citizen_immigrated", self._on_citizen_immigrated)
        event_manager.register_listener("citizen_emigrated", self._on_citizen_emigrated)
    
    def _should_settle_monthly(self, current_year: int, current_month: int) -> bool:
        """月次精算を行うべきかチェック"""
        return (current_year != self.last_settled_year or 
                current_month != self.last_settled_month)
    
    def _settle_monthly_budget(self):
        """月次精算処理"""
        # 収入を追加
        net_income = self.economic_data.monthly_income - self.economic_data.monthly_expenses
        self.economic_data.add_resource(ResourceType.MONEY, net_income)
        
        # 純利益を更新
        self.economic_data.net_income = net_income
        
        # イベント発火
        event_manager.emit_event("monthly_budget_settled", {
            'income': self.economic_data.monthly_income,
            'expenses': self.economic_data.monthly_expenses,
            'net_income': net_income,
            'money': self.economic_data.money
        })
    
    def update(self, current_year: int, current_month: int, building_manager, population_manager):
        """経済システムを更新"""
        # 市場状況更新（毎フレーム）
        self.market_condition.update_market(self.economic_data)
        
        # 月次精算チェック
        if self._should_settle_monthly(current_year, current_month):
            # 月間収支計算と精算（月1回のみ）
            self._calculate_monthly_income(building_manager, population_manager, current_year)
            self._calculate_monthly_expenses(building_manager, population_manager)
            
            # 月次精算処理
            self._settle_monthly_budget()
            
            # 精算済みフラグ更新
            self.last_settled_month = current_month
            self.last_settled_year = current_year
        
        # 資源生産・消費（毎フレーム - ただし量は調整済み）
        self._process_resource_production(building_manager)
        self._process_resource_consumption(population_manager)
        
        # 貿易機会の生成（毎フレーム）
        self._generate_trade_opportunities(current_year)
    
    def _calculate_monthly_income(self, building_manager, population_manager, current_year):
        """月間収入を計算"""
        self.monthly_income_sources.clear()
        total_income = 0
        
        # 税収
        pop_stats = population_manager.get_statistics()
        working_population = pop_stats.get('working_population', 0)
        
        # 所得税
        income_tax = int(working_population * 100 * self.tax_rate)  # 平均所得100円と仮定
        self.monthly_income_sources['所得税'] = income_tax
        total_income += income_tax
        
        # 法人税
        commercial_buildings = building_manager.get_buildings_by_category(BuildingCategory.COMMERCIAL)
        industrial_buildings = building_manager.get_buildings_by_category(BuildingCategory.INDUSTRIAL)
        
        corporate_tax = len(commercial_buildings) * 50 + len(industrial_buildings) * 100
        self.monthly_income_sources['法人税'] = corporate_tax
        total_income += corporate_tax
        
        # 特需収入（朝鮮戦争期）
        if 1950 <= current_year <= 1953:
            special_demand_income = len(industrial_buildings) * 200
            self.monthly_income_sources['特需収入'] = special_demand_income
            total_income += special_demand_income
        
        # 貿易収入
        export_income = self._calculate_export_income()
        if export_income > 0:
            self.monthly_income_sources['輸出収入'] = export_income
            total_income += export_income
        
        self.economic_data.monthly_income = total_income
        # 月次精算時にまとめて追加するため、ここでは追加しない
    
    def _calculate_monthly_expenses(self, building_manager, population_manager):
        """月間支出を計算"""
        self.monthly_expense_sources.clear()
        total_expenses = 0
        
        # 建物維持費（調整済みコスト使用）
        maintenance_cost = 0
        for building in building_manager.buildings:
            if hasattr(building, 'adjusted_maintenance_cost'):
                maintenance_cost += building.adjusted_maintenance_cost
            else:
                maintenance_cost += building.definition.maintenance_cost
        
        self.monthly_expense_sources['建物維持費'] = maintenance_cost
        total_expenses += maintenance_cost
        
        # 公務員給与
        civic_buildings = building_manager.get_buildings_by_category(BuildingCategory.CIVIC)
        government_salaries = len(civic_buildings) * 500
        self.monthly_expense_sources['公務員給与'] = government_salaries
        total_expenses += government_salaries
        
        # 社会保障費
        pop_stats = population_manager.get_statistics()
        total_population = pop_stats.get('total_population', 0)
        social_security = int(total_population * 20)  # 1人あたり20円
        self.monthly_expense_sources['社会保障費'] = social_security
        total_expenses += social_security
        
        # インフラ維持費
        infra_buildings = building_manager.get_buildings_by_category(BuildingCategory.INFRA)
        infrastructure_cost = len(infra_buildings) * 30
        self.monthly_expense_sources['インフラ維持'] = infrastructure_cost
        total_expenses += infrastructure_cost
        
        # 輸入費用
        import_cost = self._calculate_import_cost()
        if import_cost > 0:
            self.monthly_expense_sources['輸入費用'] = import_cost
            total_expenses += import_cost
        
        self.economic_data.monthly_expenses = total_expenses
        # 月次精算時にまとめて支出するため、ここでは支出しない
    
    def _process_resource_production(self, building_manager):
        """資源生産を処理（日次ベースに調整）"""
        # 生産量を1/30に調整（月30日として）
        daily_rate = 1.0 / 30.0
        
        for building in building_manager.buildings:
            # 建物タイプに応じた資源生産
            if building.definition.category == BuildingCategory.INDUSTRIAL:
                if "factory" in building.definition.id:
                    # 工場は鉄と製品を生産（日次レート）
                    self.economic_data.add_resource(ResourceType.IRON, int(10 * daily_rate))
                    self.economic_data.add_resource(ResourceType.MONEY, int(100 * daily_rate))
                    # 石炭を消費
                    self.economic_data.spend_resource(ResourceType.COAL, int(5 * daily_rate))
            
            elif building.definition.category == BuildingCategory.COMMERCIAL:
                if "shop" in building.definition.id:
                    # 商店は売上を生産（日次レート）
                    self.economic_data.add_resource(ResourceType.MONEY, int(50 * daily_rate))
                    # 米を消費
                    self.economic_data.spend_resource(ResourceType.RICE, 2)
            
            # 電力生産建物
            stats = building.get_effective_stats()
            if stats.power_production > 0:
                self.economic_data.add_resource(ResourceType.ELECTRICITY, stats.power_production)
                # 石炭を消費
                self.economic_data.spend_resource(ResourceType.COAL, stats.power_production // 10)
    
    def _process_resource_consumption(self, population_manager):
        """資源消費を処理"""
        pop_stats = population_manager.get_statistics()
        total_population = pop_stats.get('total_population', 0)
        
        # 住民の食料消費
        rice_consumption = total_population * 2  # 1人あたり2kg/月
        self.economic_data.spend_resource(ResourceType.RICE, rice_consumption)
        
        # 住民の燃料消費
        wood_consumption = total_population * 1  # 1人あたり1kg/月
        self.economic_data.spend_resource(ResourceType.WOOD, wood_consumption)
        
        # 電力消費
        electricity_consumption = total_population * 5  # 1人あたり5kW/月
        self.economic_data.spend_resource(ResourceType.ELECTRICITY, electricity_consumption)
    
    def _calculate_export_income(self) -> int:
        """輸出収入を計算"""
        export_income = 0
        
        # 余剰資源の輸出
        if self.economic_data.iron > 1000:
            export_amount = min(500, self.economic_data.iron - 1000)
            export_income += export_amount * self.economic_data.iron_price
            self.economic_data.spend_resource(ResourceType.IRON, export_amount)
        
        if self.economic_data.rice > 1500:
            export_amount = min(300, self.economic_data.rice - 1500)
            export_income += export_amount * self.economic_data.rice_price
            self.economic_data.spend_resource(ResourceType.RICE, export_amount)
        
        return export_income
    
    def _calculate_import_cost(self) -> int:
        """輸入費用を計算"""
        import_cost = 0
        
        # 不足資源の輸入
        if self.economic_data.rice < 200:
            import_amount = 300
            import_cost += import_amount * self.economic_data.rice_price
            self.economic_data.add_resource(ResourceType.RICE, import_amount)
        
        if self.economic_data.coal < 100:
            import_amount = 200
            import_cost += import_amount * self.economic_data.coal_price
            self.economic_data.add_resource(ResourceType.COAL, import_amount)
        
        return import_cost
    
    def _generate_trade_opportunities(self, current_year: int):
        """貿易機会を生成"""
        # 月に1回程度の確率で貿易イベント発生
        if random.random() < 0.3:
            resource_type = random.choice(list(ResourceType)[1:5])  # MONEY以外
            
            if random.random() < 0.6:  # 60%の確率で輸入
                amount = random.randint(100, 500)
                base_price = getattr(self.economic_data, f"{resource_type.value}_price")
                price = int(base_price * random.uniform(0.8, 1.2))
                
                trade_event = TradeEvent(resource_type, amount, price, "import")
                self.trade_events.append(trade_event)
            else:  # 40%の確率で輸出
                current_amount = self.economic_data.get_resource(resource_type)
                if current_amount > 200:
                    max_export = min(300, current_amount - 200)
                    if max_export >= 50:
                        amount = random.randint(50, max_export)
                        base_price = getattr(self.economic_data, f"{resource_type.value}_price")
                        price = int(base_price * random.uniform(0.7, 1.1))
                        
                        trade_event = TradeEvent(resource_type, amount, price, "export")
                        self.trade_events.append(trade_event)
    
    def can_afford_building(self, building_definition, current_year: int) -> bool:
        """建物を建設できるかチェック（調整済みコスト使用）"""
        # 難易度と年代に応じた調整済み建設費用
        adjusted_cost = difficulty_manager.get_adjusted_cost(building_definition.cost, current_year)
        
        if self.economic_data.money < adjusted_cost:
            return False
        
        # 建物タイプに応じた追加資源要求
        additional_costs = self._get_building_resource_costs(building_definition, adjusted_cost)
        return self.economic_data.can_afford(additional_costs)
    
    def _get_building_resource_costs(self, building_definition, adjusted_cost: int) -> Dict[ResourceType, int]:
        """建物の資源コストを取得"""
        costs = {ResourceType.MONEY: adjusted_cost}
        
        # 建物タイプに応じた材料コスト
        if building_definition.category == BuildingCategory.RESIDENTIAL:
            costs[ResourceType.WOOD] = 50
            costs[ResourceType.IRON] = 20
        elif building_definition.category == BuildingCategory.INDUSTRIAL:
            costs[ResourceType.IRON] = 100
            costs[ResourceType.COAL] = 50
        elif building_definition.category == BuildingCategory.COMMERCIAL:
            costs[ResourceType.WOOD] = 30
            costs[ResourceType.IRON] = 10
        elif building_definition.category == BuildingCategory.INFRA:
            costs[ResourceType.IRON] = 15
            costs[ResourceType.WOOD] = 10
        
        return costs
    
    def purchase_building(self, building_definition, current_year: int) -> bool:
        """建物を購入（調整済みコスト使用）"""
        adjusted_cost = difficulty_manager.get_adjusted_cost(building_definition.cost, current_year)
        costs = self._get_building_resource_costs(building_definition, adjusted_cost)
        
        if self.economic_data.pay_costs(costs):
            event_manager.emit_event("building_purchased", building_definition, costs)
            return True
        return False
    
    def execute_trade(self, trade_event: TradeEvent) -> bool:
        """貿易を実行"""
        if trade_event.event_type == "import":
            if self.economic_data.spend_resource(ResourceType.MONEY, trade_event.total_cost):
                self.economic_data.add_resource(trade_event.resource_type, trade_event.amount)
                event_manager.emit_event("trade_executed", trade_event)
                return True
        elif trade_event.event_type == "export":
            if self.economic_data.spend_resource(trade_event.resource_type, trade_event.amount):
                self.economic_data.add_resource(ResourceType.MONEY, trade_event.total_cost)
                event_manager.emit_event("trade_executed", trade_event)
                return True
        
        return False
    
    def generate_economic_event(self, year: int) -> Optional[EconomicEvent]:
        """経済イベントを生成"""
        if year >= 1950 and year <= 1953 and random.random() < 0.3:
            return EconomicEvent.create_korean_war_boom(year)
        elif year >= 1955 and random.random() < 0.2:
            return EconomicEvent.create_infrastructure_investment(year)
        elif random.random() < 0.1:
            return EconomicEvent.create_rice_shortage(year)
        elif year >= 1960 and random.random() < 0.15:
            return EconomicEvent.create_technology_advancement(year)
        
        return None
    
    def apply_economic_event(self, event: EconomicEvent):
        """経済イベントを適用"""
        for effect_type, amount in event.effects.items():
            if effect_type in [r.value for r in ResourceType]:
                resource_type = ResourceType(effect_type)
                if amount > 0:
                    self.economic_data.add_resource(resource_type, amount)
                else:
                    self.economic_data.spend_resource(resource_type, abs(amount))
        
        self.economic_events.append(event)
        event_manager.emit_event("economic_event_applied", event)
    
    def get_economic_summary(self) -> Dict[str, any]:
        """経済概要を取得"""
        return {
            'money': self.economic_data.money,
            'rice': self.economic_data.rice,
            'iron': self.economic_data.iron,
            'wood': self.economic_data.wood,
            'coal': self.economic_data.coal,
            'electricity': self.economic_data.electricity,
            'monthly_income': self.economic_data.monthly_income,
            'monthly_expenses': self.economic_data.monthly_expenses,
            'net_income': self.economic_data.monthly_income - self.economic_data.monthly_expenses,
            'total_value': self.economic_data.get_total_value(),
            'market_condition': self.market_condition.get_market_report(),
            'rice_price': self.economic_data.rice_price,
            'iron_price': self.economic_data.iron_price,
            'wood_price': self.economic_data.wood_price,
            'coal_price': self.economic_data.coal_price
        }
    
    def get_budget_breakdown(self) -> Dict[str, Dict[str, int]]:
        """予算内訳を取得"""
        return {
            'income': self.monthly_income_sources.copy(),
            'expenses': self.monthly_expense_sources.copy()
        }
    
    def _on_building_placed(self, building: Building):
        """建物配置イベントハンドラ"""
        # 建物配置時の経済効果
        if building.definition.category == BuildingCategory.COMMERCIAL:
            # 商業建物は経済活動を活性化
            self.economic_data.add_resource(ResourceType.MONEY, 200)
        elif building.definition.category == BuildingCategory.INDUSTRIAL:
            # 工業建物は雇用と生産を創出
            self.economic_data.add_resource(ResourceType.MONEY, 300)
    
    def _on_building_removed(self, building: Building):
        """建物削除イベントハンドラ"""
        # 建物削除時の経済損失
        loss = building.definition.cost // 4  # 建設費の1/4を損失
        self.economic_data.spend_resource(ResourceType.MONEY, loss)
    
    def _on_year_changed(self, new_year: int):
        """年変更イベントハンドラ"""
        # 年次経済イベントの処理
        economic_event = self.generate_economic_event(new_year)
        if economic_event:
            self.apply_economic_event(economic_event)
        
        # 年次インフレ調整
        inflation_factor = 1 + self.market_condition.inflation_rate
        self.economic_data.rice_price = int(self.economic_data.rice_price * inflation_factor)
        self.economic_data.iron_price = int(self.economic_data.iron_price * inflation_factor)
        self.economic_data.wood_price = int(self.economic_data.wood_price * inflation_factor)
        self.economic_data.coal_price = int(self.economic_data.coal_price * inflation_factor)
    
    def _on_month_changed(self, year: int, month: int):
        """月変更イベントハンドラ"""
        # 月次の貿易イベントをクリア
        self.trade_events.clear()
    
    def _on_citizen_immigrated(self, citizen):
        """住民流入イベントハンドラ"""
        # 人口増加による経済効果
        self.economic_data.add_resource(ResourceType.MONEY, 100)
    
    def _on_citizen_emigrated(self, citizen):
        """住民流出イベントハンドラ"""
        # 人口減少による経済損失
        self.economic_data.spend_resource(ResourceType.MONEY, 50)