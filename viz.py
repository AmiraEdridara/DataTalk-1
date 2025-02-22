import requests
import pandas as pd
import json

# IBM WatsonX API Credentials (Replace with actual values)
IBM_API_KEY = "hIesJ8JoLKwzsKLzRQm7zmWduGKBTpIv0-ltHEgX8XyX"
IBM_AUTH_URL = "https://iam.cloud.ibm.com/identity/token"  
IBM_MODEL_ID = "granite-13b-instruct-v2"
IBM_PROJECT_ID = "e91a92fb-a19e-4ce7-bede-65a6855a1c09"  
IBM_ENDPOINT = f"https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-01"

# Function to get IBM WatsonX Bearer Token
def get_ibm_token():
    headers = {
        "Content-Type": "application/x-www-form-urlencoded"
    }
    payload = {
        "grant_type": "urn:ibm:params:oauth:grant-type:apikey",
        "apikey": IBM_API_KEY
    }

    response = requests.post(IBM_AUTH_URL, headers=headers, data=payload)
    
    if response.status_code == 200:
        return response.json()["access_token"]
    else:
        raise Exception(f"⚠️ Failed to retrieve IBM token: {response.status_code} - {response.text}")

# Function to process visualization request
def process_visualization(user_query, df):
    token = get_ibm_token()  # Get fresh IBM token

    # Constructing Prompt for IBM WatsonX
    prompt = f"""
    Convert this natural language query into a visualization code using **Plotly**:
    Query: {user_query}

    Dataset structure:
    {df.head(3).to_dict()}

    **Rules:**
    - Use **Plotly Express (`px`)** or **Plotly Graph Objects (`go`)** for visualizations.
    - Assign the result to `fig` for visualizations.
    - Do **not** use Matplotlib (`plt`).
    - Do **not** redefine `df` or import Pandas.
    - Return only the code, no explanations.
    - Ensure the code is valid Python syntax.
    """

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "model_id": IBM_MODEL_ID,
        "project_id": IBM_PROJECT_ID,
        "input": prompt,
        "parameters": {
            "max_new_tokens": 200,
            "temperature": 0.7
        }
    }

    response = requests.post(IBM_ENDPOINT, headers=headers, json=payload)

    # Check for successful response
    if response.status_code == 200:
        response_data = response.json()
        if "results" in response_data and len(response_data["results"]) > 0:
            code = response_data["results"][0]["generated_text"].strip()
            code = code.replace("```python", "").replace("```", "").strip()

            # Prevent code from redefining the dataset
            if "pd.DataFrame" in code or "import pandas" in code or "df =" in code:
                return "⚠️ Invalid code generated. Skipping execution."

            return code
        else:
            return f"⚠️ Unexpected response format: {response_data}"
    else:
        return f"⚠️ API request failed with status code {response.status_code}: {response.text}"
