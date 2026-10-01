from sqlmodel import Field, Relationship, SQLModel
from typing import Optional

# 1. TEAM MODELS
class TeamBase(SQLModel):
    name: str = Field(index=True, unique=True)
    headquarters: str

class Team(TeamBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    heroes: list["Hero"] = Relationship(back_populates="team")

class TeamCreate(TeamBase):
    pass

class TeamPublic(TeamBase):
    id: int

# 2. HERO MODELS
class HeroBase(SQLModel):
    name: str = Field(index=True)
    age: int | None = Field(default=None)
    team_id: int | None = Field(default=None, foreign_key="team.id")
    power: str | None = None

# Schema dùng khi nhận dữ liệu tạo mới từ user
class HeroCreate(HeroBase):
    secret_name: str

# Schema dùng khi trả dữ liệu về (không có secret_name)
class HeroPublic(HeroBase):
    id: int

# Schema dùng khi update (tất cả các trường đều là tùy chọn)
class HeroUpdate(SQLModel):
    name: str | None = None
    age: int | None = None
    team_id: int | None = None
    secret_name: str | None = None
    power: str | None = None

class TeamUpdate(SQLModel):
    name: str | None = None
    headquarters: str | None = None

# 1. TẠO BẢNG TRUNG GIAN (Đặt phía trên class Hero)
class HeroMissionLink(SQLModel, table=True):
    hero_id: int | None = Field(default=None, foreign_key="hero.id", primary_key=True)
    mission_id: int | None = Field(default=None, foreign_key="mission.id", primary_key=True)

class Hero(HeroBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    team_id: int | None = Field(default=None, foreign_key="team.id")
    
    # Mối quan hệ với bảng Team (từ các phần trước)
    team: Team | None = Relationship(back_populates="heroes")
    
    # Mối quan hệ Many-to-Many với bảng Mission (từ Part 7)
    missions: list["Mission"] = Relationship(back_populates="heroes", link_model=HeroMissionLink)

# 2. TẠO CÁC MODEL CHO MISSION (Đặt ở dưới cùng)
class MissionBase(SQLModel):
    title: str

class Mission(MissionBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    # Liên kết ngược lại với bảng Hero
    heroes: list["Hero"] = Relationship(back_populates="missions", link_model=HeroMissionLink)

class MissionCreate(MissionBase):
    pass

class MissionPublic(MissionBase):
    id: int