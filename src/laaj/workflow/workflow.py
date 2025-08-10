from langgraph.graph import START, END, StateGraph

from typing import Literal

from typing_extensions import TypedDict

import json

from laaj.config import LITERAL_MODELS
from laaj.agents import get_llm_anthropic_claude_4_sonnet, get_llm_google_gemini_pro, get_llm_gpt_5, get_llm_qwen_3_instruct, chain_story, chain_laaj

class BestResponseState(TypedDict):
    model_llm_a: Literal[LITERAL_MODELS]
    model_llm_b: Literal[LITERAL_MODELS]
    response_a: str
    response_b: str
    better_llm: str
    input: str
    
builder = StateGraph(
    BestResponseState
)

def node_llm_a(state: BestResponseState):
    input = state["input"]
    llm_a = state["model_llm_a"]
    llm = None
    if llm_a == "claude-4-sonnet":
        llm = get_llm_anthropic_claude_4_sonnet()
    elif llm_a == "google-gemini-2.5-pro":
        llm = get_llm_google_gemini_pro()
    else:
        return {
            "response_a" : "Model not found, plese select only models from the list: " + str(LITERAL_MODELS),
        }
        
    if llm:
        chain = chain_story(llm)
        response = chain.invoke(input={"topic":input})
        return {
            "response_a" : response,
            "model_llm_a" : llm_a
        }
    
    return {}
    
def node_llm_b(state: BestResponseState):
    input = state["input"]
    llm_b = state["model_llm_b"]
    llm = None
    if llm_b == "claude-4-sonnet":
        llm = get_llm_anthropic_claude_4_sonnet()
    elif llm_b == "google-gemini-2.5-pro":
        llm = get_llm_google_gemini_pro()
    else:
        return {
            "response_b" : "Model not found, plese select only models from the list: " + str(LITERAL_MODELS),
        }
        
    if llm:
        chain = chain_story(llm)
        response = chain.invoke(input={"topic":input})
        return {
            "response_b" : response,
            "model_llm_b" : llm_b
        }
    
    return {}


def node_judge(state: BestResponseState):
    response_a = state["response_a"]
    response_b = state["response_b"]
    chain = chain_laaj(get_llm_gpt_5())
    response = chain.invoke(input={"answer_a":response_a, "answer_b":response_b, "question":state["input"]})
    
    if "Preference" in response:
        resultado = response["Preference"]
        if resultado == int(1):
            better_llm = state["model_llm_a"]
        elif resultado == int(2):
            better_llm = state["model_llm_b"]
        else:
            better_llm = "Empate"
        return {
            "better_llm" : better_llm
        }
    else:
        return {
            "better_llm" : "Error, Preference nao encontrado na resposta do Juiz"
        }

builder.add_node("llm_1",node_llm_a)
builder.add_node("llm_2",node_llm_b)
builder.add_node("judge",node_judge)

builder.add_edge(START, "llm_1")
builder.add_edge(START, "llm_2")
builder.add_edge("llm_1", "judge")
builder.add_edge("llm_2", "judge")
builder.add_edge("judge", END)

graph = builder.compile()

response = graph.invoke(
    input={
        "input": "Amigos",
        "model_llm_a": "google-gemini-2.5-pro",
        "model_llm_b": "claude-4-sonnet",
    }
)

print(json.dumps(response, indent=2))

# print(type(response))

