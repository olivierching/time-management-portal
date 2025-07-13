from dbconnecter import DBConnecter
import os

def extract_to_file():
    """Extract database structure and save to file"""
    
    DATABASE_URL = os.getenv('DATABASE_URL', 'Time_Management_Portal_DB.db')
    
    try:
        db = DBConnecter(DATABASE_URL)
        
        with open('database_structure_output.txt', 'w', encoding='utf-8') as f:
            f.write("TIME MANAGEMENT PORTAL - DATABASE STRUCTURE\n")
            f.write("=" * 60 + "\n\n")
            
            # Get all tables and views
            objects = db.execute_query("""
                SELECT name, type FROM sqlite_master 
                WHERE type IN ('table', 'view') 
                ORDER BY type, name
            """)
            
            f.write("TABLES AND VIEWS:\n")
            f.write("-" * 30 + "\n")
            
            for name, obj_type in objects:
                f.write(f"{obj_type.upper()}: {name}\n")
            
            f.write("\n" + "=" * 60 + "\n")
            f.write("DETAILED STRUCTURE\n")
            f.write("=" * 60 + "\n\n")
            
            # Get detailed structure for each table/view
            for name, obj_type in objects:
                f.write(f"\n{obj_type.upper()}: {name}\n")
                f.write("-" * 40 + "\n")
                
                # Get CREATE statement
                create_statements = db.execute_query(
                    "SELECT sql FROM sqlite_master WHERE name = ?", (name,)
                )
                
                if create_statements and create_statements[0][0]:
                    f.write("CREATE STATEMENT:\n")
                    f.write(create_statements[0][0] + "\n\n")
                
                # Get column info for tables
                if obj_type == 'table':
                    try:
                        columns = db.execute_query(f'PRAGMA table_info({name})')
                        
                        if columns:
                            f.write("COLUMNS:\n")
                            f.write(f"{'Name':<20} {'Type':<15} {'NotNull':<8} {'Default':<12} {'PK':<3}\n")
                            f.write("-" * 60 + "\n")
                            
                            for col in columns:
                                cid, col_name, col_type, notnull, default_val, pk = col
                                null_str = "YES" if notnull else "NO"
                                default_str = str(default_val) if default_val is not None else "NULL"
                                pk_str = "YES" if pk else "NO"
                                f.write(f"{col_name:<20} {col_type:<15} {null_str:<8} {default_str:<12} {pk_str:<3}\n")
                            
                            f.write("\n")
                            
                    except Exception as e:
                        f.write(f"Error getting table info: {e}\n\n")
            
            # Get data counts
            f.write("\n" + "=" * 60 + "\n")
            f.write("DATA SUMMARY\n")
            f.write("=" * 60 + "\n")
            
            tables = [name for name, obj_type in objects if obj_type == 'table']
            for table in tables:
                try:
                    count_result = db.execute_query(f'SELECT COUNT(*) FROM {table}')
                    count = count_result[0][0] if count_result else 0
                    f.write(f"{table:<25} {count:>8} rows\n")
                except Exception as e:
                    f.write(f"{table:<25} {'ERROR':>8}\n")
        
        db.close()
        return "Database structure extracted to 'database_structure_output.txt'"
        
    except Exception as e:
        return f"Error: {e}"

if __name__ == "__main__":
    result = extract_to_file()
    print(result)
