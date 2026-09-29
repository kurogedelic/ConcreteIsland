#!/usr/bin/env python3
"""
技術検証デモ2b: 透過処理の実装と検証

目的:
- 透過色処理の具体的な実装
- Pyxelでの透過描画テスト
- マゼンタ色(#ff00ff)の透過効果確認
"""

from PIL import Image, ImageDraw
import os
from pathlib import Path


class TransparencyTester:
    def __init__(self):
        self.transparent_color = (255, 0, 255)  # マゼンタ色
        
    def create_test_images(self):
        """透過テスト用の画像を作成"""
        print("=== Creating Test Images with Transparency ===")
        
        test_dir = Path("tech_demos/test_images")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        # テスト画像1: シンプルな透過
        self.create_simple_transparency_test(test_dir / "simple_transparency.png")
        
        # テスト画像2: 複雑な透過パターン
        self.create_complex_transparency_test(test_dir / "complex_transparency.png")
        
        # テスト画像3: 等角投影建物風
        self.create_isometric_building_test(test_dir / "isometric_building.png")
        
        return [
            test_dir / "simple_transparency.png",
            test_dir / "complex_transparency.png", 
            test_dir / "isometric_building.png"
        ]
    
    def create_simple_transparency_test(self, filename):
        """シンプルな透過テスト画像を作成"""
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 不透明な矩形
        draw.rectangle([10, 10, 30, 30], fill=(255, 0, 0, 255))  # 赤
        draw.rectangle([30, 30, 50, 50], fill=(0, 255, 0, 255))  # 緑
        
        # 透過矩形（空白部分は自動的に透過）
        
        # RGB形式で保存（透過部分がマゼンタになる）
        rgb_img = Image.new('RGB', (64, 64), self.transparent_color)
        rgb_img.paste(img, mask=img.split()[-1])  # アルファチャンネルをマスクとして使用
        
        rgb_img.save(filename)
        print(f"✓ Created {filename}")
    
    def create_complex_transparency_test(self, filename):
        """複雑な透過パターンのテスト画像を作成"""
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # チェッカーパターン
        for y in range(0, 64, 8):
            for x in range(0, 64, 8):
                if (x // 8 + y // 8) % 2 == 0:
                    color = (100, 150, 200, 255)  # 青系
                    draw.rectangle([x, y, x+8, y+8], fill=color)
        
        # 円形の透過穴
        draw.ellipse([20, 20, 44, 44], fill=(0, 0, 0, 0))
        
        # RGB形式で保存
        rgb_img = Image.new('RGB', (64, 64), self.transparent_color)
        rgb_img.paste(img, mask=img.split()[-1])
        
        rgb_img.save(filename)
        print(f"✓ Created {filename}")
    
    def create_isometric_building_test(self, filename):
        """等角投影建物風のテスト画像を作成"""
        img = Image.new('RGBA', (64, 64), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # 等角投影の建物っぽい形
        # 左面
        left_face = [(32, 10), (16, 18), (16, 40), (32, 32)]
        draw.polygon(left_face, fill=(180, 120, 80, 255))  # 茶色
        
        # 右面
        right_face = [(32, 10), (48, 18), (48, 40), (32, 32)]
        draw.polygon(right_face, fill=(150, 100, 60, 255))  # 濃い茶色
        
        # 屋根
        roof = [(32, 10), (16, 18), (32, 26), (48, 18)]
        draw.polygon(roof, fill=(200, 60, 60, 255))  # 赤い屋根
        
        # RGB形式で保存
        rgb_img = Image.new('RGB', (64, 64), self.transparent_color)
        rgb_img.paste(img, mask=img.split()[-1])
        
        rgb_img.save(filename)
        print(f"✓ Created {filename}")
    
    def analyze_transparency_conversion(self, test_images):
        """透過変換の効果を分析"""
        print(f"\n=== Analyzing Transparency Conversion ===")
        
        results = []
        
        for img_path in test_images:
            try:
                img = Image.open(img_path).convert('RGB')
                width, height = img.size
                
                # ピクセル分析
                pixels = list(img.getdata())
                transparent_pixels = sum(1 for p in pixels if p == self.transparent_color)
                total_pixels = len(pixels)
                
                # 色統計
                unique_colors = set(pixels)
                non_transparent_colors = unique_colors - {self.transparent_color}
                
                result = {
                    'file': img_path.name,
                    'size': (width, height),
                    'total_pixels': total_pixels,
                    'transparent_pixels': transparent_pixels,
                    'transparency_ratio': transparent_pixels / total_pixels,
                    'unique_colors': len(unique_colors),
                    'non_transparent_colors': len(non_transparent_colors),
                    'has_magenta_transparency': transparent_pixels > 0
                }
                
                results.append(result)
                
                print(f"✓ {img_path.name}:")
                print(f"    Size: {width}x{height}")
                print(f"    Transparent pixels: {transparent_pixels}/{total_pixels} ({result['transparency_ratio']:.1%})")
                print(f"    Unique colors: {len(unique_colors)}")
                print(f"    Non-transparent colors: {len(non_transparent_colors)}")
                
            except Exception as e:
                print(f"✗ Error analyzing {img_path}: {e}")
        
        return results
    
    def test_pyxel_transparency_simulation(self, test_images):
        """Pyxelでの透過描画をシミュレート"""
        print(f"\n=== Pyxel Transparency Simulation ===")
        
        # Pyxelカラーパレット（16色）のシミュレート
        pyxel_palette = [
            (0, 0, 0),        # 0: Black
            (43, 51, 95),     # 1: Navy
            (126, 32, 114),   # 2: Purple  
            (25, 149, 156),   # 3: Green
            (139, 72, 82),    # 4: Brown
            (57, 92, 152),    # 5: Dark blue
            (169, 193, 255),  # 6: Light blue
            (238, 238, 238),  # 7: White
            (212, 24, 108),   # 8: Red
            (211, 132, 65),   # 9: Orange
            (233, 195, 91),   # 10: Yellow
            (112, 198, 169),  # 11: Light green
            (118, 150, 222),  # 12: Sky blue
            (163, 163, 163),  # 13: Gray
            (255, 151, 152),  # 14: Pink (transparent color)
            (237, 199, 176)   # 15: Peach
        ]
        
        def find_closest_pyxel_color(target_color):
            """最も近いPyxelカラーを検索"""
            if target_color == self.transparent_color:
                return 14  # 透過色インデックス
            
            min_distance = float('inf')
            closest_index = 0
            
            for i, palette_color in enumerate(pyxel_palette):
                if i == 14:  # 透過色をスキップ
                    continue
                
                distance = sum((a - b) ** 2 for a, b in zip(target_color, palette_color))
                if distance < min_distance:
                    min_distance = distance
                    closest_index = i
            
            return closest_index
        
        for img_path in test_images:
            try:
                img = Image.open(img_path).convert('RGB')
                width, height = img.size
                
                print(f"\n--- Simulating {img_path.name} ---")
                
                # Pyxelカラーインデックスに変換
                pyxel_indices = []
                color_mapping = {}
                
                for y in range(height):
                    row = []
                    for x in range(width):
                        pixel = img.getpixel((x, y))
                        
                        if pixel not in color_mapping:
                            index = find_closest_pyxel_color(pixel)
                            color_mapping[pixel] = index
                        
                        row.append(color_mapping[pixel])
                    pyxel_indices.append(row)
                
                # 統計
                transparent_count = sum(row.count(14) for row in pyxel_indices)
                total_pixels = width * height
                unique_indices = set()
                for row in pyxel_indices:
                    unique_indices.update(row)
                
                print(f"    Original colors mapped to {len(unique_indices)} Pyxel colors")
                print(f"    Transparent pixels: {transparent_count}/{total_pixels} ({transparent_count/total_pixels:.1%})")
                print(f"    Color indices used: {sorted(unique_indices)}")
                
                # 色マッピング品質
                mapping_errors = []
                for original_color, pyxel_index in color_mapping.items():
                    if original_color != self.transparent_color and pyxel_index != 14:
                        pyxel_color = pyxel_palette[pyxel_index]
                        error = sum((a - b) ** 2 for a, b in zip(original_color, pyxel_color)) ** 0.5
                        mapping_errors.append(error)
                
                if mapping_errors:
                    avg_error = sum(mapping_errors) / len(mapping_errors)
                    max_error = max(mapping_errors)
                    print(f"    Average color mapping error: {avg_error:.2f}")
                    print(f"    Maximum color mapping error: {max_error:.2f}")
                
            except Exception as e:
                print(f"✗ Error simulating {img_path}: {e}")
    
    def run_transparency_tests(self):
        """全透過テストを実行"""
        print("=== Transparency Processing Test Suite ===\n")
        
        # テスト画像作成
        test_images = self.create_test_images()
        
        # 透過変換分析
        conversion_results = self.analyze_transparency_conversion(test_images)
        
        # Pyxel透過シミュレーション
        self.test_pyxel_transparency_simulation(test_images)
        
        # 結果サマリー
        print(f"\n=== Transparency Test Summary ===")
        
        total_files = len(conversion_results)
        files_with_transparency = sum(1 for r in conversion_results if r['has_magenta_transparency'])
        avg_transparency = sum(r['transparency_ratio'] for r in conversion_results) / total_files if total_files > 0 else 0
        
        print(f"Test images created: {total_files}")
        print(f"Images with transparency: {files_with_transparency}")
        print(f"Average transparency ratio: {avg_transparency:.1%}")
        print(f"Transparency conversion: {'✓' if files_with_transparency > 0 else '✗'}")
        print(f"Magenta transparency color: {self.transparent_color}")
        
        return {
            'test_images': [str(p) for p in test_images],
            'conversion_results': conversion_results,
            'transparent_color': self.transparent_color,
            'summary': {
                'total_files': total_files,
                'files_with_transparency': files_with_transparency,
                'average_transparency_ratio': avg_transparency
            }
        }


def main():
    """メイン実行関数"""
    try:
        tester = TransparencyTester()
        results = tester.run_transparency_tests()
        
        # 結果を保存
        import json
        with open('tech_demos/transparency_test_results.json', 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✓ Transparency test complete! Results saved to tech_demos/transparency_test_results.json")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()