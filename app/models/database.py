import mysql.connector
from mysql.connector import Error
from app.config import Config

def get_db_connection():
    try:
        connection = mysql.connector.connect(**Config.DB_CONFIG)
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

def get_products():
    try:
        connection = mysql.connector.connect(**Config.DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT id, name, description, price, stock_quantity
        FROM products
        WHERE stock_quantity > 0
        """
        cursor.execute(query)
        products = cursor.fetchall()
        
        cursor.close()
        connection.close()
        
        if not products:
            print("Warning: No products found in database")
            return []
            
        return products
    except Error as e:
        print(f"Error fetching products: {str(e)}")
        return None 