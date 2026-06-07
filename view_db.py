import sqlite3

conn = sqlite3.connect("chat_history.db")

cursor = conn.cursor()

cursor.execute("SELECT * FROM chats")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()