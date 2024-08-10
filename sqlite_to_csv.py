# Import libraries
import sqlite3
import csv
import config
import subprocess
import os
from dotenv import load_dotenv


load_dotenv()


# Get tables in a database
def get_tables(db_file):
    db_file = db_file
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type = 'table'")
    rows = cursor.fetchall()
    tables = [row[0] for row in rows]
    return(tables)


# Function to export contents of db table to csv
# Will be useful if we want to migrate data from sqlie DB to postgres
def export_table_to_csv(db_file, table_name, csv_file):
    conn = sqlite3.connect(db_file)
    cursor = conn.cursor()
    cursor.execute(f"SELECT * from {table_name}")
    rows = cursor.fetchall()
    with open(csv_file, "w") as file:
        writer = csv.writer(file)
        writer.writerow([desc[0] for desc in cursor.description])
        writer.writerows(rows)
    conn.close()


# Export csv to remote postgres
def export_csv_to_postgres():
    out_dict = {}
    for t in ["blog", "image", "user", "project"]:
        csv_file = config.base_dir + f"/sqlite_csv_copies/{t}.csv"
        with open(csv_file, "r") as file:
            csv_reader = csv.DictReader(file)
            header = next(csv_reader)
        out_dict[f"{t}"] = ",".join([key for key in header.keys()])
    for t, cols in out_dict.items():
        subprocess.run([
            "psql", os.environ.get("DATABASE_URL"),
            "-c", "\\copy " + f'''"{t}"''' + f"({cols}) FROM '{csv_file}' DELIMITER ',' CSV HEADER"
        ])


# Execute script
if __name__ == "__main__":
    db_file = config.base_dir + "/instance/blog.db"
    tables = get_tables(db_file = db_file)
    for t in tables:
        export_table_to_csv(
            db_file = db_file,
            table_name = t,
            csv_file = config.base_dir + f"/sqlite_csv_copies/{t}.csv"
        )
    export_csv_to_postgres()