# 実装計画書 - 戦後日本復興シミュレーション 2.0

## 版情報
- **バージョン**: 2.0
- **作成日**: 2025年1月
- **想定期間**: 8週間 (フルタイム換算)
- **マイルストーン**: 4フェーズ

---

## 1. 開発方針

### 1.1 アジャイル開発原則
- **短期イテレーション**: 1週間スプリント
- **継続的統合**: 毎日のビルド・テスト
- **早期フィードバック**: プロトタイプでの検証
- **品質第一**: 各フェーズで完全動作を保証

### 1.2 技術選択理由
- **Pyxel 2.x**: 軽量・高速・クロスプラットフォーム
- **モジュラー設計**: 保守性・拡張性・テスト容易性
- **データ駆動**: 設定変更での迅速な調整
- **.pyxres形式**: Pyxel推奨のパフォーマンス最適化

### 1.3 品質目標
- **起動時間**: 5秒以内
- **フレームレート**: 60 FPS維持
- **メモリ使用量**: 100MB以下
- **クラッシュ率**: 1%以下

---

## 2. フェーズ1: 基盤構築 (2週間)

### 2.1 目標
- モジュラーアーキテクチャの実装
- 新アセット管理システムの構築
- 基本グリッドシステムの実装

### 2.2 マイルストーン
| 項目 | 期限 | 成功基準 |
|------|------|----------|
| プロジェクト構造作成 | Day 1 | 全モジュールディレクトリ作成、import可能 |
| コアシステム実装 | Day 3 | GameEngine, EventManager動作 |
| アセットマネージャー | Day 5 | .pyxres読み込み、スプライト描画 |
| グリッドシステム | Day 7 | 等角投影、座標変換完全動作 |
| 255色パレット対応 | Day 10 | パレット読み込み、色精度向上確認 |
| 統合テスト | Day 14 | 全システム連携、基本描画動作 |

### 2.3 詳細タスク

#### Week 1: アーキテクチャ構築
```python
# Day 1-2: プロジェクト構造
babel_game/
├── main.py                 # ✓ エントリーポイント
├── core/
│   ├── game_engine.py     # ✓ メインループ
│   ├── event_manager.py   # ✓ イベント管理
│   └── time_manager.py    # ✓ 時間管理
├── systems/
│   ├── grid_system.py     # ✓ グリッド・座標
│   └── cursor_system.py   # ✓ 入力処理
└── config/
    └── game_config.py     # ✓ 設定管理

# Day 3-4: コアシステム実装
class GameEngine:
    def initialize(self):     # ✓ システム初期化
    def update(self):         # ✓ フレーム更新
    def render(self):         # ✓ 描画処理
    def shutdown(self):       # ✓ 終了処理

# Day 5-7: アセット管理
class AssetManager:
    def load_pyxres(self):    # ✓ .pyxres読み込み
    def get_sprite(self):     # ✓ スプライト取得
    def draw_sprite(self):    # ✓ 描画処理
```

#### Week 2: グリッド・パレット実装
```python
# Day 8-10: グリッドシステム
class GridSystem:
    def screen_to_grid(self): # ✓ 座標変換
    def grid_to_screen(self): # ✓ 逆変換
    def draw_grid(self):      # ✓ グリッド描画

# Day 11-12: 255色パレット
class PaletteManager:
    def load_palette(self):   # ✓ パレット読み込み
    def apply_colors(self):   # ✓ Pyxelに適用
    def map_colors(self):     # ✓ 色マッピング

# Day 13-14: 統合テスト
- ✓ 全システム統合動作
- ✓ パフォーマンス測定
- ✓ メモリ使用量確認
```

### 2.4 成果物
- **実行可能プロトタイプ**: 基本描画・入力動作
- **アセット変換ツール**: PNG → .pyxres変換
- **テストスイート**: ユニット・統合テスト
- **ドキュメント**: API仕様、使用方法

---

## 3. フェーズ2: ゲームプレイ実装 (3週間)

### 3.1 目標
- 建物配置システム実装
- 住民シミュレーション実装
- 基本的な経済システム実装

