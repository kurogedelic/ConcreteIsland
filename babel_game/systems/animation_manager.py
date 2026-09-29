"""
アニメーション管理システム
Animation Management System
"""

import pyxel
from typing import Dict, List, Optional, Tuple
from systems.asset_manager import asset_manager


class AnimationFrame:
    """アニメーションフレーム"""
    
    def __init__(self, sprite_name: str, duration: int = 30):
        self.sprite_name = sprite_name
        self.duration = duration  # フレーム数


class Animation:
    """アニメーション"""
    
    def __init__(self, animation_id: str, frames: List[AnimationFrame], loop: bool = True):
        self.animation_id = animation_id
        self.frames = frames
        self.loop = loop
        self.current_frame = 0
        self.frame_counter = 0
        self.playing = True
    
    def update(self):
        """アニメーションを更新"""
        if not self.playing or not self.frames:
            return
        
        self.frame_counter += 1
        current_frame_data = self.frames[self.current_frame]
        
        if self.frame_counter >= current_frame_data.duration:
            self.frame_counter = 0
            self.current_frame += 1
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.playing = False
    
    def get_current_sprite(self) -> str:
        """現在のスプライト名を取得"""
        if not self.frames:
            return ""
        return self.frames[self.current_frame].sprite_name
    
    def reset(self):
        """アニメーションをリセット"""
        self.current_frame = 0
        self.frame_counter = 0
        self.playing = True


class AnimationManager:
    """アニメーション管理クラス"""
    
    def __init__(self):
        self.animations: Dict[str, Animation] = {}
        self.tile_animations: Dict[Tuple[int, int], str] = {}  # (x, y) -> animation_id
        
        # アニメーションを定義
        self._define_animations()
    
    def _define_animations(self):
        """アニメーションを定義"""
        # 水のアニメーション
        water_frames = [
            AnimationFrame("tile_water-1-1", 60),  # 60フレーム (1秒)
            AnimationFrame("tile_water-1-2", 60),  # 60フレーム (1秒)
        ]
        self.animations["water"] = Animation("water", water_frames, loop=True)
        
        # 火のアニメーション（もし複数フレームがあれば）
        fire_frames = [
            AnimationFrame("tile_fire-2-1", 30),
        ]
        self.animations["fire"] = Animation("fire", fire_frames, loop=True)
        
        # 煙のアニメーション（発電所など）
        smoke_frames = [
            AnimationFrame("tile_thermal_power-1-1", 45),
            AnimationFrame("tile_thermal_power-1-2", 45),
            AnimationFrame("tile_thermal_power-1-3", 45),
            AnimationFrame("tile_thermal_power-1-4", 45),
        ]
        self.animations["thermal_power"] = Animation("thermal_power", smoke_frames, loop=True)
        
        # 原子力発電所のアニメーション
        nuclear_frames = [
            AnimationFrame("tile_nuclear_power-1-1", 90),
            AnimationFrame("tile_nuclear_power-1-2", 90),
            AnimationFrame("tile_nuclear_power-1-3", 90),
        ]
        self.animations["nuclear_power"] = Animation("nuclear_power", nuclear_frames, loop=True)
        
        # 石炭発電所のアニメーション
        coal_frames = [
            AnimationFrame("tile_coal_power_plant-3-1", 40),
            AnimationFrame("tile_coal_power_plant-3-2", 40),
            AnimationFrame("tile_coal_power_plant-3-3", 40),
            AnimationFrame("tile_coal_power_plant-3-4", 40),
        ]
        self.animations["coal_power"] = Animation("coal_power", coal_frames, loop=True)
        
        # 小工場のアニメーション
        factory_frames = [
            AnimationFrame("tile_small_factory-1-1", 50),
            AnimationFrame("tile_small_factory-1-2", 50),
        ]
        self.animations["small_factory"] = Animation("small_factory", factory_frames, loop=True)
        
        # 自動車工場のアニメーション
        auto_factory_frames = [
            AnimationFrame("tile_auto_factory-1-1", 60),
            AnimationFrame("tile_auto_factory-1-2", 60),
            AnimationFrame("tile_auto_factory-1-3", 60),
        ]
        self.animations["auto_factory"] = Animation("auto_factory", auto_factory_frames, loop=True)
        
        print(f"Defined {len(self.animations)} animations")
    
    def update(self):
        """全アニメーションを更新"""
        for animation in self.animations.values():
            animation.update()
    
    def get_animated_sprite(self, animation_id: str) -> Optional[str]:
        """アニメーションIDから現在のスプライト名を取得"""
        if animation_id in self.animations:
            return self.animations[animation_id].get_current_sprite()
        return None
    
    def set_tile_animation(self, x: int, y: int, animation_id: str):
        """タイルにアニメーションを設定"""
        if animation_id in self.animations:
            self.tile_animations[(x, y)] = animation_id
    
    def get_tile_animation(self, x: int, y: int) -> Optional[str]:
        """タイルのアニメーションIDを取得"""
        return self.tile_animations.get((x, y))
    
    def get_tile_sprite(self, x: int, y: int) -> Optional[str]:
        """タイルの現在のスプライト名を取得"""
        animation_id = self.get_tile_animation(x, y)
        if animation_id:
            return self.get_animated_sprite(animation_id)
        return None
    
    def remove_tile_animation(self, x: int, y: int):
        """タイルのアニメーションを削除"""
        if (x, y) in self.tile_animations:
            del self.tile_animations[(x, y)]
    
    def has_animation(self, animation_id: str) -> bool:
        """アニメーションが存在するかチェック"""
        return animation_id in self.animations
    
    def get_animation_list(self) -> List[str]:
        """利用可能なアニメーションIDのリストを取得"""
        return list(self.animations.keys())
    
    def reset_animation(self, animation_id: str):
        """アニメーションをリセット"""
        if animation_id in self.animations:
            self.animations[animation_id].reset()
    
    def reset_all_animations(self):
        """全アニメーションをリセット"""
        for animation in self.animations.values():
            animation.reset()


# グローバルアニメーションマネージャーインスタンス
animation_manager = AnimationManager()