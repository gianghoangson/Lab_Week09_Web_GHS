import os
from sqlmodel import create_engine, Session
from fastapi import Depends
from typing import Annotated

# 1. Khai báo chuỗi kết nối PostgreSQL
# Cấu trúc: postgresql+psycopg://username:password@host:port/database_name
# Nếu không có biến môi trường, mặc định sẽ dùng chuỗi kết nối local của bài Lab
default_url = "postgresql+psycopg://app_user:son14032006@localhost:5432/app_db"
DATABASE_URL = os.getenv("DATABASE_URL", default_url)

# 2. Tạo Engine (Cỗ máy kết nối với Database)
# echo=True để in các câu lệnh SQL ra terminal (giúp dễ debug)
engine = create_engine(DATABASE_URL, echo=True)

# 3. Hàm tạo Session (Phiên làm việc cho mỗi request)
def get_session():
    with Session(engine) as session:
        yield session

# 4. Dependency Injection cho FastAPI
# Giúp tái sử dụng code gọn gàng hơn ở các file API sau này
SessionDep = Annotated[Session, Depends(get_session)]