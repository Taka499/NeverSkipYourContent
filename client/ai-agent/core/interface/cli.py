# core/interface/cli.py
import asyncio

from core.agent import run_agent
from core.config import LocalAppSettings, initialize_settings

async def main():
    print("MCP ReAct Agent CLI")
    # initialize settings from LocalAppSettings
    # This will load settings from the local .env file and environment variables
    initialize_settings(LocalAppSettings)
    while True:
        try:
            prompt = input("Enter your prompt (or 'exit' to quit): ")
            if prompt.lower() == 'exit':
                print("Exiting the CLI.")
                break
            
            response = await run_agent(prompt)
            print(f"Agent Response: {response}")
        except KeyboardInterrupt:
            print("\nExiting the CLI.")
            break
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(main())
