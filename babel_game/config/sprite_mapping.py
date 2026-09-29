"""
スプライト名マッピング設定
Sprite Name Mapping Configuration
"""

# 建物IDから実際のスプライトファイル名へのマッピング
BUILDING_SPRITE_MAPPING = {
    # 住宅 
    "barracks": "tile_barracks_house-1-1",        # JSON建物ID
    "barracks_house": "tile_barracks_house-1-1",  # sprite_name
    "barrack_house": "tile_barracks_house-1-1",   # UI建物ID (主要)
    "wooden_house": "tile_wooden_house-1-1",
    "municipal_housing": "tile_residential_dense-2-1", 
    "high_rise_housing": "tile_high_rise_housing-1-1",
    
    # 商業
    "personal_shop": "tile_personal_shop-1-1",
    "shopping_street": "tile_commercial_light-2-1",
    "department_store": "tile_department_store-1-1",
    
    # 工業
    "small_factory": "tile_industrial_light-2-1",
    "auto_factory": "tile_auto_factory-1-1",
    
    # 公共施設
    "koban": "tile_koban-1-1",
    "fire_station": "tile_fire_station-1-1",
    "wooden_school": "tile_wooden_school-1-1",
    "concrete_school": "tile_concrete_school-1-1",
    "hospital": "tile_hospital-1-1",
    
    # インフラ
    "road": "tile_road-1-1",
    "rail_station": "tile_train_station_wooden-1-1",
    "thermal_power": "tile_thermal_power-1-1",
    "water_pump": "tile_water_pump-2-1",
    
    # 娯楽
    "sento": "tile_sento-1-1",
    "cinema": "tile_cinema-1-1",
    
    # 特殊
    "nuclear_power": "tile_nuclear_power-1-1",
    "tv_tower": "tile_tv_tower-1-1",
    "airport": "tile_airport-1-1",
    
    # 地形
    "terrain_grass": "tile_grass-1-1",
    "terrain_dirt": "tile_soil-1-1", 
    "terrain_water": "tile_water-1-1",
    "terrain_road": "tile_road-1-1",
    "terrain_waste": "tile_waste-1-1",
    "terrain_sand": "tile_sand-1-1",
    
    # 追加の地形タイプ（terrain_generatorの地形タイプに対応）
    3: "tile_road-1-1",    # 道路地形
    4: "tile_waste-1-1",   # 荒廃地  
    5: "tile_sand-1-1"     # 砂地
}

# 建物IDからアイコンファイル名へのマッピング
BUILDING_ICON_MAPPING = {
    # 住宅
    "barracks": "barracks_icon",        # JSON建物ID
    "barracks_house": "barracks_icon",  # sprite_name  
    "barrack_house": "barracks_icon",   # UI建物ID (主要)
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
    result = BUILDING_SPRITE_MAPPING.get(building_id, f"building_{building_id}")
    print(f"SPRITE MAPPING: get_sprite_name({building_id}) -> {result}")
    if building_id == "barracks":
        print(f"BARRACKS DEBUG: Expected barracks_house-1-1.png, got {result}")
    return result

def get_icon_name(building_id: str) -> str:
    """建物IDから実際のアイコン名を取得"""
    return BUILDING_ICON_MAPPING.get(building_id, f"icon_{building_id}")