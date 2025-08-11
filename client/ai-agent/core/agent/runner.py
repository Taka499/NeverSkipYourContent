# core/agent/runner.py

from typing import Optional

from langgraph.prebuilt import create_react_agent

from core.agent.llm import get_llm
from core.agent.tools import get_mcp_tools


async def run_agent(prompt: str, session_id: Optional[str] = None, user_id: Optional[str] = None) -> str:
    model = get_llm()
    tools = await get_mcp_tools()

    agent = create_react_agent(model, tools)
    
    response = await agent.ainvoke(
        {
            "message": prompt,
        }
    )
    
    return response.get("message", "No response from agent.")
