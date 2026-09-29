#!/usr/bin/env python3
"""
技術検証デモ1: アセット分析とパフォーマンス予測

目的:
- 既存PNGファイルの分析
- ファイルサイズとメモリ使用量の予測
- .pyxres形式への変換効果の試算
"""

import os
import time
from pathlib import Path
from PIL import Image
import json


class AssetAnalyzer:
    def __init__(self):
        self.results = {}
        
    def analyze_png_files(self, directory="assets/tiles"):
        """PNGファイルを分析"""
        print(f"=== PNG File Analysis: {directory} ===")
        
        png_files = list(Path(directory).glob("*.png"))
        if not png_files:
            print(f"No PNG files found in {directory}")
            return
        
        print(f"Found {len(png_files)} PNG files")
        
        total_file_size = 0
        total_pixel_count = 0
        total_load_time = 0
        files_analyzed = 0
        
        results = []
        
        for png_file in png_files:
            try:
                # ファイル情報
                file_size = os.path.getsize(png_file) / 1024  # KB
                
                # 画像読み込み時間測定
                start_time = time.time()
                img = Image.open(png_file)
                img.load()
                load_time = time.time() - start_time
                
                # 画像情報
                width, height = img.size
                mode = img.mode
                pixel_count = width * height
                
                # 透過チャンネルの確認
                has_alpha = mode in ('RGBA', 'LA') or 'transparency' in img.info
                
                result = {
                    'file': png_file.name,
                    'file_size_kb': file_size,
                    'width': width,
                    'height': height,
                    'mode': mode,
                    'has_alpha': has_alpha,
                    'pixel_count': pixel_count,
                    'load_time': load_time,
                    'bytes_per_pixel': file_size * 1024 / pixel_count if pixel_count > 0 else 0
                }
                
                results.append(result)
                
                total_file_size += file_size
                total_pixel_count += pixel_count
                total_load_time += load_time
                files_analyzed += 1
                
                print(f"✓ {png_file.name}: {width}x{height} {mode}, {file_size:.1f}KB, {load_time:.4f}s")
                
            except Exception as e:
                print(f"✗ Error analyzing {png_file.name}: {e}")
        
        # サマリー
        if files_analyzed > 0:
            avg_load_time = total_load_time / files_analyzed
            avg_file_size = total_file_size / files_analyzed
            avg_pixel_count = total_pixel_count / files_analyzed
            
            print(f"\n--- PNG Analysis Summary ---")
            print(f"Files analyzed: {files_analyzed}")
            print(f"Total file size: {total_file_size:.1f}KB")
            print(f"Average file size: {avg_file_size:.1f}KB")
            print(f"Average load time: {avg_load_time:.4f}s")
            print(f"Total pixels: {total_pixel_count:,}")
            print(f"Average pixels: {avg_pixel_count:.0f}")
            print(f"Loading speed: {total_file_size/max(total_load_time, 0.001):.1f} KB/s")
        
        return results
    
    def predict_pyxres_performance(self, png_results):
        """pyxres形式への変換効果を予測"""
        print(f"\n=== .pyxres Performance Prediction ===")
        
        if not png_results:
            print("No PNG results to analyze")
            return
        
        # 予測計算
        total_pixels = sum(r['pixel_count'] for r in png_results)
        total_png_size = sum(r['file_size_kb'] for r in png_results)
        
        # Pyxelの画像バンクサイズ (256x256 = 65536 pixels per bank)
        pixels_per_bank = 256 * 256
        estimated_banks = (total_pixels + pixels_per_bank - 1) // pixels_per_bank
        
        # 1ピクセル = 1バイト (8bit color index) と仮定
        estimated_pyxres_size = total_pixels / 1024  # KB
        
        # 圧縮効果予測 (pyxresは非圧縮と仮定)
        compression_ratio = total_png_size / max(estimated_pyxres_size, 1)
        
        print(f"Total PNG size: {total_png_size:.1f}KB")
        print(f"Estimated .pyxres size: {estimated_pyxres_size:.1f}KB")
        print(f"Size ratio (PNG/pyxres): {compression_ratio:.2f}x")
        print(f"Estimated banks needed: {estimated_banks}")
        print(f"Total pixels: {total_pixels:,}")
        print(f"Pixels per bank: {pixels_per_bank:,}")
        
        # メモリ使用量予測
        estimated_memory_mb = (estimated_banks * pixels_per_bank) / 1024 / 1024
        print(f"Estimated memory usage: {estimated_memory_mb:.1f}MB")
        
        # 読み込み時間予測 (仮定: pyxresはPNGより2-3倍高速)
        total_png_load_time = sum(r['load_time'] for r in png_results)
        estimated_pyxres_load_time = total_png_load_time / 2.5
        
        print(f"Total PNG load time: {total_png_load_time:.3f}s")
        print(f"Estimated .pyxres load time: {estimated_pyxres_load_time:.3f}s")
        print(f"Estimated speedup: {total_png_load_time/max(estimated_pyxres_load_time, 0.001):.1f}x")
        
        # 目標との比較
        print(f"\n--- Target Comparison ---")
        target_memory = 100  # MB
        target_load_time = 5  # seconds
        
        print(f"Memory target: {target_memory}MB")
        print(f"Memory estimate: {estimated_memory_mb:.1f}MB {'✓' if estimated_memory_mb <= target_memory else '✗'}")
        
        print(f"Load time target: {target_load_time}s")
        print(f"Load time estimate: {estimated_pyxres_load_time:.3f}s {'✓' if estimated_pyxres_load_time <= target_load_time else '✗'}")
        
        return {
            'estimated_banks': estimated_banks,
            'estimated_memory_mb': estimated_memory_mb,
            'estimated_load_time': estimated_pyxres_load_time,
            'compression_ratio': compression_ratio
        }
    
    def analyze_sprite_distribution(self, png_results):
        """スプライトサイズ分布を分析"""
        print(f"\n=== Sprite Size Distribution Analysis ===")
        
        if not png_results:
            return
        
        size_counts = {}
        size_totals = {}
        
        for result in png_results:
            size_key = f"{result['width']}x{result['height']}"
            
            if size_key not in size_counts:
                size_counts[size_key] = 0
                size_totals[size_key] = 0
            
            size_counts[size_key] += 1
            size_totals[size_key] += result['file_size_kb']
        
        print("Sprite sizes found:")
        for size_key in sorted(size_counts.keys()):
            count = size_counts[size_key]
            total_size = size_totals[size_key]
            avg_size = total_size / count
            
            print(f"  {size_key}: {count} files, {total_size:.1f}KB total, {avg_size:.1f}KB avg")
        
        # アニメーション検出の試み
        potential_animations = self.detect_potential_animations(png_results)
        if potential_animations:
            print(f"\nPotential animations detected:")
            for base_name, frames in potential_animations.items():
                print(f"  {base_name}: {len(frames)} frames")
    
    def detect_potential_animations(self, png_results):
        """ファイル名からアニメーションを検出"""
        animations = {}
        
        for result in png_results:
            filename = result['file']
            
            # -数字.png パターンを検索
            if '-' in filename:
                base_name = filename.split('-')[0]
                
                if base_name not in animations:
                    animations[base_name] = []
                
                animations[base_name].append(filename)
        
        # 2フレーム以上のもののみ返す
        return {k: v for k, v in animations.items() if len(v) > 1}
    
    def save_analysis_results(self, results, filename="tech_demos/asset_analysis.json"):
        """分析結果をJSONで保存"""
        try:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(results, f, ensure_ascii=False, indent=2)
            
            print(f"\n✓ Analysis results saved to {filename}")
            
        except Exception as e:
            print(f"✗ Failed to save results: {e}")
    
    def run_analysis(self):
        """全分析を実行"""
        print("=== Asset Performance Analysis ===\n")
        
        # PNG分析
        png_results = self.analyze_png_files()
        
        if png_results:
            # パフォーマンス予測
            predictions = self.predict_pyxres_performance(png_results)
            
            # スプライト分布分析
            self.analyze_sprite_distribution(png_results)
            
            # 結果保存
            analysis_results = {
                'png_files': png_results,
                'predictions': predictions,
                'summary': {
                    'total_files': len(png_results),
                    'total_size_kb': sum(r['file_size_kb'] for r in png_results),
                    'total_pixels': sum(r['pixel_count'] for r in png_results),
                    'analysis_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
            self.save_analysis_results(analysis_results)
        
        print(f"\n✓ Asset analysis complete!")


def main():
    """メイン実行関数"""
    try:
        analyzer = AssetAnalyzer()
        analyzer.run_analysis()
        
    except Exception as e:
        print(f"Analysis failed: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()