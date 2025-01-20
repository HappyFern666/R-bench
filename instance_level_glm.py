from openai import OpenAI
from zhipuai import ZhipuAI
import base64
import json
import os
import time
import random
import io
from utils import draw_mask, draw_box, instance_qs_construct
from PIL import Image

#from config import token



# local:  http://192.168.56.1:8000/v1
# zeabur: https://jimmy-kimi.zeabur.app/v1

# This is for official kimi-api


# SET THE PATH OF THE DATASET JSON FILE HERE
json_file_path = os.path.join('data_filterd', 'instance-level_filterd.json')

# SET THE FOLDER PATH OF IMAGES IN THE DATASET HERE
image_folder_path = os.path.join('image', 'validation')

output_list = []
# SET THE PATH OF THE OUTPUT JSON FILE HERE
# 如果报错的话，试下手动创建这个文件并写入 []  (一个空列表)
output_path = 'glm_instance_level.json'

with open(output_path, 'r') as json_file:
    try:
        output_list = json.load(json_file)
    except Exception:
        print('not yet have json file')

id_set = set(datum['question_id'] for datum in output_list)

data = None
with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)

# 69 / 99 / 25
# "eyJhbGciOiJIUzUxMiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJ1c2VyLWNlbnRlciIsImV4cCI6MTc0MjAzMzA4MiwiaWF0IjoxNzM0MjU3MDgyLCJqdGkiOiJjdGZhamVoMDUyMmt2YjA2ZXM1ZyIsInR5cCI6InJlZnJlc2giLCJhcHBfaWQiOiJraW1pIiwic3ViIjoiY3RmYWplaDA1MjJrdmIwNmVzMzAiLCJzcGFjZV9pZCI6ImN0ZmFqZWgwNTIya3ZiMDZlczJnIiwiYWJzdHJhY3RfdXNlcl9pZCI6ImN0ZmFqZWgwNTIya3ZiMDZlczIwIiwic3NpZCI6IjE3MzAzMjEyMzk4NDE5NzEzNjMiLCJkZXZpY2VfaWQiOiI3MzkwMTg1ODEwNTg0MzE3NDUxIn0.9maqyJ5uKAp6ihzjFomRbmdPTajBfiXKWH4ZlsEJDgD2otAJ7I9gw2V0OBqX3zRgAWKcYN7a-bsxHVaa4t-wKg",

api_key = "09e51b9f99ec4491b622ac6c34c192e0.gnWSsd9Ez2rfXmPC"

selected_key_idx = 0

random.seed(42)
print(len(data), len(id_set))



def encode_image(image_path, datum, is_box):
    with Image.open(image_path) as image:
        
        modified_image = draw_box(image, datum) if is_box else draw_mask(image, datum)
        buffer = io.BytesIO()
        modified_image.save(buffer, format="PNG")
        byte_data = buffer.getvalue()

        #modified_image.show()

        return base64.b64encode(byte_data).decode('utf-8')



def result(output_list):
    last_no_resp = False
    correct = sum(1 for d in output_list if d['is_correct'])
    TP = sum(1 for d in output_list if d['is_correct'] and d['answer'][0].lower() == 'y')
    TN = sum(1 for d in output_list if d['is_correct'] and d['answer'][0].lower() == 'n')
    FP = sum(1 for d in output_list if (not d['is_correct']) and d['answer'][0].lower() == 'y')
    FN = sum(1 for d in output_list if (not d['is_correct']) and  d['answer'][0].lower() == 'n')

    len_out = len(output_list)
    print(len(data))
    print('ACC:',  correct/len_out, correct, len_out )
    print('Precision:', TP/(TP+FP), TP, TP+FP )
    print('Recall: (ACC of true label)', TP/(TP+FN), TP, TP+FN)
    print('Acc of False label:', TN/(FP+TN), TN, FP+TN )
    print('Ratio of Yes:', (TP+FP)/len(output_list))
    exit()

#sub_list = [d for d in output_list if d.get('type')=='mask']
#result(sub_list)
#result(output_list)
    
for i, datum in enumerate(data):
    image_name = datum['image']
    
    question_id = datum['question_id']

    if question_id in id_set:
        continue

    qtype = datum['qtype']
    label = datum['label']

    image_path = os.path.join(image_folder_path, image_name)
    is_box = random.randint(0,1)
    type = 'box' if is_box else 'mask'
    text = instance_qs_construct(datum, type)

    #print(text)
    base64_image = encode_image(image_path, datum, is_box)
    base64_url = f"data:image/png;base64,{base64_image}"
    #print(base64_url)

    client = ZhipuAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model = "glm-4v-plus-0111",
            messages=[
                #{"role":"system", "content": "Answer only 'Yes' or 'No' for the following questions."},
                {"role":"system", "content": "For the following questions, answer 'Yes' or 'No' and you should explain in detail how you got the answer."},
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": text},
                        {
                            "type": "image_url",
                            "image_url": {
                                #"url": "https://mj101-1317487292.cos.ap-shanghai.myqcloud.com/ai/test.pdf"
                                "url": base64_url
                            }
                        }
                    ],
                }
            ]
        )
    except Exception:
        print('error when generating response')
        continue

    if response.choices == None:
        print('no response')
        
        continue

    last_no_resp = False

    ans = response.choices[0].message.content
    datum_output = {}
    datum_output['question_id'] = question_id
    datum_output['qtype'] = qtype
    datum_output['type'] = type
    datum_output['answer'] = ans
    datum_output['is_correct'] = ans[0].lower() == label[0].lower()

    print(ans, label)
    output_list.append(datum_output)
    id_set.add(question_id)
    
    time.sleep(random.random())

    if i % 10 == 0:
        with open(output_path, 'w') as f:
            json.dump(output_list, f)

'''
A example of response
ChatCompletion(id='cu3403blmiu557eb578g', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='Yes, the car is parked on the grass. It is positioned on a well-maintained lawn, which is a common practice at car shows to provide a soft surface for the vehicles and to prevent damage to paved surfaces. The grass appears to be green and healthy, indicating that the event is likely taking place in a season or region where the grass is kept in good condition.', role='assistant', function_call=None, tool_calls=None))], created=1736851470, model='kimi', object='chat.completion', service_tier=None, system_fingerprint=None, usage=CompletionUsage(completion_tokens=1, prompt_tokens=1, total_tokens=2), segment_id='cu3403qm52t3v4iadq90')
'''

#print(response.choices[0].message.content)
