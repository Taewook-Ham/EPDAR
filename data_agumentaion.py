import ijson

import json

from decimal import Decimal

from tqdm import tqdm

import openai





openai.api_key = ""
#openai.api_key = ""





input_json_file_path = "./np/nq-train.json"

output_json_file_path = 'output_data_wiki.json' 





def add_data(data, output_data):

    question = data["question"]



   

    generated_sentence = generate_sentence(question)



 

    positive_ctx = {

        "title": "Generated",

        "text": generated_sentence,

        "score": 1000,

        "title_score": 0,

        "passage_id": None,

    }





    if "positive_ctxs" in data:

        data["positive_ctxs"].append(positive_ctx)

    else:

        data["positive_ctxs"] = [positive_ctx]





    output_data.append(data)





def generate_sentence(question):

    prompt = f"Below is a question from the Natural Question Dataset. Generate a Wikipedia passage containing the {Answer} to this question: {Question}.'"

    response = openai.Completion.create(

        engine="text-davinci-003",  

        prompt=prompt,

        max_tokens=150 

    )

    return response.choices[0].text





def save_data(data, output_file):

    

    output_file.write(json.dumps(data, default=lambda x: float(x) if isinstance(x, Decimal) else None))

    output_file.write('\n')




resumed_index = 47210





output_data = []

num_processed = 0  

batch_size = 100 



with open(input_json_file_path, 'r') as json_file:

    data_stream = ijson.items(json_file, 'item')

    

    

    for _ in range(resumed_index):

        next(data_stream)



    for data in tqdm(data_stream):

        add_data(data, output_data)

        num_processed += 1



        if num_processed % batch_size == 0:

            

            with open(output_json_file_path, 'a') as output_file:

                for saved_data in output_data:

                    save_data(saved_data, output_file)

                output_data = []





with open(output_json_file_path, 'a') as output_file:

    for saved_data in output_data:

        save_data(saved_data, output_file)

        output_data = []




