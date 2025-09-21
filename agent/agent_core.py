# File: agent/agent_core.py
import os
import logging
from typing import List, Dict, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.prompts import PromptTemplate
from langchain.tools import BaseTool

MODEL_NAME = "gemini-1.5-flash-latest"
AGENT_PROMPT_TEMPLATE = """
You are a world-class AI assistant. Your goal is to complete the user's request by planning and executing steps using the available tools.

TOOLS:
{tools}

INSTRUCTIONS:
1. Think Step-by-Step.
2. Use a tool if necessary.
3. Observe the result.
4. Reflect and decide the next step.
5. When the task is complete, provide a clear final answer.

Begin!

User's Request: {input}

Thought Log:
{agent_scratchpad}
"""

class SuperAgent:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.1, google_api_key=os.getenv("GEMINI_API_KEY"), convert_system_message_to_human=True)
        self.tools: List[BaseTool] = []
        self.agent_executor: AgentExecutor = None
        logging.info(f"SuperAgent initialized with model: {MODEL_NAME}")

    def register_tools(self, tools: List[BaseTool]):
        self.tools = tools
        prompt = PromptTemplate.from_template(AGENT_PROMPT_TEMPLATE)
        agent_runnable = create_react_agent(self.llm, self.tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=agent_runnable, 
            tools=self.tools, 
            verbose=True, 
            handle_parsing_errors=True,
            max_iterations=15
        )
        logging.info(f"Registered {len(tools)} tools.")

    async def process_request(self, request: str) -> Dict[str, Any]:
        if not self.agent_executor:
            return {"type": "error", "message": "Agent is not ready."}
        
        try:
            response = await self.agent_executor.ainvoke({"input": request})
            return {"type": "success", "final_answer": response.get("output")}
        except Exception as e:
            logging.error(f"Error processing request: {e}", exc_info=True)
            return {"type": "error", "message": str(e)}
