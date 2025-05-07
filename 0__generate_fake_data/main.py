import os 
import json
import uuid
import time
from faker import Faker
from google.cloud import bigquery
from dotenv import load_dotenv

load_dotenv()
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("GCP_DATASET_ID")
TABLE_ID = os.getenv("GCP_TABLE_ID")
ROW_COUNT = 1000

# Initialisation Faker
fake = Faker()
Faker.seed(42)

def generate_unique_users(n):
    seen_emails = set()
    users = []
    while len(users) < n:
        first_name = fake.first_name()
        last_name = fake.last_name()
        email = fake.unique.email()
        living_city = fake.city()
        living_country = fake.country()
        birth_date = fake.date_of_birth(minimum_age=18, maximum_age=80).isoformat()
        profession = fake.job()
        user_id = str(uuid.uuid4())
        if email not in seen_emails:
            users.append({
                "id": user_id,
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "living_city": living_city,
                "living_country": living_country,
                "birth_date": birth_date,
                "profession": profession
            })
            seen_emails.add(email)
    return users

def create_dataset_if_not_exists(client):
    dataset_ref = bigquery.Dataset(f"{PROJECT_ID}.{DATASET_ID}")
    try:
        client.get_dataset(dataset_ref)
    except Exception:
        client.create_dataset(dataset_ref)
        print(f"Dataset {DATASET_ID} created.")

def drop_table_if_exists(client):
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    try:
        client.delete_table(table_ref, not_found_ok=True)
        print(f"Table {table_ref} deleted if exists.")
    except Exception as e:
        print(f"Error while deleting the table: {e}")

def create_table_if_not_exists(client):
    schema = [
        bigquery.SchemaField("id", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("first_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("last_name", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("email", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("city", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("country", "STRING", mode="REQUIRED"),
        bigquery.SchemaField("birth_date", "DATE", mode="REQUIRED"),
        bigquery.SchemaField("profession", "STRING", mode="REQUIRED"),
    ]
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    try:
        client.get_table(table_ref)
    except Exception:
        table = bigquery.Table(table_ref, schema=schema)
        client.create_table(table)
        print(f"Table {table_ref} created.")

def insert_users(client, users):
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"
    errors = client.insert_rows_json(table_ref, users)
    if errors:
        print("Errors:", errors)
    else:
        print(f"{len(users)} users inserted into {table_ref}.")

def main():
    
    # Auth handled by env or default credentials
    client = bigquery.Client(project=PROJECT_ID)
    create_dataset_if_not_exists(client)
    time.sleep(1)
    
    drop_table_if_exists(client)
    time.sleep(1)
    
    create_table_if_not_exists(client)
    time.sleep(1)
    
    users = generate_unique_users(ROW_COUNT)
    insert_users(client, users)
    
    # Save IDs in JSON file to be used in Locust
    user_ids = [user["id"] for user in users]
    output = {"user_ids": user_ids}
    output_path = os.path.join(os.path.dirname(__file__), "user_ids.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2)
    print(f"IDs saved at {output_path}")
    return "Done"

if __name__ == "__main__":
    main()
