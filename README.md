# R-Bench
![teaser](assets/r-bench.png)

This repo is based on the previous repo of the paper [Evaluating and Analyzing Relationship Hallucinations in Large Vision-Language Models (ICML2024)](https://www.bing.com/ck/a?!&&p=2f0bd6012a4f4b51JmltdHM9MTcxOTM2MDAwMCZpZ3VpZD0zMjgwNWY0Mi03YmRkLTZkYzEtMTdmNi00YzE3N2FiYjZjODUmaW5zaWQ9NTE4OQ&ptn=3&ver=2&hsh=3&fclid=32805f42-7bdd-6dc1-17f6-4c177abb6c85&psq=Evaluating+and+analyzing+relationship&u=a1aHR0cHM6Ly9hcnhpdi5vcmcvaHRtbC8yNDA2LjE2NDQ5djE&ntb=1) and our own code.

```
@InProceedings{pmlr-v235-wu24l,
  title = 	 {Evaluating and Analyzing Relationship Hallucinations in Large Vision-Language Models},
  author =       {Wu, Mingrui and Ji, Jiayi and Huang, Oucheng and Li, Jiale and Wu, Yuhang and Sun, Xiaoshuai and Ji, Rongrong},
  booktitle = 	 {Proceedings of the 41st International Conference on Machine Learning},
  pages = 	 {53553--53570},
  year = 	 {2024},
  editor = 	 {Salakhutdinov, Ruslan and Kolter, Zico and Heller, Katherine and Weller, Adrian and Oliver, Nuria and Scarlett, Jonathan and Berkenkamp, Felix},
  volume = 	 {235},
  series = 	 {Proceedings of Machine Learning Research},
  month = 	 {21--27 Jul},
  publisher =    {PMLR},
  pdf = 	 {https://raw.githubusercontent.com/mlresearch/v235/main/assets/wu24l/wu24l.pdf},
  url = 	 {https://proceedings.mlr.press/v235/wu24l.html},
  }
```


## Data
Download [R-Bench](https://drive.google.com/file/d/1sqO0MWBg_HXp5cIKb-nstjNEEk5crUWH/view?usp=sharing).
The main annotation files include:
```
- image-level_filterd.json
- instance-level_filterd.json
- nocaps_pope_obj_random_image.json
- nocaps_pope_obj_popular_image.json
- nocaps_pope_obj_adversarial_image.json
- web_data
- instance_mask
```
These files contain annotations for image-level, instance-level(box and mask share same questions), pope-object, and web-data questions. For image-level and instance-level questions, we randomly sampled five subsets into the `[type]_ids_[subset].json` files.

Download the images from [image](https://drive.google.com/file/d/10JXRdzTRMylWQA160qdoYITGO10g6N8k/view?usp=sharing) (source from [Open Image validation set (v4)](https://storage.googleapis.com/openimages/web/download_v7.html)).

```
wget https://drive.google.com/file/d/10JXRdzTRMylWQA160qdoYITGO10g6N8k/view?usp=sharing

unzip image.zip
```

## Eval
**Step1:** To run LVLM on R-Bench using the official inference script of the LVLMs.

For Image-level, pseudocode is as follows,
```
for line in questions:
    question_id = line['question_id']
    question = line['text']
    image = open(line['image'])
    text = model(question, image)
    answer_file.write(json.dumps("question_id": question_id, "text":text))
```

For Instance-level, pseudocode is as follows, set ```instance_level_box=True``` or ```instance_level_mask=True``` to get result for Instance-Level result with Box or Mask.
```
import instance_qs_construct, draw_box, draw_mask

for line in questions:
    question_id = line['question_id']
    question = instance_qs_construct(line, type='mask' if instance_level_mask else 'box')
    if instance_level_box:
      image = draw_box(line)
    elif instance_level_mask:
      image = draw_mask(line)
    text = model(question, image)
    answer_file.write(json.dumps("question_id": question_id, "text":text))
```

and format the result.json file as follows:
```
{"question_id": 0, "text":[model output]}
{"question_id": 1, "text":[model output]}
...
```
Tips: We provide instance-level question tools in `utils.py`. Please use the `draw_mask` and `draw_box` functions to draw the mask or box on input images, respectively. Additionally, use the `instance_qs_construct` function to reformat the instance questions.

**Step 1.1:** Evaluate with open-source LLaVA.
We provide LLaVA demos for reference. After setting up the LLaVA environment, place the `demos/eval-rbench.py` file into the `llava/eval/` directory and execute `llava-r-bench.sh`.
```
# 1. Clone the repository and navigate to LLaVA folder
git clone https://github.com/haotian-liu/LLaVA.git
cd LLaVA

# 2. Install Package
conda create -n llava python=3.10 -y
conda activate llava
pip install --upgrade pip  # enable PEP 660 support
pip install -e .

# 3. Copy the eval-rbench.py and lllava-r-bench.sh to LLaVA folder
cp R-bench/demos/eval-rbench.py LLaVA/llava/eval/
cp R-bench/demos/llava-r-bench.sh LLaVA/

# 4. Run the script
chmod +x llava-r-bench.sh
./llava-r-bench.sh
```

**Step 1.2:** Evaluate with API.
We provide an example of using ZhipuAI's API for evaluation. Here's how to get started:

1. Install the required package:
```bash
pip install zhipuai
```

2. Set up your API key:
```python
import zhipuai
zhipuai.api_key = "YOUR_API_KEY"
```

3. Run the evaluation script:
```bash
python test_glm_api.py  # default: image-level evaluation
```

You can specify different evaluation types using the `--type` argument:
```bash
# For image-level evaluation
python test_glm_api.py --type image-level

# For instance-level evaluation with masks
python test_glm_api.py --type instance-level-mask

# For instance-level evaluation with boxes
python test_glm_api.py --type instance-level-box
```

The script will process the images and questions according to the specified type and save the results in the format:
```json
{"question_id": 0, "qtype": "positive", "answer": "[model output]"}
{"question_id": 1, "qtype": "negative", "answer": "[model output]"}
...
```
Note: Make sure to properly configure your API key and handle rate limits according to your API usage agreement. 

**Step2:** Eval with,
```
sh eval.sh
```
Tips: You can just replace ```--result-file``` with the file you generated, and the ```eval.py``` script will automatically calculate the average results for different subsets. The results obtained through our script are for the ```Image(All)```, and the results for ```Image(subset)``` in the paper are for reference only.

**Step3:** Fine-grained reasoning evaluation.

To evaluate the quality of reasoning explanations generated by the model, we compare them with human-annotated "ground truth" explanations using cosine similarity between their sentence embeddings.


1. Install Dependencies:
```bash
pip install sentence-transformers scikit-learn numpy
```

2. Prepare Data:
Ensure your result file (e.g., `result.json`) contains entries in the following format:
```json
{
    "question id": 6187,
    "answer": "Model generated explanation",
    "labeled reason": "Human annotated ground truth"
}
```

3. Run Evaluation:
```bash
python cal_cos_similarity.py
```

The evaluation script will output:
- Cosine similarity score for each question
- Average similarity score across all questions

Note: By default, we use `all-MiniLM-L6-v2` as the sentence encoder, which is a lightweight yet effective model. You can modify the model name in the `calculate_cosine_similarity` function if you prefer to use other pre-trained models.

## 分工
黄叙川：
1. 阅读论文、准备presentation PPT、presentation
2. 复现论文中测试LLaVA的结果
3. 基于论文已有benchmark调用glm-4v-flash的API进行测试、
4. 撰写论文
5. 考虑R-Bench中欠缺考虑的情况，构思test cases进行补充

吕嘉楠：
1. 阅读论文，准备pre和ppt
2. 在glm-4v-plus-0111和kimi上测试
3. 撰写论文
4. 构建subset寻找原始R-bench存在的问题

## Acknowledge
The evaluation code is based on [POPE](https://github.com/AoiDragon/POPE).
