import os
import json
from audio_embed import  select_related_audio
import chromadb
import pydantic
import openai

with open('./key.txt', 'r') as fr:
    api_key = fr.read().strip()

openai_client = openai.OpenAI(api_key=api_key)


with open('./webapp_testable_sounds.txt', 'r+') as fr:
    notindb = [os.path.join('dataset', x.strip()) for x in fr.readlines()]

chroma_client = chromadb.PersistentClient(path="webapp_db/")
collection = chroma_client.get_collection('documents')



eval_prompt = """
You are tasked with evaluating if a mechanic had diagnosed the issue correctly. 
The mechanic wll try and tell you the the Issue.

You are given the true issue, and the mechanic suggests a maximum of 5 issues. The mechanic doesn't try and guess the 
true issue verbatim, but rather the same idea. 

Example:
Problem: The true issue is a bad-serpentine-belt. The mechanic suggests python dictionaries: 'worn-serpentine-belt', 'bad-ac-compressor'
Result: The mechanic has sucessfully diagnosed the at least problem. 

If the mechanic has sucessfully diagnosed the problem, your 'verdict' is boolean true.
If the mechanic failed to identity the problem, your 'verdict' is boolean false.

For the verdict, a 'reason' must be appended, which is 20 words or less. Your output should be in the form of JSON.


The true issue: {problem}
"""

class AnswerSchema(pydantic.BaseModel):
    reason: str
    verdict: bool


def evaluate (prob: str, solutions): 
    try:
        print(solutions)
        completion = openai_client.beta.chat.completions.parse( 
                model='o3-mini',
                messages=[
                    { "role": "system", "content": eval_prompt.format(problem=prob) },
                    { "role": "user", "content": f"I, the mechanic, suggest {solutions}" }
                ],
                response_format=AnswerSchema
        )
        event = completion.choices[0].message.parsed
        if not event:
            return { 'verdict': None, 'reason': 'OpenAI failed to respond'}
        return event.dict()
    except Exception as e:
        import traceback
        print(e)
        print(traceback.format_exc())
        return { 'verdict': None, 'reason': 'OpenAI no respond'}



if __name__ == '__main__':
    evaluation = { 'distribution': {'yes': 0, 'no': 0, 'na': 0}, 'judgements': [] }
    for entr in notindb:
        solutions = select_related_audio(collection, entr)
        result = evaluate(entr, solutions['metadatas'][0])
        if result['verdict'] == None:
            evaluation['distribution']['na'] += 1
        if result['verdict'] == True:
            evaluation['distribution']['yes'] += 1
        elif result['verdict'] == False:
            evaluation['distribution']['no'] += 1
        else:
            print('something went wrong while evaluating', result)
            ...
        evaluation['judgements'].append({ 'id': entr, **result })
    
    import time
    timestr = time.strftime("%Y%m%d-%H%M%S")

    with open(f'./eval-{timestr}.json', 'w+') as fw:
        json.dump(evaluation, fw)
    dist = evaluation['distribution']
    total = dist['yes']+dist['no']+dist['na']
    print(f'Total {total} yes={dist['yes']/total} no={dist['no']/total} na={dist['na']/total}' )
