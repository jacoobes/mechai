import os
import chromadb
import pydantic
import openai

with open('./key.txt', 'r') as fr:
    api_key = fr.read().strip()

openai_client = openai.OpenAI(api_key=api_key)


with open('./webapp_testable_sounds.txt', 'r+') as fr:
    notindb = [os.path.join('dataset', x.strip()) for x in fr.readlines()]





eval_prompt = """
You are tasked with evaluating if a mechanic had diagnosed the issue correctly. 
The mechanic wll try and tell you the the Issue.

You are given the true issue, and the mechanic suggests a maximum of 5 issues. The mechanic doesn't try and guess the 
true issue verbatim, but rather the same idea. 

Example:
Problem: The true issue is a bad-serpentine-belt. The mechanic suggests worn-serpentine-belt, bad-ac-compressor, worn-generator-bearing.
Result: The mechanic has sucessfully diagnosed the at least problem. 

If the mechanic has sucessfully diagnosed the problem, your 'verdict' is boolean true.
If the mechanic failed to identity the problem, your 'verdict' is boolean false.

For the verdict, a 'reason' must be appended, which is 20 words or less. Your output should be in the form of JSON.


The problem: {problem}
"""

class AnswerSchema(pydantic.BaseModel):
    reason: str
    verdict: bool


def evaluate (problem: str): 
    solutions = []
    completion = openai_client.chat.completions.create( 
            model='o3-mini',
            messages=[
                { "role": "system", "content": eval_prompt.format(problem=prob) },
                { "role": "user", "content": "I think it is xyz" }
            ],
            response_format=AnswerSchema
    )
    event = completion.choices[0].message.parsed
    return event


