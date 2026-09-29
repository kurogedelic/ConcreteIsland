    def _draw_terrain(self):
        """地形を描画（視界カリング対応・高速化）"""
        # 視界内のセルを取得
        visible_cells = self.viewport_culling.get_visible_cells(self.grid_width, self.grid_height)

        # 描画順序を最適化（後ろから前へ）
        optimized_cells = self.viewport_culling.optimize_draw_order(visible_cells)

        for x, y in optimized_cells:
            screen_x, screen_y = self.grid_to_screen(x, y)

            # カメラオフセット適用
            screen_x += self.camera_x
            screen_y += self.camera_y

            terrain_type = self.terrain[y][x]

            # パフォーマンスのため、色付き菱形のみ描画
            color = self._get_terrain_color(terrain_type)
            self._draw_isometric_cell(screen_x, screen_y, color)
