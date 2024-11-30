from typing import Dict, TypedDict
from langgraph.graph import END, StateGraph
import pprint

import openai

# Create a "openai_api_key.txt" file first and put your api key there.
api_key_path = "openai_api_key.txt"
openai.api_key_path = api_key_path

'''
models:
    gpt-3.5-turbo
    gpt-4-turbo
    gpt-4o
'''
# Change the model accordingly.
model_name="gpt-4o"

# Defining the structure of the graph state
class GraphState(TypedDict):
    keys: Dict[str, any]
workflow = StateGraph(GraphState)


################################ Defining the nodes ############################

def get_input_data(state: GraphState) -> GraphState:
    file_path = "input_notes.txt"    
    with open(file_path, 'r') as file:
        input_data = file.read()
        
    state['keys']['input_data'] = input_data
    return state

# def clean_input_data(state: GraphState) -> GraphState:
#     cleaned_data = state['keys']['input_data'].strip()
#     state['keys']['cleaned_data'] = cleaned_data
#     return state

def segment_chapters(state: GraphState) -> GraphState:
    print("---Segmenting Chapters---")
    input_data = state['keys']['input_data']
    
    prompt_template = """ You are an expert book editor. Your task is to read the provided text and identify natural divisions within the text to create chapter titles. 
    Use the context and content to determine appropriate and descriptive chapter titles that accurately reflect the main themes or events of each section. 
    The goal is to segment the text into logical, coherent chapters. Provide a list of titles for each chapters you identify.
    
    BookTitle: [Title of the book]
    Chapter 1: [Title of Chapter 1]
    Chapter 2: [Title of Chapter 2]

    (Continue this pattern for all chapters)
    """
        
    # Initializing the language model using OpenAI
    response = openai.ChatCompletion.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are an expert book editor."},
            {"role": "user", "content": prompt_template + "\n\n" + input_data}
        ],
        max_tokens=1024,
        temperature=0.7,
    )
    
    chapters_text = response['choices'][0]['message']['content'].strip()
        
    print("CHAPTERS: ", chapters_text)
    
    # Parse chapters
    chapters_lines = chapters_text.split('\n')
    
    chapter_titles = []
    for line in chapters_lines:
        if 'BookTitle' in line:
            title = line.split(':')[1].strip()
            state["keys"]["book_title"] = title
        elif 'Chapter' in line:
            # Extract the chapter title by splitting the line by ':'
            chapter_title = line.split(':')[1].strip()
            chapter_titles.append(chapter_title)
    ##
    
    state["keys"]["chapters"] = chapter_titles
    return state

def summarize_chapters(state: GraphState) -> GraphState:
    print("---Creating Chapter Summaries---")
    input_data = state['keys']['input_data']
    chapters = state['keys']['chapters']
    title = state['keys']['book_title']

    prompt_template = """ You are a skilled writer tasked with creating a chapter for a book. 
    Your assignment is to write a chapter named {chapter_title} for the book titled "{book_title}". 
    You should aim to provide engaging and informative content that aligns with the theme or topic of the book.

    Content of Chapter:
    (Continue writting the content of the Chapter)
    """
    
    # TODO: Use another prompt to refine the already generated content
    # refine_template = (
    #     " "
    # )
    
    chapter_summaries = []
    for _, chapter_title in enumerate(chapters, start=1):
        
        response = openai.ChatCompletion.create(
            model=model_name,
            messages=[
                {"role": "system", "content": "You are an expert book editor."},
                {"role": "user", "content": prompt_template.format(chapter_title=chapter_title, book_title=title) + "\n\n" + input_data}
            ],
            max_tokens=1024,
            temperature=0.7,
        )
        
        # Extracting the generated summary from the response
        summary = response['choices'][0]['message']['content'].strip()    
        chapter_summaries.append(summary)

    state['keys']['chapter_summaries'] = chapter_summaries
    return state

def compile_documentation(state: GraphState) -> GraphState:
    print("---Compiling Documentation---")
    chapter_titles = state["keys"]["chapters"]
    chapter_summaries = state["keys"]["chapter_summaries"]
    book_title = state["keys"]["book_title"]
    
    document = ""
    document += f"# {book_title} \n\n"      # Markdown format
    cnt=1
    for chapter_title, summary in zip(chapter_titles, chapter_summaries):
        document += f"## Chapter {cnt}: {chapter_title}\n\n{summary}\n\n" 
        cnt+=1
    
    state["keys"]["document"] = document
    with open("output_book.md", "w") as file:
        file.write(document)
        
    print("Documentation compiled and saved.")
    return state

######################### Add nodes to the workflow ###########################
workflow.add_node("get_input_data", get_input_data)
# workflow.add_node("clean_input_data", clean_input_data)
workflow.add_node("segment_chapters", segment_chapters)
workflow.add_node("summarize_chapters", summarize_chapters)
workflow.add_node("compile_documentation", compile_documentation)

###################### Define edges (transitions) between nodes ################
workflow.set_entry_point("get_input_data") # entery point (start node)

# workflow.add_edge("get_input_data", "clean_input_data")
# workflow.add_edge("clean_input_data", "segment_chapters")
workflow.add_edge("get_input_data", "segment_chapters")
workflow.add_edge("segment_chapters", "summarize_chapters")
workflow.add_edge("summarize_chapters", "compile_documentation")
workflow.add_edge("compile_documentation", END)

# Compile the Workflow
app = workflow.compile()

#########################################################################

# Stream and handle outputs
inputs = {"keys": {"input_data": ""}}
for output in app.stream(inputs):
    for key, value in output.items():
        pprint.pprint(f"Node '{key}':")
        pprint.pprint(value)
    pprint.pprint("\n---\n")


# pprint.pprint(value['keys']['document'])
