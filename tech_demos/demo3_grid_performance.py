#!/usr/bin/env python3
"""
技術検証デモ3: 大規模グリッド描画のパフォーマンステスト

目的:
- 大量のタイル描画時の性能測定
- 視界カリング（Frustum Culling）の効果検証
- 等角投影座標変換の性能測定
- メモリ使用量の監視
"""

import time
import math
import random
from typing import List, Tuple, Dict, Set
import psutil


class GridPerformanceTester:
    def __init__(self):
        self.process = psutil.Process()
        
    def measure_memory(self):
        """現在のメモリ使用量を取得 (MB)"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def test_coordinate_conversion_performance(self):
        """座標変換の大量処理性能をテスト"""
        print("=== Coordinate Conversion Performance Test ===")
        
        CELL_SIZE = 32
        
        def grid_to_screen(grid_x: int, grid_y: int) -> Tuple[int, int]:
            """グリッド座標をスクリーン座標に変換（等角投影）"""
            iso_x = (grid_x - grid_y) * (CELL_SIZE // 2)
            iso_y = (grid_x + grid_y) * (CELL_SIZE // 4)
            
            screen_x = iso_x + 400  # 画面中央オフセット
            screen_y = iso_y + 300
            
            return screen_x, screen_y
        
        def screen_to_grid(screen_x: int, screen_y: int) -> Tuple[int, int]:
            """スクリーン座標をグリッド座標に変換"""
            iso_x = screen_x - 400
            iso_y = screen_y - 300
            
            grid_x = (iso_x / (CELL_SIZE // 2) + iso_y / (CELL_SIZE // 4)) / 2
            grid_y = (iso_y / (CELL_SIZE // 4) - iso_x / (CELL_SIZE // 2)) / 2
            
            return int(grid_x), int(grid_y)
        
        # 大量変換テスト
        num_conversions = 1000000
        print(f"Testing {num_conversions:,} coordinate conversions...")
        
        # Grid to Screen 変換
        start_time = time.time()
        for i in range(num_conversions):
            grid_x = i % 100
            grid_y = (i // 100) % 100
            screen_x, screen_y = grid_to_screen(grid_x, grid_y)
        
        grid_to_screen_time = time.time() - start_time
        
        # Screen to Grid 変換
        start_time = time.time()
        for i in range(num_conversions):
            screen_x = (i % 800) + 100
            screen_y = ((i // 800) % 600) + 100
            grid_x, grid_y = screen_to_grid(screen_x, screen_y)
        
        screen_to_grid_time = time.time() - start_time
        
        print(f"Grid to Screen: {grid_to_screen_time:.3f}s ({num_conversions/grid_to_screen_time:.0f} ops/sec)")
        print(f"Screen to Grid: {screen_to_grid_time:.3f}s ({num_conversions/screen_to_grid_time:.0f} ops/sec)")
        
        return {
            'grid_to_screen_time': grid_to_screen_time,
            'screen_to_grid_time': screen_to_grid_time,
            'conversions_per_second': num_conversions / max(grid_to_screen_time, 0.001)
        }
    
    def test_frustum_culling_performance(self):
        """視界カリング性能をテスト"""
        print(f"\n=== Frustum Culling Performance Test ===")
        
        class Rect:
            def __init__(self, x: int, y: int, w: int, h: int):
                self.x = x
                self.y = y
                self.w = w
                self.h = h
            
            def intersects(self, other: 'Rect') -> bool:
                """矩形の交差判定"""
                return not (self.x >= other.x + other.w or
                           self.x + self.w <= other.x or
                           self.y >= other.y + other.h or
                           self.y + self.h <= other.y)
        
        # 大規模グリッド生成
        GRID_SIZE = 1000
        TILE_SIZE = 32
        
        tiles = []
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                # 等角投影座標計算
                iso_x = (x - y) * (TILE_SIZE // 2)
                iso_y = (x + y) * (TILE_SIZE // 4)
                
                tile_rect = Rect(iso_x, iso_y, TILE_SIZE, TILE_SIZE)
                tiles.append(tile_rect)
        
        print(f"Created {len(tiles):,} tiles ({GRID_SIZE}x{GRID_SIZE} grid)")
        
        # 異なる視界サイズでテスト
        viewport_sizes = [
            (800, 600),   # 通常画面
            (1920, 1080), # フルHD
            (400, 300)    # 小画面
        ]
        
        results = []
        
        for vp_width, vp_height in viewport_sizes:
            print(f"\nTesting viewport: {vp_width}x{vp_height}")
            
            # カメラ位置をランダムに移動
            camera_positions = [
                (0, 0),       # 原点
                (5000, 3000), # 中央
                (10000, 6000) # 端
            ]
            
            for cam_x, cam_y in camera_positions:
                viewport = Rect(cam_x, cam_y, vp_width, vp_height)
                
                # カリングなし（全タイル処理）
                start_time = time.time()
                visible_no_culling = 0
                for tile in tiles:
                    # 描画処理をシミュレート（軽い計算）
                    visible_no_culling += 1
                
                no_culling_time = time.time() - start_time
                
                # カリングあり（視界内タイルのみ処理）
                start_time = time.time()
                visible_with_culling = 0
                for tile in tiles:
                    if tile.intersects(viewport):
                        # 描画処理をシミュレート
                        visible_with_culling += 1
                
                culling_time = time.time() - start_time
                
                speedup = no_culling_time / max(culling_time, 0.001)
                culling_ratio = visible_with_culling / len(tiles)
                
                result = {
                    'viewport': (vp_width, vp_height),
                    'camera': (cam_x, cam_y),
                    'total_tiles': len(tiles),
                    'visible_tiles': visible_with_culling,
                    'culling_ratio': culling_ratio,
                    'no_culling_time': no_culling_time,
                    'culling_time': culling_time,
                    'speedup': speedup
                }
                
                results.append(result)
                
                print(f"  Camera({cam_x},{cam_y}): {visible_with_culling:,}/{len(tiles):,} visible ({culling_ratio:.1%})")
                print(f"    No culling: {no_culling_time:.4f}s")
                print(f"    With culling: {culling_time:.4f}s")
                print(f"    Speedup: {speedup:.1f}x")
        
        return results
    
    def test_large_grid_memory_usage(self):
        """大規模グリッドのメモリ使用量をテスト"""
        print(f"\n=== Large Grid Memory Usage Test ===")
        
        memory_before = self.measure_memory()
        
        # 異なるサイズのグリッドでメモリ使用量を測定
        grid_sizes = [100, 500, 1000, 2000]
        memory_results = []
        
        for grid_size in grid_sizes:
            print(f"\nTesting {grid_size}x{grid_size} grid...")
            
            memory_before_grid = self.measure_memory()
            
            # グリッドデータ構造を作成
            grid_data = {}
            tile_count = 0
            
            for y in range(grid_size):
                for x in range(grid_size):
                    # タイルデータを作成
                    tile_data = {
                        'x': x,
                        'y': y,
                        'terrain_type': random.randint(0, 5),
                        'building_id': random.randint(0, 20) if random.random() < 0.3 else None,
                        'population': random.randint(0, 100) if random.random() < 0.2 else 0,
                        'resources': {
                            'power': random.randint(0, 10),
                            'water': random.randint(0, 10)
                        }
                    }
                    
                    grid_data[(x, y)] = tile_data
                    tile_count += 1
            
            memory_after_grid = self.measure_memory()
            memory_delta = memory_after_grid - memory_before_grid
            
            # メモリ効率計算
            bytes_per_tile = (memory_delta * 1024 * 1024) / tile_count if tile_count > 0 else 0
            
            result = {
                'grid_size': grid_size,
                'tile_count': tile_count,
                'memory_before': memory_before_grid,
                'memory_after': memory_after_grid,
                'memory_delta': memory_delta,
                'bytes_per_tile': bytes_per_tile
            }
            
            memory_results.append(result)
            
            print(f"  Tiles created: {tile_count:,}")
            print(f"  Memory delta: {memory_delta:.1f}MB")
            print(f"  Bytes per tile: {bytes_per_tile:.1f}")
            
            # 大きなグリッドは削除してメモリを解放
            del grid_data
        
        # 最適なグリッドサイズの推定
        print(f"\n--- Memory Usage Analysis ---")
        target_memory_mb = 50  # 目標メモリ使用量
        
        for result in memory_results:
            if result['memory_delta'] > 0:
                max_tiles = (target_memory_mb * 1024 * 1024) / result['bytes_per_tile']
                max_grid_size = int(math.sqrt(max_tiles))
                
                print(f"Grid {result['grid_size']}x{result['grid_size']}: "
                      f"{result['bytes_per_tile']:.1f} bytes/tile, "
                      f"max grid for {target_memory_mb}MB: ~{max_grid_size}x{max_grid_size}")
        
        return memory_results
    
    def test_rendering_simulation(self):
        """描画処理のシミュレーション"""
        print(f"\n=== Rendering Simulation Test ===")
        
        # 描画シミュレーション関数
        def simulate_tile_rendering(tile_count: int, effect_count: int = 0):
            """タイル描画をシミュレート"""
            render_time = 0
            
            for i in range(tile_count):
                # 基本タイル描画（軽い処理）
                render_time += 0.000001  # 1マイクロ秒と仮定
                
                # エフェクト描画（重い処理）
                if i < effect_count:
                    render_time += 0.00001  # 10マイクロ秒と仮定
            
            return render_time
        
        # 異なるシナリオでテスト
        scenarios = [
            {'name': 'Small City', 'visible_tiles': 500, 'effects': 10},
            {'name': 'Medium City', 'visible_tiles': 2000, 'effects': 50},
            {'name': 'Large City', 'visible_tiles': 8000, 'effects': 200},
            {'name': 'Mega City', 'visible_tiles': 32000, 'effects': 800}
        ]
        
        target_fps = 60
        target_frame_time = 1.0 / target_fps
        
        print(f"Target: {target_fps} FPS ({target_frame_time*1000:.2f}ms per frame)")
        
        for scenario in scenarios:
            start_time = time.time()
            
            # 1秒間のフレーム描画をシミュレート
            frames_rendered = 0
            total_render_time = 0
            
            while time.time() - start_time < 1.0:
                frame_start = time.time()
                
                # フレーム描画シミュレート
                render_time = simulate_tile_rendering(
                    scenario['visible_tiles'],
                    scenario['effects']
                )
                
                total_render_time += render_time
                frames_rendered += 1
                
                # フレームレート制限シミュレート
                frame_time = time.time() - frame_start
                if frame_time < target_frame_time:
                    time.sleep(target_frame_time - frame_time)
            
            actual_fps = frames_rendered
            avg_render_time = total_render_time / frames_rendered if frames_rendered > 0 else 0
            
            print(f"\n{scenario['name']}:")
            print(f"  Visible tiles: {scenario['visible_tiles']:,}")
            print(f"  Effects: {scenario['effects']}")
            print(f"  Actual FPS: {actual_fps}")
            print(f"  Avg render time: {avg_render_time*1000:.3f}ms")
            print(f"  Performance: {'✓' if actual_fps >= target_fps * 0.9 else '✗'}")
    
    def run_performance_tests(self):
        """全パフォーマンステストを実行"""
        print("=== Grid Performance Test Suite ===\n")
        
        initial_memory = self.measure_memory()
        print(f"Initial memory: {initial_memory:.1f}MB\n")
        
        # 座標変換性能テスト
        coord_results = self.test_coordinate_conversion_performance()
        
        # 視界カリング性能テスト
        culling_results = self.test_frustum_culling_performance()
        
        # メモリ使用量テスト
        memory_results = self.test_large_grid_memory_usage()
        
        # 描画シミュレーション
        self.test_rendering_simulation()
        
        final_memory = self.measure_memory()
        
        # 結果サマリー
        print(f"\n=== Performance Test Summary ===")
        print(f"Initial memory: {initial_memory:.1f}MB")
        print(f"Final memory: {final_memory:.1f}MB")
        print(f"Memory delta: {final_memory - initial_memory:.1f}MB")
        
        print(f"\nCoordinate conversion: {coord_results['conversions_per_second']:.0f} ops/sec")
        
        # 最良のカリング結果
        best_culling = max(culling_results, key=lambda x: x['speedup'])
        print(f"Best culling speedup: {best_culling['speedup']:.1f}x")
        print(f"  (viewport: {best_culling['viewport']}, visible: {best_culling['culling_ratio']:.1%})")
        
        # メモリ効率
        if memory_results:
            avg_bytes_per_tile = sum(r['bytes_per_tile'] for r in memory_results if r['bytes_per_tile'] > 0) / len([r for r in memory_results if r['bytes_per_tile'] > 0])
            print(f"Average memory per tile: {avg_bytes_per_tile:.1f} bytes")
        
        return {
            'coordinate_performance': coord_results,
            'culling_results': culling_results,
            'memory_results': memory_results,
            'memory_usage': {
                'initial': initial_memory,
                'final': final_memory,
                'delta': final_memory - initial_memory
            }
        }


def main():
    """メイン実行関数"""
    try:
        tester = GridPerformanceTester()
        results = tester.run_performance_tests()
        
        # 結果を保存
        import json
        with open('tech_demos/grid_performance_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✓ Grid performance test complete! Results saved to tech_demos/grid_performance_results.json")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()