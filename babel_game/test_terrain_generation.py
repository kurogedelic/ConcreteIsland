#!/usr/bin/env python3
"""
地形生成システムのテスト
Terrain Generation System Test
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from systems.terrain_generator import terrain_generator, TerrainGenConfig, MapType, TerrainType
import time

def test_perlin_noise():
    """パーリンノイズのテスト"""
    print("Testing Perlin Noise...")
    
    from systems.terrain_generator import PerlinNoise
    noise = PerlinNoise(seed=12345)
    
    # 基本ノイズ値のテスト
    test_points = [(0, 0), (1, 1), (2.5, 3.7), (10, 10)]
    for x, y in test_points:
        noise_val = noise.noise(x, y)
        print(f"  Noise({x}, {y}) = {noise_val:.4f}")
        assert -1 <= noise_val <= 1, f"Noise value out of range: {noise_val}"
    
    # オクターブノイズのテスト
    octave_val = noise.octave_noise(1.5, 2.5, 4, 0.5, 2.0)
    print(f"  Octave noise = {octave_val:.4f}")
    assert -1 <= octave_val <= 1, f"Octave noise value out of range: {octave_val}"
    
    print("✓ Perlin noise test passed")
    return True

def test_basic_generation():
    """基本地形生成テスト"""
    print("Testing basic terrain generation...")
    
    config = TerrainGenConfig()
    config.seed = 54321
    config.map_type = MapType.COASTAL
    
    start_time = time.time()
    terrain = terrain_generator.generate_terrain(config)
    generation_time = time.time() - start_time
    
    print(f"  Generation time: {generation_time:.3f}s")
    print(f"  Grid size: {len(terrain)}x{len(terrain[0])}")
    
    # 地形の検証
    assert len(terrain) == 32, f"Unexpected grid height: {len(terrain)}"
    assert len(terrain[0]) == 32, f"Unexpected grid width: {len(terrain[0])}"
    
    # 全セルが有効な地形タイプかチェック
    valid_terrain_types = {t.value for t in TerrainType}
    for y in range(len(terrain)):
        for x in range(len(terrain[0])):
            terrain_type = terrain[y][x]
            assert terrain_type in valid_terrain_types, f"Invalid terrain type: {terrain_type}"
    
    print("✓ Basic generation test passed")
    return terrain

def test_terrain_info(terrain):
    """地形情報テスト"""
    print("Testing terrain info...")
    
    info = terrain_generator.get_terrain_info(terrain)
    
    print(f"  Total tiles: {info['total_tiles']}")
    print(f"  Map type: {info['map_type']}")
    print(f"  Seed: {info['seed']}")
    print("  Terrain distribution:")
    
    total_percentage = 0
    for terrain_name, data in info['terrain_distribution'].items():
        count = data['count']
        percentage = data['percentage']
        print(f"    {terrain_name}: {count} tiles ({percentage:.1f}%)")
        total_percentage += percentage
    
    # パーセンテージの合計が100%に近いかチェック
    assert abs(total_percentage - 100.0) < 0.1, f"Total percentage error: {total_percentage}"
    
    print("✓ Terrain info test passed")
    return info

def test_map_types():
    """各マップタイプのテスト"""
    print("Testing different map types...")
    
    map_types = [MapType.ISLAND, MapType.COASTAL, MapType.INLAND, MapType.PENINSULA, MapType.RIVER_VALLEY]
    
    results = {}
    
    for map_type in map_types:
        print(f"  Testing {map_type.value}...")
        
        config = TerrainGenConfig()
        config.map_type = map_type
        config.seed = 98765
        
        start_time = time.time()
        terrain = terrain_generator.generate_terrain(config)
        generation_time = time.time() - start_time
        
        info = terrain_generator.get_terrain_info(terrain)
        
        # 水域の割合をチェック
        water_data = info['terrain_distribution'].get('水域', {'percentage': 0})
        water_percentage = water_data['percentage']
        
        results[map_type.value] = {
            'generation_time': generation_time,
            'water_percentage': water_percentage,
            'total_terrain_types': len(info['terrain_distribution'])
        }
        
        print(f"    Generated in {generation_time:.3f}s")
        print(f"    Water coverage: {water_percentage:.1f}%")
        print(f"    Terrain types: {len(info['terrain_distribution'])}")
        
        # 島の場合は水域が多いはず
        if map_type == MapType.ISLAND:
            assert water_percentage > 30, f"Island should have more water: {water_percentage}%"
        
        # 内陸の場合は水域が少ないはず
        if map_type == MapType.INLAND:
            assert water_percentage < 20, f"Inland should have less water: {water_percentage}%"
    
    print("✓ Map types test passed")
    return results

def test_terrain_features():
    """地形特徴のテスト"""
    print("Testing terrain features...")
    
    # 戦災荒廃地の生成テスト
    config = TerrainGenConfig()
    config.wasteland_probability = 0.3  # 高めに設定
    config.seed = 11111
    
    terrain = terrain_generator.generate_terrain(config)
    info = terrain_generator.get_terrain_info(terrain)
    
    # 荒廃地が生成されているかチェック
    wasteland_data = info['terrain_distribution'].get('荒廃地', {'percentage': 0})
    wasteland_percentage = wasteland_data['percentage']
    
    print(f"  Wasteland coverage: {wasteland_percentage:.1f}%")
    assert wasteland_percentage > 10, f"Should have significant wasteland: {wasteland_percentage}%"
    
    # 河川生成テスト
    config.map_type = MapType.RIVER_VALLEY
    config.river_count = 3
    config.river_width = 3
    
    terrain = terrain_generator.generate_terrain(config)
    info = terrain_generator.get_terrain_info(terrain)
    
    water_data = info['terrain_distribution'].get('水域', {'percentage': 0})
    water_percentage = water_data['percentage']
    
    print(f"  River valley water coverage: {water_percentage:.1f}%")
    assert water_percentage > 15, f"River valley should have rivers: {water_percentage}%"
    
    print("✓ Terrain features test passed")
    return True

def test_config_save_load():
    """設定保存・読み込みテスト"""
    print("Testing config save/load...")
    
    # 設定を作成
    config = TerrainGenConfig()
    config.map_type = MapType.PENINSULA
    config.seed = 99999
    config.base_frequency = 0.08
    config.octaves = 6
    config.water_threshold = 0.35
    
    # 保存
    config_file = "test_terrain_config.json"
    terrain_generator.config = config
    terrain_generator.save_terrain_config(config_file)
    
    # 読み込み
    loaded_config = terrain_generator.load_terrain_config(config_file)
    
    # 検証
    assert loaded_config.map_type == config.map_type
    assert loaded_config.seed == config.seed
    assert loaded_config.base_frequency == config.base_frequency
    assert loaded_config.octaves == config.octaves
    assert loaded_config.water_threshold == config.water_threshold
    
    print(f"  Config saved and loaded successfully")
    print(f"  Map type: {loaded_config.map_type.value}")
    print(f"  Seed: {loaded_config.seed}")
    
    # クリーンアップ
    os.remove(config_file)
    
    print("✓ Config save/load test passed")
    return True

def test_performance():
    """パフォーマンステスト"""
    print("Testing performance...")
    
    # 複数回生成してパフォーマンスを測定
    config = TerrainGenConfig()
    config.map_type = MapType.COASTAL
    
    times = []
    for i in range(5):
        config.seed = i + 1000
        start_time = time.time()
        terrain = terrain_generator.generate_terrain(config)
        generation_time = time.time() - start_time
        times.append(generation_time)
    
    avg_time = sum(times) / len(times)
    min_time = min(times)
    max_time = max(times)
    
    print(f"  Average generation time: {avg_time:.3f}s")
    print(f"  Min time: {min_time:.3f}s")
    print(f"  Max time: {max_time:.3f}s")
    
    # 1秒以内で生成できることを確認
    assert avg_time < 1.0, f"Generation too slow: {avg_time:.3f}s"
    
    print("✓ Performance test passed")
    return True

def visualize_terrain(terrain, filename="terrain_preview.txt"):
    """地形を可視化（テキスト形式）"""
    print(f"Visualizing terrain to {filename}...")
    
    terrain_chars = {
        TerrainType.WATER.value: '~',
        TerrainType.SAND.value: '.',
        TerrainType.GRASS.value: ' ',
        TerrainType.FOREST.value: '♠',
        TerrainType.MOUNTAIN.value: '^',
        TerrainType.WASTELAND.value: 'X'
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("Terrain Preview\n")
        f.write("=" * 40 + "\n")
        f.write("Legend: ~ Water, . Sand, (space) Grass, ♠ Forest, ^ Mountain, X Wasteland\n")
        f.write("=" * 40 + "\n")
        
        for y in range(len(terrain)):
            line = ""
            for x in range(len(terrain[0])):
                terrain_type = terrain[y][x]
                char = terrain_chars.get(terrain_type, '?')
                line += char
            f.write(line + "\n")
    
    print(f"  Terrain visualization saved to {filename}")

if __name__ == "__main__":
    print("Terrain Generation System Test Suite")
    print("=" * 50)
    
    try:
        # テスト実行
        tests = [
            test_perlin_noise,
            test_basic_generation,
            lambda: test_terrain_info(test_basic_generation()),
            test_map_types,
            test_terrain_features,
            test_config_save_load,
            test_performance
        ]
        
        passed = 0
        sample_terrain = None
        
        for i, test in enumerate(tests):
            print()
            try:
                result = test()
                if i == 1:  # basic generation test
                    sample_terrain = result
                passed += 1
            except Exception as e:
                print(f"✗ Test failed with exception: {e}")
                import traceback
                traceback.print_exc()
        
        # サンプル地形の可視化
        if sample_terrain:
            print()
            visualize_terrain(sample_terrain)
        
        print("\n" + "=" * 50)
        print(f"Tests completed: {passed}/{len(tests)} passed")
        
        if passed == len(tests):
            print("🎉 All terrain generation tests passed!")
        else:
            print("⚠️  Some tests failed")
        
    except Exception as e:
        print(f"\nTest suite failed with error: {e}")
        import traceback
        traceback.print_exc()