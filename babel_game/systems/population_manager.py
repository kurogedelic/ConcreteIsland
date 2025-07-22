"""
人口管理システム
Population Management System
"""

import random
from typing import Dict, List, Optional, Tuple
from models.citizen import Citizen, CitizenJob, CitizenAge
from models.building import Building, BuildingCategory
from core.event_manager import event_manager
from config.game_config import GameConfig


class PopulationManager:
    """人口管理クラス"""
    
    def __init__(self):
        self.citizens: List[Citizen] = []
        self.population_growth_rate = 0.02  # 年間人口増加率
        self.birth_rate = 0.025  # 出生率
        self.death_rate = 0.015  # 死亡率
        self.migration_rate = 0.01  # 移住率
        
        # 統計情報
        self.total_population = 0
        self.working_population = 0
        self.unemployed_population = 0
        self.average_happiness = 50.0
        self.average_age = 30.0
        
        # 住宅・職場管理
        self.available_housing: List[Tuple[int, int, int]] = []  # (x, y, capacity)
        self.available_jobs: List[Tuple[CitizenJob, int, int, int]] = []  # (job, x, y, salary)
        
        # イベントリスナー登録
        self._register_event_listeners()
    
    def _register_event_listeners(self):
        """イベントリスナーを登録"""
        event_manager.register_listener("building_placed", self._on_building_placed)
        event_manager.register_listener("building_removed", self._on_building_removed)
        event_manager.register_listener("year_changed", self._on_year_changed)
        event_manager.register_listener("month_changed", self._on_month_changed)
    
    def initialize_population(self, building_manager):
        """初期人口を設定"""
        # 住宅建物から初期住民を生成
        residential_buildings = building_manager.get_buildings_by_category(BuildingCategory.RESIDENTIAL)
        
        for building in residential_buildings:
            capacity = building.get_effective_stats().population_capacity
            # 初期は70%程度の入居率
            initial_residents = int(capacity * 0.7)
            
            for _ in range(initial_residents):
                citizen = self._create_citizen(building.x, building.y)
                self.citizens.append(citizen)
        
        self._update_statistics()
        print(f"初期人口: {len(self.citizens)}人")
    
    def update(self, current_year: int, current_month: int, building_manager):
        """人口システムを更新"""
        # 住宅・職場情報を更新
        self._update_housing_and_jobs(building_manager)
        
        # 住民の状態更新
        city_state = {'current_year': current_year}
        for citizen in self.citizens:
            citizen.update_needs(city_state)
            citizen.calculate_happiness()
            citizen.update_movement()
        
        # 統計更新
        self._update_statistics()
    
    def _update_housing_and_jobs(self, building_manager):
        """住宅と職場情報を更新"""
        self.available_housing.clear()
        self.available_jobs.clear()
        
        for building in building_manager.buildings:
            stats = building.get_effective_stats()
            
            # 住宅容量
            if stats.population_capacity > 0:
                current_residents = self._count_residents_at(building.x, building.y)
                available_capacity = stats.population_capacity - current_residents
                if available_capacity > 0:
                    self.available_housing.append((building.x, building.y, available_capacity))
            
            # 雇用機会
            if stats.jobs_provided > 0:
                current_workers = self._count_workers_at(building.x, building.y)
                available_jobs = stats.jobs_provided - current_workers
                
                if available_jobs > 0:
                    # 建物タイプに応じた職業と給与
                    job_type, salary = self._get_job_info(building.definition.category)
                    for _ in range(available_jobs):
                        self.available_jobs.append((job_type, building.x, building.y, salary))
    
    def _get_job_info(self, building_category: BuildingCategory) -> Tuple[CitizenJob, int]:
        """建物カテゴリから職業情報を取得"""
        job_mapping = {
            BuildingCategory.INDUSTRIAL: (CitizenJob.FACTORY_WORKER, 80),
            BuildingCategory.COMMERCIAL: (CitizenJob.SHOP_KEEPER, 60),
            BuildingCategory.CIVIC: (CitizenJob.GOVERNMENT, 100),
            BuildingCategory.RECREATION: (CitizenJob.OFFICE_WORKER, 70)
        }
        return job_mapping.get(building_category, (CitizenJob.OFFICE_WORKER, 50))
    
    def _count_residents_at(self, x: int, y: int) -> int:
        """指定位置の住民数をカウント"""
        return sum(1 for c in self.citizens if c.home_x == x and c.home_y == y)
    
    def _count_workers_at(self, x: int, y: int) -> int:
        """指定位置の労働者数をカウント"""
        return sum(1 for c in self.citizens if c.work_x == x and c.work_y == y)
    
    def _create_citizen(self, x: int, y: int, birth_year: int = None) -> Citizen:
        """新しい住民を作成"""
        if birth_year is None:
            # 戦後復興期の年齢分布を考慮
            age_distribution = [
                (1920, 0.1),  # 高齢者
                (1925, 0.15), # 中年
                (1930, 0.2),  # 青年
                (1935, 0.25), # 若年成人
                (1940, 0.3)   # 青少年
            ]
            
            rand = random.random()
            cumulative = 0
            for year, prob in age_distribution:
                cumulative += prob
                if rand < cumulative:
                    birth_year = year
                    break
            else:
                birth_year = 1945  # デフォルト
        
        citizen = Citizen(x, y, birth_year)
        
        # 初期職業の設定（成人のみ）
        if citizen.get_age_category(1945) == CitizenAge.ADULT:
            if random.random() < 0.7:  # 70%の確率で職業を持つ
                citizen.find_job(self.available_jobs)
        
        return citizen
    
    def process_migration(self, current_year: int):
        """移住処理"""
        # 住宅不足による人口流出
        housing_shortage = max(0, len(self.citizens) - self._get_total_housing_capacity())
        if housing_shortage > 0:
            # 住宅不足者の一部が流出
            emigrants = min(housing_shortage, int(len(self.citizens) * 0.1))
            for _ in range(emigrants):
                if self.citizens:
                    citizen = random.choice(self.citizens)
                    self.citizens.remove(citizen)
                    event_manager.emit_event("citizen_emigrated", citizen)
        
        # 新規移住者（住宅に余裕がある場合）
        available_housing_capacity = self._get_available_housing_capacity()
        if available_housing_capacity > 0:
            # 都市の魅力度に基づく移住者数
            attraction_factor = min(1.0, self.average_happiness / 100.0)
            potential_immigrants = int(available_housing_capacity * attraction_factor * self.migration_rate)
            
            for _ in range(potential_immigrants):
                if self.available_housing:
                    housing = random.choice(self.available_housing)
                    immigrant = self._create_citizen(housing[0], housing[1], 
                                                   current_year - random.randint(20, 40))
                    self.citizens.append(immigrant)
                    event_manager.emit_event("citizen_immigrated", immigrant)
    
    def process_birth_death(self, current_year: int):
        """出生・死亡処理"""
        # 出生処理
        adult_population = len([c for c in self.citizens 
                              if c.get_age_category(current_year) == CitizenAge.ADULT])
        potential_births = int(adult_population * self.birth_rate)
        
        for _ in range(potential_births):
            # 住宅に余裕がある場合のみ
            if self.available_housing:
                housing = random.choice(self.available_housing)
                newborn = self._create_citizen(housing[0], housing[1], current_year)
                self.citizens.append(newborn)
                event_manager.emit_event("citizen_born", newborn)
        
        # 死亡処理
        deaths = []
        for citizen in self.citizens:
            age = current_year - citizen.birth_year
            death_probability = self.death_rate
            
            # 年齢による死亡率調整
            if age > 70:
                death_probability *= 3
            elif age > 60:
                death_probability *= 2
            elif age < 1:
                death_probability *= 2
            
            # 健康状態の影響
            health_factor = max(0.1, citizen.health / 100.0)
            death_probability /= health_factor
            
            if random.random() < death_probability:
                deaths.append(citizen)
        
        for citizen in deaths:
            self.citizens.remove(citizen)
            event_manager.emit_event("citizen_died", citizen)
    
    def _get_total_housing_capacity(self) -> int:
        """総住宅容量を取得"""
        return sum(capacity for _, _, capacity in self.available_housing)
    
    def _get_available_housing_capacity(self) -> int:
        """利用可能住宅容量を取得"""
        total_capacity = self._get_total_housing_capacity()
        current_residents = len(self.citizens)
        return max(0, total_capacity - current_residents)
    
    def _update_statistics(self):
        """統計情報を更新"""
        if not self.citizens:
            self.total_population = 0
            self.working_population = 0
            self.unemployed_population = 0
            self.average_happiness = 0
            self.average_age = 0
            return
        
        self.total_population = len(self.citizens)
        self.working_population = len([c for c in self.citizens if c.job != CitizenJob.UNEMPLOYED])
        self.unemployed_population = self.total_population - self.working_population
        
        total_happiness = sum(c.happiness for c in self.citizens)
        self.average_happiness = total_happiness / self.total_population
        
        current_year = 1945  # 仮の年（実際はgame_engineから取得）
        total_age = sum(current_year - c.birth_year for c in self.citizens)
        self.average_age = total_age / self.total_population
    
    def get_citizen_at(self, x: int, y: int) -> Optional[Citizen]:
        """指定位置の住民を取得"""
        for citizen in self.citizens:
            if citizen.x == x and citizen.y == y:
                return citizen
        return None
    
    def get_statistics(self) -> Dict[str, float]:
        """統計情報を取得"""
        return {
            'total_population': self.total_population,
            'working_population': self.working_population,
            'unemployed_population': self.unemployed_population,
            'unemployment_rate': (self.unemployed_population / max(1, self.total_population)) * 100,
            'average_happiness': self.average_happiness,
            'average_age': self.average_age,
            'available_housing': self._get_available_housing_capacity(),
            'available_jobs': len(self.available_jobs)
        }
    
    def get_population_by_age(self, current_year: int) -> Dict[str, int]:
        """年齢別人口を取得"""
        age_groups = {'child': 0, 'adult': 0, 'elderly': 0}
        
        for citizen in self.citizens:
            age_category = citizen.get_age_category(current_year)
            age_groups[age_category.value] += 1
        
        return age_groups
    
    def _on_building_placed(self, building: Building):
        """建物配置イベントハンドラ"""
        stats = building.get_effective_stats()
        
        # 住宅建物の場合、移住者を追加する可能性
        if stats.population_capacity > 0:
            # 30%の確率で即座に住民が入居
            if random.random() < 0.3:
                new_residents = min(stats.population_capacity, 
                                  random.randint(1, stats.population_capacity))
                for _ in range(new_residents):
                    citizen = self._create_citizen(building.x, building.y)
                    self.citizens.append(citizen)
        
        self._update_statistics()
    
    def _on_building_removed(self, building: Building):
        """建物削除イベントハンドラ"""
        # 該当建物の住民・労働者を処理
        affected_citizens = []
        
        for citizen in self.citizens:
            # 住居を失った住民
            if citizen.home_x == building.x and citizen.home_y == building.y:
                if self.available_housing:
                    # 他の住宅に移転
                    new_housing = random.choice(self.available_housing)
                    citizen.home_x = new_housing[0]
                    citizen.home_y = new_housing[1]
                else:
                    # 住宅不足で流出
                    affected_citizens.append(citizen)
            
            # 職場を失った住民
            if citizen.work_x == building.x and citizen.work_y == building.y:
                citizen.lose_job()
        
        # 住宅不足者を削除
        for citizen in affected_citizens:
            self.citizens.remove(citizen)
        
        self._update_statistics()
    
    def _on_year_changed(self, new_year: int):
        """年変更イベントハンドラ"""
        # 年次人口変動処理
        self.process_birth_death(new_year)
        self.process_migration(new_year)
        self._update_statistics()
    
    def _on_month_changed(self, year: int, month: int):
        """月変更イベントハンドラ"""
        # 月次の失業者就職活動
        unemployed = [c for c in self.citizens if c.job == CitizenJob.UNEMPLOYED]
        for citizen in unemployed:
            if citizen.get_age_category(year) == CitizenAge.ADULT:
                citizen.find_job(self.available_jobs)
    
    def _restore_citizen_from_dict(self, citizen_data: Dict) -> Optional[Citizen]:
        """辞書から住民インスタンスを復元（ロード用）"""
        try:
            from models.citizen import Citizen
            citizen = Citizen.from_dict(citizen_data)
            return citizen
        except Exception as e:
            print(f"Error restoring citizen from dict: {e}")
            return None