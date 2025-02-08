import boto3
import time

# Initialize the DynamoDB resource
dynamodb = boto3.resource('dynamodb')

# Define the table name and schema
table_name = "TransactionsTable"

def create_transactions_table():
    try:
        # Create the table
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'id',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'id',
                    'AttributeType': 'S'  # String type
                }
            ],
            BillingMode='PAY_PER_REQUEST'  # Cost-effective on-demand pricing
        )

        print(f"Creating table '{table_name}', this may take a few seconds...")
        # Wait until the table exists before returning
        table.meta.client.get_waiter('table_exists').wait(TableName=table_name)
        print(f"Table '{table_name}' created successfully!")
    
    except Exception as e:
        print(f"Error creating table: {e}")

if __name__ == "__main__":
    create_transactions_table()
