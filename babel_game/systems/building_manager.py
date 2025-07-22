"""
建物管理システム
Building Management System
"""

import json
import os
from typing import Dict, List, Optional, Set, Tuple
from models.building import Building, BuildingDefinition, BuildingCategory
from core.event_manager import event_manager
from config.game_config import GameConfig
from config.sprite_mapping import get_sprite_name, get_icon_name
from systems.animation_manager import animation_manager
from systems.difficulty_manager import difficulty_manager


class BuildingManager:
    """建物管理クラス"""
    
    def __init__(self):
        self.definitions: Dict[str, BuildingDefinition] = {}
        self.buildings: List[Building] = []
        self.grid_occupation: Dict[Tuple[int, int], Building] = {}
        self.unlocked_buildings: Set[str] = set()
        
        # 統計情報
        self.total_population_capacity = 0
        self.total_jobs = 0
        self.total_power_consumption = 0
        self.total_power_production = 0
        self.total_water_consumption = 0
        self.total_water_production = 0
        self.total_maintenance_cost = 0
        
        # イベントリスナー登録
        self._register_event_listeners()
    
    def _register_event_listeners(self):
        """イベントリスナーを登録"""
        event_manager.register_listener("year_changed", self._on_year_changed)
        event_manager.register_listener("build_requested", self._on_build_requested)
        event_manager.register_listener("destroy_requested", self._on_destroy_requested)
        event_manager.register_listener("technology_unlock", self._on_technology_unlock)
        event_manager.register_listener("technology_event_triggered", self._on_technology_event)
    
    def load_building_definitions(self, filepath: str = None) -> bool:
        """建物定義を読み込み"""
        if filepath is None:
            filepath = GameConfig.BUILDINGS_JSON
        
        try:
            # 相対パスの解決
            if not os.path.isabs(filepath):
                current_dir = os.path.dirname(os.path.abspath(__file__))
                filepath = os.path.join(current_dir, "..", filepath)
                filepath = os.path.normpath(filepath)
            
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 建物定義を読み込み
            buildings_data = data.get('buildings', {})
            for building_id, building_data in buildings_data.items():
                building_data['id'] = building_id
                # スプライト名を実際のファイル名にマッピング
                building_data['sprite_name'] = get_sprite_name(building_id)
                building_data['icon_name'] = get_icon_name(building_id)
                definition = BuildingDefinition.from_dict(building_data)
                self.definitions[building_id] = definition
            
            print(f"Loaded {len(self.definitions)} building definitions")
            
            # 初期アンロック処理
            self._update_unlocked_buildings(1945, 0)
            
            return True
            
        except Exception as e:
            print(f"Failed to load building definitions: {e}")
            # フォールバックとしてテスト用建物を作成
            self._create_test_buildings()
            return False
    
    def _create_test_buildings(self):
        """テスト用建物定義を作成"""
        from models.building import BuildingUnlockCondition, BuildingStats
        
        # バラック住宅
        barrack = BuildingDefinition(
            id="barrack_house",
            name_jp="バラック住宅",
            name_en="Barrack House",
            category=BuildingCategory.RESIDENTIAL,
            cost=100,
            maintenance_cost=5,
            unlock_condition=BuildingUnlockCondition(year=1945, population=0),
            stats=BuildingStats(population_capacity=4, happiness_effect=-5),
            sprite_name="building_house",
            icon_name="building_house"
        )
        
        # 小工場
        factory = BuildingDefinition(
            id="small_factory",
            name_jp="小工場",
            name_en="Small Factory",
            category=BuildingCategory.INDUSTRIAL,
            cost=500,
            maintenance_cost=20,
            unlock_condition=BuildingUnlockCondition(year=1945, population=10),
            stats=BuildingStats(jobs_provided=8, power_consumption=5, pollution=3),
            sprite_name="building_factory",
            icon_name="building_factory"
        )
        
        # 個人商店
        shop = BuildingDefinition(
            id="small_shop",
            name_jp="個人商店",
            name_en="Small Shop",
            category=BuildingCategory.COMMERCIAL,
            cost=300,
            maintenance_cost=10,
            unlock_condition=BuildingUnlockCondition(year=1945, population=5),
            stats=BuildingStats(jobs_provided=3, happiness_effect=2),
            sprite_name="building_shop",
            icon_name="building_shop"
        )
        
        # 道路
        road = BuildingDefinition(
            id="road",
            name_jp="道路",
            name_en="Road",
            category=BuildingCategory.INFRA,
            cost=10,
            maintenance_cost=1,
            unlock_condition=BuildingUnlockCondition(year=1945, population=0),
            stats=BuildingStats(happiness_effect=1),
            sprite_name="terrain_road",
            icon_name="terrain_road"
        )
        
        self.definitions = {
            "barrack_house": barrack,
            "small_factory": factory,
            "small_shop": shop,
            "road": road
        }
        
        self._update_unlocked_buildings(1945, 0)
        print("Created test building definitions")
    
    def can_place_building(self, building_id: str, x: int, y: int, grid_system) -> Tuple[bool, str]:
        """建物が配置可能かチェック"""
        # 建物定義の確認
        if building_id not in self.definitions:
            return False, "Unknown building type"
        
        if building_id not in self.unlocked_buildings:
            return False, "Building not unlocked"
        
        definition = self.definitions[building_id]
        
        # グリッド範囲チェック
        for dy in range(definition.size_height):
            for dx in range(definition.size_width):
                cell_x, cell_y = x + dx, y + dy
                
                # グリッド境界チェック
                if not grid_system.is_valid_grid_position(cell_x, cell_y):
                    return False, "Out of bounds"
                
                # 占有チェック
                if (cell_x, cell_y) in self.grid_occupation:
                    return False, "Cell already occupied"
                
                # 地形チェック（道路以外は建設可能地のみ）
                terrain_type = grid_system.terrain[cell_y][cell_x]
                if definition.id != "road" and terrain_type not in [0, 1]:  # 草地または土地
                    return False, "Invalid terrain"
        
        return True, "OK"
    
    def place_building(self, building_id: str, x: int, y: int, current_year: int, grid_system) -> Optional[Building]:
        """建物を配置"""
        can_place, reason = self.can_place_building(building_id, x, y, grid_system)
        if not can_place:
            print(f"Cannot place building: {reason}")
            return None
        
        definition = self.definitions[building_id]
        building = Building(definition, x, y)
        building.placed_year = current_year
        
        # 難易度と年代に応じてコストと維持費を調整
        building.adjusted_cost = difficulty_manager.get_adjusted_cost(definition.cost, current_year)
        building.adjusted_maintenance_cost = difficulty_manager.get_maintenance_cost(
            building.adjusted_cost, definition.category.value
        )
        
        # グリッド占有情報を更新
        for cell in building.get_occupying_cells():
            self.grid_occupation[cell] = building
        
        # 道路の場合は地形も更新
        if building_id == "road":
            grid_system.terrain[y][x] = 3  # 道路地形
        
        self.buildings.append(building)
        self._update_statistics()
        
        # アニメーション設定
        self._setup_building_animation(building)
        
        # イベント発行
        event_manager.emit_event("building_placed", building)
        
        print(f"Placed {building.name_jp} at ({x}, {y})")
        return building
    
    def remove_building(self, x: int, y: int) -> Optional[Building]:
        """建物を削除"""
        if (x, y) not in self.grid_occupation:
            return None
        
        building = self.grid_occupation[(x, y)]
        
        # グリッド占有情報をクリア
        for cell in building.get_occupying_cells():
            if cell in self.grid_occupation:
                del self.grid_occupation[cell]
        
        # 建物リストから削除
        if building in self.buildings:
            self.buildings.remove(building)
        
        # アニメーション削除
        animation_manager.remove_tile_animation(building.x, building.y)
        
        self._update_statistics()
        
        # イベント発行
        event_manager.emit_event("building_removed", building)
        
        print(f"Removed {building.name_jp} from ({x}, {y})")
        return building
    
    def get_building_at(self, x: int, y: int) -> Optional[Building]:
        """指定座標の建物を取得"""
        return self.grid_occupation.get((x, y))
    
    def get_buildings_by_category(self, category: BuildingCategory) -> List[Building]:
        """カテゴリ別の建物リストを取得"""
        return [b for b in self.buildings if b.category == category]
    
    def update(self, current_year: int):
        """建物システムを更新"""
        # 全建物の状態更新
        for building in self.buildings:
            building.update(current_year)
        
        # 統計更新
        self._update_statistics()
    
    def _update_statistics(self):
        """統計情報を更新"""
        self.total_population_capacity = 0
        self.total_jobs = 0
        self.total_power_consumption = 0
        self.total_power_production = 0
        self.total_water_consumption = 0
        self.total_water_production = 0
        self.total_maintenance_cost = 0
        
        for building in self.buildings:
            stats = building.get_effective_stats()
            self.total_population_capacity += stats.population_capacity
            self.total_jobs += stats.jobs_provided
            self.total_power_consumption += stats.power_consumption
            self.total_power_production += stats.power_production
            self.total_water_consumption += stats.water_consumption
            self.total_water_production += stats.water_production
            self.total_maintenance_cost += building.definition.maintenance_cost
    
    def _update_unlocked_buildings(self, current_year: int, population: int):
        """アンロック可能な建物を更新"""
        newly_unlocked = []
        
        for building_id, definition in self.definitions.items():
            if building_id in self.unlocked_buildings:
                continue
            
            condition = definition.unlock_condition
            
            # 年代チェック
            if current_year < condition.year:
                continue
            
            # 人口チェック
            if population < condition.population:
                continue
            
            # 前提条件チェック
            prerequisites_met = all(
                prereq in self.unlocked_buildings 
                for prereq in condition.prerequisites
            )
            if not prerequisites_met:
                continue
            
            # アンロック
            self.unlocked_buildings.add(building_id)
            newly_unlocked.append(definition)
        
        # 新規アンロック通知
        for definition in newly_unlocked:
            event_manager.emit_event("building_unlocked", definition)
            print(f"Unlocked: {definition.name_jp}")
    
    def get_unlocked_buildings(self) -> List[BuildingDefinition]:
        """アンロック済み建物定義のリストを取得"""
        return [self.definitions[bid] for bid in self.unlocked_buildings]
    
    def get_building_definition(self, building_id: str) -> Optional[BuildingDefinition]:
        """建物定義を取得"""
        return self.definitions.get(building_id)
    
    def _on_year_changed(self, new_year: int):
        """年変更イベントハンドラ"""
        # 現在の人口を取得（仮）
        current_population = self.total_population_capacity  # 簡易計算
        self._update_unlocked_buildings(new_year, current_population)
    
    def _on_build_requested(self, x: int, y: int, building_id: str):
        """建設要求イベントハンドラ"""
        if building_id:
            # grid_systemの参照が必要（将来改善）
            print(f"Build requested: {building_id} at ({x}, {y})")
    
    def _on_destroy_requested(self, x: int, y: int):
        """破壊要求イベントハンドラ"""
        building = self.remove_building(x, y)
        if building:
            print(f"Destroyed: {building.name_jp}")
    
    def _on_technology_unlock(self, data: Dict[str, any]):
        """技術アンロックイベントハンドラ"""
        building_id = data.get("building_id")
        event = data.get("event")
        
        if building_id and building_id in self.definitions:
            if building_id not in self.unlocked_buildings:
                self.unlocked_buildings.add(building_id)
                definition = self.definitions[building_id]
                event_manager.emit_event("building_unlocked", definition)
                print(f"技術により建物がアンロック: {definition.name_jp}")
    
    def _on_technology_event(self, event):
        """技術イベントハンドラ"""
        print(f"技術イベント: {event.name_jp} - {event.description_jp}")
        
        # 技術イベントによる建物アンロック（既に_on_technology_unlockで処理済み）
        # 他の効果があればここで処理
    
    def _setup_building_animation(self, building: Building):
        """建物のアニメーションを設定"""
        # 建物IDに基づいてアニメーションを設定
        animation_mapping = {
            "thermal_power": "thermal_power",
            "nuclear_power": "nuclear_power", 
            "coal_power_plant": "coal_power",
            "small_factory": "small_factory",
            "auto_factory": "auto_factory"
        }
        
        if building.definition.id in animation_mapping:
            animation_id = animation_mapping[building.definition.id]
            if animation_manager.has_animation(animation_id):
                animation_manager.set_tile_animation(building.x, building.y, animation_id)
                print(f"Set animation '{animation_id}' for building {building.name_jp}")
    
    def get_statistics(self) -> Dict[str, int]:
        """統計情報を取得"""
        return {
            'total_buildings': len(self.buildings),
            'population_capacity': self.total_population_capacity,
            'jobs_provided': self.total_jobs,
            'power_consumption': self.total_power_consumption,
            'power_production': self.total_power_production,
            'water_consumption': self.total_water_consumption,
            'water_production': self.total_water_production,
            'maintenance_cost': self.total_maintenance_cost,
            'unlocked_buildings': len(self.unlocked_buildings)
        }