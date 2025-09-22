# File: main.py (ULTRA-SIMPLE, BULLETPROOF VERSION)
from flask import Flask, request, jsonify
import os
import logging

# Imports ko yahan le aayein
from agent.agent_core import SuperAgent
from tools.tool_registry import get_all_tools

# Logging setup
logging.basicConfig(level=logging.INFO)

# Flask app initialize karna
app = Flask(__name__)

# Agent ko global variable ke taur par rakhein
agent_instance = None

def initialize_agent_globally():
    """
    Agent ko sirf ek baar initialize karta hai.
    """
    global agent_instance
    if agent_instance is not None:
        return

    logging.info("Attempting to initialize Super-Agent...")
    try:
        if not os.getenv("GEMINI_API_KEY") or not os.getenv("GITHUB_TOKEN"):
            raise ConnectionError("API keys not found in environment variables.")

        agent_instance = SuperAgent()
        tools = get_all_tools()
        agent_instance.register_tools(tools)
        logging.info("✅ Super-Agent initialized successfully!")
    except Exception as e:
        logging.error(f"❌ CRITICAL: Agent initialization failed: {e}", exc_info=True)
        # Yahan error ko raise karein taake logs mein nazar aaye
        raise e

@app.route('/')
def home():
    return "<h1>Super-Agent is alive!</h1>", 200

@app.route('/ask', methods=['POST'])
def ask_agent():
    # Har request par check karein ke agent initialize hua ya nahi
    if agent_instance is None:
        return jsonify({"error": "Agent is not initialized. Check server logs for critical errors."}), 500

    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Request must be JSON with a 'prompt' key."}), 400

    user_prompt = data['prompt']
    
    try:
        # Naya, saada tareeqa agent ko run karne ka
        # Hum ab asyncio istemal nahi kar rahe
        result = agent_instance.agent_executor.invoke({"input": user_prompt})
        final_answer = result.get('output', 'Agent did not provide a final answer.')
        return jsonify({"type": "success", "final_answer": final_answer})
    except Exception as e:
        logging.error(f"Error during request processing: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

# Server ko start karne se pehle agent ko initialize karein
# Yeh Cloudflare ke "Health Check" ke liye zaroori hai
initialize_agent_globally()
