# File: agent/agent_core.py
# Version 2.1 - Simple & Synchronous

import os
import logging
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain.tools import BaseTool

# Hamara pasandeeda, taiz tareen model
MODEL_NAME = "gemini-1.5-flash-latest"

# Agent ko behtar sochne ke liye hidayat
AGENT_PROMPT_TEMPLATE = """
You are a world-class AI assistant named Super-Agent. Your goal is to complete the user's request by planning and executing steps using the available tools.

TOOLS:
------
You have access to the following tools:
{tools}

INSTRUCTIONS:
-------------
1.  **Think Step-by-Step:** Always break down the user's request into a series of smaller, logical steps.
2.  **Use Tools:** For each step, decide if you need to use a tool. If so, choose the best tool and provide the correct input.
3.  **Observe the Result:** After using a tool, carefully observe the result.
4.  **Reflect and Repeat:** Based on the result, decide your next step. If something went wrong, analyze the error and try to fix it.
5.  **Final Answer:** When you have successfully completed all steps and fulfilled the user's request, provide a clear, final answer summarizing what you did.

Begin!

User's Request: {input}

Thought Log:
{agent_scratchpad}
"""

class SuperAgent:
    def __init__(self):
        # API key ab seedha yahan se li jayegi
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY is not set in the environment.")
            
        self.llm = ChatGoogleGenerativeAI(model=MODEL_NAME, google_api_key=api_key, temperature=0.1, convert_system_message_to_human=True)
        self.tools: List[BaseTool] = []
        self.agent_executor: AgentExecutor = None
        logging.info(f"SuperAgent initialized with model: {MODEL_NAME}")

    def register_tools(self, tools: List[BaseTool]):
        self.tools = tools
        prompt = PromptTemplate.from_template(AGENT_PROMPT_TEMPLATE)
        
        # Agent ko banana
        agent_runnable = create_react_agent(self.llm, self.tools, prompt)
        
        # Agent ko chalane wala executor banana
        self.agent_executor = AgentExecutor(
            agent=agent_runnable, 
            tools=self.tools, 
            verbose=True, 
            handle_parsing_errors=True, # Yeh ghalat outputs ko behtar handle karta hai
            max_iterations=15 # Taake agent anant loop mein na phans jaye
        )
        logging.info(f"Registered {len(tools)} tools.")

    # YEH FUNCTION AB SAADA (SYNCHRONOUS) HAI
    def process_request(self, request: str) -> Dict[str, Any]:
        """
        Processes the user's request using the agent executor.
        This is now a standard synchronous function.
        """
        if not self.agent_executor:
            return {"type": "error", "message": "Agent is not ready. No tools registered."}
        
        try:
            # 'ainvoke' (async) ki jagah ab 'invoke' (sync) istemal hoga
            response = self.agent_executor.invoke({"input": request})
            return {"type": "success", "final_answer": response.get("output")}
        except Exception as e:
            logging.error(f"Error processing request '{request}': {e}", exc_info=True)
            return {"type": "error", "message": str(e)}

