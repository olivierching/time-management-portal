from dbconnecter import DBConnecter
import os

def extract_database_structure():
    """Extract and display the complete database structure"""
    
    DATABASE_URL = os.getenv('DATABASE_URL', 'Time_Management_Portal_DB.db')
    
    try:
        db = DBConnecter(DATABASE_URL)
        
        # Write output to file instead of print
        output = []
        output.append("=" * 80)
        output.append("TIME MANAGEMENT PORTAL - DATABASE STRUCTURE")
        output.append("=" * 80)
        output.append("")
        
        # Get all tables and views
        objects = db.execute_query("""
            SELECT name, type FROM sqlite_master 
            WHERE type IN ('table', 'view') 
            ORDER BY type, name
        """)
        
        output.append("OVERVIEW:")
        output.append("-" * 40)
        tables = [name for name, obj_type in objects if obj_type == 'table']
        views = [name for name, obj_type in objects if obj_type == 'view']
        
        output.append(f"Tables ({len(tables)}):")
        for table in tables:
            output.append(f"  • {table}")
        
        if views:
            output.append(f"\nViews ({len(views)}):")
            for view in views:
                output.append(f"  • {view}")
        
        output.append("")
        output.append("=" * 80)
        output.append("DETAILED STRUCTURE")
        output.append("=" * 80)
        
        # Get detailed structure for each table/view
        for name, obj_type in objects:
            print(f"\n{obj_type.upper()}: {name}")
            print("-" * 60)
            
            # Get CREATE statement
            create_statements = db.execute_query(
                "SELECT sql FROM sqlite_master WHERE name = ?", (name,)
            )
            
            if create_statements and create_statements[0][0]:
                print("CREATE STATEMENT:")
                print(create_statements[0][0])
                print()
            
            # Get column info for tables
            if obj_type == 'table':
                try:
                    # Get table info using PRAGMA
                    columns = db.execute_query(f'PRAGMA table_info({name})')
                    
                    if columns:
                        print("COLUMNS:")
                        print(f"{'Name':<25} {'Type':<15} {'NotNull':<8} {'Default':<15} {'PK':<5}")
                        print("-" * 75)
                        
                        for col in columns:
                            cid, col_name, col_type, notnull, default_val, pk = col
                            null_str = "YES" if notnull else "NO"
                            default_str = str(default_val) if default_val is not None else "NULL"
                            pk_str = "YES" if pk else "NO"
                            print(f"{col_name:<25} {col_type:<15} {null_str:<8} {default_str:<15} {pk_str:<5}")
                        
                        print()
                        
                        # Get foreign keys
                        foreign_keys = db.execute_query(f'PRAGMA foreign_key_list({name})')
                        
                        if foreign_keys:
                            print("FOREIGN KEYS:")
                            for fk in foreign_keys:
                                id, seq, table, from_col, to_col, on_update, on_delete, match = fk
                                print(f"  {from_col} -> {table}.{to_col}")
                            print()
                        
                        # Get indexes
                        indexes = db.execute_query(f'PRAGMA index_list({name})')
                        
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
        
        # Get data counts
        print("\n" + "=" * 80)
        print("DATA SUMMARY")
        print("=" * 80)
        
        for table in tables:
            try:
                count_result = db.execute_query(f'SELECT COUNT(*) FROM {table}')
                count = count_result[0][0] if count_result else 0
                print(f"{table:<30} {count:>10} rows")
            except Exception as e:
                print(f"{table:<30} {'ERROR':>10} ({str(e)})")
        
        db.close()
        print(f"\nDatabase structure extraction completed successfully!")
        
    except Exception as e:
        print(f"Error accessing database: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    extract_database_structure()
