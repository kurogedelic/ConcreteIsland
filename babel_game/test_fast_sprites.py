#!/usr/bin/env python3
"""
高速スプライトシステムのテスト
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from systems.fast_sprite_manager import FastSpriteManager
import time

def test_fast_sprites():
    print('Testing fast sprite system...')
    
    # FastSpriteManagerのテスト
    fsm = FastSpriteManager()
    
    start_time = time.time()
    success = fsm.build_atlas_from_assets()
    build_time = time.time() - start_time
    
    print(f'Atlas build success: {success}')
    print(f'Build time: {build_time:.2f}s')
    
    if success:
        print(f'Sprites in atlas: {len(fsm.atlas.sprite_map)}')
        
        # 最初の10個のスプライトを表示
        sprite_names = list(fsm.atlas.sprite_map.keys())[:10]
        for name in sprite_names:
            info = fsm.atlas.get_sprite_info(name)
            if info:
                print(f'  - {name}: {info["width"]}x{info["height"]} at ({info["x"]},{info["y"]})')
        
        # アトラスファイルサイズ確認
        atlas_path = fsm.atlas_file
        if os.path.exists(atlas_path):
            file_size = os.path.getsize(atlas_path)
            print(f'Atlas file size: {file_size:,} bytes')
        
        # ロードテスト
        print('\nTesting atlas load...')
        fsm2 = FastSpriteManager()
        start_time = time.time()
        load_success = fsm2.load_sprites()
        load_time = time.time() - start_time
        
        print(f'Load success: {load_success}')
        print(f'Load time: {load_time:.2f}s')
        
        if load_success:
            print(f'Loaded sprites: {len(fsm2.atlas.sprite_map)}')
            
            # 比較
            speed_improvement = build_time / load_time if load_time > 0 else float('inf')
            print(f'Speed improvement: {speed_improvement:.1f}x faster')
    
    return success

if __name__ == "__main__":
    test_fast_sprites()