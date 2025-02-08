import streamlit as st
import boto3
import openai
import uuid
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set OpenAI API key from environment variable
openai.api_key = os.getenv("OPENAI_API_KEY")

# Initialize DynamoDB
dynamodb = boto3.resource('dynamodb')
table_name = "TransactionsTable"  # Ensure this matches your DynamoDB setup
table = dynamodb.Table(table_name, region_name="us-east-1")

# Streamlit UI
st.title("Enhanced Expense Tracker with OpenAI GPT")
st.write("Enter your expense details, and we will help extract the store, amount, and save them.")

# Mandatory date field
transaction_date = st.date_input("Transaction Date (Mandatory)")

# Freeform transaction message
transaction_message = st.text_area("Transaction Message (Mandatory)", placeholder="Enter the expense message...")

# Optional fields for store and amount (if LLM extraction is incorrect or missing)
optional_store = st.text_input("Specify Store Name (Optional)", placeholder="Provide store name if not in the message")
optional_amount = st.text_input("Specify Amount (Optional)", placeholder="Provide amount if not in the message")

if st.button("Extract and Save Transaction"):
    if not transaction_message.strip():
        st.error("Please enter a transaction message.")
    elif not transaction_date:
        st.error("Please select a transaction date.")
    else:
        try:
            # Call OpenAI API to extract details
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Extract the date, amount, and store name from the following transaction message and return in JSON format as {\"date\": \"\", \"amount\": \"\", \"store\": \"\"}"},
                    {"role": "user", "content": transaction_message}
                ]
            )

            # Parse OpenAI API response safely
            content = response['choices'][0]['message']['content'].strip()
            result = json.loads(content)
            # print(f"Extracted result: {result}")

            # Default to optional inputs if LLM extraction is incomplete
            store = result.get("store") if result.get("store") else optional_store
            amount = result.get("amount") if result.get("amount") else optional_amount

            if not store:
                st.error("Failed to determine store name. Please provide a valid input.")
            elif not amount:
                st.error("Failed to determine the amount. Please provide a valid input.")
            else:
                # Save to DynamoDB
                transaction_id = str(uuid.uuid4())
                item = {
                    "id": transaction_id,
                    "date": str(transaction_date),
                    "amount": amount,
                    "store": store,
                    "original_message": transaction_message
                }

                table.put_item(Item=item)

                # Display extracted and saved details
                st.success("Transaction saved successfully!")
                st.write(f"**Date:** {transaction_date}")
                st.write(f"**Amount:** {amount}")
                st.write(f"**Store:** {store}")

        except json.JSONDecodeError:
            st.error("Failed to parse the OpenAI response. Please try again with a different input.")
        except Exception as e:
            st.error(f"An error occurred: {e}")

# Option to view saved transactions
if st.checkbox("View Saved Transactions"):
    response = table.scan()
    items = response.get("Items", [])
    if items:
        for item in items:
            st.write(f"**Date:** {item['date']} | **Amount:** {item['amount']} | **Store:** {item['store']}")
    else:
        st.info("No transactions found.")
