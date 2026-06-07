import sqlite3

conn = sqlite3.connect(
    "chat_history.db"
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS chats (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_message TEXT,

    bot_response TEXT,

    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP

)
""")

conn.commit()

conn.close()

print("Database created successfully!")