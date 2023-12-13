from pymysql import connections
from config import *


def create_connection():
    return connections.Connection(
        host=customhost,
        port=3306,
        user=customuser,
        password=custompass,
        db=customdb
    )
