import pyodbc
import pandas as pd

def connect_to_db(server, database):
    """Establish a connection to the SQL Server database using Windows Authentication."""
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"Trusted_Connection=yes;"
    )
    return pyodbc.connect(connection_string)

def fetch_data(connection, from_date, to_date):
    """Fetch data from the database for the given date range and records starting with PGW."""
    query = f"""
        SELECT cdr_file, date_cdr
        FROM log_daily_load_control_ggsn
        WHERE date_cdr BETWEEN '{from_date}' AND '{to_date}'
        AND cdr_file LIKE 'PGW%'
    """
    return pd.read_sql(query, connection)

def main():
    # Database connection details
    server = "RWNEWMISSVR\\RATDB"
    database = "GGSN_SGSN"

    # Date range for the check
    from_date = "20241001"
    to_date = "20241005"

    # Connect to the database using Windows Authentication
    connection = connect_to_db(server, database)

    try:
        # Fetch data from the database
        data = fetch_data(connection, from_date, to_date)

        # Display results
        if not data.empty:
            print("Files starting with PGW within the date range:")
            print(data)
        else:
            print("No files found starting with PGW within the date range.")

    finally:
        connection.close()

if __name__ == "__main__":
    main()
