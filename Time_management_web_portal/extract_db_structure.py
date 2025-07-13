#!/usr/bin/env python3
"""
Database Structure Extractor for Time Management Portal
"""

import sqlite3
import os

def extract_database_structure():
    db_path = 'Time_Management_Portal_DB.db'
    
    if not os.path.exists(db_path):
        print(f"Database file {db_path} not found!")
        return
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        print("=" * 80)
        print("TIME MANAGEMENT PORTAL - DATABASE STRUCTURE")
        print("=" * 80)
        print()
        
        # Get all tables and views
        cursor.execute("""
            SELECT name, type FROM sqlite_master 
            WHERE type IN ('table', 'view') 
            ORDER BY type, name
        """)
        objects = cursor.fetchall()
        
        print("OVERVIEW:")
        print("-" * 40)
        tables = [name for name, obj_type in objects if obj_type == 'table']
        views = [name for name, obj_type in objects if obj_type == 'view']
        
        print(f"Tables: {len(tables)}")
        for table in tables:
            print(f"  • {table}")
        
        print(f"\nViews: {len(views)}")
        for view in views:
            print(f"  • {view}")
        
        print("\n" + "=" * 80)
        print("DETAILED STRUCTURE")
        print("=" * 80)
        
        # Get detailed structure for each table/view
        for name, obj_type in objects:
            print(f"\n{obj_type.upper()}: {name}")
            print("-" * 60)
            
            # Get CREATE statement
            cursor.execute(f"SELECT sql FROM sqlite_master WHERE name = ?", (name,))
            create_sql = cursor.fetchone()
            if create_sql and create_sql[0]:
                print("CREATE STATEMENT:")
                print(create_sql[0])
                print()
            
            # Get column info for tables
            if obj_type == 'table':
                try:
                    cursor.execute(f'PRAGMA table_info({name})')
                    columns = cursor.fetchall()
                    
                    if columns:
                        print("COLUMNS:")
                        print(f"{'Name':<20} {'Type':<15} {'Null':<8} {'Default':<15} {'PK':<5}")
                        print("-" * 70)
                        
                        for col in columns:
                            cid, col_name, col_type, notnull, default_val, pk = col
                            null_str = "NO" if notnull else "YES"
                            default_str = str(default_val) if default_val is not None else "NULL"
                            pk_str = "YES" if pk else "NO"
                            print(f"{col_name:<20} {col_type:<15} {null_str:<8} {default_str:<15} {pk_str:<5}")
                        
                        print()
                        
                        # Get foreign keys
                        cursor.execute(f'PRAGMA foreign_key_list({name})')
                        foreign_keys = cursor.fetchall()
                        
                        if foreign_keys:
                            print("FOREIGN KEYS:")
                            for fk in foreign_keys:
                                id, seq, table, from_col, to_col, on_update, on_delete, match = fk
                                print(f"  {from_col} -> {table}.{to_col}")
                            print()
                        
                        # Get indexes
                        cursor.execute(f'PRAGMA index_list({name})')
                        indexes = cursor.fetchall()
                        
                        if indexes:
                            print("INDEXES:")
                            for idx in indexes:
                                seq, idx_name, unique, origin, partial = idx
                                unique_str = " (UNIQUE)" if unique else ""
                                print(f"  {idx_name}{unique_str}")
                            print()
                            
                except Exception as e:
                    print(f"Error getting table info: {e}")
                    print()
        
        # Get some sample data counts
        print("\n" + "=" * 80)
        print("DATA SUMMARY")
        print("=" * 80)
        
        for table in tables:
            try:
                cursor.execute(f'SELECT COUNT(*) FROM {table}')
                count = cursor.fetchone()[0]
                print(f"{table:<30} {count:>10} rows")
            except Exception as e:
                print(f"{table:<30} {'ERROR':>10} ({str(e)})")
        
        conn.close()
        print(f"\nDatabase structure extraction completed successfully!")
        
    except Exception as e:
        print(f"Error accessing database: {e}")

if __name__ == "__main__":
    extract_database_structure()
