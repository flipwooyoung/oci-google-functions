import io
import os
import json
import sys
import datetime

from fdk import response
import oci
from openai import OpenAI

#This automatically gets added if you add in your api key from the readme
API_KEY_STRING = os.environ['openai_key']
#If your too lazy (Heavily recommended you dont do this), uncomment the next line
#API_KEY_STRING = "your_api_key"

#Change this if you want to change how the GPT model should function.
GPT_PROMPT = "You will be given a paragraph about a foosball match narration. Clean it up to be appropriate, politically friendly, without changing the content or length at all."

#Change this to be your TEXT PROMPT to pass to GPT
TEXT_PROMPT = "And it's all over here. Folks. As the panthers have dominated the hornets in this 3 minute foosball thriller, the final score a convincing 50 in favor of the panthers dressed in their sleek black shirts, which appear as blue in our database. Let's take a look at the stats and what a telling story they tell. The panthers had a slight edge in possession with 54.57% of the ball, while, the hornets managed 45.43%. And what they did with that possession was pure magic as they found the back of the net 5 times in terms of maturation, we played out the full 300.92 seconds and what an exciting 5 minutes it was and let's not forget this was a 2 player effort, with each team relying on their individual skills to get the job done. But. In the end it was the panthers day and they celebrated with a resounding victory. The. Hornets, on, the other hand, will, have to go back to the drawing board and regroup for their next match."

def handler(ctx, data: io.BytesIO=None):

    try:
        data_bytes = data.getvalue()
        data_str = data_bytes.decode('utf-8')

        resp = openai_transform(TEXT_PROMPT)
    except (Exception, ValueError) as ex:
        logging.getLogger().error(str(ex))

    

    return response.Response(
        ctx,
        response_data=json.dumps(resp),
        headers={"Content-Type": "application/json"}
    )

def openai_transform(text_prompt):
    client = OpenAI(api_key=API_KEY_STRING)

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": GPT_PROMPT},
            {
                "role": "user",
                "content": text_prompt
            }
        ]
    )

    gpt_message = completion.choices[0].message
    text_content = gpt_message.content

    response = text_content

    return response
