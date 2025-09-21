# File: main.py (Final Version with Lazy Initialization)
from flask import Flask, request, jsonify
import os
import asyncio
import logging

# Inhein abhi import nahi karenge, function ke andar karenge
# from agent.agent_core import SuperAgent
# from tools.tool_registry import get_all_tools

app = Flask(__name__)

# Agent ko global variable ke taur par rakhein, lekin initialize na karein
agent_instance = None
agent_initialized = False

def initialize_agent_globally():
    """
    Agent ko sirf ek baar initialize karta hai, jab pehli request aati hai.
    """
    global agent_instance, agent_initialized
        
    # Agar pehle se initialized hai to dobara na karein
    if agent_initialized:
        return

    print("First request received. Initializing Super-Agent now...")
    logging.info("First request received. Initializing Super-Agent now...")
        
    # Ab yahan import karein
    from agent.agent_core import SuperAgent
    from tools.tool_registry import get_all_tools

    try:
        # API keys ko check karna
        if not os.getenv("GEMINI_API_KEY") or not os.getenv("GITHUB_TOKEN"):
            raise ConnectionError("API keys are not set in Cloudflare environment variables.")

        agent_instance = SuperAgent()
        tools = get_all_tools()
        agent_instance.register_tools(tools)
        agent_initialized = True
        print("✅ Super-Agent initialized successfully!")
        logging.info("✅ Super-Agent initialized successfully!")
    except Exception as e:
        # Agar initialization fail ho to log karein
        agent_instance = None
        agent_initialized = False
        print(f"❌ CRITICAL: Agent initialization failed: {e}")
        logging.error(f"❌ CRITICAL: Agent initialization failed: {e}", exc_info=True)


@app.before_request
def ensure_agent_is_ready():
    """
    Har request se pehle yeh function chalta hai aur agent ko initialize karta hai.
    """
    initialize_agent_globally()


@app.route('/')
def home():
    return "<h1>Super-Agent is alive!</h1><p>Send POST requests to /ask</p>", 200


@app.route('/ask', methods=['POST'])
def ask_agent():
    if not agent_initialized or not agent_instance:
        return jsonify({"error": "Agent could not be initialized. Check server logs."}), 500

    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Request must be JSON with a 'prompt' key."}), 400

    user_prompt = data['prompt']
        
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(agent_instance.process_request(user_prompt))
        loop.close()
            
        return jsonify(result)
    except Exception as e:
        logging.error(f"Error during request processing: {e}", exc_info=True)
        return jsonify({"error": str(e)}), 500

