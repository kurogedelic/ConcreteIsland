#!/usr/bin/env python3
"""
技術検証デモ1(簡易版): 既存アセットでの性能検証

目的:
- 既存PNG読み込みの性能測定
- メモリ使用量の監視
- Pyxelの基本的な描画性能確認
"""

import pyxel
import time
import psutil
import os
from pathlib import Path
from PIL import Image


class SimplePerformanceTest:
    def __init__(self):
        self.process = psutil.Process()
        self.results = {}
        
    def measure_memory(self):
        """現在のメモリ使用量を取得 (MB)"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def test_png_loading_performance(self):
        """PNG読み込み性能をテスト"""
        print("=== PNG Loading Performance Test ===")
        
        # PNG ファイルを検索
        png_files = list(Path("assets/tiles").glob("*.png"))
        print(f"Found {len(png_files)} PNG files")
        
        if not png_files:
            print("No PNG files found in assets/tiles/")
            return
        
        memory_before = self.measure_memory()
        results = []
        
        for png_file in png_files[:10]:  # 最初の10ファイルをテスト
            start_time = time.time()
            
            try:
                # PIL でPNG読み込み
                img = Image.open(png_file)
                img.load()  # 実際にデータを読み込み
                
                load_time = time.time() - start_time
                file_size = os.path.getsize(png_file) / 1024  # KB
                
                results.append({
                    'file': png_file.name,
                    'load_time': load_time,
                    'file_size': file_size,
                    'width': img.width,
                    'height': img.height
                })
                
                print(f"✓ {png_file.name}: {load_time:.4f}s ({file_size:.1f}KB, {img.width}x{img.height})")
                
            except Exception as e:
                print(f"✗ Error loading {png_file.name}: {e}")
        
        memory_after = self.measure_memory()
        
        # 結果サマリー
        if results:
            total_time = sum(r['load_time'] for r in results)
            total_size = sum(r['file_size'] for r in results)
            avg_time = total_time / len(results)
            
            print(f"\n--- PNG Loading Summary ---")
            print(f"Files loaded: {len(results)}")
            print(f"Total time: {total_time:.3f}s")
            print(f"Average time: {avg_time:.4f}s per file")
            print(f"Total file size: {total_size:.1f}KB")
            print(f"Memory delta: {memory_after - memory_before:.1f}MB")
            print(f"Loading speed: {total_size/max(total_time, 0.001):.1f} KB/s")
        
        return results
    
    def test_pyxel_basic_performance(self):
        """Pyxelの基本描画性能をテスト"""
        print(f"\n=== Pyxel Basic Rendering Performance Test ===")
        
        memory_before = self.measure_memory()
        
        # Pyxelを初期化
        pyxel.init(800, 600, title="Performance Test")
        
        # 描画性能テスト
        frame_times = []
        test_frames = 120  # 2秒間 (60FPS想定)
        
        print(f"Testing {test_frames} frames of rendering...")
        
        for frame in range(test_frames):
            frame_start = time.time()
            
            # 画面クリア
            pyxel.cls(0)
            
            # 大量の矩形描画 (負荷テスト)
            for i in range(100):
                x = (i * 23) % 780
                y = (i * 17) % 580
                color = i % 16
                pyxel.rect(x, y, 16, 16, color)
            
            # 大量の円描画
            for i in range(50):
                x = (i * 31) % 780
                y = (i * 37) % 580
                color = (i + 8) % 16
                pyxel.circb(x, y, 8, color)
            
            frame_time = time.time() - frame_start
            frame_times.append(frame_time)
            
            # 進捗表示
            if frame % 30 == 0:
                print(f"Frame {frame}/{test_frames}")
        
        pyxel.quit()
        
        memory_after = self.measure_memory()
        
        # フレーム性能分析
        if frame_times:
            avg_frame_time = sum(frame_times) / len(frame_times)
            max_frame_time = max(frame_times)
            min_frame_time = min(frame_times)
            fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
            
            print(f"\n--- Rendering Performance Summary ---")
            print(f"Frames rendered: {len(frame_times)}")
            print(f"Average frame time: {avg_frame_time*1000:.2f}ms")
            print(f"Estimated FPS: {fps:.1f}")
            print(f"Min frame time: {min_frame_time*1000:.2f}ms")
            print(f"Max frame time: {max_frame_time*1000:.2f}ms")
            print(f"Memory delta: {memory_after - memory_before:.1f}MB")
            
            # 目標との比較
            target_fps = 60
            target_frame_time = 1.0 / target_fps * 1000  # 16.67ms
            
            print(f"\n--- Target Comparison ---")
            print(f"Target FPS: {target_fps}")
            print(f"Actual FPS: {fps:.1f} {'✓' if fps >= target_fps * 0.9 else '✗'}")
            print(f"Target frame time: {target_frame_time:.2f}ms")
            print(f"Actual frame time: {avg_frame_time*1000:.2f}ms {'✓' if avg_frame_time*1000 <= target_frame_time*1.1 else '✗'}")
        
        return frame_times
    
    def test_coordinate_conversion_performance(self):
        """座標変換性能をテスト"""
        print(f"\n=== Coordinate Conversion Performance Test ===")
        
        # 等角投影座標変換関数
        def screen_to_grid(screen_x, screen_y, cell_size=32):
            """スクリーン座標をグリッド座標に変換"""
            # 等角投影の逆変換
            iso_x = screen_x - 400  # 画面中央オフセット
            iso_y = screen_y - 300
            
            grid_x = (iso_x / (cell_size // 2) + iso_y / (cell_size // 4)) / 2
            grid_y = (iso_y / (cell_size // 4) - iso_x / (cell_size // 2)) / 2
            
            return int(grid_x), int(grid_y)
        
        def grid_to_screen(grid_x, grid_y, cell_size=32):
            """グリッド座標をスクリーン座標に変換"""
            # 等角投影変換
            iso_x = (grid_x - grid_y) * (cell_size // 2)
            iso_y = (grid_x + grid_y) * (cell_size // 4)
            
            screen_x = iso_x + 400  # 画面中央オフセット
            screen_y = iso_y + 300
            
            return screen_x, screen_y
        
        # 大量の座標変換テスト
        num_conversions = 100000
        
        print(f"Testing {num_conversions} coordinate conversions...")
        
        # Screen to Grid変換テスト
        start_time = time.time()
        for i in range(num_conversions):
            screen_x = i % 800
            screen_y = (i // 800) % 600
            grid_x, grid_y = screen_to_grid(screen_x, screen_y)
        
        screen_to_grid_time = time.time() - start_time
        
        # Grid to Screen変換テスト
        start_time = time.time()
        for i in range(num_conversions):
            grid_x = i % 32
            grid_y = (i // 32) % 32
            screen_x, screen_y = grid_to_screen(grid_x, grid_y)
        
        grid_to_screen_time = time.time() - start_time
        
        print(f"\n--- Coordinate Conversion Summary ---")
        print(f"Conversions tested: {num_conversions}")
        print(f"Screen to Grid time: {screen_to_grid_time:.3f}s")
        print(f"Grid to Screen time: {grid_to_screen_time:.3f}s")
        print(f"Screen to Grid rate: {num_conversions/screen_to_grid_time:.0f} conversions/sec")
        print(f"Grid to Screen rate: {num_conversions/grid_to_screen_time:.0f} conversions/sec")
        
        # 精度テスト
        print(f"\n--- Conversion Accuracy Test ---")
        test_points = [(16, 16), (0, 0), (31, 31), (15, 20)]
        
        for grid_x, grid_y in test_points:
            screen_x, screen_y = grid_to_screen(grid_x, grid_y)
            back_x, back_y = screen_to_grid(screen_x, screen_y)
            
            error_x = abs(grid_x - back_x)
            error_y = abs(grid_y - back_y)
            
            print(f"Grid({grid_x},{grid_y}) -> Screen({screen_x},{screen_y}) -> Grid({back_x},{back_y}) Error:({error_x},{error_y})")
    
    def run_all_tests(self):
        """全てのテストを実行"""
        print("=== Simple Performance Test Suite ===\n")
        
        initial_memory = self.measure_memory()
        print(f"Initial memory usage: {initial_memory:.1f}MB\n")
        
        # PNG読み込みテスト
        png_results = self.test_png_loading_performance()
        
        # Pyxel描画性能テスト
        frame_results = self.test_pyxel_basic_performance()
        
        # 座標変換性能テスト
        self.test_coordinate_conversion_performance()
        
        final_memory = self.measure_memory()
        print(f"\n=== Overall Summary ===")
        print(f"Initial memory: {initial_memory:.1f}MB")
        print(f"Final memory: {final_memory:.1f}MB")
        print(f"Total memory delta: {final_memory - initial_memory:.1f}MB")
        
        print(f"\n✓ Performance testing complete!")


def main():
    """メイン実行関数"""
    try:
        tester = SimplePerformanceTest()
        tester.run_all_tests()
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()