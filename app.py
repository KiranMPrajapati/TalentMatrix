from flask import Flask, jsonify, request
from main import add_jd_collection, retrieve


app = Flask(__name__)


@app.route('/add_jd_to_database', methods=['GET'])
def add_jd_to_database():
    """Route to add job descriptions to the database."""
    jd_path = request.args.get('jd_path', 'JD_data.csv') 
    try:
        add_jd_collection(jd_path)
        return jsonify({"message": "Created collection successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/retrieve', methods=['GET'])
def retrieve_collection():
    """Route to retrieve job descriptions based on a resume."""
    resume_path = request.args.get('resume_path')
    top_k = int(request.args.get('top_k', 2))

    if not resume_path:
        return jsonify({"error": "Missing 'resume_path' parameter"}), 400

    try:
        results = retrieve(resume_path, top_k)
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=8000)
