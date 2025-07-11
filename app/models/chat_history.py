import mysql.connector
from mysql.connector import Error
from app.config import Config
from datetime import datetime
import logging

def create_chat_history_table():
    try:
        connection = mysql.connector.connect(**Config.DB_CONFIG)
        cursor = connection.cursor()
        
        # First create the table if it doesn't exist
        query = """
        CREATE TABLE IF NOT EXISTS chat_history (
            id INT AUTO_INCREMENT PRIMARY KEY,
            session_id VARCHAR(255) NOT NULL,
            user_message TEXT NOT NULL,
            bot_response TEXT NOT NULL,
            product_context TEXT,
            product_links TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            INDEX (session_id)
        )
        """
        cursor.execute(query)
        
        # Check if product_links column exists
        cursor.execute("SHOW COLUMNS FROM chat_history LIKE 'product_links'")
        if not cursor.fetchone():
            # Add product_links column if it doesn't exist
            cursor.execute("ALTER TABLE chat_history ADD COLUMN product_links TEXT AFTER product_context")
        
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Error as e:
        print(f"Error creating/updating chat history table: {e}")
        return False

def update_table_structure():
    """Update the table structure to add new columns if needed"""
    try:
        connection = mysql.connector.connect(**Config.DB_CONFIG)
        cursor = connection.cursor()
        
        # Check if product_links column exists
        cursor.execute("SHOW COLUMNS FROM chat_history LIKE 'product_links'")
        if not cursor.fetchone():
            # Add product_links column if it doesn't exist
            cursor.execute("ALTER TABLE chat_history ADD COLUMN product_links TEXT AFTER product_context")
            print("Added product_links column to chat_history table")
        
        connection.commit()
        cursor.close()
        connection.close()
        return True
    except Error as e:
        print(f"Error updating table structure: {e}")
        return False

def save_chat_history(session_id, user_message, bot_response, product_context=None, product_links=None):
    try:
        connection = mysql.connector.connect(**Config.DB_CONFIG)
        cursor = connection.cursor()
        
        query = """
        INSERT INTO chat_history (session_id, user_message, bot_response, product_context, product_links)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(query, (session_id, user_message, bot_response, product_context, product_links))
        connection.commit()
        
        cursor.close()
        connection.close()
        return True
    except Error as e:
        print(f"Error saving chat history: {e}")
        return False

def get_chat_history(session_id, limit=10):
    try:
        connection = mysql.connector.connect(**Config.DB_CONFIG)
        cursor = connection.cursor(dictionary=True)
        
        query = """
        SELECT user_message, bot_response, product_links, created_at
        FROM chat_history
        WHERE session_id = %s
        ORDER BY created_at DESC
        LIMIT %s
        """
        cursor.execute(query, (session_id, limit))
        history = cursor.fetchall()
        
        cursor.close()
        connection.close()
        return history
    except Error as e:
        print(f"Error fetching chat history: {e}")
        return None

def clear_chat_history(session_id):
    """Clear all chat history for a given session ID"""
    try:
        conn = mysql.connector.connect(**Config.DB_CONFIG)
        cursor = conn.cursor()
        
        query = "DELETE FROM chat_history WHERE session_id = %s"
        cursor.execute(query, (session_id,))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return True
    except Exception as e:
        logging.error(f"Error clearing chat history: {str(e)}")
        return False 