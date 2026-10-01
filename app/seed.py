from sqlmodel import Session, select, SQLModel
from app.database import engine
from app.models import Hero, Team, Mission

def main():
    # 1. Tạo các bảng nếu chưa có (create_all)
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # 2. Kiểm tra xem đã có team nào chưa. Nếu có thì dừng lại (để chạy an toàn nhiều lần)
        existing_team = session.exec(select(Team)).first()
        if existing_team:
            print("already seeded")
            return
        
        # 3. Tạo 2 đội (Teams)
        team_avengers = Team(name="Avengers", headquarters="Avengers Tower")
        team_justice = Team(name="Justice League", headquarters="Watchtower")
        
        # 4. Tạo 2 nhiệm vụ (Missions) - Chú ý tên nhiệm vụ để khớp với Checkpoint 8
        mission_sokovia = Mission(title="Battle of Sokovia")
        mission_thanos = Mission(title="Defeat Thanos")
        
        # 5. Tạo ít nhất 5 anh hùng và gán Team, Mission bằng RELATIONSHIPS (không dùng ID)
        hero1 = Hero(name="Iron Man", age=45, secret_name="Tony", team=team_avengers, missions=[mission_sokovia, mission_thanos])
        hero2 = Hero(name="Captain America", age=100, secret_name="Steve", team=team_avengers, missions=[mission_sokovia])
        hero3 = Hero(name="Spider-Man", age=18, secret_name="Peter", team=team_avengers, missions=[mission_thanos])
        hero4 = Hero(name="Batman", age=40, secret_name="Bruce", team=team_justice, missions=[])
        hero5 = Hero(name="Superman", age=35, secret_name="Clark", team=team_justice, missions=[])
        
        # Thêm vào session và lưu xuống DB (SQLModel sẽ tự động xử lý thứ tự thêm)
        session.add(hero1)
        session.add(hero2)
        session.add(hero3)
        session.add(hero4)
        session.add(hero5)
        
        session.commit()
        print("Database seeded successfully!")

if __name__ == "__main__":
    main()