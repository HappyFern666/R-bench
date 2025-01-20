import base64
import json
import argparse
import os
import time
import random
from zhipuai import ZhipuAI
from PIL import Image
from utils import draw_box, draw_mask, instance_qs_construct

parser = argparse.ArgumentParser()
parser.add_argument("--type", type=str, choices=['image-level','instance-level-box', 'instance-level-mask'], default='image-level')
args = parser.parse_args()

print(args.type)

# SET THE PATH OF THE DATASET JSON FILE HERE
if args.type == 'image-level':
    json_file_path = os.path.join('data_filterd', 'image-level_filterd.json')
elif args.type == 'instance-level-mask':
    json_file_path = os.path.join('data_filterd', 'instance-level_filterd.json')
elif args.type == 'instance-level-box':
    json_file_path = os.path.join('data_filterd', 'instance-level_filterd.json')

# SET THE FOLDER PATH OF IMAGES IN THE DATASET HERE
image_folder_path = os.path.join('image', 'validation')

output_list = []
# SET THE PATH OF THE OUTPUT JSON FILE HERE
# 如果报错的话，试下手动创建这个文件并写入 []  (一个空列表)
if args.type == 'image-level':
    output_path = 'output/glm_4v_flash/image-level_out.json'
elif args.type == 'instance-level-mask':
    output_path = 'output/glm_4v_flash/instance-level-mask_out.json'
elif args.type == 'instance-level-box':
    output_path = 'output/glm_4v_flash/instance-level-box_out.json'

with open(output_path, 'r') as json_file:
    try:
        output_list = json.load(json_file)
    except Exception:
        print('not yet have json file')

id_set = set(datum['question_id'] for datum in output_list)

data = None
with open(json_file_path, 'r') as json_file:
    data = json.load(json_file)

sample_size = int(len(data) * 0.05)
sampled_data = random.sample(data, sample_size)

print(len(sampled_data), len(id_set))

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')
    
for i, datum in enumerate(sampled_data):
    print(i)
    image_name = datum['image']
    if args.type == 'image-level':
        text = datum['text']
    elif args.type == 'instance-level-mask':
        text = instance_qs_construct(datum, type='mask')
    elif args.type == 'instance-level-box':
        text = instance_qs_construct(datum, type='box')
    question_id = datum['question_id']

    if question_id in id_set:
        continue

    qtype = datum['qtype']
    label = datum['label']

    image_path = os.path.join(image_folder_path, image_name)
    if args.type == 'image-level':
        image_base64url = encode_image(image_path)
    else:
        image = Image.open(image_path)
        if args.type == 'instance-level-mask':
            image = draw_mask(image=image, line=datum)
            save_path = f"temp/temp_instance_mask{i}.png"
        elif args.type == 'instance-level-box':
            image = draw_box(image=image, line=datum)
            save_path = f"temp/temp_instance_box{i}.png"
        image.save(save_path, format="PNG")
        image_base64url = encode_image(save_path)
    base64_url = f"data:image/png;base64,{image_base64url}"

    client = ZhipuAI(api_key=os.environ.get("API_KEY"))

    try:
        response = client.chat.completions.create(
            model = "glm-4v-flash",
            messages=[
                {"role":"system", "content": "Answer 'Yes' or 'No' for all the following questions."},
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
    except Exception as e:
        print('Exception:', e)
        print('sleep 10 seconds')
        time.sleep(10)
        continue

    if response.choices == None:
        print('No response, sleep 10 seconds')
        time.sleep(10)
        continue

    ans = response.choices[0].message.content
    datum_output = {}
    datum_output['question_id'] = question_id
    datum_output['qtype'] = qtype
    datum_output['answer'] = ans

    print(ans, label)
    output_list.append(datum_output)
    id_set.add(question_id)
    
    time.sleep(random.random())

    if i % 20 == 0:
        with open(output_path, 'w') as f:
            json.dump(output_list, f)
    
    if args.type != 'image-level':
        os.remove(save_path)
    