"""
住民データモデル
Citizen Data Model
"""

from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import random


class CitizenAge(Enum):
    """住民年齢カテゴリ"""
    CHILD = "child"      # 0-14歳
    ADULT = "adult"      # 15-64歳
    ELDERLY = "elderly"  # 65歳以上


class CitizenJob(Enum):
    """住民職業"""
    UNEMPLOYED = "unemployed"  # 無職
    FARMER = "farmer"          # 農業
    FACTORY_WORKER = "factory_worker"  # 工場労働者
    SHOP_KEEPER = "shop_keeper"        # 商店主
    OFFICE_WORKER = "office_worker"    # 事務員
    TEACHER = "teacher"                # 教師
    DOCTOR = "doctor"                  # 医師
    GOVERNMENT = "government"          # 公務員


@dataclass
class CitizenNeeds:
    """住民ニーズ"""
    food: float = 50.0       # 食料（0-100）
    shelter: float = 50.0    # 住居（0-100）
    work: float = 50.0       # 仕事（0-100）
    education: float = 50.0  # 教育（0-100）
    health: float = 50.0     # 健康（0-100）
    recreation: float = 50.0 # 娯楽（0-100）
    
    def get_overall_satisfaction(self) -> float:
        """総合満足度を計算"""
        return (self.food + self.shelter + self.work + 
                self.education + self.health + self.recreation) / 6


