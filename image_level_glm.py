from openai import OpenAI
from zhipuai import ZhipuAI
import base64
import json
import os
import time
import random
#from config import token



# SET THE PATH OF THE DATASET JSON FILE HERE
json_file_path = os.path.join('data_filterd', 'image-level_filterd.json')

# SET THE FOLDER PATH OF IMAGES IN THE DATASET HERE
image_folder_path = os.path.join('image', 'validation')

output_list = []
# SET THE PATH OF THE OUTPUT JSON FILE HERE
# 如果报错的话，试下手动创建这个文件并写入 []  (一个空列表)
output_path = 'glm_image_level.json'

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

api_key = "28579bf18dc44681b4f963b2c9bb88d3.x0rjqSCdY1qww46A"

selected_key_idx = 0


print(len(data), len(id_set))



def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
last_no_resp = False
    
for i, datum in enumerate(data):
    print(i)
    image_name = datum['image']
    text = datum['text']
    question_id = datum['question_id']

    if question_id in id_set:
        continue
    if i < 72:
        continue

    qtype = datum['qtype']
    label = datum['label']

    image_path = os.path.join(image_folder_path, image_name)
    base64_image = encode_image(image_path)
    base64_url = f"data:image/png;base64,{base64_image}"
    #print(base64_url)

    client = ZhipuAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model = "glm-4v-plus-0111",
            messages=[
                {"role":"system", "content": "Answer only 'Yes' or 'No' for the following questions."},
                #{"role":"user", "content": "Who are you?"},
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
    datum_output['answer'] = ans
    datum_output['is_correct'] = ans[0].lower() == label[0].lower()

    print(ans, label)
    output_list.append(datum_output)
    id_set.add(question_id)
    
    time.sleep(random.random())

    if i % 10 == 0 or i == len(data)-1:
        with open(output_path, 'w') as f:
            json.dump(output_list, f)

'''
A example of response
ChatCompletion(id='cu3403blmiu557eb578g', choices=[Choice(finish_reason='stop', index=0, logprobs=None, message=ChatCompletionMessage(content='Yes, the car is parked on the grass. It is positioned on a well-maintained lawn, which is a common practice at car shows to provide a soft surface for the vehicles and to prevent damage to paved surfaces. The grass appears to be green and healthy, indicating that the event is likely taking place in a season or region where the grass is kept in good condition.', role='assistant', function_call=None, tool_calls=None))], created=1736851470, model='kimi', object='chat.completion', service_tier=None, system_fingerprint=None, usage=CompletionUsage(completion_tokens=1, prompt_tokens=1, total_tokens=2), segment_id='cu3403qm52t3v4iadq90')
'''

#print(response.choices[0].message.content)
