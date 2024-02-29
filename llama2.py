import os
from dotenv import load_dotenv
import replicate
from replicate.client import Client

load_dotenv()

replicate = Client(api_token=os.getenv['REPLICATE_API_TOKEN'])

# Generate output
def generate_response(content,input):
    output = replicate.run(
        "meta/llama-2-70b-chat:02e509c789964a7ea8736978a43525956ef40397be9033abf9fd2badfe68c9e3",
        input={
            "debug": False,
            "top_k": 1,
            "top_p": 1,
            "prompt": input,
            "temperature": 0.9,
            "system_prompt": content,
            "max_new_tokens": 500,
            "min_new_tokens": -1
        }
    )