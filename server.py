import os
import sys
from mcp.server.fastmcp import FastMCP
from rag_code import *
from tavily import TavilyClient
from dotenv import load_dotenv

load_dotenv()

# Create a clean Stdio-compatible FastMCP server instance
mcp = FastMCP("mcp-rag-server")


@mcp.tool()
def machine_learning_faq_retrieval_tool(query: str) -> str:
    """Retrieve the most relevant documents from the machine learning
       FAQ collection. Use this tool when the user asks about ML.

    Input:
        query: str -> The user query to retrieve the most relevant documents

    Output:
        context: str -> most relevant documents retrieved from a vector DB
    """

    # check type of text
    if not isinstance(query, str):
        raise ValueError("query must be a string")
    
    retriever = Retriever(QdrantVDB("ml_faq_collection"), EmbedData())
    response = retriever.search(query)

    return response


@mcp.tool()
def tavily_web_search_tool(query: str) -> list[str]:
    """
    Search for information on a given topic using Tavily.
    Use this tool when the user asks about a specific topic or question 
    that is not related to general machine learning.

    Args:
        query: str -> The user query to search for information

    Returns:
        List of relevant search result snippets with source URLs.
    """
    # check type of text
    if not isinstance(query, str):
        raise ValueError("query must be a string")

    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise RuntimeError("TAVILY_API_KEY not found in environment.")

    client = TavilyClient(api_key=api_key)

    response = client.search(
        query=query,
        search_depth="advanced",
        max_results=5,
        include_answer=True,
        include_raw_content=False,
    )

    context = []

    # AI-generated answer (if available)
    if response.get("answer"):
        context.append(f"Answer: {response['answer']}")

    # Search results
    for result in response.get("results", []):
        context.append(
            f"""
                Title: {result.get('title', '')}
                URL: {result.get('url', '')}
                Content: {result.get('content', '')}
            """.strip()
        )

    return context



if __name__ == "__main__":
    print("Starting MCP server at http://127.0.0.1:8080 on port 8080")
    mcp.run()