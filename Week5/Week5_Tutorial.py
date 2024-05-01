# pip install openai
from openai import OpenAI
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


# Pretty print the message based on the role
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


# New functions
# Our api call where we get the current price of bitcoin
def get_bitcoin_price():
    # The url for our api
    api_url = "https://min-api.cryptocompare.com/data/generateAvg?fsym=BTC&tsym=USD&e=coinbase"
    try:
        # Call the api to get the data
        response = requests.get(api_url)
        data = response.json()
        # Grab the raw section of the data
        raw_data = data.get("RAW")
        # If the raw data exists, return it
        if raw_data:
            return f"The price of bitcoin is ${raw_data['PRICE']}"
    # Error handling
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except Exception as ex:
        print(f"An error occured: {ex}")
    return "The function failed to run"

def get_crypto_price(currency, currency_code):
    #Instead of hardcoding the currency code, we can pass it as a parameter
    api_url = f"https://min-api.cryptocompare.com/data/generateAvg?fsym={currency_code}&tsym=USD&e=coinbase"
    try:
        # Call the api to get the data, just like normal
        response = requests.get(api_url)
        data = response.json()
        # Grab the raw section of the data
        raw_data = data.get("RAW")
        # If the raw data exists, return it
        if raw_data:
            # Return the price of the currency, making sure to say the right currency name
            return f"The price of {currency} is ${raw_data['PRICE']}"
    # Error handling
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
    except Exception as ex:
        print(f"An error occured: {ex}")
    return "The function failed to run"

# Function where we execute the function call
# All it does is read the function name from the AI response, and if we have it configured, call the function
def execute_function_call(message):
    # Check if the AI is calling the function get_bitcoin_price
    if message.tool_calls[0].function.name == "get_bitcoin_price":
        # run that function, and store the string output
        results = get_bitcoin_price()

    elif message.tool_calls[0].function.name == "get_crypto_price":
        # Load the arguments from our function call
        # These are the parameters we will pass to our function
        # Its returned as a string, so we will need to convert it into a json object using loads
        args = json.loads(message.tool_calls[0].function.arguments)
        # Run the function with the arguments, and store the string output
        results = get_crypto_price(args["currency"], args["currency_code"])
    # If the function does not exist, return an error message
    else:
        # Return a failure string so the AI knows what went wrong
        results = f"Error: function {message.tool_calls[0].function.name} does not exist"
    return results


# List of tools we have
# This is where we define the functions we have available to us, their descriptions, and their parameters
# For this first test, we are using a function with no parameters
tools = [
    {
        "type": "function",
        "function": {
            "name": "get_bitcoin_price",
            "description": "Returns the current price of bitcoin",
        }
    },
    # This is our new function with support for parameters
    # It takes in a currency name and a currency code
    {
        "type": "function",
        "function": {
            "name": "get_crypto_price",
            "description": "Returns the current price of a cryptocurrency given its name and code",
            "parameters": {
                "type": "object",
                "properties": {
                    "currency": {
                        "type": "string",
                        "description": "The name of the cryptocurrency, e.g., Bitcoin"
                    },
                    "currency_code": {
                        "type": "string",
                        "description": "The code of the cryptocurrency, e.g., BTC"
                    }
                },
                "required": ["currency", "currency_code"]
            }
        }
    }
]


# Our modified conversation function with function calling
def conversation_with_functions():
    # Our message list
    message_list = []
    # Just like before, we start with a system prompt
    system_prompt = {'role': 'system', 'content': "You are a helpful assistant. If asked to, you can get the current price of bitcoin. You can also get the price of any cryptocurrency given its name and code."}
    # Print out the system prompt
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

        # Make the api call, just like normal
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=message_list,
            # Pass in the tools we have available
            tools=tools,
        )
        # Store the message from the api, this is not the string, this is the entire message object
        # This means that is has info about if a function is being called or not
        message = completion.choices[0].message
        # print(message)
        # If the message has a function call, we need to execute it
        if completion.choices[0].message.tool_calls:
            # Execute the function call stored in the message
            results = execute_function_call(completion.choices[0].message)
            # Create a response message with the function results
            # This includes the tool call id, the function name, and the results of the function
            response = {"role": "function", "tool_call_id": message.tool_calls[0].id,
                        "name": message.tool_calls[0].function.name, "content": results}
            # Print out the response
            pretty_print_message(response)
            # Add the response to the message list, just like we would a normal message
            message_list.append(response)
            # We got the function response, but this is just the raw output from the function
            # We want the AI to say the message, so we have to make another completion
            completion = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=message_list,
            )
            # Get the AI's response, and print it out, just like you would a normal message
            response = {'role': 'assistant', 'content': completion.choices[0].message.content}
            pretty_print_message(response)
            message_list.append(response)
        # Normal AI message without function calling
        else:
            response = {'role': 'assistant', 'content': completion.choices[0].message.content}
            pretty_print_message(response)
            message_list.append(response)


# conversation()
conversation_with_functions()
