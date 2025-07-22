"""
チュートリアルシステム
Tutorial System
"""

from typing import List, Optional, Dict, Any
from core.event_manager import event_manager
from config.game_config import GameConfig
import pyxel


class TutorialStep:
    """チュートリアルステップクラス"""
    
    def __init__(self, step_id: str, title: str, description: str, 
                 trigger_condition: str = "manual", 
                 required_action: str = None,
                 highlight_area: Dict[str, int] = None,
                 skip_condition: str = None):
        self.step_id = step_id
        self.title = title
        self.description = description
        self.trigger_condition = trigger_condition
        self.required_action = required_action
        self.highlight_area = highlight_area or {}
        self.skip_condition = skip_condition
        
        # 状態
        self.completed = False
        self.active = False
        self.skipped = False
        self.progress = 0.0
        
        # UI状態
        self.show_popup = True
        self.popup_x = 0
        self.popup_y = 0
        self.popup_width = 300
        self.popup_height = 120
    
    def activate(self):
        """ステップを開始"""
        self.active = True
        self.completed = False
        self.skipped = False
        self.progress = 0.0
        print(f"チュートリアルステップ開始: {self.title}")
    
    def complete(self):
        """ステップを完了"""
        self.completed = True
        self.active = False
        self.progress = 1.0
        print(f"チュートリアルステップ完了: {self.title}")
    
    def skip(self):
        """ステップをスキップ"""
        self.skipped = True
        self.active = False
        self.progress = 1.0
        print(f"チュートリアルステップスキップ: {self.title}")
    
    def update_progress(self, progress: float):
        """進行状況を更新"""
        self.progress = min(1.0, max(0.0, progress))
        if self.progress >= 1.0:
            self.complete()
    
    def is_finished(self) -> bool:
        """完了またはスキップされたかチェック"""
        return self.completed or self.skipped


