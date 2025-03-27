import functools
import inspect

import langchain.tools
from colorama import Fore, Style, init
from dotenv import load_dotenv
from eunomia_sdk_python import EunomiaClient
from humanlayer import HumanLayer
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from tavily import TavilyClient

# Add OPENAI_API_KEY and TAVILY_API_KEY to your environment variables
load_dotenv()

eunomia = EunomiaClient()
hl = HumanLayer()
tavily = TavilyClient()
init()


# Create a decorator to check access with Eunomia and require human approval with HumanLayer if access is denied
def eunomia_hl(argument_name):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Get the function signature and bind the arguments to it
            sig = inspect.signature(func)
            try:
                bound_args = sig.bind(*args, **kwargs)
                bound_args.apply_defaults()
            except TypeError as e:
                raise TypeError(f"Error binding arguments: {e}")

            # If the argument is not present, raise an error
            if argument_name not in bound_args.arguments:
                raise ValueError(f"Required argument '{argument_name}' is missing")

            # We check access with Eunomia
            has_access = eunomia.check_access(
                principal_attributes={"caller": "agent"},
                resource_attributes={
                    "tool_name": func.__name__,
                    argument_name: bound_args.arguments[argument_name],
                },
            )

            # We require human approval if access is denied
            return (
                func(*args, **kwargs)
                if has_access
                else hl.require_approval()(func)(*args, **kwargs)
            )

        return wrapper

    return decorator


# Define the web_search tool using Tavily, decorated with Eunomia and HumanLayer
@eunomia_hl("query")
def web_search(query: str) -> str:
    """Search the web for information."""
    return tavily.search(query)


# Create the agent
tools = [
    langchain.tools.StructuredTool.from_function(web_search),
]
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant that can search the web for information.",
        ),
        ("human", "{input}"),
        ("placeholder", "{agent_scratchpad}"),
    ]
)

agent = create_tool_calling_agent(llm, tools, prompt)
agent_executor = AgentExecutor(agent=agent, tools=tools)


# Run the agent in a loop
def main() -> None:
    print(f"{Fore.YELLOW}Agent: {Style.RESET_ALL}", end="")
    print("Hello, how can I help you today?")
    while True:
        user_input = input(f"{Fore.GREEN}You: {Style.RESET_ALL}")
        if user_input.lower() in ["exit", "quit", "bye"]:
            print(f"{Fore.CYAN}Thank you for chatting!{Style.RESET_ALL}")
            break
        print(f"{Fore.YELLOW}Agent: {Style.RESET_ALL}", end="")
        result = agent_executor.invoke({"input": user_input})
        print(result["output"])


if __name__ == "__main__":
    main()
