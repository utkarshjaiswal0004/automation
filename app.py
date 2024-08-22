from flask import Flask, request, jsonify
import json
import subprocess
import os

app = Flask(__name__)

@app.route('/process', methods=['POST'])
def process_json():
    data = request.json

    # Save JSON data to a file
    with open('data.json', 'w') as f:
        json.dump(data, f)

    # Initialize the output variable
    image_urls = {}

    try:
        # Call the Selenium script with the JSON data
        subprocess.run(
            ['python', 'selenium_script.py', json.dumps(data)],
            capture_output=True, text=True
        )

        # Read the JSON file created by the Selenium script
        if os.path.exists('image_urls.json'):
            with open('image_urls.json', 'r') as f:
                image_urls = json.load(f)
        else:
            image_urls = {"error": "No image URLs found."}

    except Exception as e:
        image_urls = {"error": f"Failed to process Selenium script: {e}"}
    
    finally:
        # Ensure the data.json and image_urls.json files are deleted after processing
        if os.path.exists('data.json'):
            os.remove('data.json')
        if os.path.exists('image_urls.json'):
            os.remove('image_urls.json')

    return jsonify(image_urls)

if __name__ == '__main__':
    app.run(debug=True)
