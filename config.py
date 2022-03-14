from dotenv import load_dotenv
import os


load_dotenv()
BOT_TOKEN_API = os.getenv('BOT_TOKEN_API')
POSTGRES_USER = os.getenv('POSTGRES_USER')
POSTGRES_PASSWORD = os.getenv('POSTGRES_PASSWORD')
POSTGRES_DB_NAME = os.getenv('POSTGRES_DB_NAME')
ALL_APTEKI = 'https://allapteki.ru/socket.io/'
POSTGRES_URI = '0.0.0.0'