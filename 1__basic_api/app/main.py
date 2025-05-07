import os
from dotenv import load_dotenv
from google.cloud import bigquery
from fastapi import FastAPI, HTTPException

app = FastAPI() 
bq_client = bigquery.Client()

load_dotenv()
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATASET_ID = os.getenv("GCP_DATASET_ID")
TABLE_ID = os.getenv("GCP_TABLE_ID")

@app.get('/hello')
async def hello():
    """
    Endpoint to test API
    """
    return {"message": "Hello, World!"}

@app.get("/users_bq/{user_id}")
async def get_user(user_id: str):
    """
    Get user information from BigQuery
    """
    query = f"""
        SELECT 
            first_name,
            last_name,
            email,
            city,
            country,
            birth_date,
            profession
        FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        WHERE id = @user_id
    """
    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("user_id", "STRING", user_id)
        ]
    )

    try:
        query_job = bq_client.query(query, job_config=job_config)
        results = query_job.result()

        # Convert results to a dictionary
        user_data = [dict(row) for row in results]
        if not user_data:
            raise HTTPException(status_code=404, detail="User not found")

        return user_data[0]  # Return the first result (unique id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error querying BigQuery: {str(e)}")
