import sqlite3

def check_schema():
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("TABLES:")
    for table in tables:
        tname = table[0]
        print(f"\n- {tname}")
        cursor.execute(f"PRAGMA table_info({tname});")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")

if __name__ == '__main__':
    check_schema()