### 3.2 マイルストーン
| 項目 | 期限 | 成功基準 |
|------|------|----------|
| 建物配置システム | Day 7 | 全建物タイプ配置・削除可能 |
| 住民システム | Day 14 | 住民生成・移動・ニーズ管理 |
| 経済システム | Day 17 | 収入・支出・資源管理 |
| UI実装 | Day 19 | 情報表示・建設パレット |
| セーブ/ロード | Day 21 | 完全なゲーム状態保存・復元 |

### 3.3 詳細タスク

#### Week 3: 建物システム
```python
# 建物配置
class BuildingSystem:
    def can_place(self):      # ✓ 配置可能判定
    def place_building(self): # ✓ 建物配置
    def remove_building(self): # ✓ 建物削除
    def validate_terrain(self): # ✓ 地形制約確認

# データ駆動建物定義
buildings.json:
  - ✓ 40種類の建物定義
  - ✓ 配置制約・コスト・効果
  - ✓ スプライト・アニメーション情報
```

#### Week 4: 住民システム
```python
class PopulationSystem:
    def create_citizen(self):  # ✓ 住民生成
    def update_citizens(self): # ✓ 住民状態更新
    def calculate_happiness(self): # ✓ 幸福度計算
    def handle_migration(self): # ✓ 移住処理

class Citizen:
    age: int                  # ✓ 年齢
    occupation: str           # ✓ 職業
    happiness: float          # ✓ 幸福度
    needs: Dict[str, float]   # ✓ ニーズ管理
```

#### Week 5: 経済・UI
```python
class EconomySystem:
    def calculate_income(self): # ✓ 収入計算
    def process_expenses(self): # ✓ 支出処理
    def manage_resources(self): # ✓ 資源管理
    def handle_trade(self):     # ✓ 貿易処理

class UIManager:
    def draw_hud(self):        # ✓ ステータス表示
    def draw_build_palette(self): # ✓ 建設パレット
    def draw_info_panel(self): # ✓ 情報パネル
```

### 3.4 成果物
- **プレイアブルプロトタイプ**: 基本ゲームプレイループ
- **建物ライブラリ**: 40種類の建物実装
- **住民AI**: 基本的な需要・供給シミュレーション
- **データファイル**: JSON形式の設定ファイル

---

## 4. フェーズ3: コンテンツ実装 (2週間)

### 3.1 目標
- 全建物・技術ツリー実装
- イベントシステム実装
- チュートリアル実装

### 3.2 マイルストーン
| 項目 | 期限 | 成功基準 |
|------|------|----------|
| 技術ツリー | Day 5 | 年代順技術解放システム |
| イベントシステム | Day 8 | 災害・特需イベント実装 |
| チュートリアル | Day 12 | 新規プレイヤー誘導 |
| コンテンツ実装 | Day 14 | 全建物・全機能実装完了 |

### 3.3 詳細タスク

#### Week 6: 技術・イベント
```python
class TechnologySystem:
    def unlock_technology(self): # ✓ 技術解放
    def check_prerequisites(self): # ✓ 前提条件確認
    def apply_effects(self):     # ✓ 技術効果適用

class EventSystem:
    def trigger_disaster(self):  # ✓ 災害発生
    def handle_special_demand(self): # ✓ 朝鮮戦争特需
    def process_seasons(self):   # ✓ 季節変化
```

#### Week 7: チュートリアル・コンテンツ
```python
class TutorialSystem:
    def show_introduction(self): # ✓ ゲーム紹介
    def guide_building(self):    # ✓ 建設ガイド
    def explain_mechanics(self): # ✓ システム説明

# コンテンツ追加
- ✓ 全建物スプライト (.pyxres形式)
- ✓ BGM・効果音実装
- ✓ アニメーション (煙、人の動き)
```

---

## 5. フェーズ4: ポリッシュ・最適化 (1週間)

### 5.1 目標
- バランス調整
- パフォーマンス最適化
- バグ修正・品質保証

### 5.2 マイルストーン
| 項目 | 期限 | 成功基準 |
|------|------|----------|
| パフォーマンス最適化 | Day 3 | 目標性能達成 |
| バランス調整 | Day 5 | プレイテスト通過 |
| バグ修正 | Day 6 | 致命的バグゼロ |
| リリース準備 | Day 7 | 配布パッケージ完成 |

### 5.3 詳細タスク

