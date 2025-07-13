import sqlite3
import sys
import os

print("Starting database structure extraction...")
print(f"Current directory: {os.getcwd()}")
print(f"Python version: {sys.version}")

db_path = 'Time_Management_Portal_DB.db'
print(f"Looking for database at: {db_path}")
print(f"Database exists: {os.path.exists(db_path)}")

if os.path.exists(db_path):
    print(f"Database file size: {os.path.getsize(db_path)} bytes")
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        print("Successfully connected to database!")
        
        # Get all tables and views
        cursor.execute("SELECT name, type FROM sqlite_master WHERE type IN ('table', 'view') ORDER BY type, name")
        objects = cursor.fetchall()
        
        print(f"\nFound {len(objects)} database objects:")
        
        for name, obj_type in objects:
            print(f"  {obj_type}: {name}")
            
            # Get CREATE statement
            cursor.execute("SELECT sql FROM sqlite_master WHERE name = ?", (name,))
            create_sql = cursor.fetchone()
            if create_sql and create_sql[0]:
                print(f"    CREATE: {create_sql[0][:100]}...")
        
        conn.close()
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
else:
    print("Database file not found!")
    print("Files in current directory:")
    for file in os.listdir('.'):
        print(f"  {file}")