class Citizen:
    """住民クラス"""
    
    def __init__(self, x: int, y: int, birth_year: int = 1945):
        self.id = self._generate_id()
        self.x = x
        self.y = y
        self.birth_year = birth_year
        self.age = 0
        self.name_family = self._generate_family_name()
        self.name_given = self._generate_given_name()
        
        # 基本属性
        self.job = CitizenJob.UNEMPLOYED
        self.income = 0
        self.education_level = 0  # 0-100
        self.health = 100.0
        self.happiness = 50.0
        
        # ニーズ
        self.needs = CitizenNeeds()
        
        # 位置・移動
        self.home_x = x
        self.home_y = y
        self.work_x = None
        self.work_y = None
        self.target_x = x
        self.target_y = y
        self.moving = False
        
        # 家族関係
        self.family_id = None
        self.spouse_id = None
        self.children_ids = []
        self.parent_ids = []
        
        # 行動状態
        self.current_activity = "home"  # home, work, shopping, recreation
        self.activity_timer = 0
        
    def _generate_id(self) -> str:
        """ユニークIDを生成"""
        return f"citizen_{random.randint(100000, 999999)}"
    
    def _generate_family_name(self) -> str:
        """戦後日本の一般的な姓を生成"""
        family_names = [
            "田中", "佐藤", "鈴木", "高橋", "渡辺", "伊藤", "山本", "中村",
            "小林", "加藤", "吉田", "山田", "佐々木", "山口", "松本", "井上",
            "木村", "林", "斎藤", "清水", "山崎", "森", "阿部", "池田",
            "橋本", "山下", "石川", "中島", "前田", "藤田"
        ]
        return random.choice(family_names)
    
    def _generate_given_name(self) -> str:
        """戦後世代の一般的な名前を生成"""
        male_names = [
            "博", "清", "茂", "実", "誠", "勇", "明", "武", "正", "和夫",
            "一郎", "二郎", "三郎", "太郎", "健", "進", "豊", "隆", "昭", "光男"
        ]
        female_names = [
            "和子", "幸子", "洋子", "美子", "節子", "恵子", "京子", "悦子",
            "みどり", "さくら", "ひろ子", "としこ", "けい子", "まり子", "ゆき",
            "きよ", "はな", "もも", "すみ", "たえ"
        ]
        
        # 50%の確率で男女を決定
        if random.random() < 0.5:
            return random.choice(male_names)
        else:
            return random.choice(female_names)
    
    def get_age_category(self, current_year: int) -> CitizenAge:
        """年齢カテゴリを取得"""
        self.age = current_year - self.birth_year
        if self.age < 15:
            return CitizenAge.CHILD
        elif self.age < 65:
            return CitizenAge.ADULT
        else:
            return CitizenAge.ELDERLY
    
    def get_full_name(self) -> str:
        """フルネームを取得"""
        return f"{self.name_family} {self.name_given}"
    
    def update_needs(self, city_state: Dict):
        """ニーズを更新"""
        # 基本的な減衰
        self.needs.food = max(0, self.needs.food - 2.0)
        self.needs.shelter = max(0, self.needs.shelter - 1.0)
        self.needs.recreation = max(0, self.needs.recreation - 1.5)
        
        # 仕事関連
        if self.job == CitizenJob.UNEMPLOYED:
            self.needs.work = max(0, self.needs.work - 3.0)
        else:
            self.needs.work = min(100, self.needs.work + 2.0)
        
        # 年齢による影響
        age_category = self.get_age_category(city_state.get('current_year', 1945))
        if age_category == CitizenAge.ELDERLY:
            self.needs.health = max(0, self.needs.health - 1.5)
        elif age_category == CitizenAge.CHILD:
            self.needs.education = max(0, self.needs.education - 2.0)
    
    def satisfy_need(self, need_type: str, amount: float):
        """ニーズを満たす"""
        if hasattr(self.needs, need_type):
            current_value = getattr(self.needs, need_type)
            setattr(self.needs, need_type, min(100.0, current_value + amount))
    
    def calculate_happiness(self) -> float:
        """幸福度を計算"""
        satisfaction = self.needs.get_overall_satisfaction()
        
        # 健康の影響
        health_factor = self.health / 100.0
        
        # 収入の影響（基本生活費との比較）
        basic_cost = 50  # 基本生活費
        income_factor = min(1.0, self.income / basic_cost) if basic_cost > 0 else 0
        
        # 総合幸福度計算
        self.happiness = (satisfaction * 0.6 + health_factor * 100 * 0.2 + 
                         income_factor * 100 * 0.2)
        
        return self.happiness
    
    def find_job(self, available_jobs: List[Tuple[CitizenJob, int, int, int]]) -> bool:
        """仕事を探す"""
        if self.job != CitizenJob.UNEMPLOYED:
            return False
        
        age_category = self.get_age_category(1945)  # 仮の年
        if age_category != CitizenAge.ADULT:
            return False
        
        # 利用可能な仕事から選択
        suitable_jobs = []
        for job, x, y, salary in available_jobs:
            # 距離チェック（簡易版）
            distance = abs(self.home_x - x) + abs(self.home_y - y)
            if distance <= 10:  # 通勤可能距離
                suitable_jobs.append((job, x, y, salary))
        
        if suitable_jobs:
            job, x, y, salary = random.choice(suitable_jobs)
            self.job = job
            self.work_x = x
            self.work_y = y
            self.income = salary
            return True
        
        return False
    
    def lose_job(self):
        """失業する"""
        self.job = CitizenJob.UNEMPLOYED
        self.work_x = None
        self.work_y = None
        self.income = 0
    
    def move_to(self, target_x: int, target_y: int):
        """指定位置に移動開始"""
        self.target_x = target_x
        self.target_y = target_y
        self.moving = True
    
    def update_movement(self):
        """移動状態を更新"""
        if not self.moving:
            return
        
        # 簡単な移動アルゴリズム
        if self.x != self.target_x:
            self.x += 1 if self.target_x > self.x else -1
        elif self.y != self.target_y:
            self.y += 1 if self.target_y > self.y else -1
        else:
            self.moving = False
    
    def update_activity(self, current_hour: int):
        """活動状態を更新"""
        self.activity_timer -= 1
        
        if self.activity_timer <= 0:
            # 時間帯による活動決定
            if 6 <= current_hour < 8:  # 朝
                if self.job != CitizenJob.UNEMPLOYED and self.work_x is not None:
                    self.current_activity = "work"
                    self.move_to(self.work_x, self.work_y)
                    self.activity_timer = 480  # 8時間労働
            elif 8 <= current_hour < 16:  # 昼間
                if self.current_activity != "work":
                    self.current_activity = "home"
                    self.move_to(self.home_x, self.home_y)
                    self.activity_timer = 120
            elif 16 <= current_hour < 18:  # 夕方
                if random.random() < 0.3:  # 30%の確率で買い物
                    self.current_activity = "shopping"
                    self.activity_timer = 60
            else:  # 夜
                self.current_activity = "home"
                self.move_to(self.home_x, self.home_y)
                self.activity_timer = 240
    
    def get_status_text(self) -> str:
        """状態テキストを取得"""
        job_names = {
            CitizenJob.UNEMPLOYED: "無職",
            CitizenJob.FARMER: "農業",
            CitizenJob.FACTORY_WORKER: "工場員",
            CitizenJob.SHOP_KEEPER: "商店主",
            CitizenJob.OFFICE_WORKER: "事務員",
            CitizenJob.TEACHER: "教師",
            CitizenJob.DOCTOR: "医師",
            CitizenJob.GOVERNMENT: "公務員"
        }
        
        activity_names = {
            "home": "在宅",
            "work": "労働",
            "shopping": "買い物",
            "recreation": "娯楽"
        }
        
        job_text = job_names.get(self.job, "不明")
        activity_text = activity_names.get(self.current_activity, "不明")
        
        return f"{self.get_full_name()} ({self.age}歳) {job_text} - {activity_text}"
    
    def to_dict(self) -> Dict:
        """辞書形式に変換（セーブ用）"""
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'birth_year': self.birth_year,
            'name_family': self.name_family,
            'name_given': self.name_given,
            'job': self.job.value,
            'income': self.income,
            'education_level': self.education_level,
            'health': self.health,
            'happiness': self.happiness,
            'home_x': self.home_x,
            'home_y': self.home_y,
            'work_x': self.work_x,
            'work_y': self.work_y,
            'family_id': self.family_id,
            'spouse_id': self.spouse_id,
            'children_ids': self.children_ids,
            'parent_ids': self.parent_ids,
            'needs': {
                'food': self.needs.food,
                'shelter': self.needs.shelter,
                'work': self.needs.work,
                'education': self.needs.education,
                'health': self.needs.health,
                'recreation': self.needs.recreation
            }
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Citizen':
        """辞書から住民を復元（ロード用）"""
        citizen = cls(data['x'], data['y'], data['birth_year'])
        citizen.id = data['id']
        citizen.name_family = data['name_family']
        citizen.name_given = data['name_given']
        citizen.job = CitizenJob(data['job'])
        citizen.income = data['income']
        citizen.education_level = data['education_level']
        citizen.health = data['health']
        citizen.happiness = data['happiness']
        citizen.home_x = data['home_x']
        citizen.home_y = data['home_y']
        citizen.work_x = data.get('work_x')
        citizen.work_y = data.get('work_y')
        citizen.family_id = data.get('family_id')
        citizen.spouse_id = data.get('spouse_id')
        citizen.children_ids = data.get('children_ids', [])
        citizen.parent_ids = data.get('parent_ids', [])
        
        # ニーズ復元
        needs_data = data.get('needs', {})
        citizen.needs.food = needs_data.get('food', 50.0)
        citizen.needs.shelter = needs_data.get('shelter', 50.0)
        citizen.needs.work = needs_data.get('work', 50.0)
        citizen.needs.education = needs_data.get('education', 50.0)
        citizen.needs.health = needs_data.get('health', 50.0)
        citizen.needs.recreation = needs_data.get('recreation', 50.0)
        
        return citizen