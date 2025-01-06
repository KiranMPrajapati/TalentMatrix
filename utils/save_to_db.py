import psycopg2

from config import CONFIG_DATA

# PostgreSQL connection parameters
db_params = {
    "dbname": CONFIG_DATA['db_params']['dbname'],
    "user": CONFIG_DATA['db_params']['user'],
    "password": CONFIG_DATA['db_params']['password'],
    "host": CONFIG_DATA['db_params']['host'],
    "port": CONFIG_DATA['db_params']['port']
}

def save_to_postgresql(results):
    try:
        # Connect to PostgreSQL
        conn = psycopg2.connect(**db_params)
        cur = conn.cursor()

        for index, result in enumerate(results):
            query = """
            INSERT INTO jd_resume_match_result (resume_path, job_description, similarity_score, chunk_id, rank)
            VALUES (%s, %s, %s, %s, %s);
            """
            cur.execute(query, (
                result['resume_path'],
                result['page_content'],
                result['similarity_score'],
                result['chunk_id'],
                index,
            ))
        
        conn.commit()

        print("Data saved successfully!")

        cur.close()
        conn.close()

    except Exception as e:
        print(f"Failed to save data to PostgreSQL: {e}")
        raise

# Example usage
# resume_path = "/path/to/resume.pdf"
# results = [
#     {
#         'page_content': 'Job: machine learning engineer\n Position: AI/ML\n Location: Zurich\n Job Description: [',
#         'metadata': {},
#         'similarity_score': 0.43,
#         'chunk_id': 'id_3658'
#     },
#     {
#         'page_content': 'Job: model\n Position: Artificial Intelligence Intern\n Location: Clamart, Hauts-de-Seine\n Job Description: [',
#         'metadata': {},
#         'similarity_score': 0.37,
#         'chunk_id': 'id_2932'
#     }
# ]

# save_to_postgresql(resume_path, results, db_params)
