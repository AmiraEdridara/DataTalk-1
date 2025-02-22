import requests
import pandas as pd
import json

# IBM WatsonX API Credentials (Replace with your actual API key and endpoint)
IBM_API_KEY = "ApiKey-9eec6e59-90b1-4006-9a06-eafe8379fd02"
IBM_ENDPOINT = "https://us-south.ml.cloud.ibm.com"

def process_visualization(user_query, df):
    columns = df.columns.tolist()
    column_string = ', '.join(columns)

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
        "Authorization": f"Bearer {IBM_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "input": {"text": prompt},
        "alternate_intents": False
    }

    response = requests.post(IBM_ENDPOINT, headers=headers, json=payload)

    # Check for successful response
    if response.status_code == 200:
        response_data = response.json()

        if 'output' in response_data:
            code = response_data["output"]["generic"][0]["text"].strip()
            code = code.replace("```python", "").replace("```", "").strip()

            # Prevent code from redefining the dataset
            if "pd.DataFrame" in code or "import pandas" in code or "df =" in code:
                return "⚠️ Invalid code generated. Skipping execution."

            return code
        else:
            return f"⚠️ Unexpected response format: {response_data}"
    else:
        return f"⚠️ API request failed with status code {response.status_code}: {response.text}"
