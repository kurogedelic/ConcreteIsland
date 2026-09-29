# モジュラーアーキテクチャ設計書

## 版情報
- **バージョン**: 2.0
- **作成日**: 2025年1月
- **対象**: 戦後日本復興シミュレーション

---

## 1. アーキテクチャ概要

### 1.1 設計原則
- **関心の分離**: 各モジュールは単一責任を持つ
- **疎結合**: モジュール間の依存関係を最小化
- **高凝集**: 関連機能を同一モジュールに集約
- **インターフェース指向**: 明確なAPIを定義

### 1.2 ディレクトリ構造
```
babel_game/
├── main.py                    # エントリーポイント
├── config/                    # 設定ファイル
│   ├── __init__.py
│   ├── game_config.py         # ゲーム設定
│   └── graphics_config.py     # グラフィックス設定
├── core/                      # コアシステム
│   ├── __init__.py
│   ├── game_engine.py         # メインゲームループ
│   ├── event_manager.py       # イベント管理
│   └── time_manager.py        # 時間管理
├── systems/                   # ゲームシステム
│   ├── __init__.py
│   ├── grid_system.py         # グリッド・座標システム
│   ├── cursor_system.py       # カーソル・入力システム
│   ├── building_system.py     # 建物管理システム
│   ├── economy_system.py      # 経済システム
│   ├── population_system.py   # 住民システム
│   └── disaster_system.py     # 災害システム
├── assets/                    # アセット管理
│   ├── __init__.py
│   ├── asset_manager.py       # アセットローダー
│   ├── sprite_manager.py      # スプライト管理
│   └── animation_manager.py   # アニメーション管理
├── ui/                        # ユーザーインターフェース
│   ├── __init__.py
│   ├── ui_manager.py          # UI管理
│   ├── info_panel.py          # 情報パネル
│   ├── build_palette.py       # 建設パレット
│   └── hud.py                 # ヘッドアップディスプレイ
├── entities/                  # ゲームエンティティ
│   ├── __init__.py
│   ├── building.py            # 建物エンティティ
│   ├── citizen.py             # 住民エンティティ
│   └── tile.py                # タイルエンティティ
├── data/                      # ゲームデータ
│   ├── buildings.json         # 建物定義
│   ├── technologies.json      # 技術ツリー
│   └── events.json           # イベントデータ
├── resources/                 # リソースファイル
│   ├── sprites.pyxres         # スプライト
│   ├── ui.pyxres             # UIアセット
│   └── palette.pyxpal        # カラーパレット
├── utils/                     # ユーティリティ
│   ├── __init__.py
│   ├── math_utils.py          # 数学ユーティリティ
│   ├── file_utils.py          # ファイル操作
│   └── debug_utils.py         # デバッグ機能
└── tests/                     # テストコード
    ├── test_grid_system.py
    ├── test_building_system.py
    └── test_asset_manager.py
```

---

## 2. コアシステム

### 2.1 ゲームエンジン (`core/game_engine.py`)

```python
class GameEngine:
    def __init__(self):
        self.systems = {}
        self.running = False
        self.delta_time = 0
        
    def register_system(self, name: str, system):
        """システムを登録"""
        
    def initialize(self):
        """全システムを初期化"""
        
    def update(self, delta_time: float):
        """全システムを更新"""
        
    def render(self):
        """全システムを描画"""
        
    def shutdown(self):
        """リソースを解放"""
```

### 2.2 イベントマネージャー (`core/event_manager.py`)

```python
class EventManager:
    def __init__(self):
        self.listeners = {}
        
    def subscribe(self, event_type: str, callback):
        """イベントリスナーを登録"""
        
    def publish(self, event_type: str, data: dict):
        """イベントを発行"""
        
    def unsubscribe(self, event_type: str, callback):
        """イベントリスナーを削除"""
```

### 2.3 時間管理 (`core/time_manager.py`)

```python
class TimeManager:
    def __init__(self):
        self.game_year = 1945
        self.game_month = 1
        self.game_day = 1
        self.time_scale = 1.0
        self.paused = False
        
    def update(self, delta_time: float):
        """ゲーム時間を進行"""
        
    def pause(self):
        """時間停止"""
        
    def set_speed(self, speed: float):
        """時間倍率設定"""
```

---

## 3. システム層

### 3.1 グリッドシステム (`systems/grid_system.py`)

```python
class GridSystem:
    def __init__(self, width: int, height: int, cell_size: int):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.tiles = {}  # {(x, y): Tile}
        
    def get_tile(self, x: int, y: int) -> Optional[Tile]:
        """タイルを取得"""
        
    def is_valid_position(self, x: int, y: int) -> bool:
        """座標が有効か確認"""
        
    def screen_to_grid(self, screen_x: int, screen_y: int) -> Tuple[int, int]:
        """スクリーン座標をグリッド座標に変換"""
        
    def grid_to_screen(self, grid_x: int, grid_y: int) -> Tuple[int, int]:
        """グリッド座標をスクリーン座標に変換"""
```

### 3.2 建物システム (`systems/building_system.py`)

```python
class BuildingSystem:
    def __init__(self, grid_system: GridSystem):
        self.grid = grid_system
        self.buildings = {}  # {building_id: Building}
        
    def can_place_building(self, building_type: str, x: int, y: int) -> bool:
        """建物配置可能か確認"""
        
    def place_building(self, building_type: str, x: int, y: int) -> Optional[int]:
        """建物を配置"""
        
    def remove_building(self, building_id: int):
        """建物を削除"""
        
    def update_buildings(self, delta_time: float):
        """全建物を更新"""
```

