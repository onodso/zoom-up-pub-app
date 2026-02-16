"""
Entities モデル — 統一エンティティモデル（1,835ノード）

市区町村(1,741) + 都道府県(47) + 教育委員会(47) を統一管理する。
地理空間が中核 → 地図表示の基盤。
"""
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, func
from database import Base


class Entity(Base):
    """統一エンティティモデル（1,835ノード）"""
    __tablename__ = "entities"

    # 主キー: "M{code}" (municipality) / "P{code}" (prefecture) / "E{code}" (education_board)
    entity_id = Column(String(10), primary_key=True, index=True)
    
    # エンティティ情報
    name = Column(String(100), nullable=False, comment="自治体名・都道府県名・教育委員会名")
    entity_type = Column(String(20), nullable=False, index=True, comment="municipality / prefecture / education_board")
    
    # 都道府県コード（市区町村の場合は親の都道府県、都道府県自身の場合は自分のコード）
    prefecture_code = Column(String(2), index=True, comment="都道府県コード (01-47)")
    
    # 地理情報（地図表示の核心）
    latitude = Column(Float, nullable=True, comment="緯度")
    longitude = Column(Float, nullable=True, comment="経度")
    
    # 基礎データ
    population = Column(Integer, nullable=True, comment="人口")
    fiscal_index = Column(Float, nullable=True, comment="財政力指数")
    official_url = Column(Text, nullable=True, comment="公式サイトURL")
    
    # Activity Index（スコア）
    activity_index = Column(Float, default=0.0, index=True, comment="DX Activity Index (0-100)")
    
    # メタデータ
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # 備考（将来的な拡張用）
    metadata_json = Column(Text, nullable=True, comment="追加メタデータ（JSON形式）")


    def __repr__(self):
        return f"<Entity {self.entity_id} ({self.entity_type}): {self.name}>"
