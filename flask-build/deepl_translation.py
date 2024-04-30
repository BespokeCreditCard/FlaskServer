import config
import requests
import deepl

def translate(promptKorean):
    try: 
        deepl_key = config.DEEPL
        translator = deepl.Translator(deepl_key)
        result = translator.translate_text(promptKorean, target_lang="EN-US")
        print(type(result))
        translated_prompt = result.text
        print("번역 완료:", translated_prompt)
        return translated_prompt
    except Exception as e:
        print("오류 발생: ", e)
    