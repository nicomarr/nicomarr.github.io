---
layout: post
title: "Set up a Local LLM-powered Research Assistant for Health & Life Sciences"
categories: tutorials
---

Welcome to the second in a series of short tutorials aimed at making Large Language Model (LLM)-powered applications more accessible for health and life sciences researchers. 
This tutorial introduces [Scholaris](https://pypi.org/project/scholaris/), a Python package that allows anyone to set up a research assistant on a local computer and leverage function calling capabilities "out of the box". 
Scholaris is designed specifically for use in health and life sciences to help gain insights from scholarly articles and interact with academic databases. 

In this tutorial, you'll learn: 
- How to use [Scholaris](https://nicomarr.github.io/scholaris/) to set up an assistant and leverage its tools for various research tasks.
- How tool or function calling works using an LLM. 
- How to customize the assistant for your specific research needs.
<br>
<br>
<div style="background-color: #e6ffe6; padding: 15px; border-radius: 15px; margin: 30px 0;"> 
	<strong>Is this for you?</strong>
	This tutorial and the <a href="https://nicomarr.github.io/scholaris/">Scholaris Python package</a> is suitable for anyone and does not require any prior knowledge of Python programming. 
	The only prerequisite is that you are willing to learn and explore new tools and technologies.
	If you find particular terminology or concepts confusing, feel free to use <a href="https://you.com/">a cloud-hosted large language model</a> and ask it to explain them in simpler terms.
	Throughout this tutorial, you will also find text boxes with additional explanations. Feel free to skip these if you are already familiar with the concepts.
	If you are an experienced software developer, you may still find the tutorial useful for specific applications in health and life sciences.
	Be sure to check out the last section on customizing the assistant to suit specific research needs.
</div>
<br>

## Getting started
<div style="background-color: #e6f3ff; padding: 15px; border-radius: 15px; margin: 30px 0;"> <strong>Note!</strong>
This section assumes that you have Python and the Ollama app installed on your local computer. 
If you want to follow along with the code examples, see the <a href="https://nicomarr.github.io/scholaris/#installation">documentation</a> for installation instructions.
</div>

To get started, import and initialize the `Assistant` class from Scholaris: 
```python
from scholaris.core import *
assistant = Assistant() 
```

This creates an instance of the `Assistant` class with default settings. At the time of writing, the default model is [Llama 3.1 8B](https://ollama.com/library/llama3.1). 
You can also customize various parameters if needed, such as specifying a different model or adding custom tools (more on this in a later section).
A detailed description of how to do so can also be found in the [documentation pages](https://nicomarr.github.io/scholaris/). 
For now, let's take advantage of the core functionality and default options.

The primary way to interact with the Scholaris assistant is through the `chat` method. Here's an example:
```python
response = assistant.chat("Briefly tell me about the tools you have available.")
``` 

This will prompt the assistant to describe its available tools and capabilities. 
<br>

<div style="background-color: #e6f3ff; padding: 15px; border-radius: 15px; margin: 30px 0;">
    <strong>Terminology explained:</strong>
    <ul>
		<br>
		<li>
			A <strong>class</strong> in Python is like a blueprint or a template for creating <strong>objects</strong>. It's a way to bundle data and functionality together.
			<strong>Objects</strong> are instances of classes, and they can have attributes (variables) and methods (functions).
		</li>
		<br>
        <li>
			The terms <strong>function calling</strong> and <strong>tool calling</strong> are often used interchangeably. 
			Strictly speaking, functions typically receive one or more parameters as input to generate (return) one or more outputs, 
			whereas a tool is a more broadly defined term in the context of large language model (LLM)-driven applications.
			Tools may refer to a wider range of operations, including functions, code blocks that are executed without additional parameters, 
			multiple functions executed in sequence or parallel, or other types of actions. 
			In the context of LLM-driven applications, both function calling and tool calling refer to the model's ability to generate structured outputs. 
			These outputs are based on predefined schemas, not on the actual code that is executed. 
			If an LLM-powered application or workflow has the capability to call functions or tools, it may also be referred to as being "agentic".
		</li>
		<br>
        <li>
			<strong>JSON</strong>, short for JavaScript Object Notation, is a lightweight, text-based data format that is easy for humans to read and write, 
			and simple for LLMs to parse and generate. JSON uses curly braces for objects, colons to separate keys and values, 
			and commas to separate key-value pairs or elements of list objects. Originally developed for JavaScript, JSON has become a widely-used standard for data exchange in web applications and beyond.
		</li>
		<br>
		<li>
			<strong>API</strong>, short for Application Programming Interface, is a set of rules and protocols that allow different software applications to communicate with each other.
			It is the primary way of how an application is interacting with an external service or tool, such as a database, web service, or library (analogous to how humans interact through a graphical user interface, e.g., a web browser).
		</li>
	</ul>
</div>
<br>

## Function / tool calling 
Before we dive into a few use cases, let's first review what tool or function calling is and how it works. 

In a nutshell, the process of tool / function calling involves multiple steps, as illustrated below: 
<br>
<br>

**Figure 1.** Flowchart of a basic LLM-powered application with function calling, illustrating the process from user input to final response generation.
![Figure 1](/assets/img/fucntion-calling.svg)
<br>
<br>

1. **Tool / function calling:**
The LLM receives a system message with core instructions (often including an assigned role), the user prompt, and a description of available functions with their parameters.
If the tool call is made in the middle of a conversation, the LLM also receives as input the conversation history of the session (i.e., since the initialization of the assistant or since the last reset). Otherwise, LLMs are stateless (i.e., they do not have persistent memory of previous interactions).
When using Scholaris, the conversation history is automatically stored in an attribute of the `Assistant` class, called `conversation_history`. 
Be sure to check out the [documentation on how to access and use the conversation history](https://nicomarr.github.io/scholaris/#conversation-history).
Importantly, the LLM does not "see" the source code for execution. Instead, it receives a description of the purpose and usage of a code element, like a Python function, usually provided as text formatted using JSON. 
The content of this JSON-formatted string is equivalent to the "docstring". 
It is the programmer's responsibility to ensure proper functionality. Based on the user prompt, the LLM returns the most suitable function name and its parameters for the Python interpreter to execute. 

2. **Execution of the selected tool / function:**
The Python code for the selected function or tool (and any nested functions) is executed, using optional or required parameters provided by the LLM.
These functions may be designed to retrieve data from external databases, extract information from local files, or perform tasks like listing the contents of a specific directory. 
Scholaris includes several [built-in tools](https://nicomarr.github.io/scholaris/#tools) that can be called by the LLM, such as:

	- `get_file_names` 
	- `extract_text_from_pdf` 
	- `get_titles_and_first_authors` 
	- `summarize_local_document` 
	- `describe_python_code` 
	- `id_converter_tool` 
	- `query_openalex_api` 
	- `query_semantic_scholar_api` 
	- `respond_to_generic_queries`
<br>
<br>

3. **Response generation:** 
Finally, the LLM is "called" again to generate a response based on the output of the executed function, the user prompt, and the conversation history as context (which also includes the system message).
A programmer can extend this step by implementing additional routines and logic, such as:

    - **Self-reflection** - a mechanism that can be implemented, allowing the LLM to evaluate the response it generated for accuracy and completeness, and repeat the response generation, if necessary. 
	- **Iterative loops** - can be implemented, which call additional functions or prompt the user for more details, creating an iterative process by which the response is refined.
	- **Multi-step problem solving** - for complex queries. A workflow can be designed that breaks down tasks into multiple steps. 
	Different functions might be called in sequence or in parallel to gather all necessary information before a comprehensive response is formulated.
	- **Integration of multiple function outputs** - can be combined, allowing information from different sources to be synthesized to provide a more holistic answer.

These additional steps are not part of the core functionality of Scholaris and would need to be implemented by the user. 
<br>
<br>

## Use cases

Let's explore a few practical use cases: 

### 1. Extracting information and summarizing content from local files

By default, the assistant has access to a single directory, called `data`. 
Within this directory, the assistant can list and read the following file formats and extensions: `.pdf`, `.txt`, `.md` or `.markdown`, `.csv`, and `.py`. 
If not already present, the `data` directory is created in the parent directory when the assistant is initialized. 

Extracting information from local files is particularly useful for content that contains sensitive information (e.g., your local files might contain identifying information of study subjects) or for content that is outside your main area of expertise (e.g., a Python script for data analysis obtained from a colleague or collaborator, or a medical chart with diagnostic codes). Additionally, it is useful for documents that are very technical in nature or otherwise difficult to read. 

Let's use the [source code of Scholaris](https://github.com/nicomarr/scholaris/blob/main/scholaris/core.py) as an example! To extract and summarize the content of the source code file, you must first copy it to your local `data` directory. 
You can do this using your file manager (e.g., Finder or Explorer), in the terminal, or by using the Python `shutil` module, like so:
```python
import shutil
shutil.copy("path/to/scholaris/core.py", "data/core.py") # Make sure to replace "path/to/scholaris/core.py" with the actual path to the file.
```
Now you can ask the assistant to summarize the content of the file:

```python
response = assistant.chat("Summarize the content of the file `core.py` in the local `data` directory.")
```
You may also ask the assistant to list the contents of the `data` directory:
```python 
response = assistant.chat("List the contents of the local `data` directory.")
```
<br>

There are numerous ways to customize the assistant to suit your needs. 
In the next section, we will explore these possibilities in more detail. For now, let's illustrate another use case.
<br>
<br>

### 2. Retrieving citation metrics from an external source, such as the OpenAlex API

The assistant can query the OpenAlex API to retrieve citation metrics for a given Digital Object Identifier (DOI). 
This is particularly helpful if you want to include citation metrics in your literature search or when you need to quickly assess the impact of a specific article. 
Here's an example:
```python
response = assistant.chat("How often has the article with the DOI `10.1172/jci.insight.144499` been cited?")
```
This will prompt the assistant to query the OpenAlex API and return the citation metrics for the specified DOI.
<br>
<br>

## Customizing the assistant for your needs

<div style="background-color: #e6ffe6; padding: 15px; border-radius: 15px; margin: 30px 0;">
	<strong>Tip:</strong>
	To customize the assistant, it is helpful to have a basic understanding of Python programming. 
	If you are new to Python, consider taking a beginner course, such as <a href="https://www.deeplearning.ai/short-courses/ai-python-for-beginners/">AI Python for Beginners</a>, 
	a free short course offered by <a href="https://www.deeplearning.ai/">DeepLearning.AI</a> (approximate time to complete: 4-5 hours).
	Basic knowledge of how to define a function in Python is all you need to customize the assistant with new tools.
</div>	

Scholaris is designed to be highly customizable, allowing you to extend its capabilities to suit your specific research needs. 
The core tools or functions are passed to the assistant like "building blocks" during initialization. 
Therefore, there is no need to modify the source code and Assistant class in order to expand the tools.
There are several ways to customize the assistant:

### 1. Limiting or replacing the core functions
If you want to change the core functions, you can do so by passing the desired core functions as an argument (in the form of dictionaries) to the `Assistant` class when it is initialized. 
For example, to limit the assistant’s ability to respond to generic questions and access external data from the OpenAlex and Semantic Scholar APIs, you would initialize the assistant as follows: 
```python
assistant = Assistant(tools = {
    "query_openalex_api": query_openalex_api,
    "query_semantic_scholar_api": query_semantic_scholar_api,
    "respond_to_generic_queries": respond_to_generic_queries,
	"describe_tools": describe_tools
    })
```
When the assistant is initialized in this way, it will no longer be able to access information from the local `data` directory or extract information from local files, even though the `data` directory is still present.

Similarly, you can initialize the assistant to only be able to extract information from local files and summarize the content of local documents:
```python
assistant = Assistant(tools = {
	"get_file_names": get_file_names,
	"extract_text_from_pdf": extract_text_from_pdf,
	"summarize_local_document": summarize_local_document,
	"describe_python_code": describe_python_code,
	"respond_to_generic_queries": respond_to_generic_queries,
	"describe_tools": describe_tools
	})
```
When the assistant is initialized in this way, it will no longer be able to make API calls to external sources.

It is recommended to keep the `describe_tools` function and `respond_to_generic_queries` function in the core tools to maintain the assistant's ability to describe its tools (including newly added tools) and respond to generic queries, respectively. 
The latter tool also represents a fallback mechanism in case the assistant is unable to identify the user's intent or the user's query is outside the scope of the core tools. 
When using [Scholaris](https://pypi.org/project/scholaris/), the research assistant is designed to use a tool to generate a final response to a user’s prompt. This is to ensure that the assistant is primarily providing information which is relevant for health and life sciences. 
Otherwise it will abort the conversation. Be sure to check out the tools section in the [documentation](https://nicomarr.github.io/scholaris/#tools) for more details (see callout box: **What happens if the assistant is initialized without any tools?**) 
<br>
<br>

### 2. Adding new tools
You can also add new tools to the assistant to extend its capabilities. In this case, the core tools will be appended, not replaced. This is achieved simply by defining a new function in Python. Be sure to use [type hints](https://docs.python.org/3/library/typing.html#module-typing), [Google-style docstrings](https://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html), and the `@json_schema_decorator` function of the [Scholaris Python package](https://nicomarr.github.io/scholaris/core.html#json_schema_decorator) to automatically generate the schema for your new function.
Your new function can then be passed to the `Assistant` class during initialization, like so:
```python
assistant = Assistant(add_tools = {"your_new_function": your_new_function})
```
More details can be found in the [Developer Guide](https://nicomarr.github.io/scholaris/#defining-new-tools) section of the documentation.

Let's revisit a few key points and ideas to consider when using the [Scholaris](https://pypi.org/project/scholaris/) package and customizing the assistant:

- Many other libraries and Software Development Kits (SDKs) require you to write JSON schemas of the functions or tools to be called by the LLM. 
This is simplified in Scholaris by using the `@json_schema_decorator` and Google-syle docstrings, which are easy to write and read.

- [Scholaris](https://pypi.org/project/scholaris/) is designed so that functions or tools are passed as building blocks during initialization of the assistant. 
Therefore, there is no need to modify the source code of the `Assistant` class in order to expand its capabilities, 
unless you want to implement more complex logic and agentic workflows, including multi-step reasoning and/or loops (more on this below).

- [Scholaris](https://pypi.org/project/scholaris/) is developed to serve as a framework for building LLM-powered research assistants in health and life sciences rather than a robust production-ready tool. 
Therefore, you may also modify the existing tools and functions or add similar tools to extend the assistant's capabilities. 
Consider using the assistance of an LLM to modify the provided core functions to suit your specific research needs. To do so, you may use larger cloud-hosted LLMs to aid you in this process, although for simple modifications, smaller (local) models may suffice.
For example, you can modify the `summarize_local_document` function to extract specific information from a document that is relevant to your research by modifying the prompt used inside the function.

- Always use LLMs responsibly and be aware of their limitations. Use additional models, such as [Llama Guard](https://www.llama.com/docs/model-cards-and-prompt-formats/llama-guard-3/), in production environments to ensure that the assistant does not generate harmful or inappropriate content.
<br>
<br>

### 3. Implementing more complex logic and agentic workflows (for advanced users)

If you want to implement more complex logic and agentic workflows, such as multi-step reasoning, iterative loops, or self-reflection, you will need to modify the [source code](https://github.com/nicomarr/scholaris/blob/main/scholaris/core.py) of the `Assistant` class. 
The Scholaris package has been written using a ‘literate’ programming style and [nbdev](https://nbdev.fast.ai/), which means that the source code is written in a way that is easy to read and understand. 
This makes it easier for you to modify the source code to suit your specific needs. Be sure to also view the Jupyter notebook with the ‘literate’ source code and additional tests [here](https://github.com/nicomarr/scholaris/blob/main/nbs/01_core.ipynb).
<br>
<br>

## Wrapping up

In this tutorial, you learned how to set up a LLM-powered research assistant for health and life sciences. Be sure to check out the [documentation pages](https://nicomarr.github.io/scholaris/) for more details on how to use the [Scholaris Python package](https://pypi.org/project/scholaris/).
Consider it as an application to help you accelerate your research aimed at creating a positive impact, and keep the limitations of LLMs in mind: 
> Current AI systems lack several essential characteristics of human-level intelligence, including the ability to learn, navigate, and understand the physical world, persistent memory, the ability to plan complex action sequences, and the ability to be controllable and safe by design (not by fine-tuning).
> [cf. Yann LeCun - Keynote at the Hudson Forum](https://www.youtube.com/watch?v=4DsCtgtQlZU)


<br>
<br>
<br>
If you spotted any errors or inconsistencies in this tutorial, please feel free to open an issue on the [GitHub repository's issue page](https://github.com/nicomarr/scholaris/issues).