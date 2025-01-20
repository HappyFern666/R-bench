#!/bin/bash

### image level
python eval_glm.py \
    --annotation-dir data_filterd \
    --question-file data_filterd/image-level_filterd.json \
    --question-id-file data_filterd/nocaps_image-level_rel_ids_holder.json \
    --result-file output/glm_4v_flash/image-level_out.json \
    --eval_image

### instance level mask
python eval_glm.py \
    --annotation-dir data_filterd \
    --question-file data_filterd/instance-level_filterd.json \
    --question-id-file data_filterd/instance-level_ids_holder.json \
    --result-file output/glm_4v_flash/instance-level-mask_out.json \
    --eval_instance

### instance level box
python eval_glm.py \
    --annotation-dir data_filterd \
    --question-file data_filterd/instance-level_filterd.json \
    --question-id-file data_filterd/instance-level_ids_holder.json \
    --result-file output/glm_4v_flash/instance-level-box_out.json \
    --eval_instance