import mysql.connector

def get_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="Root@123",
        database="movie_recommendation_db"
    )