### 3.3 経済システム (`systems/economy_system.py`)

```python
class EconomySystem:
    def __init__(self):
        self.resources = {
            'money': 1000,
            'rice': 100,
            'iron': 50,
            'wood': 200
        }
        
    def can_afford(self, cost: dict) -> bool:
        """コストを支払えるか確認"""
        
    def spend_resources(self, cost: dict) -> bool:
        """リソースを消費"""
        
    def earn_resources(self, income: dict):
        """リソースを獲得"""
        
    def calculate_income(self) -> dict:
        """月間収入を計算"""
```

---

## 4. アセット管理

### 4.1 アセットマネージャー (`assets/asset_manager.py`)

```python
class AssetManager:
    def __init__(self):
        self.loaded_resources = {}
        self.sprite_manager = SpriteManager()
        self.animation_manager = AnimationManager()
        
    def load_resource_file(self, filename: str):
        """Pyxelリソースファイルを読み込み"""
        
    def get_sprite(self, sprite_name: str) -> Optional[Sprite]:
        """スプライトを取得"""
        
    def preload_essential_assets(self):
        """必須アセットを事前読み込み"""
        
    def unload_unused_assets(self):
        """未使用アセットを解放"""
```

### 4.2 スプライトマネージャー (`assets/sprite_manager.py`)

```python
class SpriteManager:
    def __init__(self):
        self.sprites = {}  # {name: SpriteData}
        
    def register_sprite(self, name: str, bank: int, x: int, y: int, w: int, h: int):
        """スプライトを登録"""
        
    def draw_sprite(self, name: str, x: int, y: int, flip_x: bool = False):
        """スプライトを描画"""
        
    def get_sprite_size(self, name: str) -> Tuple[int, int]:
        """スプライトサイズを取得"""
```

---

## 5. ユーザーインターフェース

### 5.1 UIマネージャー (`ui/ui_manager.py`)

```python
class UIManager:
    def __init__(self, event_manager: EventManager):
        self.panels = {}
        self.active_panels = []
        self.event_manager = event_manager
        
    def register_panel(self, name: str, panel: UIPanel):
        """UIパネルを登録"""
        
    def show_panel(self, name: str):
        """パネルを表示"""
        
    def hide_panel(self, name: str):
        """パネルを非表示"""
        
    def update(self, delta_time: float):
        """全パネルを更新"""
        
    def render(self):
        """全パネルを描画"""
```

### 5.2 建設パレット (`ui/build_palette.py`)

```python
class BuildPalette(UIPanel):
    def __init__(self, x: int, y: int):
        super().__init__(x, y)
        self.building_types = []
        self.selected_type = None
        
    def add_building_type(self, building_type: str, icon: str):
        """建物タイプを追加"""
        
    def handle_click(self, x: int, y: int):
        """クリック処理"""
        
    def render(self):
        """パレットを描画"""
```

---

## 6. データ駆動設計

### 6.1 建物定義 (`data/buildings.json`)

```json
{
  "barracks": {
    "name": "バラック住宅",
    "size": [1, 1],
    "cost": {"money": 100, "wood": 10},
    "maintenance": {"money": 5},
    "capacity": 4,
    "unlock_year": 1945,
    "sprite": "barracks_1x1",
    "animation": null
  },
  "wooden_house": {
    "name": "木造住宅",
    "size": [2, 2],
    "cost": {"money": 500, "wood": 50},
    "maintenance": {"money": 20},
    "capacity": 8,
    "unlock_year": 1948,
    "sprite": "wooden_house_2x2",
    "animation": "smoke"
  }
}
```

### 6.2 技術ツリー (`data/technologies.json`)

```json
{
  "basic_construction": {
    "name": "基礎建設",
    "year": 1945,
    "unlocks": ["barracks", "road"],
    "prerequisites": []
  },
  "improved_housing": {
    "name": "住宅改良",
    "year": 1948,
    "unlocks": ["wooden_house"],
    "prerequisites": ["basic_construction"]
  }
}
```

---

## 7. パフォーマンス最適化

### 7.1 遅延読み込み戦略
- **段階的ロード**: 必須アセット → UI → 建物 → 効果音
- **オンデマンド**: 使用時にのみアセット読み込み
- **キャッシュ**: 頻繁に使用するアセットをメモリ保持

### 7.2 描画最適化
- **視界カリング**: 画面外オブジェクトを描画スキップ
- **レベル・オブ・ディテール**: ズームレベルに応じた描画品質
- **バッチ描画**: 同一スプライトをまとめて描画

### 7.3 メモリ管理
- **オブジェクトプール**: 頻繁に生成・削除されるオブジェクトを再利用
- **弱参照**: 循環参照を避ける
- **ガベージコレクション**: 適切なタイミングでメモリ解放

---

## 8. テスト戦略

### 8.1 ユニットテスト
- **各システムの独立テスト**
- **モック使用でシステム間依存を排除**
- **データ駆動テスト**

### 8.2 統合テスト
- **システム間連携のテスト**
- **セーブ/ロード整合性テスト**
- **パフォーマンス回帰テスト**

### 8.3 E2Eテスト
- **実際のゲームプレイシナリオ**
- **UI操作の自動化**
- **長時間実行安定性テスト**

---

*このアーキテクチャは開発の進行に合わせて継続的に見直され、改良されます。*