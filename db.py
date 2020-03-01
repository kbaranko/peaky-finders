import config 
import psycopg2

conn = psycopg2.connect(database=config.db_name, user=config.user, password=config.password, host="127.0.0.1", port="5432")
print("Database Connected....")
cur = conn.cursor()
cur.execute("CREATE TABLE 24hr_predictions(id serial PRIMARY KEY, datetime CHAR(50), predicted_load INT);")
print("Table Created....")
conn.commit()
conn.close()