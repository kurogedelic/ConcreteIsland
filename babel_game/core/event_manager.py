"""
イベント管理システム
Event Management System
"""

from typing import Dict, List, Callable, Any


class EventManager:
    """ゲーム内イベントを管理するクラス"""
    
    def __init__(self):
        self._listeners: Dict[str, List[Callable]] = {}
        self._events_queue: List[tuple] = []
    
    def register_listener(self, event_type: str, callback: Callable):
        """イベントリスナーを登録"""
        if event_type not in self._listeners:
            self._listeners[event_type] = []
        self._listeners[event_type].append(callback)
    
    def unregister_listener(self, event_type: str, callback: Callable):
        """イベントリスナーを解除"""
        if event_type in self._listeners:
            if callback in self._listeners[event_type]:
                self._listeners[event_type].remove(callback)
    
    def emit_event(self, event_type: str, *args, **kwargs):
        """イベントを発生させる"""
        self._events_queue.append((event_type, args, kwargs))
    
    def process_events(self):
        """キューに溜まったイベントを処理"""
        while self._events_queue:
            event_type, args, kwargs = self._events_queue.pop(0)
            self._dispatch_event(event_type, *args, **kwargs)
    
    def _dispatch_event(self, event_type: str, *args, **kwargs):
        """イベントをリスナーに配信"""
        if event_type in self._listeners:
            for callback in self._listeners[event_type]:
                try:
                    callback(*args, **kwargs)
                except Exception as e:
                    print(f"Event listener error: {e}")
    
    def clear_all_listeners(self):
        """全てのリスナーをクリア"""
        self._listeners.clear()
        self._events_queue.clear()


# グローバルイベントマネージャーインスタンス
event_manager = EventManager()