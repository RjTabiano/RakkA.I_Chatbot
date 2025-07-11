from flask import Blueprint, request, jsonify
from app.models.database import get_products
from app.models.ai_model import initialize_model
from typing import List, Dict, Any
from app.models.chat_history import save_chat_history, get_chat_history, create_chat_history_table, clear_chat_history, update_table_structure
import uuid
import json
from collections.abc import Mapping

# Create a Blueprint for our routes
api = Blueprint('api', __name__)

# Initialize the chat
chat = initialize_model()

# Create chat history table on startup and update structure if needed
create_chat_history_table()
update_table_structure()

@api.route('/chat', methods=['POST'])
def chat_endpoint():
    try:
        data = request.json or {}
        user_message = data.get('message', '')
        session_id = data.get('session_id')
        
        if not user_message:
            return jsonify({'error': 'No message provided'}), 400
            
        if not session_id:
            return jsonify({'error': 'No session ID provided'}), 400

        # Get products from database
        products = get_products()
        if not products:
            print("Error: Failed to fetch products from database")
            return jsonify({'error': 'Failed to fetch products from database'}), 500

        # Create a context with product information
        product_context = "Available products:\n"
        product_links = []
        try:
            for product in products:
                if not isinstance(product, dict):
                    if isinstance(product, Mapping):
                        product = dict(product)
                    else:
                        keys = ['id', 'name', 'description', 'price', 'stock_quantity']
                        product = dict(zip(keys, product))
                product_context += f"- {product['name']}: {product['description']} (Price: ${product['price']}, Stock: {product['stock_quantity']})\n"
                product_links.append({
                    'name': product['name'],
                    'url': f"/product_info/{product['id']}"
                })
        except KeyError as e:
            print(f"Error processing product data: {str(e)}")
            print(f"Product data: {product}")
            return jsonify({'error': 'Invalid product data format'}), 500

        # Combine user message with product context and instructions
        full_prompt = f"""You are a helpful e-commerce assistant. When recommending products, always mention that you can provide direct links to them.

Available products:
{product_context}

User question: {user_message}

Instructions:
1. If the user asks about a specific product, provide a helpful response and mention that you can provide a direct link to the product.
2. If recommending products, explain why they might be suitable and mention that you can provide direct links.
3. Keep responses friendly and professional.
4. Always include product prices and stock information in your response.
5. Only recommend products if the user is specifically asking for recommendations or information about products.
6. For general questions or non-product related queries, provide a helpful response without product recommendations.
"""
        
        try:
            # Generate response using Gemini
            response = chat.send_message(full_prompt)
            
            product_keywords = ['product', 'recommend', 'suggestion', 'looking for', 'price', 'cost', 'buy', 'purchase', 'available', 'stock']
            should_include_links = any(keyword in user_message.lower() for keyword in product_keywords)
            
            if not save_chat_history(
                session_id=session_id,
                user_message=user_message,
                bot_response=response.text,
                product_context=product_context,
                product_links=json.dumps(product_links) if should_include_links else None
            ):
                print(f"Warning: Failed to save chat history for session {session_id}")
            
            return jsonify({
                'response': response.text,
                'products': products,
                'product_links': product_links if should_include_links else []
            })
        except Exception as e:
            print(f"Error generating response: {str(e)}")
            return jsonify({'error': 'Failed to generate response'}), 500

    except Exception as e:
        print(f"Error in chat endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/chat/history/<session_id>', methods=['GET'])
def get_history(session_id):
    try:
        if not session_id:
            return jsonify({'error': 'No session ID provided'}), 400
            
        history = get_chat_history(session_id)
        if history is None:
            return jsonify({'error': 'Failed to fetch chat history'}), 500
            
        return jsonify({
            'history': history
        })
    except Exception as e:
        print(f"Error in history endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/chat/logout', methods=['POST'])
def logout():
    try:
        data = request.json or {}
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'No session ID provided'}), 400
            
        # Clear chat history for this session
        if clear_chat_history(session_id):
            return jsonify({
                'message': 'Chat history cleared successfully'
            })
        else:
            return jsonify({
                'error': 'Failed to clear chat history'
            }), 500
            
    except Exception as e:
        print(f"Error in logout endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

@api.route('/', methods=['GET'])
def home():
    return jsonify({
        'status': 'online',
        'message': 'Chatbot API is running'
    }) 