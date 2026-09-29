#!/usr/bin/env python3
"""
技術検証デモ4: 等角投影座標変換システムの精度検証

目的:
- 等角投影座標変換の精度確認
- カーソル位置の正確性検証
- 境界ケースでの挙動テスト
- 最適な変換パラメータの特定
"""

import math
import time
from typing import Tuple, List, Dict
from pathlib import Path
import json


class IsometricPrecisionTester:
    def __init__(self, cell_size: int = 32):
        self.cell_size = cell_size
        self.screen_center_x = 400
        self.screen_center_y = 300
        
    def grid_to_screen(self, grid_x: int, grid_y: int) -> Tuple[int, int]:
        """グリッド座標をスクリーン座標に変換（等角投影）"""
        iso_x = (grid_x - grid_y) * (self.cell_size // 2)
        iso_y = (grid_x + grid_y) * (self.cell_size // 4)
        
        screen_x = iso_x + self.screen_center_x
        screen_y = iso_y + self.screen_center_y
        
        return screen_x, screen_y
    
    def screen_to_grid(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """スクリーン座標をグリッド座標に変換"""
        iso_x = screen_x - self.screen_center_x
        iso_y = screen_y - self.screen_center_y
        
        grid_x = (iso_x / (self.cell_size // 2) + iso_y / (self.cell_size // 4)) / 2
        grid_y = (iso_y / (self.cell_size // 4) - iso_x / (self.cell_size // 2)) / 2
        
        return int(round(grid_x)), int(round(grid_y))
    
    def screen_to_grid_precise(self, screen_x: int, screen_y: int) -> Tuple[float, float]:
        """スクリーン座標をグリッド座標に変換（浮動小数点精度）"""
        iso_x = screen_x - self.screen_center_x
        iso_y = screen_y - self.screen_center_y
        
        grid_x = (iso_x / (self.cell_size // 2) + iso_y / (self.cell_size // 4)) / 2
        grid_y = (iso_y / (self.cell_size // 4) - iso_x / (self.cell_size // 2)) / 2
        
        return grid_x, grid_y
    
    def test_conversion_accuracy(self):
        """座標変換の精度をテスト"""
        print("=== Coordinate Conversion Accuracy Test ===")
        
        # テストポイント定義
        test_points = [
            # 基本ケース
            (0, 0), (1, 0), (0, 1), (1, 1),
            # 対称ケース
            (5, 5), (-5, -5), (5, -5), (-5, 5),
            # 大きな値
            (50, 50), (100, 100), (-50, -50),
            # 非対称
            (7, 3), (13, 29), (-17, 8)
        ]
        
        total_error_x = 0
        total_error_y = 0
        max_error = 0
        accuracy_results = []
        
        print(f"Testing {len(test_points)} coordinate points...")
        
        for original_x, original_y in test_points:
            # 前方変換: Grid -> Screen
            screen_x, screen_y = self.grid_to_screen(original_x, original_y)
            
            # 逆変換: Screen -> Grid
            recovered_x, recovered_y = self.screen_to_grid(screen_x, screen_y)
            
            # 精密逆変換
            precise_x, precise_y = self.screen_to_grid_precise(screen_x, screen_y)
            
            # エラー計算
            error_x = abs(original_x - recovered_x)
            error_y = abs(original_y - recovered_y)
            total_error = math.sqrt(error_x**2 + error_y**2)
            
            # 精密エラー計算
            precise_error_x = abs(original_x - precise_x)
            precise_error_y = abs(original_y - precise_y)
            precise_total_error = math.sqrt(precise_error_x**2 + precise_error_y**2)
            
            total_error_x += error_x
            total_error_y += error_y
            max_error = max(max_error, total_error)
            
            result = {
                'original': (original_x, original_y),
                'screen': (screen_x, screen_y),
                'recovered': (recovered_x, recovered_y),
                'precise_recovered': (precise_x, precise_y),
                'error': (error_x, error_y),
                'total_error': total_error,
                'precise_error': precise_total_error
            }
            
            accuracy_results.append(result)
            
            print(f"Grid({original_x:3},{original_y:3}) -> Screen({screen_x:4},{screen_y:4}) -> Grid({recovered_x:3},{recovered_y:3}) "
                  f"Error:({error_x},{error_y}) Total:{total_error:.3f}")
        
        # 統計
        avg_error_x = total_error_x / len(test_points)
        avg_error_y = total_error_y / len(test_points)
        
        print(f"\n--- Accuracy Summary ---")
        print(f"Average X error: {avg_error_x:.3f}")
        print(f"Average Y error: {avg_error_y:.3f}")
        print(f"Maximum total error: {max_error:.3f}")
        
        perfect_conversions = sum(1 for r in accuracy_results if r['total_error'] == 0)
        print(f"Perfect conversions: {perfect_conversions}/{len(test_points)} ({perfect_conversions/len(test_points)*100:.1f}%)")
        
        return accuracy_results
    
    def test_cursor_precision(self):
        """カーソル位置の精度をテスト"""
        print(f"\n=== Cursor Precision Test ===")
        
        # 各グリッドセルの境界でのカーソル精度をテスト
        GRID_SIZE = 10
        cursor_results = []
        
        for grid_y in range(GRID_SIZE):
            for grid_x in range(GRID_SIZE):
                # グリッドセルの中心
                center_screen_x, center_screen_y = self.grid_to_screen(grid_x, grid_y)
                
                # セル内の複数のポイントをテスト
                test_offsets = [
                    (0, 0),      # 中心
                    (-8, -4),    # 左上
                    (8, -4),     # 右上
                    (-8, 4),     # 左下
                    (8, 4),      # 右下
                    (0, -4),     # 上
                    (0, 4),      # 下
                    (-8, 0),     # 左
                    (8, 0)       # 右
                ]
                
                for offset_x, offset_y in test_offsets:
                    screen_x = center_screen_x + offset_x
                    screen_y = center_screen_y + offset_y
                    
                    detected_grid_x, detected_grid_y = self.screen_to_grid(screen_x, screen_y)
                    
                    # 正確性チェック
                    correct = (detected_grid_x == grid_x and detected_grid_y == grid_y)
                    
                    result = {
                        'target_grid': (grid_x, grid_y),
                        'screen_pos': (screen_x, screen_y),
                        'detected_grid': (detected_grid_x, detected_grid_y),
                        'offset': (offset_x, offset_y),
                        'correct': correct
                    }
                    
                    cursor_results.append(result)
        
        # 精度統計
        correct_detections = sum(1 for r in cursor_results if r['correct'])
        total_tests = len(cursor_results)
        accuracy_percentage = correct_detections / total_tests * 100
        
        print(f"Cursor precision tests: {total_tests}")
        print(f"Correct detections: {correct_detections}")
        print(f"Accuracy: {accuracy_percentage:.1f}%")
        
        # エラーケースの分析
        error_cases = [r for r in cursor_results if not r['correct']]
        if error_cases:
            print(f"Error cases: {len(error_cases)}")
            
            # エラーパターンの分析
            error_patterns = {}
            for error in error_cases[:10]:  # 最初の10個のエラーを表示
                pattern = f"Target{error['target_grid']} -> Detected{error['detected_grid']}"
                error_patterns[pattern] = error_patterns.get(pattern, 0) + 1
                
                print(f"  {pattern} at offset{error['offset']}")
        
        return cursor_results
    
    def test_boundary_cases(self):
        """境界ケースでの挙動をテスト"""
        print(f"\n=== Boundary Cases Test ===")
        
        boundary_cases = [
            # 極値
            (-1000, -1000),
            (1000, 1000),
            (0, 1000),
            (1000, 0),
            # ゼロ周辺
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1),
            # 画面境界付近
            (-100, 50), (100, -50),
        ]
        
        boundary_results = []
        
        for grid_x, grid_y in boundary_cases:
            try:
                screen_x, screen_y = self.grid_to_screen(grid_x, grid_y)
                recovered_x, recovered_y = self.screen_to_grid(screen_x, screen_y)
                
                error_x = abs(grid_x - recovered_x)
                error_y = abs(grid_y - recovered_y)
                
                result = {
                    'original': (grid_x, grid_y),
                    'screen': (screen_x, screen_y),
                    'recovered': (recovered_x, recovered_y),
                    'error': (error_x, error_y),
                    'valid': True
                }
                
                print(f"Grid({grid_x:4},{grid_y:4}) -> Screen({screen_x:6},{screen_y:6}) -> Grid({recovered_x:4},{recovered_y:4}) "
                      f"Error:({error_x},{error_y})")
                
            except Exception as e:
                result = {
                    'original': (grid_x, grid_y),
                    'error_message': str(e),
                    'valid': False
                }
                print(f"Grid({grid_x:4},{grid_y:4}) -> ERROR: {e}")
            
            boundary_results.append(result)
        
        # 有効な結果の統計
        valid_results = [r for r in boundary_results if r['valid']]
        if valid_results:
            max_error = max(max(r['error']) for r in valid_results)
            avg_error = sum(sum(r['error']) for r in valid_results) / (len(valid_results) * 2)
            
            print(f"\nBoundary test summary:")
            print(f"Valid results: {len(valid_results)}/{len(boundary_cases)}")
            print(f"Average error: {avg_error:.3f}")
            print(f"Maximum error: {max_error}")
        
        return boundary_results
    
    def test_different_cell_sizes(self):
        """異なるセルサイズでの精度をテスト"""
        print(f"\n=== Different Cell Sizes Test ===")
        
        cell_sizes = [16, 24, 32, 48, 64]
        size_results = []
        
        for cell_size in cell_sizes:
            print(f"\nTesting cell size: {cell_size}px")
            
            # 一時的にセルサイズを変更
            original_cell_size = self.cell_size
            self.cell_size = cell_size
            
            # 基本的な精度テスト
            test_points = [(0, 0), (5, 5), (10, -5), (-7, 3)]
            errors = []
            
            for grid_x, grid_y in test_points:
                screen_x, screen_y = self.grid_to_screen(grid_x, grid_y)
                recovered_x, recovered_y = self.screen_to_grid(screen_x, screen_y)
                
                error = abs(grid_x - recovered_x) + abs(grid_y - recovered_y)
                errors.append(error)
            
            avg_error = sum(errors) / len(errors)
            max_error = max(errors)
            
            result = {
                'cell_size': cell_size,
                'average_error': avg_error,
                'maximum_error': max_error,
                'test_points': len(test_points)
            }
            
            size_results.append(result)
            
            print(f"  Average error: {avg_error:.3f}")
            print(f"  Maximum error: {max_error}")
            
            # セルサイズを元に戻す
            self.cell_size = original_cell_size
        
        # 最適なセルサイズの推定
        best_size = min(size_results, key=lambda x: x['average_error'])
        print(f"\nBest cell size: {best_size['cell_size']}px (avg error: {best_size['average_error']:.3f})")
        
        return size_results
    
    def optimize_conversion_parameters(self):
        """変換パラメータの最適化"""
        print(f"\n=== Conversion Parameter Optimization ===")
        
        # 異なるオフセット値でテスト
        test_configs = [
            {'center_x': 400, 'center_y': 300, 'name': 'Default'},
            {'center_x': 400, 'center_y': 308, 'name': 'Y offset +8'},  # CLAUDE.mdに記載されたオフセット
            {'center_x': 408, 'center_y': 300, 'name': 'X offset +8'},
            {'center_x': 408, 'center_y': 308, 'name': 'Both offset +8'},
            {'center_x': 400, 'center_y': 304, 'name': 'Y offset +4'},
        ]
        
        optimization_results = []
        
        for config in test_configs:
            print(f"\nTesting {config['name']} (center: {config['center_x']}, {config['center_y']})")
            
            # 一時的に設定変更
            original_center_x = self.screen_center_x
            original_center_y = self.screen_center_y
            
            self.screen_center_x = config['center_x']
            self.screen_center_y = config['center_y']
            
            # 精度テスト
            test_points = [(i, j) for i in range(-5, 6) for j in range(-5, 6)]
            total_error = 0
            perfect_count = 0
            
            for grid_x, grid_y in test_points:
                screen_x, screen_y = self.grid_to_screen(grid_x, grid_y)
                recovered_x, recovered_y = self.screen_to_grid(screen_x, screen_y)
                
                error = abs(grid_x - recovered_x) + abs(grid_y - recovered_y)
                total_error += error
                
                if error == 0:
                    perfect_count += 1
            
            avg_error = total_error / len(test_points)
            perfect_ratio = perfect_count / len(test_points)
            
            result = {
                'config': config['name'],
                'center_x': config['center_x'],
                'center_y': config['center_y'],
                'average_error': avg_error,
                'perfect_ratio': perfect_ratio,
                'test_points': len(test_points)
            }
            
            optimization_results.append(result)
            
            print(f"  Average error: {avg_error:.3f}")
            print(f"  Perfect conversions: {perfect_count}/{len(test_points)} ({perfect_ratio:.1%})")
            
            # 設定を元に戻す
            self.screen_center_x = original_center_x
            self.screen_center_y = original_center_y
        
        # 最適な設定
        best_config = min(optimization_results, key=lambda x: x['average_error'])
        print(f"\nBest configuration: {best_config['config']}")
        print(f"  Center: ({best_config['center_x']}, {best_config['center_y']})")
        print(f"  Average error: {best_config['average_error']:.3f}")
        print(f"  Perfect ratio: {best_config['perfect_ratio']:.1%}")
        
        return optimization_results
    
    def run_precision_tests(self):
        """全精度テストを実行"""
        print("=== Isometric Precision Test Suite ===")
        print(f"Cell size: {self.cell_size}px")
        print(f"Screen center: ({self.screen_center_x}, {self.screen_center_y})\n")
        
        # 各テストを実行
        accuracy_results = self.test_conversion_accuracy()
        cursor_results = self.test_cursor_precision()
        boundary_results = self.test_boundary_cases()
        size_results = self.test_different_cell_sizes()
        optimization_results = self.optimize_conversion_parameters()
        
        # 結果サマリー
        perfect_accuracy = sum(1 for r in accuracy_results if r['total_error'] == 0)
        cursor_accuracy = sum(1 for r in cursor_results if r['correct']) / len(cursor_results) * 100
        
        print(f"\n=== Precision Test Summary ===")
        print(f"Coordinate accuracy: {perfect_accuracy}/{len(accuracy_results)} perfect ({perfect_accuracy/len(accuracy_results)*100:.1f}%)")
        print(f"Cursor precision: {cursor_accuracy:.1f}%")
        print(f"Boundary tests: {len([r for r in boundary_results if r['valid']])}/{len(boundary_results)} valid")
        
        # 推奨設定
        best_cell_size = min(size_results, key=lambda x: x['average_error'])['cell_size']
        best_optimization = min(optimization_results, key=lambda x: x['average_error'])
        
        print(f"\n=== Recommendations ===")
        print(f"Recommended cell size: {best_cell_size}px")
        print(f"Recommended center: ({best_optimization['center_x']}, {best_optimization['center_y']})")
        
        return {
            'accuracy_results': accuracy_results,
            'cursor_results': cursor_results,
            'boundary_results': boundary_results,
            'size_results': size_results,
            'optimization_results': optimization_results,
            'recommendations': {
                'cell_size': best_cell_size,
                'screen_center_x': best_optimization['center_x'],
                'screen_center_y': best_optimization['center_y']
            }
        }


def main():
    """メイン実行関数"""
    try:
        tester = IsometricPrecisionTester()
        results = tester.run_precision_tests()
        
        # 結果を保存
        with open('tech_demos/isometric_precision_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✓ Isometric precision test complete! Results saved to tech_demos/isometric_precision_results.json")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()