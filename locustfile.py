import os
from locust import HttpUser, task, between


current_dir = os.path.abspath(__file__)
base_path = os.path.abspath(os.path.join(current_dir, "../../TalentMatrix"))

class LoadTestUser(HttpUser):
    wait_time = between(1, 3)

    @task
    def test_add_jd_to_database(self):
        """Test the /add_jd_to_database endpoint."""
        self.client.get("/add_jd_to_database", params={"jd_path": os.path.join(base_path, "/data/dataset/jobDescriptions/JD_data.csv")})

    @task
    def test_retrieve_collection(self):
        """Test the /api/retrieve endpoint."""
        self.client.get("/api/retrieve", params={
            "resume_path": os.path.join(base_path, "data/dataset/trainResumes/candidate_001.pdf"),
            "top_k": 2
        })