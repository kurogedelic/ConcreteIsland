#!/usr/bin/env python3
"""
技術検証デモ2: 255色パレット対応と透過処理テスト

目的:
- PNG画像の色分析
- 255色パレットへの減色効果測定
- 透過ピクセルの検出と処理
- Pyxelでの色精度比較
"""

import os
import time
from pathlib import Path
from PIL import Image
import json
from collections import Counter
import numpy as np


class ColorPaletteAnalyzer:
    def __init__(self):
        self.results = {}
        
    def analyze_color_usage(self, directory="assets/tiles"):
        """PNG画像の色使用状況を分析"""
        print(f"=== Color Usage Analysis: {directory} ===")
        
        png_files = list(Path(directory).glob("*.png"))[:20]  # サンプル20ファイル
        if not png_files:
            print(f"No PNG files found in {directory}")
            return
        
        print(f"Analyzing {len(png_files)} PNG files for color usage...")
        
        all_colors = set()
        transparent_pixels = 0
        total_pixels = 0
        file_results = []
        
        for png_file in png_files:
            try:
                img = Image.open(png_file).convert('RGBA')
                width, height = img.size
                pixel_count = width * height
                total_pixels += pixel_count
                
                # ピクセルデータを取得
                pixels = list(img.getdata())
                
                # 色統計
                colors_in_file = set()
                transparent_in_file = 0
                
                for r, g, b, a in pixels:
                    if a < 128:  # 透過ピクセル
                        transparent_in_file += 1
                        transparent_pixels += 1
                    else:
                        color = (r, g, b)
                        colors_in_file.add(color)
                        all_colors.add(color)
                
                # ファイル結果
                result = {
                    'file': png_file.name,
                    'width': width,
                    'height': height,
                    'total_pixels': pixel_count,
                    'unique_colors': len(colors_in_file),
                    'transparent_pixels': transparent_in_file,
                    'transparency_ratio': transparent_in_file / pixel_count if pixel_count > 0 else 0
                }
                
                file_results.append(result)
                
                print(f"✓ {png_file.name}: {len(colors_in_file)} colors, {transparent_in_file} transparent pixels")
                
            except Exception as e:
                print(f"✗ Error analyzing {png_file.name}: {e}")
        
        # 全体統計
        print(f"\n--- Color Usage Summary ---")
        print(f"Files analyzed: {len(file_results)}")
        print(f"Total unique colors: {len(all_colors)}")
        print(f"Total pixels: {total_pixels:,}")
        print(f"Transparent pixels: {transparent_pixels:,}")
        print(f"Transparency ratio: {transparent_pixels/max(total_pixels, 1):.1%}")
        
        avg_colors = sum(r['unique_colors'] for r in file_results) / len(file_results) if file_results else 0
        print(f"Average colors per file: {avg_colors:.1f}")
        
        return {
            'total_unique_colors': len(all_colors),
            'file_results': file_results,
            'all_colors': list(all_colors),
            'transparent_pixels': transparent_pixels,
            'total_pixels': total_pixels
        }
    
    def create_255_color_palette(self, all_colors, method='kmeans'):
        """255色パレットを生成"""
        print(f"\n=== Creating 255-Color Palette ({method}) ===")
        
        if len(all_colors) <= 255:
            print(f"Colors already fit in 255 palette: {len(all_colors)} colors")
            return all_colors
        
        print(f"Reducing from {len(all_colors)} to 255 colors...")
        
        if method == 'kmeans':
            return self._create_kmeans_palette(all_colors)
        elif method == 'median_cut':
            return self._create_median_cut_palette(all_colors)
        else:
            # 単純な間引き
            step = len(all_colors) // 255
            return all_colors[::max(step, 1)][:255]
    
    def _create_kmeans_palette(self, all_colors):
        """K-meansクラスタリングで255色パレットを作成"""
        try:
            from sklearn.cluster import KMeans
            import numpy as np
            
            # 色データをnumpy配列に変換
            color_array = np.array(all_colors)
            
            # K-meansクラスタリング
            kmeans = KMeans(n_clusters=254, random_state=42, n_init=10)  # 254色（透過色用に1色予約）
            kmeans.fit(color_array)
            
            # クラスタ中心を整数に変換
            palette = []
            for center in kmeans.cluster_centers_:
                r, g, b = map(int, center)
                palette.append((r, g, b))
            
            # 透過色を追加（マゼンタ）
            palette.append((255, 0, 255))
            
            print(f"✓ K-means palette created: {len(palette)} colors")
            return palette
            
        except ImportError:
            print("sklearn not available, using simple sampling")
            return self._create_simple_palette(all_colors)
    
    def _create_median_cut_palette(self, all_colors):
        """Median Cut アルゴリズムで255色パレットを作成"""
        # シンプルな実装
        def median_cut(colors, depth):
            if depth == 0 or len(colors) <= 1:
                if colors:
                    r_avg = sum(c[0] for c in colors) // len(colors)
                    g_avg = sum(c[1] for c in colors) // len(colors)
                    b_avg = sum(c[2] for c in colors) // len(colors)
                    return [(r_avg, g_avg, b_avg)]
                return []
            
            # 最大分散のチャンネルを見つける
            r_values = [c[0] for c in colors]
            g_values = [c[1] for c in colors]
            b_values = [c[2] for c in colors]
            
            r_range = max(r_values) - min(r_values)
            g_range = max(g_values) - min(g_values)
            b_range = max(b_values) - min(b_values)
            
            if r_range >= g_range and r_range >= b_range:
                colors.sort(key=lambda c: c[0])
            elif g_range >= b_range:
                colors.sort(key=lambda c: c[1])
            else:
                colors.sort(key=lambda c: c[2])
            
            # 中央で分割
            mid = len(colors) // 2
            left = median_cut(colors[:mid], depth - 1)
            right = median_cut(colors[mid:], depth - 1)
            
            return left + right
        
        # 8レベルで分割（2^8 = 256色）
        palette = median_cut(list(all_colors), 8)
        return palette[:254] + [(255, 0, 255)]  # 透過色追加
    
    def _create_simple_palette(self, all_colors):
        """シンプルなサンプリングで255色パレットを作成"""
        step = len(all_colors) // 254
        palette = all_colors[::max(step, 1)][:254]
        palette.append((255, 0, 255))  # 透過色追加
        return palette
    
    def test_color_mapping_accuracy(self, original_colors, palette):
        """色マッピング精度をテスト"""
        print(f"\n=== Color Mapping Accuracy Test ===")
        
        def find_closest_color(target, palette):
            """最も近い色を検索"""
            min_distance = float('inf')
            closest = palette[0]
            
            for color in palette:
                if color == (255, 0, 255):  # 透過色をスキップ
                    continue
                
                distance = sum((a - b) ** 2 for a, b in zip(target, color))
                if distance < min_distance:
                    min_distance = distance
                    closest = color
            
            return closest, min_distance
        
        # サンプル色をテスト
        test_colors = original_colors[:100] if len(original_colors) > 100 else original_colors
        
        total_error = 0
        max_error = 0
        error_distribution = []
        
        for original in test_colors:
            mapped, distance = find_closest_color(original, palette)
            error = distance ** 0.5  # RMS距離
            
            total_error += error
            max_error = max(max_error, error)
            error_distribution.append(error)
        
        avg_error = total_error / len(test_colors) if test_colors else 0
        
        print(f"Colors tested: {len(test_colors)}")
        print(f"Average mapping error: {avg_error:.2f}")
        print(f"Maximum mapping error: {max_error:.2f}")
        
        # エラー分布
        low_error = sum(1 for e in error_distribution if e < 10)
        med_error = sum(1 for e in error_distribution if 10 <= e < 30)
        high_error = sum(1 for e in error_distribution if e >= 30)
        
        print(f"Error distribution:")
        print(f"  Low error (<10): {low_error} ({low_error/len(test_colors)*100:.1f}%)")
        print(f"  Medium error (10-30): {med_error} ({med_error/len(test_colors)*100:.1f}%)")
        print(f"  High error (>=30): {high_error} ({high_error/len(test_colors)*100:.1f}%)")
        
        return {
            'average_error': avg_error,
            'maximum_error': max_error,
            'low_error_ratio': low_error / len(test_colors) if test_colors else 0
        }
    
    def test_transparency_processing(self, directory="assets/tiles"):
        """透過処理をテスト"""
        print(f"\n=== Transparency Processing Test ===")
        
        png_files = list(Path(directory).glob("*.png"))[:10]  # サンプル10ファイル
        
        transparency_results = []
        
        for png_file in png_files:
            try:
                # 元画像
                img = Image.open(png_file).convert('RGBA')
                width, height = img.size
                
                # 透過ピクセル統計
                pixels = list(img.getdata())
                transparent_count = sum(1 for r, g, b, a in pixels if a < 128)
                
                # 透過色置換シミュレーション
                processed_pixels = []
                for r, g, b, a in pixels:
                    if a < 128:
                        # 透過色（マゼンタ）に置換
                        processed_pixels.append((255, 0, 255))
                    else:
                        processed_pixels.append((r, g, b))
                
                result = {
                    'file': png_file.name,
                    'size': (width, height),
                    'total_pixels': len(pixels),
                    'transparent_pixels': transparent_count,
                    'transparency_ratio': transparent_count / len(pixels),
                    'has_transparency': transparent_count > 0
                }
                
                transparency_results.append(result)
                
                print(f"✓ {png_file.name}: {transparent_count}/{len(pixels)} transparent pixels ({result['transparency_ratio']:.1%})")
                
            except Exception as e:
                print(f"✗ Error processing {png_file.name}: {e}")
        
        # 透過処理サマリー
        files_with_transparency = sum(1 for r in transparency_results if r['has_transparency'])
        avg_transparency = sum(r['transparency_ratio'] for r in transparency_results) / len(transparency_results) if transparency_results else 0
        
        print(f"\n--- Transparency Summary ---")
        print(f"Files tested: {len(transparency_results)}")
        print(f"Files with transparency: {files_with_transparency}")
        print(f"Average transparency ratio: {avg_transparency:.1%}")
        
        return transparency_results
    
    def generate_test_palette_file(self, palette, filename="tech_demos/test_palette_255.json"):
        """テスト用255色パレットファイルを生成"""
        print(f"\n=== Generating Test Palette File ===")
        
        try:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            
            # JSON形式で保存
            palette_data = {
                'format': '255_color_palette',
                'transparent_color_index': 255,
                'colors': [
                    {
                        'index': i,
                        'rgb': color,
                        'hex': f"#{color[0]:02x}{color[1]:02x}{color[2]:02x}"
                    }
                    for i, color in enumerate(palette)
                ]
            }
            
            with open(filename, 'w') as f:
                json.dump(palette_data, f, indent=2)
            
            print(f"✓ Palette file saved: {filename}")
            print(f"✓ Colors in palette: {len(palette)}")
            
            return filename
            
        except Exception as e:
            print(f"✗ Failed to save palette: {e}")
            return None
    
    def run_color_analysis(self):
        """全色分析を実行"""
        print("=== Color Palette Analysis Suite ===\n")
        
        # 色使用量分析
        color_usage = self.analyze_color_usage()
        
        if not color_usage:
            print("No color data to analyze")
            return
        
        # 255色パレット生成
        palette = self.create_255_color_palette(color_usage['all_colors'])
        
        # 色マッピング精度テスト
        mapping_accuracy = self.test_color_mapping_accuracy(color_usage['all_colors'], palette)
        
        # 透過処理テスト
        transparency_results = self.test_transparency_processing()
        
        # テスト用パレットファイル生成
        palette_file = self.generate_test_palette_file(palette)
        
        # 結果保存
        results = {
            'color_usage': color_usage,
            'palette': palette,
            'mapping_accuracy': mapping_accuracy,
            'transparency_results': transparency_results,
            'palette_file': palette_file,
            'summary': {
                'original_colors': color_usage['total_unique_colors'],
                'palette_colors': len(palette),
                'compression_ratio': len(palette) / color_usage['total_unique_colors'] if color_usage['total_unique_colors'] > 0 else 1,
                'average_mapping_error': mapping_accuracy['average_error'],
                'transparency_support': len([r for r in transparency_results if r['has_transparency']]) > 0
            }
        }
        
        # 結果保存
        try:
            with open('tech_demos/color_analysis_results.json', 'w') as f:
                json.dump(results, f, indent=2, default=str)
            print(f"\n✓ Color analysis results saved to tech_demos/color_analysis_results.json")
        except Exception as e:
            print(f"✗ Failed to save results: {e}")
        
        # サマリー表示
        print(f"\n=== Color Analysis Summary ===")
        print(f"Original unique colors: {color_usage['total_unique_colors']}")
        print(f"255-color palette: {len(palette)} colors")
        print(f"Color reduction ratio: {results['summary']['compression_ratio']:.3f}")
        print(f"Average mapping error: {mapping_accuracy['average_error']:.2f}")
        print(f"Low error mapping: {mapping_accuracy['low_error_ratio']:.1%}")
        print(f"Transparency support: {'✓' if results['summary']['transparency_support'] else '✗'}")
        
        return results


def main():
    """メイン実行関数"""
    try:
        analyzer = ColorPaletteAnalyzer()
        results = analyzer.run_color_analysis()
        
        print(f"\n✓ Color palette analysis complete!")
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()