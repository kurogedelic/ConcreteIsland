#!/usr/bin/env python3
"""
技術検証デモ5: 日本語フォント表示とUI配置の動作確認

目的:
- 日本語BDFフォントの読み込み確認
- 日本語テキストの表示品質検証
- UI要素の配置精度確認
- 文字エンコーディングの動作確認
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Tuple


class JapaneseUITester:
    def __init__(self):
        self.test_results = {}
        
    def check_font_file_availability(self):
        """日本語フォントファイルの利用可能性を確認"""
        print("=== Japanese Font File Availability Check ===")
        
        # 既知のフォントファイルパス
        font_paths = [
            "umplus_j10r.bdf",  # 既存のフォント
            "assets/fonts/umplus_j10r.bdf",
            "/usr/share/fonts/umplus_j10r.bdf",
            "tech_demos/test_fonts/umplus_j10r.bdf"
        ]
        
        available_fonts = []
        
        for font_path in font_paths:
            if os.path.exists(font_path):
                try:
                    file_size = os.path.getsize(font_path)
                    available_fonts.append({
                        'path': font_path,
                        'size_kb': file_size / 1024,
                        'exists': True
                    })
                    print(f"✓ Found: {font_path} ({file_size/1024:.1f}KB)")
                except Exception as e:
                    print(f"✗ Error accessing {font_path}: {e}")
            else:
                print(f"✗ Not found: {font_path}")
        
        if not available_fonts:
            print("No Japanese font files found. Creating test font info...")
            self.create_test_font_info()
        
        return available_fonts
    
    def create_test_font_info(self):
        """テスト用フォント情報を作成"""
        print("Creating test font information...")
        
        # BDFフォントの基本情報
        bdf_info = {
            'format': 'BDF (Bitmap Distribution Format)',
            'encoding': 'ISO10646-1 (Unicode)',
            'typical_size': '100-500KB for Japanese fonts',
            'characters': {
                'ascii': 95,      # 基本ASCII文字
                'hiragana': 83,   # ひらがな
                'katakana': 86,   # カタカナ
                'kanji': 1000,    # 常用漢字の一部
                'symbols': 50     # 記号類
            },
            'font_metrics': {
                'font_size': '10pt',
                'cell_width': 10,
                'cell_height': 10,
                'baseline': 8
            }
        }
        
        # テスト用ディレクトリを作成
        test_dir = Path("tech_demos/test_fonts")
        test_dir.mkdir(parents=True, exist_ok=True)
        
        with open(test_dir / "bdf_font_info.json", 'w', encoding='utf-8') as f:
            json.dump(bdf_info, f, ensure_ascii=False, indent=2)
        
        print(f"✓ Font info saved to {test_dir / 'bdf_font_info.json'}")
    
    def test_japanese_text_encoding(self):
        """日本語テキストのエンコーディングをテスト"""
        print(f"\n=== Japanese Text Encoding Test ===")
        
        # テスト用日本語テキスト
        test_texts = {
            'hiragana': 'あいうえおかきくけこ',
            'katakana': 'アイウエオカキクケコ',
            'kanji': '日本語文字表示テスト',
            'mixed': '戦後日本復興シミュレーション',
            'game_ui': {
                'population': '人口',
                'money': '資金',
                'happiness': '幸福度',
                'year': '年',
                'buildings': {
                    'barracks': 'バラック住宅',
                    'wooden_house': '木造住宅',
                    'school': '学校',
                    'hospital': '病院',
                    'factory': '工場'
                }
            }
        }
        
        encoding_results = []
        
        for category, text in test_texts.items():
            if category == 'game_ui':
                # ゲームUI用のテキストを再帰的に処理
                ui_results = self._test_ui_text_encoding(text)
                encoding_results.append({
                    'category': category,
                    'ui_elements': ui_results
                })
            else:
                result = self._test_single_text_encoding(category, text)
                encoding_results.append(result)
        
        return encoding_results
    
    def _test_single_text_encoding(self, category: str, text: str) -> Dict:
        """単一テキストのエンコーディングをテスト"""
        try:
            # UTF-8エンコーディング
            utf8_bytes = text.encode('utf-8')
            utf8_length = len(utf8_bytes)
            
            # 文字数カウント
            char_count = len(text)
            
            # バイト効率
            bytes_per_char = utf8_length / char_count if char_count > 0 else 0
            
            result = {
                'category': category,
                'text': text,
                'char_count': char_count,
                'utf8_bytes': utf8_length,
                'bytes_per_char': bytes_per_char,
                'encoding_success': True
            }
            
            print(f"✓ {category}: '{text[:20]}...' ({char_count} chars, {utf8_length} bytes)")
            
            return result
            
        except Exception as e:
            print(f"✗ Encoding error for {category}: {e}")
            return {
                'category': category,
                'text': text,
                'error': str(e),
                'encoding_success': False
            }
    
    def _test_ui_text_encoding(self, ui_data: Dict) -> List[Dict]:
        """UI用テキストのエンコーディングをテスト"""
        results = []
        
        for key, value in ui_data.items():
            if isinstance(value, str):
                result = self._test_single_text_encoding(f"ui_{key}", value)
                results.append(result)
            elif isinstance(value, dict):
                # ネストした辞書を再帰処理
                nested_results = self._test_ui_text_encoding(value)
                results.extend(nested_results)
        
        return results
    
    def test_ui_layout_calculations(self):
        """UI配置計算をテスト"""
        print(f"\n=== UI Layout Calculations Test ===")
        
        # 画面サイズ
        SCREEN_WIDTH = 800
        SCREEN_HEIGHT = 600
        
        # UI要素の配置テスト
        ui_elements = {
            'info_window': {
                'position': 'bottom_left',
                'width': 200,
                'height': 150,
                'margin': 10
            },
            'build_palette': {
                'position': 'bottom_right',
                'width': 180,
                'height': 200,
                'margin': 10
            },
            'status_bar': {
                'position': 'top',
                'width': SCREEN_WIDTH,
                'height': 30,
                'margin': 0
            }
        }
        
        layout_results = []
        
        for element_name, config in ui_elements.items():
            # 位置計算
            x, y = self._calculate_ui_position(
                config['position'],
                config['width'],
                config['height'],
                config['margin'],
                SCREEN_WIDTH,
                SCREEN_HEIGHT
            )
            
            # 重複チェック用の矩形
            rect = {
                'x': x,
                'y': y,
                'width': config['width'],
                'height': config['height']
            }
            
            result = {
                'element': element_name,
                'position': config['position'],
                'calculated_xy': (x, y),
                'rect': rect,
                'within_screen': self._is_within_screen(rect, SCREEN_WIDTH, SCREEN_HEIGHT)
            }
            
            layout_results.append(result)
            
            print(f"✓ {element_name}: {config['position']} -> ({x}, {y}) "
                  f"[{config['width']}x{config['height']}] "
                  f"{'✓' if result['within_screen'] else '✗'}")
        
        # 重複チェック
        overlaps = self._check_ui_overlaps(layout_results)
        if overlaps:
            print(f"\n⚠️  UI Overlaps detected:")
            for overlap in overlaps:
                print(f"  {overlap['element1']} overlaps with {overlap['element2']}")
        else:
            print(f"\n✓ No UI overlaps detected")
        
        return layout_results, overlaps
    
    def _calculate_ui_position(self, position: str, width: int, height: int, 
                              margin: int, screen_w: int, screen_h: int) -> Tuple[int, int]:
        """UI要素の位置を計算"""
        positions = {
            'top_left': (margin, margin),
            'top_right': (screen_w - width - margin, margin),
            'bottom_left': (margin, screen_h - height - margin),
            'bottom_right': (screen_w - width - margin, screen_h - height - margin),
            'top': (0, margin),
            'center': ((screen_w - width) // 2, (screen_h - height) // 2)
        }
        
        return positions.get(position, (0, 0))
    
    def _is_within_screen(self, rect: Dict, screen_w: int, screen_h: int) -> bool:
        """UI要素が画面内にあるかチェック"""
        return (rect['x'] >= 0 and rect['y'] >= 0 and
                rect['x'] + rect['width'] <= screen_w and
                rect['y'] + rect['height'] <= screen_h)
    
    def _check_ui_overlaps(self, layout_results: List[Dict]) -> List[Dict]:
        """UI要素の重複をチェック"""
        overlaps = []
        
        for i, element1 in enumerate(layout_results):
            for j, element2 in enumerate(layout_results[i+1:], i+1):
                rect1 = element1['rect']
                rect2 = element2['rect']
                
                # 矩形の重複判定
                if self._rectangles_overlap(rect1, rect2):
                    overlaps.append({
                        'element1': element1['element'],
                        'element2': element2['element'],
                        'rect1': rect1,
                        'rect2': rect2
                    })
        
        return overlaps
    
    def _rectangles_overlap(self, rect1: Dict, rect2: Dict) -> bool:
        """2つの矩形が重複するかチェック"""
        return not (rect1['x'] >= rect2['x'] + rect2['width'] or
                   rect2['x'] >= rect1['x'] + rect1['width'] or
                   rect1['y'] >= rect2['y'] + rect2['height'] or
                   rect2['y'] >= rect1['y'] + rect1['height'])
    
    def test_text_rendering_simulation(self):
        """テキスト描画のシミュレーション"""
        print(f"\n=== Text Rendering Simulation ===")
        
        # フォントメトリクス（BDFフォント想定）
        font_metrics = {
            'char_width': 10,
            'char_height': 10,
            'line_spacing': 12,
            'baseline_offset': 8
        }
        
        # テスト用テキスト
        test_texts = [
            "人口: 1,234",
            "資金: ¥56,789",
            "年度: 1955年",
            "バラック住宅",
            "戦後復興期"
        ]
        
        rendering_results = []
        
        for text in test_texts:
            # 描画サイズ計算
            text_width = len(text) * font_metrics['char_width']
            text_height = font_metrics['char_height']
            
            # 描画位置計算（例：中央配置）
            screen_width = 200
            x_offset = (screen_width - text_width) // 2
            y_offset = 20
            
            # 文字ごとの描画位置
            char_positions = []
            for i, char in enumerate(text):
                char_x = x_offset + i * font_metrics['char_width']
                char_y = y_offset
                char_positions.append({
                    'char': char,
                    'x': char_x,
                    'y': char_y
                })
            
            result = {
                'text': text,
                'text_width': text_width,
                'text_height': text_height,
                'position': (x_offset, y_offset),
                'char_positions': char_positions,
                'fits_in_area': text_width <= screen_width
            }
            
            rendering_results.append(result)
            
            print(f"✓ '{text}': {text_width}px width, position ({x_offset}, {y_offset}) "
                  f"{'✓' if result['fits_in_area'] else '✗'}")
        
        return rendering_results
    
    def test_ui_responsiveness(self):
        """UI応答性をテスト"""
        print(f"\n=== UI Responsiveness Test ===")
        
        # 異なる画面サイズでのUI配置
        screen_sizes = [
            (640, 480),   # VGA
            (800, 600),   # SVGA
            (1024, 768),  # XGA
            (1280, 720),  # HD
        ]
        
        responsiveness_results = []
        
        for width, height in screen_sizes:
            print(f"\nTesting screen size: {width}x{height}")
            
            # UI要素の配置を再計算
            ui_elements = {
                'info_panel': {'width': 200, 'height': 150, 'position': 'bottom_left'},
                'build_palette': {'width': 180, 'height': 200, 'position': 'bottom_right'},
                'status_bar': {'width': width, 'height': 30, 'position': 'top'}
            }
            
            element_results = []
            usable_area = {'x': 0, 'y': 30, 'width': width, 'height': height - 30}
            
            for name, config in ui_elements.items():
                x, y = self._calculate_ui_position(
                    config['position'], config['width'], config['height'],
                    10, width, height
                )
                
                fits = (x >= 0 and y >= 0 and 
                       x + config['width'] <= width and 
                       y + config['height'] <= height)
                
                element_result = {
                    'element': name,
                    'position': (x, y),
                    'size': (config['width'], config['height']),
                    'fits': fits
                }
                
                element_results.append(element_result)
                print(f"  {name}: ({x}, {y}) {config['width']}x{config['height']} {'✓' if fits else '✗'}")
            
            # 利用可能な描画エリア計算
            occupied_areas = [r for r in element_results if r['fits']]
            available_area = self._calculate_available_area(width, height, occupied_areas)
            
            result = {
                'screen_size': (width, height),
                'elements': element_results,
                'available_area': available_area,
                'all_elements_fit': all(r['fits'] for r in element_results)
            }
            
            responsiveness_results.append(result)
            print(f"  Available area: {available_area['width']}x{available_area['height']} "
                  f"at ({available_area['x']}, {available_area['y']})")
        
        return responsiveness_results
    
    def _calculate_available_area(self, screen_width: int, screen_height: int, 
                                 occupied_areas: List[Dict]) -> Dict:
        """利用可能な描画エリアを計算"""
        # 簡単な計算（UI要素を除いた中央エリア）
        margin = 10
        ui_left = max((area['position'][0] + area['size'][0] + margin 
                      for area in occupied_areas 
                      if area['position'][0] < screen_width // 2), default=margin)
        
        ui_right = min((area['position'][0] - margin 
                       for area in occupied_areas 
                       if area['position'][0] > screen_width // 2), default=screen_width - margin)
        
        ui_top = max((area['position'][1] + area['size'][1] + margin 
                     for area in occupied_areas 
                     if area['position'][1] < screen_height // 2), default=margin)
        
        ui_bottom = min((area['position'][1] - margin 
                        for area in occupied_areas 
                        if area['position'][1] > screen_height // 2), default=screen_height - margin)
        
        return {
            'x': ui_left,
            'y': ui_top,
            'width': max(0, ui_right - ui_left),
            'height': max(0, ui_bottom - ui_top)
        }
    
    def run_japanese_ui_tests(self):
        """全日本語UIテストを実行"""
        print("=== Japanese UI Test Suite ===\n")
        
        # フォントファイル確認
        font_availability = self.check_font_file_availability()
        
        # 日本語テキストエンコーディング
        encoding_results = self.test_japanese_text_encoding()
        
        # UI配置計算
        layout_results, overlaps = self.test_ui_layout_calculations()
        
        # テキスト描画シミュレーション
        rendering_results = self.test_text_rendering_simulation()
        
        # UI応答性
        responsiveness_results = self.test_ui_responsiveness()
        
        # 結果サマリー
        print(f"\n=== Japanese UI Test Summary ===")
        print(f"Font files found: {len(font_availability)}")
        print(f"Text encoding tests: {len(encoding_results)} categories")
        print(f"UI layout elements: {len(layout_results)}")
        print(f"UI overlaps: {len(overlaps)}")
        print(f"Text rendering tests: {len(rendering_results)}")
        print(f"Responsive design tests: {len(responsiveness_results)} screen sizes")
        
        # 成功率計算
        successful_encodings = sum(1 for r in encoding_results if r.get('encoding_success', True))
        successful_layouts = sum(1 for r in layout_results if r['within_screen'])
        successful_renderings = sum(1 for r in rendering_results if r['fits_in_area'])
        
        print(f"\nSuccess rates:")
        print(f"  Text encoding: {successful_encodings}/{len(encoding_results)} ({successful_encodings/len(encoding_results)*100:.1f}%)")
        print(f"  UI layout: {successful_layouts}/{len(layout_results)} ({successful_layouts/len(layout_results)*100:.1f}%)")
        print(f"  Text rendering: {successful_renderings}/{len(rendering_results)} ({successful_renderings/len(rendering_results)*100:.1f}%)")
        
        return {
            'font_availability': font_availability,
            'encoding_results': encoding_results,
            'layout_results': layout_results,
            'ui_overlaps': overlaps,
            'rendering_results': rendering_results,
            'responsiveness_results': responsiveness_results,
            'summary': {
                'font_files_found': len(font_availability),
                'encoding_success_rate': successful_encodings / len(encoding_results),
                'layout_success_rate': successful_layouts / len(layout_results),
                'rendering_success_rate': successful_renderings / len(rendering_results),
                'ui_overlaps_count': len(overlaps)
            }
        }


def main():
    """メイン実行関数"""
    try:
        tester = JapaneseUITester()
        results = tester.run_japanese_ui_tests()
        
        # 結果を保存
        with open('tech_demos/japanese_ui_test_results.json', 'w', encoding='utf-8') as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        
        print(f"\n✓ Japanese UI test complete! Results saved to tech_demos/japanese_ui_test_results.json")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()