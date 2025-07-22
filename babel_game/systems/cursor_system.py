"""
カーソル・入力システム
Cursor and Input System
"""

import pyxel
from config.game_config import GameConfig
from core.event_manager import event_manager
from typing import Optional, Tuple


class CursorSystem:
    """カーソルと入力を管理するクラス"""
    
    def __init__(self):
        self.mouse_x = 0
        self.mouse_y = 0
        self.grid_x = 0
        self.grid_y = 0
        self.grid_system = None  # GridSystemへの参照（後で設定）
        
        # カーソル状態
        self.cursor_visible = True
        self.cursor_color = GameConfig.COLOR_HIGHLIGHT
        
        # 選択状態
        self.selected_tool = "cursor"  # cursor, build, destroy, etc.
        self.selected_building = None
        self.selected_building_size = (1, 1)  # (width, height)
        
        # クリック状態
        self.left_click_pressed = False
        self.right_click_pressed = False
        self.left_click_held = False
        self.right_click_held = False
    
    def initialize(self):
        """カーソルシステムを初期化"""
        pass
    
    def set_grid_system(self, grid_system):
        """GridSystemへの参照を設定"""
        self.grid_system = grid_system
    
    def update(self):
        """カーソルシステムを更新"""
        # マウス座標更新
        self.mouse_x = pyxel.mouse_x
        self.mouse_y = pyxel.mouse_y
        
        # グリッド座標更新
        if self.grid_system:
            self.grid_x, self.grid_y = self.grid_system.screen_to_grid(self.mouse_x, self.mouse_y)
        
        # クリック状態更新
        self._update_click_state()
    
    def draw(self):
        """カーソルを描画"""
        if not self.cursor_visible:
            return
        
        # グリッドカーソル描画
        if self.grid_system and self.grid_system.is_valid_grid_position(self.grid_x, self.grid_y):
            screen_x, screen_y = self.grid_system.grid_to_screen(self.grid_x, self.grid_y)
            screen_x += self.grid_system.camera_x
            screen_y += self.grid_system.camera_y
            
            # カーソルハイライト描画
            self._draw_cursor_highlight(screen_x, screen_y)
        
        # マウスカーソル描画（デバッグ用）
        if pyxel.btn(pyxel.KEY_F1):  # デバッグモード時のみ
            pyxel.circb(self.mouse_x, self.mouse_y, 3, self.cursor_color)
    
    def handle_input(self):
        """入力処理"""
        # ツール切り替え
        if pyxel.btnp(pyxel.KEY_C):
            self.selected_tool = "cursor"
        elif pyxel.btnp(pyxel.KEY_B):
            self.selected_tool = "build"
        elif pyxel.btnp(pyxel.KEY_R):
            self.selected_tool = "destroy"
        
        # クリック処理
        if self.left_click_pressed:
            self._handle_left_click()
        
        if self.right_click_pressed:
            self._handle_right_click()
    
    def _update_click_state(self):
        """クリック状態を更新"""
        # 左クリック
        current_left = pyxel.btn(pyxel.MOUSE_BUTTON_LEFT)
        self.left_click_pressed = current_left and not self.left_click_held
        self.left_click_held = current_left
        
        # 右クリック
        current_right = pyxel.btn(pyxel.MOUSE_BUTTON_RIGHT)
        self.right_click_pressed = current_right and not self.right_click_held
        self.right_click_held = current_right
    
    def _handle_left_click(self):
        """左クリック処理"""
        if not self.grid_system or not self.grid_system.is_valid_grid_position(self.grid_x, self.grid_y):
            return
        
        # ツールに応じた処理
        if self.selected_tool == "cursor":
            # 選択ツール
            event_manager.emit_event("cell_selected", self.grid_x, self.grid_y)
        elif self.selected_tool == "build":
            # 建設ツール
            event_manager.emit_event("build_requested", self.grid_x, self.grid_y, self.selected_building)
        elif self.selected_tool == "destroy":
            # 破壊ツール
            event_manager.emit_event("destroy_requested", self.grid_x, self.grid_y)
    
    def _handle_right_click(self):
        """右クリック処理"""
        if not self.grid_system or not self.grid_system.is_valid_grid_position(self.grid_x, self.grid_y):
            return
        
        # 右クリックメニューまたは情報表示
        event_manager.emit_event("cell_info_requested", self.grid_x, self.grid_y)
    
    def _draw_cursor_highlight(self, screen_x, screen_y):
        """カーソルハイライトを描画"""
        # 建物サイズに合わせた描画
        if self.selected_tool == "build" and self.selected_building:
            self._draw_building_cursor(screen_x, screen_y)
        else:
            self._draw_single_cell_cursor(screen_x, screen_y)
    
    def _draw_single_cell_cursor(self, screen_x, screen_y):
        """1セル分のカーソルを描画"""
        half_width = self.grid_system.cell_size // 2
        half_height = self.grid_system.cell_size // 4
        
        # ツールに応じた色
        color = self._get_cursor_color()
        
        # 菱形の枠線を描画
        points = [
            (screen_x, screen_y - half_height),           # 上
            (screen_x + half_width, screen_y),            # 右
            (screen_x, screen_y + half_height),           # 下
            (screen_x - half_width, screen_y)             # 左
        ]
        
        # 枠線描画
        for i in range(4):
            next_i = (i + 1) % 4
            pyxel.line(points[i][0], points[i][1], 
                      points[next_i][0], points[next_i][1], color)
        
        # 選択したセルを半透明でハイライト（代替として点描画）
        if self.selected_tool in ["build", "destroy"]:
            # 中心点を描画
            pyxel.pset(screen_x, screen_y, color)
    
    def _draw_building_cursor(self, screen_x, screen_y):
        """建物サイズに合わせたカーソルを描画"""
        width, height = self.selected_building_size
        
        # 各セルの枠線を描画
        for dy in range(height):
            for dx in range(width):
                cell_x = self.grid_x + dx
                cell_y = self.grid_y + dy
                
                if self.grid_system and self.grid_system.is_valid_grid_position(cell_x, cell_y):
                    cell_screen_x, cell_screen_y = self.grid_system.grid_to_screen(cell_x, cell_y)
                    cell_screen_x += self.grid_system.camera_x
                    cell_screen_y += self.grid_system.camera_y
                    
                    # 配置可能かチェック
                    can_place = self._can_place_building_at(self.grid_x, self.grid_y, width, height)
                    cursor_color = GameConfig.COLOR_GRASS if can_place else 8  # 緑色 or 赤色
                    
                    self._draw_cell_outline(cell_screen_x, cell_screen_y, cursor_color)
    
    def _draw_cell_outline(self, screen_x, screen_y, color):
        """セルの輪郭を描画"""
        half_width = self.grid_system.cell_size // 2
        half_height = self.grid_system.cell_size // 4
        
        # 菱形の頂点
        points = [
            (screen_x, screen_y - half_height),           # 上
            (screen_x + half_width, screen_y),            # 右
            (screen_x, screen_y + half_height),           # 下
            (screen_x - half_width, screen_y)             # 左
        ]
        
        # 菱形の枠線を描画
        for i in range(4):
            next_i = (i + 1) % 4
            pyxel.line(points[i][0], points[i][1], points[next_i][0], points[next_i][1], color)
    
    def _can_place_building_at(self, start_x, start_y, width, height) -> bool:
        """建物が配置可能かチェック"""
        # 簡易チェック（実際の配置可能性は BuildingManager が判定）
        if not self.grid_system:
            return False
        
        for dy in range(height):
            for dx in range(width):
                cell_x = start_x + dx
                cell_y = start_y + dy
                if not self.grid_system.is_valid_grid_position(cell_x, cell_y):
                    return False
        
        return True
    
    def _get_cursor_color(self):
        """カーソルの色を取得"""
        color_map = {
            "cursor": GameConfig.COLOR_TEXT,      # 白
            "build": GameConfig.COLOR_GRASS,      # 緑
            "destroy": GameConfig.COLOR_HIGHLIGHT # 赤
        }
        return color_map.get(self.selected_tool, GameConfig.COLOR_TEXT)
    
    def get_cursor_position(self):
        """カーソル位置を取得"""
        return (self.mouse_x, self.mouse_y)
    
    def get_grid_position(self):
        """グリッド位置を取得"""
        return (self.grid_x, self.grid_y)
    
    def set_selected_building(self, building_type, building_size=(1, 1)):
        """選択中の建物を設定"""
        self.selected_building = building_type
        self.selected_building_size = building_size
        self.selected_tool = "build" if building_type else "cursor"
    
    def get_selected_tool(self):
        """選択中のツールを取得"""
        return self.selected_tool
    
    def set_cursor_visible(self, visible):
        """カーソル表示状態を設定"""
        self.cursor_visible = visible