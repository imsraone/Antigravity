import sqlite3
import pandas as pd
from typing import List, Dict, Any

# Global connection for demo purposes (in a real app, manage connection pools properly)
_conn = None

def init_db():
    """Initializes the in-memory database and seeds it with data."""
    global _conn
    _conn = sqlite3.connect(":memory:", check_same_thread=False)
    cursor = _conn.cursor()

    # Create Tables
    cursor.execute("""
        CREATE TABLE Products (
            ProductID INTEGER PRIMARY KEY,
            ProductName TEXT,
            Category TEXT,
            Price REAL
        )
    """)
    
    cursor.execute("""
        CREATE TABLE Customers (
            CustomerID INTEGER PRIMARY KEY,
            Name TEXT,
            Email TEXT,
            Country TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE Sales (
            SaleID INTEGER PRIMARY KEY,
            ProductID INTEGER,
            CustomerID INTEGER,
            Date DATE,
            Quantity INTEGER,
            TotalAmount REAL,
            FOREIGN KEY (ProductID) REFERENCES Products(ProductID),
            FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
        )
    """)

    # Seed Data
    products = [
        (1, "Laptop Pro X", "Electronics", 1200.00),
        (2, "Wireless Earbuds", "Electronics", 150.00),
        (3, "Coffee Maker 3000", "Appliances", 89.99),
        (4, "Ergonomic Chair", "Furniture", 350.50),
        (5, "Gaming Monitor", "Electronics", 450.00)
    ]
    cursor.executemany("INSERT INTO Products VALUES (?,?,?,?)", products)

    customers = [
        (1, "Alice Johnson", "alice@example.com", "USA"),
        (2, "Bob Smith", "bob@example.com", "UK"),
        (3, "Charlie Davis", "charlie@example.com", "Canada"),
        (4, "Diana Prince", "diana@example.com", "USA")
    ]
    cursor.executemany("INSERT INTO Customers VALUES (?,?,?,?)", customers)

    sales = [
        (1, 1, 1, "2023-01-15", 1, 1200.00),
        (2, 2, 2, "2023-01-16", 2, 300.00),
        (3, 3, 3, "2023-02-10", 1, 89.99),
        (4, 4, 1, "2023-03-05", 1, 350.50),
        (5, 5, 4, "2023-04-20", 1, 450.00),
        (6, 1, 2, "2023-05-12", 2, 2400.00) # Bob bought 2 laptops!
    ]
    cursor.executemany("INSERT INTO Sales VALUES (?,?,?,?,?,?)", sales)

    _conn.commit()
    print("Database initialized and seeded.")

def get_schema() -> str:
    """Returns the database schema as a string for the LLM context."""
    return """
    Tables:
    1. Products (ProductID, ProductName, Category, Price)
    2. Customers (CustomerID, Name, Email, Country)
    3. Sales (SaleID, ProductID, CustomerID, Date, Quantity, TotalAmount)
    
    Relationships:
    - Sales.ProductID references Products.ProductID
    - Sales.CustomerID references Customers.CustomerID
    """

def execute_query(query: str) -> pd.DataFrame:
    """Executes a SQL query and returns the results as a Pandas DataFrame."""
    global _conn
    if not _conn:
        init_db()
    
    try:
        # Simple safety check for valid SELECT queries (very basic)
        if not query.strip().upper().startswith("SELECT"):
            raise ValueError("Only SELECT queries are allowed.")
            
        df = pd.read_sql_query(query, _conn)
        return df
    except Exception as e:
        print(f"SQL Execution Error: {e}")
        raise e
