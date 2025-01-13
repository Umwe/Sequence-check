import pyodbc

class SQLServerConnector:
    _instance = None  # Singleton instance

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SQLServerConnector, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.server_name = "RWNEWMISSVR\\RATDB"  # Replace with your server name
        self.connection = None

    def connect(self, database_name):
        """
        Connect to the specified database.
        """
        try:
            connection_string = (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={self.server_name};"
                f"DATABASE={database_name};"
                f"Trusted_Connection=yes;"
            )
            self.connection = pyodbc.connect(connection_string)
            print(f"Connected to database: {database_name}")
        except pyodbc.Error as e:
            print(f"Error connecting to database {database_name}: {e}")
        return self.connection
