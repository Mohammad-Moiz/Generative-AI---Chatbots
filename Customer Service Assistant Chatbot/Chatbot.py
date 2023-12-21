import openai
import streamlit as st
import json

openai.api_key = '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'

def get_completion_from_messages(messages, model="gpt-3.5-turbo", temperature=0, max_tokens=500):
    response = openai.ChatCompletion.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )
    return response.choices[0].message["content"]

def process_user_message(user_input, all_messages, debug=True):
    delimiter = "```"

    # Step 1: Check input to see if it flags the Moderation API or is a prompt injection
    response = openai.Moderation.create(input=user_input)
    moderation_output = response["results"][0]

    if moderation_output["flagged"]:
        print("Step 1: Input flagged by Moderation API.")
        return "Sorry, we cannot process this request."

    def read_string_to_list(input_string):
        if input_string is None:
            return None

        try:
            input_string = input_string.replace("'", "\"")  # Replace single quotes with double quotes for valid JSON
            data = json.loads(input_string)
            return data
        except json.JSONDecodeError:
            print("Error: Invalid JSON string")
        return None

    category_and_product_response = read_string_to_list(user_input)

    if debug: print("Step 1: Input passed moderation check.")

    # Step 2: Extract the list of products

    def read_string_to_list(input_string):
        if input_string is None:
            return None

        try:
            input_string = input_string.replace("'", "\"")  # Replace single quotes with double quotes for valid JSON
            data = json.loads(input_string)
            return data
        except json.JSONDecodeError:
            print("Error: Invalid JSON string")
        return None

    category_and_product_list = read_string_to_list(category_and_product_response)
    print(category_and_product_list)

    if debug: print("Step 2: Extracted list of products.")

    # Step 3: If products are found, look them up
    def generate_output_string(output_string, debug=True):
        if output_string is None:
            return None

        try:
            output_string = output_string.replace("'", "\"")  # Replace single quotes with double quotes for valid JSON
            data = json.loads(output_string)
            return data
        except json.JSONDecodeError:
            print("Error: Invalid JSON string")
            return None

    product_information = generate_output_string(category_and_product_response)
    print(product_information)

    if debug: print("Step 3: Looked up product information.")

    # Step 4: Answer the user question
    system_message = f"""
    You are a customer service assistant for a large electronic store. \
    Respond in a friendly and helpful tone, with concise answers. \
    Make sure to ask the user relevant follow-up questions.
    """
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': f"{delimiter}{user_input}{delimiter}"},
        {'role': 'assistant', 'content': f"Relevant product information:\n{product_information}"}
    ]

    final_response = get_completion_from_messages(all_messages + messages)
    if debug: print("Step 4: Generated response to user question.")
    all_messages = all_messages + messages[1:]

    # Step 5: Put the answer through the Moderation API
    response = openai.Moderation.create(input=final_response)
    moderation_output = response["results"][0]

    if moderation_output["flagged"]:
        if debug: print("Step 5: Response flagged by Moderation API.")
        return "Sorry, we cannot provide this information."

    if debug: print("Step 5: Response passed moderation check.")

    # Step 6: Ask the model if the response answers the initial user query well
    user_message = f"""
    Customer message: {delimiter}{user_input}{delimiter}
    Agent response: {delimiter}{final_response}{delimiter}

    Does the response sufficiently answer the question?
    """
    messages = [
        {'role': 'system', 'content': system_message},
        {'role': 'user', 'content': user_message}
    ]
    evaluation_response = get_completion_from_messages(messages)

    if debug: print("Step 6: Model evaluated the response.")

    # Step 7: If yes, use this answer; if not, say that you will connect the user to a human
    if "Y" in evaluation_response:  # Using "in" instead of "==" to be safer for model output variation (e.g., "Y." or "Yes")
        if debug: print("Step 7: Model approved the response.")
        return final_response, all_messages
    else:
        if debug: print("Step 7: Model disapproved the response.")
        neg_str = "I'm unable to provide the information you're looking for. I'll connect you with a human representative for further assistance."
        return neg_str, all_messages

def collect_messages(user_input, context, debug=False):
    if debug: print(f"User Input = {user_input}")
    if user_input == "":
        return

    response, context = process_user_message(user_input, context, debug=False)
    context.append({'role': 'assistant', 'content': f"{response}"})
    st.markdown(f"**User:** {user_input}")
    st.markdown(f"**Assistant:** {response}")

# Set up Streamlit app
st.title("Customer Service Assistant")
context = [{'role': 'system', 'content': "You are a Service Assistant"}]

# Get user input
user_input = st.text_input("Enter your message:")
button_conversation = st.button("Send Message")

# Handle button click
if button_conversation:
    collect_messages(user_input, context)

# Display conversation history
st.subheader("Conversation History:")
for message in context:
    st.markdown(f"**{message['role']}**: {message['content']}")

