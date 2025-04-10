import pandas as pd
import mysql.connector
import os


def generate_create_table(table_name, attributes, primary_key):
    columns_def = []
    for attr in attributes:
        col_def = f"{attr} VARCHAR(100) NOT NULL"
        columns_def.append(col_def)

    create_stmt = f"CREATE TABLE {table_name} (\n"
    create_stmt += "  " + "\n, ".join(columns_def)

    if primary_key:
        pk = ",\n PRIMARY KEY (" + ", ".join(f"{key}" for key in primary_key) + ")"
        create_stmt += pk

    create_stmt += "\n);\n"

    return create_stmt


def generate_insert_statements(table_name, df, attributes):
    insert_statements = []
    for _, row in df.iterrows():
        values = []
        for attr in attributes:
            val = str(row[attr]).replace("'", "''")
            values.append(f"'{val}'")
        values_str = ", ".join(values)
        columns_str = ', '.join(attributes)
        stmt = f"INSERT INTO {table_name} ({columns_str}) VALUES ({values_str});"
        insert_statements.append(stmt)
    return insert_statements


def generate_sql_script(df, table_definitions):
    script = ""

    for i, table in enumerate(table_definitions):
        table_name = f"Table_{i+1}"
        attributes = table['attributes']
        primary_key = table['primary_key']

        script += generate_create_table(table_name, attributes, primary_key)

        subset_df = df[attributes].drop_duplicates()
        inserts = generate_insert_statements(table_name, subset_df, attributes)
        script += "\n".join(inserts) + "\n\n"

    return script


def execute_sql_script(
        host: str,
        user: str,
        password: str,
        database: str,
        sql_script: str
        ):

    try:
        connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password
        )
        cursor = connection.cursor()

        cursor.execute(f"CREATE DATABASE {database};")
        cursor.execute(f"USE {database};")

        statements = [stmt.strip() for stmt in sql_script.split(";") if stmt.strip()]
        for stmt in statements:
            cursor.execute(stmt)

        print(f"Database {database} Successfully Created and Populated")

    except mysql.connector.Error as err:
        print(f"MySQL Error: {err}")

    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()


def interactive_sql(host, user, password, database):
    try:
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database,
        )
        cursor = conn.cursor()
        print(f"Connected to Database {database}")

        while True:
            print("Select Choice:")
            print("1. INSERT")
            print("2. UPDATE")
            print("3. DELETE")
            print("4. Custom SQL Query")
            print("5. Show All Tables")
            print("6. View Table")
            print("7. Exit")

            choice = input("Enter Choice 1-7: ").strip()

            if choice == '1':
                table = input("Table name: ")
                columns = input("Enter Columns Separated By Commas: ")
                values = input("Enter Values Separated by Commas: ")
                query = f"INSERT INTO {table} ({columns}) VALUES ({values});"
            elif choice == '2':
                table = input("Table name: ")
                set_clause = input("SET clause (ex. col1=123, col2='value'): ")
                condition = input("WHERE clause (ex. id=1): ")
                query = f"UPDATE {table} SET {set_clause} WHERE {condition};"
            elif choice == '3':
                table = input("Table name: ")
                condition = input("WHERE clause to match rows to delete: ")
                query = f"DELETE FROM {table} WHERE {condition};"
            elif choice == '4':
                query = input("Enter full sql query: ")
        
            elif choice == '5':
                cursor.execute("SHOW TABLES;")
                tables = cursor.fetchall()
                print("\n Tables in the database:")
                for table_name in tables:
                    print(f"- {table_name}")
                continue

            elif choice == '6':
                table = input("Enter Table Name: ")
                query = f"SELECT * FROM {table};"

            elif choice == '7':
                print("Exiting Interactive Mode")
                break

            else:
                print("Invalid Choice")
                continue

            try:
                cursor.execute(query)
                if query.lower().strip().startswith("select"):
                    rows = cursor.fetchall()
                    columns = [desc[0] for desc in cursor.description]
                    print(" | ".join(columns))
                    for row in rows:
                        print(" | ".join(str(col) for col in row))
                else:
                    conn.commit()
                    print("Query successfully executed")
            except mysql.connector.Error as err:
                print(f"SQL Error: {err}")
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
