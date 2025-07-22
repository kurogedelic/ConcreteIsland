#!/usr/bin/env python3
"""
フォント読み込みテスト
Font Loading Test
"""

import pyxel
import os

def test_font():
    pyxel.init(400, 300, title="フォントテスト")
    
    # フォントファイルの存在確認
    font_path = "assets/fonts/umplus_j10r.bdf"
    if not os.path.exists(font_path):
        print(f"フォントファイルが見つかりません: {font_path}")
        return
    
    print(f"フォントファイルを読み込みます: {font_path}")
    
    # ビットマップフォントの読み込み
    try:
        font = pyxel.Font(font_path)
        print("フォントの読み込みに成功しました")
    except Exception as e:
        print(f"フォントの読み込みに失敗しました: {e}")
        return
    
    def update():
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
    
    def draw():
        pyxel.cls(0)
        
        # 標準フォントでテキスト表示
        pyxel.text(10, 10, "Standard Font: Hello World", 7)
        
        # 日本語フォントでテキスト表示
        pyxel.text(10, 30, "日本語フォント: こんにちは世界", 7, font)
        pyxel.text(10, 50, "戦後日本復興シミュレーション", 8, font)
        pyxel.text(10, 70, "1945年 - 終戦からの復興", 11, font)
        pyxel.text(10, 90, "バラック住宅、木造平屋、市営団地", 10, font)
        
        # 各種記号のテスト
        pyxel.text(10, 120, "記号テスト: ¥1,000 人口: 100人", 12, font)
        pyxel.text(10, 140, "満足度: 50% 電力: 100/200", 13, font)
        
        # UI要素のテスト
        pyxel.text(10, 170, "【建設パレット】", 15, font)
        pyxel.text(10, 190, "住宅 | 商業 | 工業 | 公共 | インフラ", 14, font)
        
        # 終了方法
        pyxel.text(10, 250, "Qキーで終了", 6, font)
    
    pyxel.run(update, draw)

if __name__ == "__main__":
    test_font()