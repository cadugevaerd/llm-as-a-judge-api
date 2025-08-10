#!/usr/bin/env python3
"""
Simple script to test LangSmith tracing with LangChain.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from langsmith_integration import LangSmithClient
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def main():
    """
    Test LangSmith tracing with a simple LLM call.
    """
    print("🔄 Testing LangSmith Tracing...")
    
    # Initialize LangSmith client
    print("\n1. Initializing LangSmith tracing...")
    langsmith_client = LangSmithClient()
    
    # Check tracing configuration
    print("\n2. Checking tracing configuration...")
    tracing_info = langsmith_client.get_tracing_info()
    for key, value in tracing_info.items():
        print(f"   {key}: {value}")
    
    if not langsmith_client.is_tracing_enabled():
        print("⚠️  Tracing is disabled - continuing without tracing")
    else:
        print("✅ Tracing is enabled!")
    
    print("\n3. Testing LLM call with tracing...")
    try:
        # Initialize LLM (this will be traced if API key is available)
        llm = ChatOpenAI(
            model="gpt-3.5-turbo",
            temperature=0.7
        )
        
        # Simple test message
        messages = [HumanMessage(content="Hello! Can you say 'Tracing test successful'?")]
        
        # Make the call - this should appear in LangSmith if configured
        print("   Making LLM call...")
        response = llm.invoke(messages)
        
        print(f"   Response: {response.content}")
        print("✅ LLM call completed successfully!")
        
        if langsmith_client.is_tracing_enabled():
            print(f"\n🎯 Check your LangSmith project '{langsmith_client.get_project_name()}' for the trace!")
        
    except Exception as e:
        print(f"❌ Error during LLM call: {e}")
        print("This might be due to missing OpenAI API key or other configuration issues")
    
    print("\n🎉 Tracing test completed!")


if __name__ == "__main__":
    main()