class TutorialManager:
    """チュートリアル管理クラス"""
    
    def __init__(self):
        self.steps: List[TutorialStep] = []
        self.current_step_index = 0
        self.tutorial_active = False
        self.tutorial_completed = False
        self.show_tutorial = True
        
        # UI状態
        self.tutorial_ui_visible = True
        self.help_overlay_visible = False
        
        # 統計
        self.start_time = 0
        self.completion_time = 0
        self.steps_completed = 0
        self.steps_skipped = 0
        
        # イベントリスナー登録
        self._register_event_listeners()
        
        # チュートリアルステップを初期化
        self._initialize_tutorial_steps()
    
    def _register_event_listeners(self):
        """イベントリスナーを登録"""
        event_manager.register_listener("tutorial_start", self._on_tutorial_start)
        event_manager.register_listener("tutorial_skip", self._on_tutorial_skip)
        event_manager.register_listener("building_placed", self._on_building_placed)
        event_manager.register_listener("camera_moved", self._on_camera_moved)
        event_manager.register_listener("year_changed", self._on_year_changed)
    
    def _initialize_tutorial_steps(self):
        """チュートリアルステップを初期化"""
        self.steps = [
            TutorialStep(
                step_id="welcome",
                title="戦後復興都市建設へようこそ",
                description="1945年、戦争で破壊された日本の都市を復興させましょう。\nまずは基本的な操作を覚えていきます。",
                trigger_condition="game_start",
                required_action="press_continue"
            ),
            TutorialStep(
                step_id="camera_control",
                title="カメラの操作",
                description="WASDキーでカメラを移動できます。\nZキーでズームイン、Xキーでズームアウトします。\nカメラを少し動かしてみましょう。",
                trigger_condition="manual",
                required_action="move_camera",
                highlight_area={"x": 50, "y": 50, "width": 200, "height": 150}
            ),
            TutorialStep(
                step_id="building_placement",
                title="建物の建設",
                description="右下の建設パレットから建物を選択できます。\n1-7キーでカテゴリを選択し、Q/Eキーで建物を選択。\nまずはバラック住宅を建ててみましょう。",
                trigger_condition="manual",
                required_action="place_building",
                highlight_area={"x": 480, "y": 450, "width": 200, "height": 150}
            ),
            TutorialStep(
                step_id="ui_overview",
                title="UI の理解",
                description="画面上部には日付、資金、人口が表示されます。\n右側には都市の詳細情報が表示されます。\nTabキーで情報パネルの表示/非表示を切り替えられます。",
                trigger_condition="manual",
                required_action="toggle_ui",
                highlight_area={"x": 480, "y": 30, "width": 200, "height": 400}
            ),
            TutorialStep(
                step_id="economy_basics",
                title="経済の基本",
                description="建物の建設には資金が必要です。\n住宅から税収を得て、商業施設で雇用を提供しましょう。\n資源（米、鉄、木材など）も重要な要素です。",
                trigger_condition="manual",
                required_action="understand_economy"
            ),
            TutorialStep(
                step_id="time_progression",
                title="時間の進行",
                description="時間は自動的に進行します。Spaceキーで一時停止できます。\nShift+数字キーで時間の速度を変更できます。\n年月が進むと新しい建物や技術がアンロックされます。",
                trigger_condition="manual",
                required_action="control_time"
            ),
            TutorialStep(
                step_id="tutorial_complete",
                title="チュートリアル完了",
                description="基本的な操作を覚えました！\n戦後の廃墟から繁栄する都市を築き上げましょう。\nF1キーでヘルプを表示できます。",
                trigger_condition="manual",
                required_action="finish_tutorial"
            )
        ]
    
    def start_tutorial(self):
        """チュートリアルを開始"""
        if self.tutorial_completed:
            return
        
        self.tutorial_active = True
        self.current_step_index = 0
        self.start_time = pyxel.frame_count
        self.steps_completed = 0
        self.steps_skipped = 0
        
        # 最初のステップを開始
        if self.steps:
            self.steps[self.current_step_index].activate()
        
        event_manager.emit_event("tutorial_started")
        print("チュートリアル開始")
    
    def update(self, game_state: Dict[str, Any]):
        """チュートリアルを更新"""
        if not self.tutorial_active or self.tutorial_completed:
            return
        
        current_step = self.get_current_step()
        if not current_step:
            return
        
        # 現在のステップの進行状況をチェック
        self._check_step_progress(current_step, game_state)
        
        # ステップが完了したら次に進む
        if current_step.is_finished():
            self._advance_to_next_step()
    
    def _check_step_progress(self, step: TutorialStep, game_state: Dict[str, Any]):
        """ステップの進行状況をチェック"""
        if step.required_action == "press_continue":
            # Continue はユーザーの手動操作を待つ
            pass
        elif step.required_action == "move_camera":
            # カメラが動いたかチェック
            if game_state.get("camera_moved", False):
                step.update_progress(1.0)
        elif step.required_action == "place_building":
            # 建物が配置されたかチェック
            if game_state.get("buildings_placed", 0) > 0:
                step.update_progress(1.0)
        elif step.required_action == "toggle_ui":
            # UIがトグルされたかチェック
            if game_state.get("ui_toggled", False):
                step.update_progress(1.0)
        elif step.required_action == "understand_economy":
            # 経済の理解（建物を2つ以上建設）
            if game_state.get("buildings_placed", 0) >= 2:
                step.update_progress(1.0)
        elif step.required_action == "control_time":
            # 時間制御（一時停止または速度変更）
            if game_state.get("time_controlled", False):
                step.update_progress(1.0)
        elif step.required_action == "finish_tutorial":
            # 最終ステップは自動完了
            step.update_progress(1.0)
    
    def _advance_to_next_step(self):
        """次のステップに進む"""
        current_step = self.get_current_step()
        if current_step:
            if current_step.completed:
                self.steps_completed += 1
            elif current_step.skipped:
                self.steps_skipped += 1
        
        self.current_step_index += 1
        
        if self.current_step_index >= len(self.steps):
            self._complete_tutorial()
        else:
            next_step = self.steps[self.current_step_index]
            next_step.activate()
    
    def _complete_tutorial(self):
        """チュートリアルを完了"""
        self.tutorial_active = False
        self.tutorial_completed = True
        self.completion_time = pyxel.frame_count
        
        event_manager.emit_event("tutorial_completed", {
            "steps_completed": self.steps_completed,
            "steps_skipped": self.steps_skipped,
            "total_time": self.completion_time - self.start_time
        })
        
        print("チュートリアル完了！")
    
    def skip_current_step(self):
        """現在のステップをスキップ"""
        current_step = self.get_current_step()
        if current_step and current_step.active:
            current_step.skip()
    
    def skip_tutorial(self):
        """チュートリアル全体をスキップ"""
        self.tutorial_active = False
        self.tutorial_completed = True
        self.steps_skipped = len(self.steps)
        
        event_manager.emit_event("tutorial_skipped")
        print("チュートリアルをスキップしました")
    
    def get_current_step(self) -> Optional[TutorialStep]:
        """現在のステップを取得"""
        if 0 <= self.current_step_index < len(self.steps):
            return self.steps[self.current_step_index]
        return None
    
    def get_progress(self) -> float:
        """全体の進行状況を取得"""
        if not self.steps:
            return 1.0
        
        completed_steps = sum(1 for step in self.steps if step.is_finished())
        return completed_steps / len(self.steps)
    
    def handle_input(self):
        """入力処理"""
        if not self.tutorial_active:
            return
        
        current_step = self.get_current_step()
        if not current_step:
            return
        
        # Enterキーで次のステップに進む（手動ステップの場合）
        if pyxel.btnp(pyxel.KEY_RETURN):
            if current_step.required_action == "press_continue":
                current_step.complete()
            elif current_step.required_action == "toggle_ui":
                current_step.complete()
            elif current_step.required_action == "understand_economy":
                current_step.complete()
            elif current_step.required_action == "control_time":
                current_step.complete()
            elif current_step.required_action == "finish_tutorial":
                current_step.complete()
        
        # Escキーで現在のステップをスキップ
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.skip_current_step()
        
        # Shift+Escキーでチュートリアル全体をスキップ
        if pyxel.btn(pyxel.KEY_SHIFT) and pyxel.btnp(pyxel.KEY_ESCAPE):
            self.skip_tutorial()
    
    def draw(self):
        """チュートリアルUI を描画"""
        if not self.tutorial_active or not self.tutorial_ui_visible:
            return
        
        current_step = self.get_current_step()
        if not current_step or not current_step.show_popup:
            return
        
        # チュートリアルポップアップの描画
        self._draw_tutorial_popup(current_step)
        
        # ハイライト領域の描画
        if current_step.highlight_area:
            self._draw_highlight_area(current_step.highlight_area)
        
        # プログレスバーの描画
        self._draw_progress_bar()
    
    def _draw_tutorial_popup(self, step: TutorialStep):
        """チュートリアルポップアップを描画"""
        # 背景
        popup_x = step.popup_x or (GameConfig.SCREEN_WIDTH - step.popup_width) // 2
        popup_y = step.popup_y or 100
        
        # 背景とボーダー
        pyxel.rect(popup_x, popup_y, step.popup_width, step.popup_height, GameConfig.COLOR_UI_BG)
        pyxel.rectb(popup_x, popup_y, step.popup_width, step.popup_height, GameConfig.COLOR_TEXT)
        
        # タイトル
        title_y = popup_y + 8
        pyxel.text(popup_x + 8, title_y, step.title, GameConfig.COLOR_HIGHLIGHT)
        
        # 説明文（複数行対応）
        desc_y = title_y + 16
        lines = step.description.split('\n')
        for i, line in enumerate(lines):
            pyxel.text(popup_x + 8, desc_y + i * 10, line, GameConfig.COLOR_TEXT)
        
        # 操作説明
        help_y = popup_y + step.popup_height - 20
        if step.required_action == "press_continue":
            pyxel.text(popup_x + 8, help_y, "Enterキーで続行", GameConfig.COLOR_TEXT)
        else:
            pyxel.text(popup_x + 8, help_y, "Enterキーで次へ | Escキーでスキップ", GameConfig.COLOR_TEXT)
    
    def _draw_highlight_area(self, highlight_area: Dict[str, int]):
        """ハイライト領域を描画"""
        x = highlight_area.get("x", 0)
        y = highlight_area.get("y", 0)
        width = highlight_area.get("width", 100)
        height = highlight_area.get("height", 100)
        
        # 点滅効果
        if (pyxel.frame_count // 30) % 2 == 0:
            pyxel.rectb(x, y, width, height, GameConfig.COLOR_HIGHLIGHT)
            pyxel.rectb(x+1, y+1, width-2, height-2, GameConfig.COLOR_HIGHLIGHT)
    
    def _draw_progress_bar(self):
        """プログレスバーを描画"""
        progress = self.get_progress()
        
        bar_x = 10
        bar_y = GameConfig.SCREEN_HEIGHT - 30
        bar_width = 200
        bar_height = 8
        
        # 背景
        pyxel.rect(bar_x, bar_y, bar_width, bar_height, GameConfig.COLOR_UI_BG)
        pyxel.rectb(bar_x, bar_y, bar_width, bar_height, GameConfig.COLOR_TEXT)
        
        # 進行状況
        progress_width = int(bar_width * progress)
        if progress_width > 0:
            pyxel.rect(bar_x + 1, bar_y + 1, progress_width - 2, bar_height - 2, GameConfig.COLOR_HIGHLIGHT)
        
        # テキスト
        progress_text = f"チュートリアル進行: {int(progress * 100)}%"
        pyxel.text(bar_x, bar_y - 12, progress_text, GameConfig.COLOR_TEXT)
    
    def set_ui_visible(self, visible: bool):
        """チュートリアルUIの表示/非表示を設定"""
        self.tutorial_ui_visible = visible
    
    def is_active(self) -> bool:
        """チュートリアルがアクティブかチェック"""
        return self.tutorial_active and not self.tutorial_completed
    
    def _on_tutorial_start(self):
        """チュートリアル開始イベントハンドラ"""
        self.start_tutorial()
    
    def _on_tutorial_skip(self):
        """チュートリアルスキップイベントハンドラ"""
        self.skip_tutorial()
    
    def _on_building_placed(self, building):
        """建物配置イベントハンドラ"""
        # 建物配置の進行状況を更新
        pass
    
    def _on_camera_moved(self, data):
        """カメラ移動イベントハンドラ"""
        # カメラ移動の進行状況を更新
        pass
    
    def _on_year_changed(self, new_year):
        """年変更イベントハンドラ"""
        # 年代進行の進行状況を更新
        pass
    
    def get_statistics(self) -> Dict[str, Any]:
        """統計情報を取得"""
        return {
            "tutorial_active": self.tutorial_active,
            "tutorial_completed": self.tutorial_completed,
            "current_step": self.current_step_index,
            "total_steps": len(self.steps),
            "progress": self.get_progress(),
            "steps_completed": self.steps_completed,
            "steps_skipped": self.steps_skipped
        }