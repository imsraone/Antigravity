import os
import re
from openai import AzureOpenAI
from dotenv import load_dotenv

load_dotenv()

def generate_sql_from_prompt(schema: str, user_prompt: str) -> str:
    """
    Generates a SQL query using Azure OpenAI based on the provided schema and user prompt.
    """

    api_key = ""
    api_base = ""
    api_version = ""
    deployment_name = ""
    
    if not all([api_key, api_base, deployment_name]):
        print("Missing Azure OpenAI credentials in environment variables.")
        # Fallback to internal mock for demonstration if config is missing, 
        # but preferably we want to fail or warn. For now let's try to proceed 
        # or return a specific error message as SQL comment.
        return "-- Error: Missing Azure OpenAI credentials. Please configure .env file."

    client = AzureOpenAI(
        api_key=api_key,
        api_version=api_version,
        azure_endpoint=api_base
    )

    system_message = f"""You are a SQL expert. 
    Your task is to convert natural language questions into valid SQLite SQL queries based on the following schema:
    
    {schema}
    
    IMPORTANT:
    - Return ONLY the SQL query. 
    - Do not include markdown formatting like ```sql or ```.
    - Do not include explanations.
    """

    try:
        response = client.chat.completions.create(
            model=deployment_name,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0
        )
        
        sql_query = response.choices[0].message.content.strip()
        
        # Cleanup potential markdown if the model ignores instruction
        sql_query = re.sub(r"```sql", "", sql_query, flags=re.IGNORECASE)
        sql_query = sql_query.replace("```", "").strip()
        
        return sql_query
        
    except Exception as e:
        print(f"Error calling Azure OpenAI: {e}")
        return f"-- Error generating SQL: {str(e)}"
