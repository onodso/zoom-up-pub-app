"""
DX進捗データモデル

政府DXダッシュボード（市区町村毎のDX進捗状況）のデータを格納。
前バージョンの MunicipalityMetric に相当するが、
TimescaleDB不要のシンプルな設計にしている。
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, func
from database import Base


class DxProgress(Base):
    """自治体DX進捗データ（政府DXダッシュボードからの実データ）"""
    __tablename__ = "dx_progress"

    id = Column(Integer, primary_key=True, index=True)

    # 時系列対応（変化率計算に必須）
    survey_year = Column(Integer, nullable=False, index=True, comment="調査年度（例: 2024）")

    # 自治体コード（municipalitiesテーブルのcodeとJOIN可能）
    municipality_code = Column(String(6), nullable=False, index=True)
    municipality_name = Column(String(50), nullable=False)

    # DX進捗カテゴリ
    # 例: 'cio_appointed', 'cio_assistant', 'dx_strategy',
    #     'cross_dept_team', 'online_rate', 'security_policy' 等
    category = Column(String(50), nullable=False, index=True)

    # 値（実施=1.0 / 未実施=0.0、または申請率のパーセンテージ 0.0〜100.0）
    value = Column(Float, nullable=True)

    # テキスト値（「実施」「未実施」「検討中」等の原文）
    value_text = Column(String(100), nullable=True)

    # データの出処
    source = Column(String(100), default="gov_dx_dashboard", comment="データ出所")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