#### 最適化項目
```python
# パフォーマンス最適化
- ✓ 描画処理最適化 (視界カリング)
- ✓ メモリ使用量削減 (オブジェクトプール)
- ✓ アセット読み込み高速化
- ✓ ガベージコレクション最適化

# バランス調整
- ✓ 建物コスト・効果バランス
- ✓ 住民幸福度計算調整
- ✓ 経済成長カーブ調整
- ✓ 災害頻度・影響度調整
```

---

## 6. 技術的課題と対策

### 6.1 予想される課題

| 課題 | リスク | 対策 |
|------|--------|------|
| Pyxel .pyxres読み込み性能 | 中 | 段階的読み込み、キャッシュ戦略 |
| 255色パレット変換精度 | 中 | カラーマッピングアルゴリズム改良 |
| 大規模都市でのFPS低下 | 高 | 視界カリング、LOD実装 |
| メモリリーク | 中 | オブジェクトプール、弱参照使用 |
| セーブデータ互換性 | 低 | バージョニング、マイグレーション |

### 6.2 技術検証項目

```python
# Week 1で検証
def verify_pyxres_performance():
    """Pyxel .pyxres読み込み性能検証"""
    start_time = time.time()
    pyxel.load("test_assets.pyxres")
    load_time = time.time() - start_time
    assert load_time < 2.0  # 2秒以内

def verify_255_color_accuracy():
    """255色マッピング精度検証"""
    original = (34, 139, 34)  # 草の色
    mapped = color_mapper.map_color(original)
    distance = color_distance(original, mapped)
    assert distance < 1000  # 距離しきい値

def verify_large_city_performance():
    """大規模都市パフォーマンス検証"""
    city = create_test_city(10000)  # 人口10000人
    fps = measure_fps(city, duration=10)
    assert fps >= 60  # 60FPS維持
```

---

## 7. リソース・体制

### 7.1 開発リソース
- **コア開発**: 1名 (フルタイム)
- **アセット作成**: 0.5名 (パートタイム)
- **テスト・QA**: 0.25名 (パートタイム)
- **合計工数**: 約320時間

### 7.2 開発環境
- **OS**: macOS/Windows/Linux対応
- **Python**: 3.8以上
- **IDE**: VSCode + Python拡張
- **バージョン管理**: Git + GitHub
- **CI/CD**: GitHub Actions

### 7.3 外部ツール
- **Pyxel Editor**: アセット作成・編集
- **GIMP/Photoshop**: PNG画像編集
- **Audacity**: 音声編集
- **Tiled**: マップエディタ (必要に応じて)

---

## 8. 成功指標・KPI

### 8.1 技術KPI
- **起動時間**: 5秒以内 ✓
- **フレームレート**: 60 FPS維持 ✓
- **メモリ使用量**: 100MB以下 ✓
- **ファイルサイズ**: 50MB以下 ✓

### 8.2 品質KPI
- **ユニットテストカバレッジ**: 80%以上
- **統合テスト成功率**: 100%
- **クラッシュ率**: 1%以下
- **メモリリーク**: ゼロ

### 8.3 ユーザビリティKPI
- **チュートリアル完了率**: 80%以上
- **平均プレイ時間**: 60分以上
- **建物配置成功率**: 95%以上

---

## 9. リスク管理

### 9.1 高リスク項目
1. **Pyxel .pyxres性能問題**
   - 影響: 起動時間・メモリ使用量
   - 軽減策: 早期プロトタイプでの検証

2. **255色パレット変換品質**
   - 影響: 視覚品質
   - 軽減策: カラーマッピングアルゴリズム改良

3. **大規模シミュレーション性能**
   - 影響: ゲームプレイ体験
   - 軽減策: 段階的最適化、プロファイリング

### 9.2 緊急時対応
- **Plan B**: 16色パレット + Bank方式への回帰
- **Plan C**: シンプル化 (建物数削減、エフェクト削減)
- **Plan D**: コア機能のみのMVP版リリース

---

## 10. 次期開発計画

### 10.1 v2.1 (メンテナンス)
- バグ修正
- バランス調整
- 軽微な機能追加

### 10.2 v3.0 (大型アップデート)
- マルチプレイヤー対応
- モデキング機能
- 追加シナリオ

---

**この実装計画により、高品質で安定した戦後日本復興シミュレーションゲームを8週間で完成させることを目指します。**