#!/usr/bin/env python3
"""
戦後日本復興シミュレーション - メインエントリーポイント
Post-War Japan Reconstruction Simulation - Main Entry Point
"""

import pyxel
from core.game_engine import GameEngine


def main():
    """ゲームのメインエントリーポイント"""
    # ゲームエンジンを初期化
    engine = GameEngine()
    
    # Pyxelを初期化
    pyxel.init(800, 600, title="ConcreteIsland", quit_key=pyxel.KEY_Q)
    
    # マウスカーソルを表示
    pyxel.mouse(visible=True)
    
    # ゲームループを開始
    pyxel.run(engine.update, engine.draw)


if __name__ == "__main__":
    main()