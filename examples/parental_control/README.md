# AI Agent with Parental Control

This example shows how to create an AI agent that can search the web, but only if the query does not contain prohibited terms, requiring human approval otherwise.

The agent uses [Tavily][tavily-github] to search the web, [HumanLayer][humanlayer-github] to seek human approval, and [Eunomia][eunomia-github] to enforce access control. The agent is written using [LangChain][langchain-github].

## Setup

Install the dependencies:

```bash
pip install -r requirements.txt
```

Add your API keys to the `.env` file:

```bash
OPENAI_API_KEY="your-api-key"
TAVILY_API_KEY="your-api-key"
```

Run the Eunomia server using the `allow_query.rego` policy. Note that you can modify the list of prohibited terms in the policy to suit your needs.

## Running

Run the agent in a loop:

```bash
python example_parental_control.py
```

You can stop the agent by typing `exit`, `quit` or `bye`.

> [!NOTE]
> The example in this script handles both conversation and human approval in the terminal. The human intervention could easily be replaced with a different UI through HumanLayer.

[eunomia-github]: https://github.com/whataboutyou-ai/eunomia
[langchain-github]: https://github.com/langchain-ai/langchain
[tavily-github]: https://github.com/tavily-ai/tavily-python
[humanlayer-github]: https://github.com/humanlayer/humanlayer
