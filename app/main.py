from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Query
from sqlmodel import SQLModel, select

from app.database import engine, SessionDep
# Import đầy đủ các model và schema cho cả Hero và Team
from app.models import (
    Hero, HeroCreate, HeroPublic, HeroUpdate,
    Team, TeamCreate, TeamPublic, TeamUpdate, Mission, MissionCreate, MissionPublic
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi tạo tất cả các bảng vào database khi server bắt đầu chạy
    SQLModel.metadata.create_all(engine)
    yield

# Khởi tạo ứng dụng FastAPI với lifespan
app = FastAPI(lifespan=lifespan)

@app.get("/")
def read_root():
    return {"Hello": "World"}

# ==========================================
# CÁC ENDPOINT CHO HERO
# ==========================================

@app.post("/heroes", response_model=HeroPublic)
def create_hero(hero_in: HeroCreate, session: SessionDep):
    # Kiểm tra team_id trước khi tạo
    if hero_in.team_id is not None:
        team = session.get(Team, hero_in.team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
            
    hero_db = Hero.model_validate(hero_in)
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)
    return hero_db

# (PART 6) LẤY DANH SÁCH - Cập nhật thêm tính năng Lọc (Filtering) theo name và age
@app.get("/heroes", response_model=list[HeroPublic])
def read_heroes(
    session: SessionDep, 
    offset: int = 0, 
    limit: int = Query(default=100, le=100),
    name: str | None = None,
    age: int | None = None
):
    statement = select(Hero)
    
    # Xây dựng câu lệnh động dựa trên tham số truyền vào
    if name:
        statement = statement.where(Hero.name == name)
    if age:
        statement = statement.where(Hero.age == age)
        
    statement = statement.offset(offset).limit(limit)
    heroes = session.exec(statement).all()
    return heroes

@app.get("/heroes/{hero_id}", response_model=HeroPublic)
def read_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero

@app.patch("/heroes/{hero_id}", response_model=HeroPublic)
def update_hero(hero_id: int, hero_in: HeroUpdate, session: SessionDep):
    hero_db = session.get(Hero, hero_id)
    if not hero_db:
        raise HTTPException(status_code=404, detail="Hero not found")
    
    # Kiểm tra team_id trước khi cập nhật
    if hero_in.team_id is not None:
        team = session.get(Team, hero_in.team_id)
        if not team:
            raise HTTPException(status_code=404, detail="Team not found")
    
    hero_data = hero_in.model_dump(exclude_unset=True)
    for key, value in hero_data.items():
        setattr(hero_db, key, value)
        
    session.add(hero_db)
    session.commit()
    session.refresh(hero_db)
    return hero_db

@app.delete("/heroes/{hero_id}")
def delete_hero(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    session.delete(hero)
    session.commit()
    return {"ok": True}


# ==========================================
# (PART 6) CÁC ENDPOINT CHO TEAM
# ==========================================

@app.post("/teams", response_model=TeamPublic)
def create_team(team_in: TeamCreate, session: SessionDep):
    team_db = Team.model_validate(team_in)
    session.add(team_db)
    session.commit()
    session.refresh(team_db)
    return team_db

@app.get("/teams", response_model=list[TeamPublic])
def read_teams(session: SessionDep, offset: int = 0, limit: int = Query(default=100, le=100)):
    teams = session.exec(select(Team).offset(offset).limit(limit)).all()
    return teams

@app.get("/teams/{team_id}", response_model=TeamPublic)
def read_team(team_id: int, session: SessionDep):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team

@app.patch("/teams/{team_id}", response_model=TeamPublic)
def update_team(team_id: int, team_in: TeamUpdate, session: SessionDep):
    team_db = session.get(Team, team_id)
    if not team_db:
        raise HTTPException(status_code=404, detail="Team not found")
    
    team_data = team_in.model_dump(exclude_unset=True)
    for key, value in team_data.items():
        setattr(team_db, key, value)
        
    session.add(team_db)
    session.commit()
    session.refresh(team_db)
    return team_db

@app.delete("/teams/{team_id}")
def delete_team(team_id: int, session: SessionDep):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    session.delete(team)
    session.commit()
    return {"ok": True}

# ==========================================
# CÁC ENDPOINT CHO MISSION (PART 7)
# ==========================================

# 1. Tạo nhiệm vụ mới (Trả về mã 201 Created)
@app.post("/missions", response_model=MissionPublic, status_code=201)
def create_mission(mission_in: MissionCreate, session: SessionDep):
    mission_db = Mission.model_validate(mission_in)
    session.add(mission_db)
    session.commit()
    session.refresh(mission_db)
    return mission_db

# 2. Gán một anh hùng vào một nhiệm vụ (Trả về mã 204 No Content)
@app.post("/heroes/{hero_id}/missions/{mission_id}", status_code=204)
def assign_hero_to_mission(hero_id: int, mission_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    mission = session.get(Mission, mission_id)
    
    # Báo lỗi 404 nếu không tìm thấy hero hoặc mission
    if not hero or not mission:
        raise HTTPException(status_code=404, detail="Hero or Mission not found")
        
    # Chỉ gán nếu anh hùng chưa có trong nhiệm vụ này (tránh trùng lặp)
    if mission not in hero.missions:
        hero.missions.append(mission)
        session.add(hero)
        session.commit()
        
    return # Mã 204 không cần return body

# 3. Lấy danh sách nhiệm vụ của một anh hùng
@app.get("/heroes/{hero_id}/missions", response_model=list[MissionPublic])
def read_hero_missions(hero_id: int, session: SessionDep):
    hero = session.get(Hero, hero_id)
    if not hero:
        raise HTTPException(status_code=404, detail="Hero not found")
    return hero.missions

@app.get("/teams/{team_id}/heroes", response_model=list[HeroPublic])
def read_team_heroes(team_id: int, session: SessionDep):
    team = session.get(Team, team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team.heroes