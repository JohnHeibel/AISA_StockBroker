# pip install openai
from openai import OpenAI
# standard python library, so you should have it
import os
# pip install python-dotenv
from dotenv import load_dotenv
# pip install termcolor
from termcolor import colored
# pip install requests
import requests
# pip install json
import json

# load the .env file
load_dotenv()
# Create a .env file and store your api key in it
# OPENAI_KEY = "sk-..."
# Set the api key variable to the environment variable
OPENAI_KEY = os.environ['OPENAI_KEY']
# Create an instance of the OpenAI class, client
client = OpenAI(api_key=OPENAI_KEY)


# Pretty print the message with different colors based on the role
# This is useful when we are dealing with function calling, as it can get
# complicated to understand what state the code is in
def pretty_print_message(message):
    # Dictionary to map the role to a color
    role_to_color = {
        "system": "red",
        "user": "green",
        "assistant": "blue",
        "function": "magenta",
    }
    # System Prompt
    if message["role"] == "system":
        print(colored(f"system: {message['content']}", role_to_color[message["role"]], force_color='True'))
    # User message, not used when using input()
    elif message["role"] == "user":
        print(colored(f"user: {message['content']}", role_to_color[message["role"]], force_color='True'))
    # AI message when calling a function
    elif message["role"] == "assistant" and message.get("function_call"):
        print(colored(f"assistant: {message['function_call']}", role_to_color[message["role"]], force_color='True'))
    # Normal AI message
    elif message["role"] == "assistant" and not message.get("function_call"):
        print(colored(f"assistant: {message['content']}", role_to_color[message["role"]], force_color='True'))
    # Function message
    elif message["role"] == "function":
        print(colored(f"function ({message['name']}): {message['content']}", role_to_color[message["role"]],
                      force_color='True'))


def conversation():
    # Create an empty list to store our messages
    message_list = []
    # Create a system prompt
    system_prompt = {'role': 'system', 'content': "You are a helpful assistant."}
    # print out the system prompt
    pretty_print_message(system_prompt)
    # Add the system prompt to the message list
    message_list.append(system_prompt)
    # Loop infinitely
    while True:
        # Get user input
        user_input = input("You: ")
        # Format the user input into a dictionary for the api
        user_prompt = {'role': 'user', 'content': user_input}
        # Add the user input to the message list
        message_list.append(user_prompt)
        # Make the api call
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=message_list,
        )
        # Add the AI's response to the message list, and then loop again
        message = {'role': 'assistant', 'content': completion.choices[0].message.content}
        # print out the AI's response
        pretty_print_message(message)
        # Add the AI's response to the message list
        message_list.append(message)


# Functions we will be making this week

def get_bitcoin_price():
    api_url = "https://min-api.cryptocompare.com/data/generateAvg?fsym=BTC&tsym=USD&e=coinbase"

    try:
        response = requests.get(api_url)
        data = response.json()
        raw_data = data.get("RAW")

        if raw_data:
            return f"The price of bitcoin is {raw_data['PRICE']}"
    except Exception as e:
        return e
print(get_bitcoin_price())


def execute_function_call(message):
    pass


tools = []


def conversation_with_functions():
    pass


#conversation()

# conversation_with_functions
