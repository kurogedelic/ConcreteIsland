"""
セーブ・ロードシステム
Save/Load System for Game State Persistence
"""

import os
import json
import gzip
import time
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass

from config.game_config import GameConfig
from core.event_manager import event_manager


@dataclass
class SaveMetadata:
    """セーブファイルのメタデータ"""
    version: str
    created_at: datetime
    game_version: str
    save_name: str
    city_name: str
    current_year: int
    current_month: int
    population: int
    money: int
    playtime_seconds: int
    difficulty: str
    
    def to_dict(self) -> Dict[str, Any]:
        """辞書形式に変換"""
        return {
            'version': self.version,
            'created_at': self.created_at.isoformat(),
            'game_version': self.game_version,
            'save_name': self.save_name,
            'city_name': self.city_name,
            'current_year': self.current_year,
            'current_month': self.current_month,
            'population': self.population,
            'money': self.money,
            'playtime_seconds': self.playtime_seconds,
            'difficulty': self.difficulty
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SaveMetadata':
        """辞書からメタデータを復元"""
        return cls(
            version=data['version'],
            created_at=datetime.fromisoformat(data['created_at']),
            game_version=data['game_version'],
            save_name=data['save_name'],
            city_name=data['city_name'],
            current_year=data['current_year'],
            current_month=data['current_month'],
            population=data['population'],
            money=data['money'],
            playtime_seconds=data['playtime_seconds'],
            difficulty=data['difficulty']
        )


class SaveManager:
    """セーブ・ロード管理クラス"""
    
    # セーブデータバージョン
    SAVE_VERSION = "1.0.0"
    GAME_VERSION = "Phase5.3"
    
    def __init__(self):
        # セーブディレクトリ
        self.saves_dir = Path("saves")
        self.saves_dir.mkdir(exist_ok=True)
        
        # 自動セーブ設定
        self.auto_save_enabled = True
        self.auto_save_interval = 300  # 5分間隔
        self.last_auto_save = time.time()
        
        # セーブスロット管理
        self.max_save_slots = 10
        self.current_save_slot = None
        
        # エラーハンドリング
        self.last_save_error = None
        self.last_load_error = None
        
        # パフォーマンス統計
        self.save_stats = {
            'total_saves': 0,
            'total_loads': 0,
            'last_save_time': 0.0,
            'last_load_time': 0.0,
            'last_save_size': 0
        }
        
        # イベントリスナー登録
        self._register_event_listeners()
    
    def _register_event_listeners(self):
        """イベントリスナーを登録"""
        event_manager.register_listener("game_save_requested", self._on_save_requested)
        event_manager.register_listener("game_load_requested", self._on_load_requested)
        event_manager.register_listener("auto_save_triggered", self._on_auto_save)
    
    def create_save_data(self, game_engine) -> Dict[str, Any]:
        """ゲーム状態からセーブデータを作成"""
        try:
            # 基本ゲーム状態
            game_state = {
                'time': {
                    'current_year': game_engine.time_manager.current_year,
                    'current_month': game_engine.time_manager.current_month,
                    'current_day': game_engine.time_manager.current_day,
                    'game_speed': game_engine.time_manager.game_speed,
                    'paused': game_engine.time_manager.paused,
                    'total_elapsed_time': game_engine.time_manager.total_elapsed_time
                },
                
                # 建物データ
                'buildings': [
                    building.to_dict() for building in game_engine.building_manager.buildings
                ],
                
                # 住民データ
                'citizens': [
                    citizen.to_dict() for citizen in game_engine.population_manager.citizens
                ],
                
                # 経済データ
                'economy': {
                    'money': game_engine.economy_manager.economic_data.money,
                    'rice': game_engine.economy_manager.economic_data.rice,
                    'iron': game_engine.economy_manager.economic_data.iron,
                    'wood': game_engine.economy_manager.economic_data.wood,
                    'coal': game_engine.economy_manager.economic_data.coal,
                    'electricity': game_engine.economy_manager.economic_data.electricity,
                    'monthly_income': game_engine.economy_manager.economic_data.monthly_income,
                    'monthly_expenses': game_engine.economy_manager.economic_data.monthly_expenses,
                    'last_settled_month': game_engine.economy_manager.last_settled_month,
                    'last_settled_year': game_engine.economy_manager.last_settled_year,
                    'tax_rate': game_engine.economy_manager.tax_rate,
                    'subsidies_enabled': game_engine.economy_manager.subsidies_enabled
                },
                
                # 技術・研究データ
                'technology': {
                    'current_era': game_engine.technology_manager.current_era.value,
                    'unlocked_buildings': list(game_engine.technology_manager.unlocked_buildings),
                    'research_progress': game_engine.technology_manager.research_progress,
                    'completed_eras': [era.value for era in game_engine.technology_manager.completed_eras]
                },
                
                # グリッド・地形データ
                'grid': {
                    'width': game_engine.grid_system.grid_width,
                    'height': game_engine.grid_system.grid_height,
                    'terrain_data': game_engine.grid_system.terrain_grid,
                    'camera_x': game_engine.grid_system.camera_x,
                    'camera_y': game_engine.grid_system.camera_y,
                    'zoom_level': game_engine.grid_system.zoom_level
                },
                
                # イベント・災害履歴
                'events': {
                    'disaster_history': [
                        {
                            'type': disaster.disaster_type,
                            'year': disaster.year,
                            'affected_area': disaster.affected_area,
                            'damage': disaster.damage_amount
                        } for disaster in game_engine.event_system.disaster_history
                    ],
                    'current_season': game_engine.event_system.current_season.value,
                    'events_enabled': not game_engine.event_system.disasters_disabled
                },
                
                # ゲーム設定
                'settings': {
                    'difficulty': game_engine.difficulty_manager.current_difficulty.value,
                    'debug_mode': game_engine.debug_mode,
                    'japanese_ui': True,  # 常に日本語UI
                },
                
                # 統計データ
                'statistics': {
                    'buildings_built': len(game_engine.building_manager.buildings),
                    'max_population_reached': max(
                        game_engine.population_manager.get_statistics()['total_population'], 
                        0
                    ),
                    'total_money_earned': game_engine.economy_manager.economic_data.money,
                    'disasters_survived': len(game_engine.event_system.disaster_history)
                }
            }
            
            return game_state
            
        except Exception as e:
            self.last_save_error = f"セーブデータ作成エラー: {str(e)}"
            print(f"Error creating save data: {e}")
            return None
    
    def save_game(self, game_engine, save_name: str, slot: int = None) -> bool:
        """ゲームを保存"""
        start_time = time.time()
        
        try:
            # セーブデータ作成
            game_data = self.create_save_data(game_engine)
            if not game_data:
                return False
            
            # メタデータ作成
            pop_stats = game_engine.population_manager.get_statistics()
            economy_stats = game_engine.economy_manager.get_economic_summary()
            
            metadata = SaveMetadata(
                version=self.SAVE_VERSION,
                created_at=datetime.now(),
                game_version=self.GAME_VERSION,
                save_name=save_name,
                city_name=f"戦後復興都市",  # 固定名前
                current_year=game_engine.time_manager.current_year,
                current_month=game_engine.time_manager.current_month,
                population=int(pop_stats['total_population']),
                money=economy_stats['money'],
                playtime_seconds=int(game_engine.time_manager.total_elapsed_time),
                difficulty=game_engine.difficulty_manager.current_difficulty.value
            )
            
            # 完全なセーブデータ
            save_data = {
                'metadata': metadata.to_dict(),
                'game_state': game_data
            }
            
            # ファイル名決定
            if slot is not None:
                filename = f"slot_{slot:02d}.save"
                self.current_save_slot = slot
            else:
                # 自動セーブまたは手動セーブ
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{save_name}_{timestamp}.save"
            
            filepath = self.saves_dir / filename
            
            # JSON → gzip圧縮で保存
            json_data = json.dumps(save_data, ensure_ascii=False, indent=2).encode('utf-8')
            compressed_data = gzip.compress(json_data, compresslevel=6)
            
            # ファイル書き込み
            with open(filepath, 'wb') as f:
                f.write(compressed_data)
            
            # 統計更新
            save_time = time.time() - start_time
            self.save_stats['total_saves'] += 1
            self.save_stats['last_save_time'] = save_time
            self.save_stats['last_save_size'] = len(compressed_data)
            
            print(f"Game saved: {filename} ({len(compressed_data)} bytes, {save_time:.2f}s)")
            
            # イベント発火
            event_manager.emit_event("game_saved", {
                'filename': filename,
                'save_time': save_time,
                'size': len(compressed_data)
            })
            
            self.last_save_error = None
            return True
            
        except Exception as e:
            self.last_save_error = f"セーブエラー: {str(e)}"
            print(f"Save error: {e}")
            return False
    
    def load_game(self, filename: str, game_engine) -> bool:
        """ゲームを読み込み"""
        start_time = time.time()
        
        try:
            filepath = self.saves_dir / filename
            if not filepath.exists():
                self.last_load_error = f"セーブファイルが見つかりません: {filename}"
                return False
            
            # ファイル読み込み
            with open(filepath, 'rb') as f:
                compressed_data = f.read()
            
            # gzip展開
            json_data = gzip.decompress(compressed_data).decode('utf-8')
            save_data = json.loads(json_data)
            
            # バージョンチェック
            metadata = SaveMetadata.from_dict(save_data['metadata'])
            if not self._check_compatibility(metadata):
                return False
            
            game_state = save_data['game_state']
            
            # ゲーム状態復元
            success = self._restore_game_state(game_state, game_engine)
            
            if success:
                load_time = time.time() - start_time
                self.save_stats['total_loads'] += 1
                self.save_stats['last_load_time'] = load_time
                
                print(f"Game loaded: {filename} ({load_time:.2f}s)")
                
                # イベント発火
                event_manager.emit_event("game_loaded", {
                    'filename': filename,
                    'load_time': load_time,
                    'metadata': metadata.to_dict()
                })
                
                self.last_load_error = None
                return True
            else:
                self.last_load_error = "ゲーム状態の復元に失敗しました"
                return False
            
        except Exception as e:
            self.last_load_error = f"ロードエラー: {str(e)}"
            print(f"Load error: {e}")
            return False
    
    def _check_compatibility(self, metadata: SaveMetadata) -> bool:
        """セーブデータの互換性をチェック"""
        # バージョン互換性チェック（簡易版）
        major_version = metadata.version.split('.')[0]
        current_major = self.SAVE_VERSION.split('.')[0]
        
        if major_version != current_major:
            self.last_load_error = f"互換性のないセーブデータバージョン: {metadata.version}"
            return False
        
        return True
    
    def _restore_game_state(self, game_state: Dict[str, Any], game_engine) -> bool:
        """ゲーム状態を復元"""
        try:
            # 時間管理システム復元
            time_data = game_state['time']
            game_engine.time_manager.current_year = time_data['current_year']
            game_engine.time_manager.current_month = time_data['current_month']
            game_engine.time_manager.current_day = time_data.get('current_day', 1)
            game_engine.time_manager.game_speed = time_data.get('game_speed', 1.0)
            game_engine.time_manager.paused = time_data.get('paused', False)
            game_engine.time_manager.total_elapsed_time = time_data.get('total_elapsed_time', 0)
            
            # 建物復元
            game_engine.building_manager.buildings.clear()
            for building_data in game_state['buildings']:
                building = game_engine.building_manager._restore_building_from_dict(
                    building_data, game_engine.time_manager.current_year
                )
                if building:
                    game_engine.building_manager.buildings.append(building)
            
            # 住民復元
            game_engine.population_manager.citizens.clear()
            for citizen_data in game_state['citizens']:
                citizen = game_engine.population_manager._restore_citizen_from_dict(citizen_data)
                if citizen:
                    game_engine.population_manager.citizens.append(citizen)
            
            # 経済データ復元
            economy_data = game_state['economy']
            econ = game_engine.economy_manager.economic_data
            econ.money = economy_data['money']
            econ.rice = economy_data.get('rice', 1000)
            econ.iron = economy_data.get('iron', 500)
            econ.wood = economy_data.get('wood', 800)
            econ.coal = economy_data.get('coal', 300)
            econ.electricity = economy_data.get('electricity', 0)
            econ.monthly_income = economy_data.get('monthly_income', 0)
            econ.monthly_expenses = economy_data.get('monthly_expenses', 0)
            
            # 経済管理システム状態復元
            game_engine.economy_manager.last_settled_month = economy_data.get('last_settled_month', 0)
            game_engine.economy_manager.last_settled_year = economy_data.get('last_settled_year', 1945)
            game_engine.economy_manager.tax_rate = economy_data.get('tax_rate', 0.1)
            game_engine.economy_manager.subsidies_enabled = economy_data.get('subsidies_enabled', True)
            
            # 技術データ復元
            tech_data = game_state['technology']
            game_engine.technology_manager._restore_from_save_data(tech_data)
            
            # グリッド・地形復元
            grid_data = game_state.get('grid', {})
            if 'terrain_data' in grid_data:
                game_engine.grid_system.terrain_grid = grid_data['terrain_data']
            game_engine.grid_system.camera_x = grid_data.get('camera_x', 0)
            game_engine.grid_system.camera_y = grid_data.get('camera_y', 0)
            game_engine.grid_system.zoom_level = grid_data.get('zoom_level', 1.0)
            
            # イベントシステム復元
            events_data = game_state.get('events', {})
            game_engine.event_system._restore_from_save_data(events_data)
            
            # 設定復元
            settings_data = game_state.get('settings', {})
            if 'difficulty' in settings_data:
                game_engine.difficulty_manager._set_difficulty_from_save(settings_data['difficulty'])
            game_engine.debug_mode = settings_data.get('debug_mode', False)
            
            print(f"Game state restored: {len(game_state['buildings'])} buildings, {len(game_state['citizens'])} citizens")
            return True
            
        except Exception as e:
            print(f"Error restoring game state: {e}")
            return False
    
    def get_save_list(self) -> List[Dict[str, Any]]:
        """セーブファイル一覧を取得"""
        save_files = []
        
        for save_file in self.saves_dir.glob("*.save"):
            try:
                # メタデータ読み込み
                with open(save_file, 'rb') as f:
                    compressed_data = f.read()
                
                json_data = gzip.decompress(compressed_data).decode('utf-8')
                save_data = json.loads(json_data)
                
                metadata = SaveMetadata.from_dict(save_data['metadata'])
                
                save_info = {
                    'filename': save_file.name,
                    'metadata': metadata.to_dict(),
                    'file_size': save_file.stat().st_size,
                    'modified_time': datetime.fromtimestamp(save_file.stat().st_mtime)
                }
                
                save_files.append(save_info)
                
            except Exception as e:
                print(f"Error reading save file {save_file}: {e}")
                continue
        
        # 作成日時でソート（新しい順）
        save_files.sort(key=lambda x: x['metadata']['created_at'], reverse=True)
        return save_files
    
    def delete_save(self, filename: str) -> bool:
        """セーブファイルを削除"""
        try:
            filepath = self.saves_dir / filename
            if filepath.exists():
                filepath.unlink()
                print(f"Save file deleted: {filename}")
                return True
            else:
                print(f"Save file not found: {filename}")
                return False
        except Exception as e:
            print(f"Error deleting save file {filename}: {e}")
            return False
    
    def auto_save(self, game_engine) -> bool:
        """自動セーブ実行"""
        if not self.auto_save_enabled:
            return False
        
        current_time = time.time()
        if current_time - self.last_auto_save < self.auto_save_interval:
            return False
        
        # 自動セーブ実行
        success = self.save_game(game_engine, "autosave")
        if success:
            self.last_auto_save = current_time
            
            # 古い自動セーブファイルを削除（最新5個まで保持）
            self._cleanup_auto_saves()
        
        return success
    
    def _cleanup_auto_saves(self):
        """古い自動セーブファイルをクリーンアップ"""
        auto_saves = list(self.saves_dir.glob("autosave_*.save"))
        auto_saves.sort(key=lambda x: x.stat().st_mtime, reverse=True)
        
        # 5個以上ある場合は古いものを削除
        for old_save in auto_saves[5:]:
            try:
                old_save.unlink()
                print(f"Cleanup: deleted old auto-save {old_save.name}")
            except Exception as e:
                print(f"Error deleting old auto-save {old_save.name}: {e}")
    
    def quick_save(self, game_engine) -> bool:
        """クイックセーブ（F5）"""
        return self.save_game(game_engine, "quicksave", slot=0)
    
    def quick_load(self, game_engine) -> bool:
        """クイックロード（F9）"""
        quicksave_files = list(self.saves_dir.glob("slot_00.save"))
        if quicksave_files:
            return self.load_game("slot_00.save", game_engine)
        else:
            print("No quicksave file found")
            return False
    
    def get_save_stats(self) -> Dict[str, Any]:
        """セーブシステムの統計を取得"""
        return {
            **self.save_stats,
            'saves_directory': str(self.saves_dir),
            'auto_save_enabled': self.auto_save_enabled,
            'auto_save_interval': self.auto_save_interval,
            'last_save_error': self.last_save_error,
            'last_load_error': self.last_load_error,
            'total_save_files': len(list(self.saves_dir.glob("*.save")))
        }
    
    def _on_save_requested(self, data):
        """セーブ要求イベントハンドラ"""
        save_name = data.get('save_name', 'manual_save')
        slot = data.get('slot')
        game_engine = data.get('game_engine')
        
        if game_engine:
            self.save_game(game_engine, save_name, slot)
    
    def _on_load_requested(self, data):
        """ロード要求イベントハンドラ"""
        filename = data.get('filename')
        game_engine = data.get('game_engine')
        
        if filename and game_engine:
            self.load_game(filename, game_engine)
    
    def _on_auto_save(self, data):
        """自動セーブイベントハンドラ"""
        game_engine = data.get('game_engine')
        
        if game_engine:
            self.auto_save(game_engine)


# グローバルインスタンス
save_manager = SaveManager()