# Import necessary modules from LangChain, Chainlit, environment management, and operator
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import PromptTemplate, ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.messages import get_buffer_string
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from operator import itemgetter

import chainlit as cl
from dotenv import load_dotenv
import os

from mail_bot.prompts import answer_template, standalone_request_template

# Load environment variables from a .env file
load_dotenv(override=True)

# Retrieve the Google API key from environment variables
GOOGLE_API_KEY_ = os.getenv("GOOGLE_API_KEY")

# Define the maximum number of interactions before clearing memory
MAX_COUNTER = 10
COUNTER = 1

# Define parameters for the Google Gemini model
gemini_model_kwargs = {
    "model": "gemini-pro",
    "google_api_key": GOOGLE_API_KEY_,
    "temperature": 0.3,
    "top_p": 0.6
}

# Initialize the LLM with the Google Gemini model
llm = ChatGoogleGenerativeAI(**gemini_model_kwargs)

# Set up memory for conversation history management
memory = ConversationBufferMemory(
    return_messages=True,
    memory_key='chat_history',
    output_key="answer",
    input_key="request"
)

## Define prompts for conversation handling

# Prompt for condensing the user request
condense_request_prompt = PromptTemplate(
    input_variables=['chat_history', 'request'],
    template=standalone_request_template
)

# Prompt for generating the answer based on the conversation history and request
answer_prompt = ChatPromptTemplate.from_template(answer_template())

### Define the chains for processing the conversation

### Standalone request chain
standalone_request_chain = {
    "standalone_request": {
        "request": lambda x: x["request"],  # Extract user request
        "chat_history": lambda x: get_buffer_string(x["chat_history"])  # Format chat history
    }
    | condense_request_prompt  # Apply prompt to condense the request
    | llm  # Use the LLM to generate a response
    | StrOutputParser(),  # Parse the output as a string
}

# Load conversation history into memory
loaded_memory = RunnablePassthrough.assign(
    chat_history=RunnableLambda(memory.load_memory_variables) | itemgetter("chat_history"),
)
chain_question = loaded_memory | standalone_request_chain

## Define answer chain for generating responses

# Variables for answer generation
answer_prompt_variables = {
    "context": lambda x: "professional AI writer",  # Define the context of the AI
    "request": itemgetter("standalone_request"),  # Use the condensed request
    "chat_history": itemgetter("chat_history")  # Use chat history from loaded memory
}

# Define the chain to generate answers
chain_answer = {
    "answer": loaded_memory | answer_prompt_variables | answer_prompt | llm,
}

# Define the overall conversational retriever chain that handles both questions and answers
conversational_retriever_chain = chain_question | chain_answer

# Function to invoke the AI model asynchronously
async def ainvoke(chain, query, memory):
    global MAX_COUNTER
    global COUNTER
    response = await chain.ainvoke({"request": query})  # Invoke the chain with the user's query
    answer = response["answer"].content  # Extract the answer from the response
    memory.save_context({"request": query}, {"answer": answer})  # Save context to memory

    # Check if the counter has reached the maximum limit
    if COUNTER == MAX_COUNTER:
        memory.clear()  # Clear memory if limit is reached
        COUNTER = 0
    else:
        COUNTER += 1  # Increment counter
    return answer  # Return the generated answer

# Chainlit code to handle the start of a conversation
@cl.on_chat_start
async def start():
    chain = conversational_retriever_chain
    msg = cl.Message(content="Starting the bot...")
    await msg.send()  # Send initial message to user
    msg.content = "Hi, Welcome to Mail Generator Assistant."
    await msg.update()  # Update message content
    cl.user_session.set("chain", chain)  # Set the chain in the user session

# Chainlit code to handle incoming user messages
@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="")
    await msg.send()  # Send an empty message to indicate processing
    chain = cl.user_session.get("chain")  # Retrieve the conversation chain from the user session
    cb = cl.AsyncLangchainCallbackHandler()  # Create an asynchronous callback handler
    cb.answer_reached = True  # Set the answer_reached flag
    answer = await ainvoke(chain=chain, query=message.content, memory=memory)  # Invoke the chain with the user message

    # Check if an answer was generated
    if answer is not None:
        msg.content = answer  # Set the generated answer as message content
    else:
        msg.content = "Unable to process, Please try again after sometime"  # Handle case where no answer is generated
    await msg.update()  # Update the message with the response
