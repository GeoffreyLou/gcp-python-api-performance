import json 
import random
from pathlib import Path
from locust import HttpUser, task, between


class GetUserInformation(HttpUser):
    wait_time = between(1, 3)
    
    def load_user_ids(self):
        """
        Load user IDs from a JSON file.
        """
        current_dir = Path(__file__).parent.parent
        json_path = current_dir / "0__generate_fake_data" /"user_ids.json"
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data["user_ids"]    

    @task
    def get_user_information(self):
        """
        Get user information from the API.
        """
        user_ids = self.load_user_ids()
        random_id = random.choice(user_ids)
        self.client.get(f"/users_bq/{random_id}") 
