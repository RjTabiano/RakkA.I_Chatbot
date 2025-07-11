import google.generativeai as genai
from app.config import Config

def initialize_model():
    genai.configure(api_key=Config.GOOGLE_API_KEY)
    
    generation_config = genai.GenerationConfig(**Config.GENERATION_CONFIG)
    
    # Create the model
    model = genai.GenerativeModel(
        model_name=Config.MODEL_NAME,
        safety_settings=Config.SAFETY_SETTINGS,
        generation_config=generation_config
    )
    
    system_prompt = """You are a helpful e-commerce assistant for RakkGears. Your role is to:
    1. Provide accurate information about products
    2. Help customers find products based on their needs
    3. Answer questions about product specifications, prices, and availability
    4. Maintain a professional and friendly tone
    5. Focus on product-related queries and avoid discussing sensitive topics
    6. Always verify product availability before making recommendations
    7. Be clear about pricing and stock information
    If you're unsure about any information, acknowledge the limitation and suggest contacting customer service."""
    
    chat = model.start_chat(history=[])
    chat.send_message(system_prompt)
    
    return chat 