#!/usr/bin/env python3
"""
セーブ・ロードシステムのテスト
Save/Load System Test
"""

import sys
import os
import json
from pathlib import Path
sys.path.append(os.path.dirname(__file__))

from systems.save_manager import save_manager, SaveMetadata
from datetime import datetime

def test_save_metadata():
    """SaveMetadataのテスト"""
    print("Testing SaveMetadata...")
    
    # メタデータ作成
    metadata = SaveMetadata(
        version="1.0.0",
        created_at=datetime.now(),
        game_version="Phase5.3",
        save_name="test_save",
        city_name="テスト都市",
        current_year=1955,
        current_month=6,
        population=1250,
        money=50000,
        playtime_seconds=3600,
        difficulty="normal"
    )
    
    # 辞書変換テスト
    data = metadata.to_dict()
    print(f"Metadata dict: {len(data)} fields")
    
    # 復元テスト
    restored = SaveMetadata.from_dict(data)
    print(f"Restored: {restored.save_name}, {restored.city_name}")
    
    assert restored.save_name == metadata.save_name
    assert restored.current_year == metadata.current_year
    assert restored.population == metadata.population
    
    print("✓ SaveMetadata test passed")
    return True

def test_save_manager_basic():
    """SaveManagerの基本機能テスト"""
    print("Testing SaveManager basic functions...")
    
    # 初期化テスト
    print(f"Saves directory: {save_manager.saves_dir}")
    print(f"Save version: {save_manager.SAVE_VERSION}")
    print(f"Game version: {save_manager.GAME_VERSION}")
    
    # 統計取得テスト
    stats = save_manager.get_save_stats()
    print(f"Save stats: {stats}")
    
    print("✓ SaveManager basic test passed")
    return True

def test_save_list():
    """セーブファイル一覧取得テスト"""
    print("Testing save file listing...")
    
    save_list = save_manager.get_save_list()
    print(f"Found {len(save_list)} save files")
    
    for i, save_info in enumerate(save_list[:3]):  # 最初の3個まで表示
        metadata = save_info['metadata']
        print(f"  {i+1}. {save_info['filename']}")
        print(f"     Name: {metadata['save_name']}")
        print(f"     Year: {metadata['current_year']}")
        print(f"     Population: {metadata['population']:,}")
        print(f"     Size: {save_info['file_size']} bytes")
    
    print("✓ Save list test passed")
    return True

def test_mock_save_data():
    """モックデータを使ったセーブデータ作成テスト"""
    print("Testing mock save data creation...")
    
    # モックゲームエンジン
    class MockTimeManager:
        current_year = 1955
        current_month = 6
        current_day = 15
        game_speed = 1.0
        paused = False
        total_elapsed_time = 3600

    class MockBuilding:
        def __init__(self, building_id, x, y):
            self.definition = type('obj', (object,), {'id': building_id})()
            self.x, self.y = x, y
            self.placed_year = 1950
            self.condition = 85
            self.active = True
            self.upgrade_level = 0
            self.data = {}
        
        def to_dict(self):
            return {
                'definition_id': self.definition.id,
                'x': self.x, 'y': self.y,
                'placed_year': self.placed_year,
                'condition': self.condition,
                'active': self.active,
                'upgrade_level': self.upgrade_level,
                'data': self.data
            }

    class MockBuildingManager:
        buildings = [
            MockBuilding("barrack_house", 5, 5),
            MockBuilding("small_shop", 7, 8),
            MockBuilding("road", 6, 6)
        ]

    class MockEconomicData:
        money = 25000
        rice = 800
        iron = 400
        wood = 600
        coal = 200
        electricity = 100
        monthly_income = 2500
        monthly_expenses = 1800

    class MockEconomyManager:
        economic_data = MockEconomicData()
        last_settled_month = 5
        last_settled_year = 1955
        tax_rate = 0.12
        subsidies_enabled = True

    class MockPopulationManager:
        citizens = []
        def get_statistics(self):
            return {'total_population': 1250}

    class MockTechnologyManager:
        current_era = type('obj', (object,), {'value': 'korean_war'})()
        unlocked_buildings = {'barrack_house', 'small_shop', 'road'}
        research_progress = {'construction': 65, 'industry': 40}
        completed_eras = []

    class MockGridSystem:
        grid_width = 32
        grid_height = 32
        terrain_grid = [[0 for _ in range(32)] for _ in range(32)]
        camera_x = 0
        camera_y = 0
        zoom_level = 1.0

    class MockEventSystem:
        disaster_history = []
        current_season = type('obj', (object,), {'value': 'summer'})()
        disasters_disabled = False

    class MockDifficultyManager:
        current_difficulty = type('obj', (object,), {'value': 'normal'})()

    class MockGameEngine:
        time_manager = MockTimeManager()
        building_manager = MockBuildingManager()
        population_manager = MockPopulationManager()
        economy_manager = MockEconomyManager()
        technology_manager = MockTechnologyManager()
        grid_system = MockGridSystem()
        event_system = MockEventSystem()
        difficulty_manager = MockDifficultyManager()
        debug_mode = False

    # セーブデータ作成テスト
    mock_engine = MockGameEngine()
    save_data = save_manager.create_save_data(mock_engine)
    
    if save_data:
        print(f"Save data created successfully")
        print(f"  Time: {save_data['time']['current_year']}/{save_data['time']['current_month']}")
        print(f"  Buildings: {len(save_data['buildings'])}")
        print(f"  Economy: ¥{save_data['economy']['money']:,}")
        print(f"  Technology era: {save_data['technology']['current_era']}")
        print(f"  Settings: {save_data['settings']}")
        
        # JSONシリアライゼーションテスト
        try:
            json_str = json.dumps(save_data, ensure_ascii=False, indent=2)
            print(f"  JSON size: {len(json_str)} characters")
        except Exception as e:
            print(f"  JSON serialization error: {e}")
            return False
        
        print("✓ Mock save data test passed")
        return True
    else:
        print("✗ Failed to create save data")
        return False

