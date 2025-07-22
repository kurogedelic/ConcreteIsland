"""
スプライト名マッピング設定
Sprite Name Mapping Configuration
"""

# 建物IDから実際のスプライトファイル名へのマッピング
BUILDING_SPRITE_MAPPING = {
    # 住宅
    "barrack_house": "tile_barracks_house_1_1",
    "wooden_house": "tile_wooden_house_1_1",
    "municipal_housing": "tile_municipal_housing_1_1",
    "high_rise_housing": "tile_high_rise_housing_1_1",
    
    # 商業
    "personal_shop": "tile_personal_shop_1_1",
    "shopping_street": "tile_shopping_street_1_1",
    "department_store": "tile_department_store_1_1",
    
    # 工業
    "small_factory": "tile_small_factory_1_1",
    "auto_factory": "tile_auto_factory_1_1",
    
    # 公共施設
    "koban": "tile_koban_1_1",
    "fire_station": "tile_fire_station_1_1",
    "wooden_school": "tile_wooden_school_1_1",
    "concrete_school": "tile_concrete_school_1_1",
    "hospital": "tile_hospital_1_1",
    
    # インフラ
    "road": "tile_road_1_1",
    "rail_station": "tile_train_station_wooden_1_1",
    "thermal_power": "tile_thermal_power_1_1",
    "water_pump": "tile_water_pump_2_1",
    
    # 娯楽
    "sento": "tile_sento_1_1",
    "cinema": "tile_cinema_1_1",
    
    # 特殊
    "nuclear_power": "tile_nuclear_power_1_1",
    "tv_tower": "tile_tv_tower_1_1",
    "airport": "tile_airport_1_1",
    
    # 地形
    "terrain_grass": "tile_grass_1_1",
    "terrain_dirt": "tile_soil_1_1",
    "terrain_water": "tile_water_1_1",
    "terrain_road": "tile_road_1_1",
    "terrain_waste": "tile_waste_1_1",
    "terrain_sand": "tile_sand_1_1"
}

# 建物IDからアイコンファイル名へのマッピング
BUILDING_ICON_MAPPING = {
    # 住宅
    "barrack_house": "icon_barracks_icon",
    "wooden_house": "icon_wooden_house_icon",
    "municipal_housing": "icon_municipal_housing_icon",
    "high_rise_housing": "icon_high_rise_housing_icon",
    
    # 商業
    "personal_shop": "icon_personal_shop_icon",
    "shopping_street": "icon_shopping_street_icon",
    "department_store": "icon_department_store_icon",
    
    # 工業
    "small_factory": "icon_small_factory_icon",
    "auto_factory": "icon_auto_factory_icon",
    
    # 公共施設
    "koban": "icon_koban_icon",
    "fire_station": "icon_fire_station_icon",
    "wooden_school": "icon_wooden_school_icon",
    "concrete_school": "icon_concrete_school_icon",
    "hospital": "icon_hospital_icon",
    
    # インフラ
    "road": "icon_road_icon",
    "rail_station": "icon_train_station_icon",
    "thermal_power": "icon_thermal_power_icon",
    "water_pump": "icon_water_pump_icon",
    
    # 娯楽
    "sento": "icon_sento_icon",
    "cinema": "icon_cinema_icon",
    
    # 特殊
    "nuclear_power": "icon_nuclear_power_icon",
    "tv_tower": "icon_tv_tower_icon",
    "airport": "icon_airport_icon"
}

def get_sprite_name(building_id: str) -> str:
    """建物IDから実際のスプライト名を取得"""
    return BUILDING_SPRITE_MAPPING.get(building_id, f"building_{building_id}")

def get_icon_name(building_id: str) -> str:
    """建物IDから実際のアイコン名を取得"""
    return BUILDING_ICON_MAPPING.get(building_id, f"icon_{building_id}")