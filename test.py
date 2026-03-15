import psycopg2
import os

conn = psycopg2.connect(
    dbname="route_pyramid",
    user="postgres",
    password='jadynrocks',
    host="localhost",
    port="5432"
)
print("Connected!")
conn.close()