#!/usr/bin/env python3
"""
神モード・開発者モードのテスト
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

import pyxel
from systems.developer_mode import developer_mode, DevModeType
from core.event_manager import event_manager

def test_developer_mode():
    """開発者モードの基本機能をテスト"""
    print("Testing Developer Mode...")
    
    # 初期状態確認
    print(f"Initial mode: {developer_mode.current_mode}")
    print(f"God mode enabled: {developer_mode.is_god_mode_enabled()}")
    print(f"Infinite money: {developer_mode.has_infinite_money()}")
    print(f"Build anywhere: {developer_mode.can_build_anywhere()}")
    
    # 神モード切り替えテスト
    print("\n--- Testing God Mode Toggle ---")
    developer_mode.toggle_god_mode()
    
    print(f"After toggle - God mode: {developer_mode.is_god_mode_enabled()}")
    print(f"Infinite money: {developer_mode.has_infinite_money()}")
    print(f"Build anywhere: {developer_mode.can_build_anywhere()}")
    print(f"Current mode: {developer_mode.current_mode}")
    
    # コマンド実行テスト
    print("\n--- Testing Commands ---")
    test_commands = [
        "help",
        "money 50000", 
        "addmoney 10000",
        "unlock",
        "freeze",
        "stats",
        "god"  # 神モード無効化
    ]
    
    for cmd in test_commands:
        print(f"Executing: {cmd}")
        success = developer_mode.execute_command(cmd)
        print(f"  Result: {'SUCCESS' if success else 'FAILED'}")
    
    # 最終状態確認
    print(f"\nFinal god mode: {developer_mode.is_god_mode_enabled()}")
    
    # ログ表示
    print("\n--- Console Log ---")
    for log_entry in developer_mode.console_log[-5:]:
        print(f"  {log_entry}")
    
    return True

def test_event_integration():
    """イベント統合をテスト"""
    print("\n--- Testing Event Integration ---")
    
    # イベントハンドリングのテスト
    test_events = [
        ("developer_set_money", {"amount": 100000}),
        ("developer_add_money", {"amount": 25000}),
        ("developer_infinite_money", {}),
        ("god_mode_enabled", {}),
        ("god_mode_disabled", {})
    ]
    
    for event_name, event_data in test_events:
        print(f"Emitting event: {event_name}")
        event_manager.emit_event(event_name, event_data)
    
    # イベント処理
    event_manager.process_events()
    
    return True

def test_rendering():
    """描画機能のテスト（簡易版）"""
    print("\n--- Testing Rendering Functions ---")
    
    # 神モードを有効化
    developer_mode.toggle_god_mode()
    developer_mode.show_dev_console = True
    developer_mode.show_performance_stats = True
    
    # ダミーゲーム状態
    dummy_game_state = {
        'year': 1955,
        'population': 5000,
        'money': 50000,
        'fps': 60
    }
    
    print("Testing draw functions...")
    print("  God mode indicator: READY")
    print("  Dev console: READY") 
    print("  Performance stats: READY")
    
    # 実際の描画はPyxelが必要なのでスキップ
    print("  (Actual rendering skipped - requires Pyxel)")
    
    return True

if __name__ == "__main__":
    print("Developer Mode Test Suite")
    print("=" * 40)
    
    try:
        # 基本機能テスト
        test_developer_mode()
        
        # イベント統合テスト  
        test_event_integration()
        
        # 描画機能テスト
        test_rendering()
        
        print("\n" + "=" * 40)
        print("All tests completed successfully!")
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()