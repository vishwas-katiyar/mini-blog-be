import os

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "vishwas")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "mysql+pymysql://sql12763741:LCFyH9TTl8@sql12.freesqldatabase.com:3306/sql12763741")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "helloworld")
    GOFILE_API_TOKEN = '0OEqTp0iDB3Y0JX2LGTPY7d9V6bWZJlS'
    