def test_file_operations():
    """ファイル操作テスト"""
    print("Testing file operations...")
    
    # テスト用セーブファイルの作成
    test_save_data = {
        'metadata': {
            'version': save_manager.SAVE_VERSION,
            'created_at': datetime.now().isoformat(),
            'game_version': save_manager.GAME_VERSION,
            'save_name': 'test_file_ops',
            'city_name': 'テストシティ',
            'current_year': 1960,
            'current_month': 3,
            'population': 2000,
            'money': 75000,
            'playtime_seconds': 7200,
            'difficulty': 'normal'
        },
        'game_state': {
            'time': {'current_year': 1960, 'current_month': 3},
            'buildings': [],
            'citizens': [],
            'economy': {'money': 75000}
        }
    }
    
    # 手動でファイル保存テスト
    import gzip
    test_file = save_manager.saves_dir / "test_manual.save"
    
    try:
        json_data = json.dumps(test_save_data, ensure_ascii=False, indent=2).encode('utf-8')
        compressed_data = gzip.compress(json_data, compresslevel=6)
        
        with open(test_file, 'wb') as f:
            f.write(compressed_data)
        
        print(f"Test file created: {test_file}")
        print(f"  Compressed size: {len(compressed_data)} bytes")
        print(f"  Compression ratio: {len(compressed_data)/len(json_data)*100:.1f}%")
        
        # 読み込みテスト
        with open(test_file, 'rb') as f:
            read_compressed = f.read()
        
        read_json = gzip.decompress(read_compressed).decode('utf-8')
        read_data = json.loads(read_json)
        
        print(f"  Read back successfully")
        print(f"  Save name: {read_data['metadata']['save_name']}")
        
        # クリーンアップ
        test_file.unlink()
        print(f"  Test file cleaned up")
        
        print("✓ File operations test passed")
        return True
        
    except Exception as e:
        print(f"✗ File operations test failed: {e}")
        return False

if __name__ == "__main__":
    print("Save/Load System Test Suite")
    print("=" * 50)
    
    try:
        # テスト実行
        tests = [
            test_save_metadata,
            test_save_manager_basic,
            test_save_list,
            test_mock_save_data,
            test_file_operations
        ]
        
        passed = 0
        for test in tests:
            print()
            try:
                if test():
                    passed += 1
            except Exception as e:
                print(f"✗ Test failed with exception: {e}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "=" * 50)
        print(f"Tests completed: {passed}/{len(tests)} passed")
        
        if passed == len(tests):
            print("🎉 All save system tests passed!")
        else:
            print("⚠️  Some tests failed")
        
    except Exception as e:
        print(f"\nTest suite failed with error: {e}")
        import traceback
        traceback.print_exc()