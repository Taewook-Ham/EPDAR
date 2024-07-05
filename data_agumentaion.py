import ijson
import json
from decimal import Decimal
from tqdm import tqdm
import openai

# API 키 설정 (본인의 키로 변경)
openai.api_key = ""
#openai.api_key = ""

# 대용량 JSON 파일의 경로
input_json_file_path = "./np/nq-train.json"
output_json_file_path = 'output_data_wiki.json'  # 저장할 JSON 파일 경로

# 데이터 처리 함수
def add_data(data, output_data):
    question = data["question"]

    # 질문을 사용하여 GPT-3로 문장 생성
    generated_sentence = generate_sentence(question)

    # positive_ctxs에 추가 데이터 생성
    positive_ctx = {
        "title": "Generated",
        "text": generated_sentence,
        "score": 1000,
        "title_score": 0,
        "passage_id": None,
    }

    # data에 positive_ctxs를 추가
    if "positive_ctxs" in data:
        data["positive_ctxs"].append(positive_ctx)
    else:
        data["positive_ctxs"] = [positive_ctx]

    # 수정된 데이터를 리스트에 추가
    output_data.append(data)

# GPT-3를 사용하여 문장 생성하는 함수
def generate_sentence(question):
    prompt = f"Generate a Wikipedia passage for the following question: '{question}'"
    response = openai.Completion.create(
        engine="text-davinci-003",  # 엔진을 text-davinci-003로 수정
        prompt=prompt,
        max_tokens=150  # 생성된 문장의 최대 길이를 150으로 설정
    )
    return response.choices[0].text

# 수정된 데이터를 저장하는 함수
def save_data(data, output_file):
    # data를 파일에 추가
    output_file.write(json.dumps(data, default=lambda x: float(x) if isinstance(x, Decimal) else None))
    output_file.write('\n')

# 중단된 위치를 설정 (반복 작업으로 이전까지 처리한 데이터 수)
# 여기서는 3120번째 데이터에서 중단되었다고 가정합니다.
resumed_index = 47210

# 입력 파일을 읽고 데이터 처리
output_data = []
num_processed = 0  # 처리된 데이터 수
batch_size = 100  # 일정한 간격으로 저장할 배치 크기

with open(input_json_file_path, 'r') as json_file:
    data_stream = ijson.items(json_file, 'item')
    
    # 데이터를 처리할 때 resumed_index까지 스킵합니다.
    for _ in range(resumed_index):
        next(data_stream)

    for data in tqdm(data_stream):
        add_data(data, output_data)
        num_processed += 1

        if num_processed % batch_size == 0:
            # 중간 결과를 파일로 저장
            with open(output_json_file_path, 'a') as output_file:
                for saved_data in output_data:
                    save_data(saved_data, output_file)
                output_data = []

# 마지막 남은 데이터를 저장
with open(output_json_file_path, 'a') as output_file:
    for saved_data in output_data:
        save_data(saved_data, output_file)
        output_data = []

print("데이터 처리 및 저장이 완료되었습니다.")
