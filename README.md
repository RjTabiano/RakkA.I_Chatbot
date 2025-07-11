# RakkGears AI Chatbot

An AI-powered chatbot for RakkGears e-commerce platform that helps customers find products and get information about them.

## Project Structure
```
RakkA.I/
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── routes.py
│   └── models/
│       ├── ai_model.py
│       └── database.py
├── run.py
├── requirements.txt
└── .env
```

## Setup Instructions

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file based on `.env.example` and fill in your configuration:
```bash
cp .env.example .env
```

4. Update the `.env` file with your:
   - Google API Key for Gemini AI
   - Database credentials
   - Other configuration settings

5. Run the application:
```bash
python run.py
```

The server will start on `http://localhost:5000`

## API Endpoints

- `GET /`: Check if the server is running
- `POST /chat`: Send messages to the chatbot
  ```json
  {
    "message": "What products do you have?"
  }
  ```

## Features

- Product information retrieval
- AI-powered product recommendations
- Real-time stock checking
- Natural language processing for customer queries 