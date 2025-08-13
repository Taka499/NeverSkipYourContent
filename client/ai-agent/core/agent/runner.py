# core/agent/runner.py

from typing import Optional

from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage

from core.agent.llm import get_llm
from core.agent.tools import get_mcp_tools

import os
os.environ["LANGCHAIN_DEBUG"] = "true"


async def run_agent(prompt: str, session_id: Optional[str] = None, user_id: Optional[str] = None) -> str:
    model = get_llm()
    tools = await get_mcp_tools()

    agent = create_react_agent(model, tools)
    
    state = {"messages": [HumanMessage(content=prompt.strip())]}

    # --- temporary debug: prove we’re not empty going in ---
    print("DEBUG: invoking agent with", state)
    
    response = await agent.ainvoke(state)
    
    # return response.get("messages", "No response from agent.")
    # ✅ pull the last AI message from the graph state
    messages = response.get("messages", [])
    return messages[-1].content if messages else "No response from agent."
