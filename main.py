# File: main.py
from flask import Flask, request, jsonify
import os
import asyncio

# Yeh line abhi error degi, lekin hum agli files bana kar isay theek kar denge.
from agent.agent_core import SuperAgent
from tools.tool_registry import get_all_tools

# Flask app initialize karna
app = Flask(__name__)

# Agent ko global scope mein initialize karna
agent = SuperAgent()
tools = get_all_tools()
agent.register_tools(tools)

@app.route('/')
def home():
    return "<h1>Super-Agent is alive!</h1><p>Send POST requests to /ask</p>", 200

@app.route('/ask', methods=['POST'])
def ask_agent():
    data = request.get_json()
    if not data or 'prompt' not in data:
        return jsonify({"error": "Request must be JSON with a 'prompt' key."}), 400

    user_prompt = data['prompt']
    
    try:
        # Agent ke async function ko Flask ke sync context mein chalana
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(agent.process_request(user_prompt))
        loop.close()
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
