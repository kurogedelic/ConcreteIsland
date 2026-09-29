#!/usr/bin/env python3
"""
技術検証デモ1: Pyxel .pyxres形式の読み込み性能とメモリ使用量テスト

目的:
- .pyxres ファイルの読み込み時間測定
- メモリ使用量の監視
- 複数ファイル読み込み時の挙動確認
- 既存PNG読み込みとの比較
"""

import pyxel
import time
import psutil
import os
from pathlib import Path


class PyxresPerformanceTest:
    def __init__(self):
        self.process = psutil.Process()
        self.results = {}
        
    def measure_memory(self):
        """現在のメモリ使用量を取得 (MB)"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def create_test_pyxres_file(self, filename: str, image_count: int = 1, size: int = 128):
        """テスト用.pyxresファイルを作成"""
        print(f"Creating test file: {filename}")
        
        # ディレクトリを確保
        Path(filename).parent.mkdir(parents=True, exist_ok=True)
        
        # Pyxelを初期化 (最小限)
        pyxel.init(size, size, title="Test", display_scale=1, capture_scale=1)
        
        # テスト用の画像を作成
        for i in range(image_count):
            # 簡単なパターンを描画
            pyxel.cls(0)
            for y in range(0, min(size, 256), 8):
                for x in range(0, min(size, 256), 8):
                    color = (x // 8 + y // 8 + i) % 16
                    pyxel.rect(x, y, 8, 8, color)
        
        # .pyxresファイルとして保存
        pyxel.save(filename)
        print(f"✓ Created {filename}")
        
        pyxel.quit()
    
    def test_pyxres_loading_speed(self, filename: str):
        """pyxresファイルの読み込み速度をテスト"""
        print(f"\n=== Testing .pyxres loading speed: {filename} ===")
        
        # メモリ使用量（読み込み前）
        memory_before = self.measure_memory()
        
        # 読み込み時間を測定
        start_time = time.time()
        
        try:
            pyxel.init(160, 120, title="Performance Test")
            pyxel.load(filename)
            
            load_time = time.time() - start_time
            memory_after = self.measure_memory()
            memory_delta = memory_after - memory_before
            
            # 結果を保存
            result = {
                'file': filename,
                'load_time': load_time,
                'memory_before': memory_before,
                'memory_after': memory_after,
                'memory_delta': memory_delta,
                'file_size': os.path.getsize(filename) / 1024 / 1024  # MB
            }
            
            print(f"✓ Load time: {load_time:.3f}s")
            print(f"✓ Memory before: {memory_before:.1f}MB")
            print(f"✓ Memory after: {memory_after:.1f}MB")
            print(f"✓ Memory delta: {memory_delta:.1f}MB")
            print(f"✓ File size: {result['file_size']:.2f}MB")
            
            pyxel.quit()
            return result
            
        except Exception as e:
            print(f"✗ Error loading {filename}: {e}")
            return None
    
    def test_multiple_loads(self, filenames: list):
        """複数ファイルの連続読み込みテスト"""
        print(f"\n=== Testing multiple .pyxres loads ===")
        
        total_start = time.time()
        memory_start = self.measure_memory()
        
        results = []
        
        for filename in filenames:
            result = self.test_pyxres_loading_speed(filename)
            if result:
                results.append(result)
        
        total_time = time.time() - total_start
        memory_end = self.measure_memory()
        memory_total = memory_end - memory_start
        
        print(f"\n=== Multiple Load Summary ===")
        print(f"Total files: {len(filenames)}")
        print(f"Total time: {total_time:.3f}s")
        print(f"Average time: {total_time/len(filenames):.3f}s per file")
        print(f"Total memory: {memory_total:.1f}MB")
        
        return results
    
    def compare_with_png_loading(self, png_files: list):
        """PNG読み込みとの比較テスト"""
        print(f"\n=== Comparing PNG vs .pyxres loading ===")
        
        # 既存のPNG読み込み時間を測定（シミュレート）
        png_times = []
        
        for png_file in png_files:
            if os.path.exists(png_file):
                start_time = time.time()
                
                # PNG読み込みシミュレート（PIL使用を想定）
                try:
                    from PIL import Image
                    img = Image.open(png_file)
                    img.load()  # 実際にデータを読み込み
                    
                    load_time = time.time() - start_time
                    png_times.append(load_time)
                    print(f"PNG {png_file}: {load_time:.3f}s")
                    
                except ImportError:
                    print("PIL not available, skipping PNG comparison")
                    break
                except Exception as e:
                    print(f"Error loading PNG {png_file}: {e}")
        
        if png_times:
            avg_png_time = sum(png_times) / len(png_times)
            print(f"Average PNG load time: {avg_png_time:.3f}s")
        
        return png_times
    
    def create_test_files(self):
        """テスト用ファイルを作成"""
        print("Creating test files...")
        
        # テスト用ディレクトリを作成
        test_dir = Path("tech_demos/test_assets")
        test_dir.mkdir(exist_ok=True, parents=True)
        
        # 異なるサイズの.pyxresファイルを作成
        test_files = [
            (test_dir / "small_test.pyxres", 1, 64),    # 小さいファイル
            (test_dir / "medium_test.pyxres", 2, 128),  # 中サイズファイル  
            (test_dir / "large_test.pyxres", 4, 256),   # 大きいファイル
        ]
        
        created_files = []
        for filename, image_count, size in test_files:
            self.create_test_pyxres_file(str(filename), image_count, size)
            created_files.append(str(filename))
        
        return created_files
    
    def run_all_tests(self):
        """全てのテストを実行"""
        print("=== Pyxel .pyxres Performance Test Suite ===\n")
        
        # テストファイルを作成
        test_files = self.create_test_files()
        
        # 個別ファイルテスト
        individual_results = []
        for filename in test_files:
            result = self.test_pyxres_loading_speed(filename)
            if result:
                individual_results.append(result)
        
        # 複数ファイル読み込みテスト
        multiple_results = self.test_multiple_loads(test_files)
        
        # PNG比較テスト（既存PNGファイルがあれば）
        png_files = list(Path("assets/tiles").glob("*.png"))[:5]  # 最初の5つ
        if png_files:
            png_results = self.compare_with_png_loading([str(f) for f in png_files])
        
        # 結果サマリー
        self.print_summary(individual_results)
        
        return individual_results
    
    def print_summary(self, results):
        """結果サマリーを表示"""
        print(f"\n=== Performance Test Summary ===")
        
        if not results:
            print("No results to summarize")
            return
        
        total_load_time = sum(r['load_time'] for r in results)
        total_memory = sum(r['memory_delta'] for r in results)
        total_file_size = sum(r['file_size'] for r in results)
        
        print(f"Files tested: {len(results)}")
        print(f"Total load time: {total_load_time:.3f}s")
        print(f"Average load time: {total_load_time/len(results):.3f}s")
        print(f"Total memory used: {total_memory:.1f}MB")
        print(f"Total file size: {total_file_size:.2f}MB")
        print(f"Memory efficiency: {total_file_size/max(total_memory, 0.1):.2f} (file_size/memory_used)")
        
        # 目標値との比較
        print(f"\n=== Target Comparison ===")
        target_load_time = 2.0  # 2秒以内
        target_memory = 50.0    # 50MB以内
        
        print(f"Load time target: {target_load_time}s")
        print(f"Load time actual: {total_load_time:.3f}s {'✓' if total_load_time <= target_load_time else '✗'}")
        
        print(f"Memory target: {target_memory}MB")
        print(f"Memory actual: {total_memory:.1f}MB {'✓' if total_memory <= target_memory else '✗'}")


def main():
    """メイン実行関数"""
    tester = PyxresPerformanceTest()
    
    try:
        results = tester.run_all_tests()
        
        print(f"\n=== Test Complete ===")
        print("Check results above for performance characteristics")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()