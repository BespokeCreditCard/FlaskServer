import config
import os
from flask import Flask, request, render_template, jsonify
import boto3, json
from werkzeug.utils import secure_filename
from socket import *
import get_benefits
import top5_cards_flask
import dall_e
import deepl_translation
import time
import base64
import werkzeug
from flask_cors import CORS
from PIL import Image
import io

app = Flask(__name__)

@app.route('/')
def hello() :
    a = config.USER
    return a+"A"

################################################################################
# !! 주의 route 뒤에 경로는 위에 Spring에서 적은 경로와 같아야함 !!
################################################################################
@app.route('/get_cluster', methods=['POST'])
def get_cluster():
    # 시작 시간
    start_time = time.time()

	# Spring으로부터 String 전달받음
    seq_dict = request.get_json()
    seq = seq_dict["seq"]

	# # Spring으로부터 JSON 객체를 전달받음
    print("=====================================")

   	# Spring에서 받은 데이터를 출력해서 확인
    print("Type:", type(seq), seq)
    result = get_benefits.model_result(seq)

    # result를 dumps 메서드를 사용하여 문자열로 저장
    response = json.dumps(result, ensure_ascii=False)

    # result를 json으로 저장
    # response = jsonify(result)
    print("군집에 속한 전체 카드, 혜택들")
    print("TYPE:", type(response), response)

    # 종료 시간
    end_time = time.time()
    # print("end :", end_time)
    print(f"실행 시간: {end_time - start_time:.2f}초")
    print("=====================================")
    
    # Spring으로 response 전달
    return response

@app.route('/get_top5_cards', methods=['POST'])
def get_top5_cards():
    # 시작 시간
    start_time = time.time()
    # print("start :", start_time)
    print("============")

    # seq, selected_benefits, cluster_num 필요
    dto_json = request.get_json()
    
   	# Spring에서 받은 데이터를 출력해서 확인
    print("Type:", type(dto_json), dto_json)

    # # json에서 seq, selected_benefits 가져오기
    seq = dto_json["seq"]
    selected_benefits = dto_json["selectedBenefits"]
    cluster_num = dto_json["clusterNum"]

    ################################################################################
    # sample data
    ################################################################################
    # seq_idx = 26
    # seq = "K1D7OY9NU64NH9WBSSBD"
    # selected_benefits = ["모든가맹점", "교통", "쇼핑", "카페", "병원/약국"]
    # cluster_num = 3
    ################################################################################

    result = top5_cards_flask.get_top_5(seq, selected_benefits, cluster_num)

    # result를 dumps 메서드를 사용하여 response에 저장
    response = json.dumps(result, ensure_ascii=False)

    # 종료 시간
    end_time = time.time()
    # print("end :", end_time)
    print(f"실행 시간: {end_time - start_time:.2f}초")
    print("============")

    # Spring으로 response 전달
    return response
################################################################################
# DALL-E
################################################################################
@app.route('/generate_img', methods=['POST'])
def generate_img():
    # 시작 시간
    start_time = time.time()
    # print("start :", start_time)
    print("=====================================")

    prompt = request.form.get("prompt", None)
    mode = int(request.form.get("mode", 0))
    input_img = request.files.get("input_img", None)
    mask_img = request.form.get("mask_img", None)  # Base64 문자열로 전송된 마스크 이미지

    # input_img가 werkzeug.datastructures.FileStorage 객체면, bytes 형식으로 변환
    if isinstance(input_img, werkzeug.datastructures.FileStorage):
        input_img_bytes = input_img.read()
    else:
        input_img_bytes = input_img
        
    # mask_img가 Base64 문자열이면, bytes 형식으로 변환
    if mask_img:
        mask_img_bytes = base64.b64decode(mask_img.split(",")[1])
    else:
        mask_img_bytes = mask_img
    print("=====================================")

    # dall-e 모델 사용
    # b64_img1, b64_img2 = dall_e.generate_img(prompt, input_img_bytes, mask_img_bytes, mode)

    ### 시연 영상용 b64 이미지
    imgs = ["hamster1", "hamster2", "hamster3", "hamster4", "baby_doge1", "baby_doge2", "landscape1", "landscape2"]

    with Image.open(f'./dall_e_imgs/{imgs[6]}.png') as img:
        # PIL Image 객체를 바이트 버퍼로 변환
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")        
        # 바이트 버퍼를 Base64 문자열로 변환
        b64_img1 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    with Image.open(f'./dall_e_imgs/{imgs[7]}.png') as img:
        # PIL Image 객체를 바이트 버퍼로 변환
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        # 바이트 버퍼를 Base64 문자열로 변환
        b64_img2 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    # 결과 확인을 위해 변수의 앞부분을 출력합니다.
    print("b64_img1의 앞부분:", b64_img1[:100])
    print("b64_img2의 앞부분:", b64_img2[:100])
    print(type(b64_img1))

    result = {"b64_img1":b64_img1, "b64_img2":b64_img2}

    # result를 dumps 메서드를 사용하여 response에 저장
    response = json.dumps(result, ensure_ascii=False)

    # 종료 시간
    end_time = time.time()
    # print("end :", end_time)
    print(f"실행 시간: {end_time - start_time:.2f}초")
    print("=====================================")

    # Spring으로 response 전달
    return response

################################################################################
# DeepL 번역
################################################################################
@app.route('/translate', methods=['POST'])
def deepl_translate():
    start_time = time.time()
    print("=====================================")

    promptKorean_dict = request.get_json()
    promptKorean = promptKorean_dict["promptKorean"]
    translated_prompt = deepl_translation.translate(promptKorean)

    result = {"translatedPrompt":translated_prompt}
    response = json.dumps(result, ensure_ascii=False)

    end_time = time.time()
    print(f"실행 시간: {end_time - start_time:.2f}초")
    print("=====================================")
    return response

# 0.0.0.0 으로 모든 IP에 대한 연결을 허용
CORS(app)
if __name__ == '__main__':
    app.run(host='0.0.0.0',debug=True)