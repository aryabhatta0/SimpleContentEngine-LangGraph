#### Questions
1. What is LangGraph?
2. How to use LangGraph to build content engine
3. How to receive/handle the inputs?
4. Atlast, we'll be using WordPress to generate blog using AI.

## What is LangGraph?
It is a tool or framework that helps organize and process text-based data in a structured way. 

Here’s how to explain it simply:
- Imagine you’re writing a story, but instead of writing it all at once, you break it into small, manageable parts (like sentences or paragraphs).
- These parts are then linked together like a chain or graph, showing how they relate to each other.
- LangGraph works similarly—it organizes and connects pieces of text or language, helping tools like OpenAI's GPT-3.5 understand the input better and create well-structured outputs.

**Its purpose is to structure workflows with various states/nodes defined.**


## Working with LangGraph:
STEPS:

1. Initialization and Setup

```python
from typing import Dict, TypedDict
from langgraph.graph import END, StateGraph
class GraphState(TypedDict):
    keys: Dict[str, any]
```
`workflow = StateGraph(GraphState)`

2. Define Nodes \
`workflow.add_node()` \
*Each node is defined as a func in itself*

3. Build the Graph

- `workflow.set_entry_point()`
- `workflow.add_edge()`
- `workflow.add_conditional_edges()`

4. Compile the Workflow \
`app = workflow.compile()`

5. Run the Workflow \
`for output in app.stream(inputs):`

## How to call openai API
```python
import openai
response = openai.ChatCompletion.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are an expert ...."},
            {"role": "user", "content": prompt_template + "\n\n" + input_data}
        ],
        max_tokens=1024,
        temperature=0.7,
    )
```