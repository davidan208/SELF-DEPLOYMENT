import requests
from configs.config import settings

async def llm_answer(
    provider = "",
    model_name= "",
    messages = [],
    generation_config = {},
    safety_settings = []
):
    def openai_messages_to_gemini_contents(messages):
        contents = []
        for message in messages:
            content = dict()
            content["role"] = message["role"]
            content["parts"] = [
                {
                    "text": message["content"][0]["text"]
                }
            ]
            contents.append(content)
        return contents

    if generation_config == {}:
        generation_config = {
            "temperature": 0.2,
            "top_p": 0.2
        }

    if provider == "gemini" and safety_settings == []:
        safety_settings = [
            {
                'category': 'HARM_CATEGORY_DANGEROUS_CONTENT',
                'threshold': 'BLOCK_NONE'
            },
            {
                'category': 'HARM_CATEGORY_HARASSMENT',
                'threshold': 'BLOCK_NONE'
            },
            {
                'category': 'HARM_CATEGORY_HATE_SPEECH',
                'threshold': 'BLOCK_NONE'
            },
            {
                'category': 'HARM_CATEGORY_SEXUALLY_EXPLICIT',
                'threshold': 'BLOCK_NONE'
            }
        ]

    output_text, status_code = "", 500
    if provider in ("deepseek", "openai"):
        API_URL = "https://api.deepseek.com/chat/completions" if provider == "deepseek" else "https://api.openai.com/v1/chat/completions"
        API_KEY = settings.DEEPSEEK_TOKEN if provider == "deepseek" else settings.OPENAI_TOKEN
        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }
        data = {
            "model": model_name,
            "messages": messages,
        }
        for key, value in generation_config.items():
            data[key] = value
        try:
            response = requests.post(API_URL, headers=headers, json=data)
            status_code = response.status_code
            response.raise_for_status()
            
            result = response.json()
            output_text = result['choices'][0]['message']['content']
            
        except requests.exceptions.HTTPError as errh:
            output_text = str(errh)
        except requests.exceptions.RequestException as err:
            output_text = str(err)
        except Exception as e:
            output_text = str(e)
    elif provider == "gemini":
        API_URL = f"https://generativelanguage.googleapis.com/v1/models/{model_name}:generateContent?key={settings.GEMINI_TOKEN}"
        headers = {
            'Content-Type': 'application/json'
        }
        data = {
            "contents": openai_messages_to_gemini_contents(messages=messages),
            'generationConfig': generation_config,
            'safetySettings': safety_settings,
        }
        try:
            response = requests.post(API_URL, headers=headers, json=data)
            status_code = response.status_code
            response.raise_for_status()
            
            result = response.json()
            output_text = result["candidates"][0]["content"]["parts"][0]["text"]
            
        except requests.exceptions.HTTPError as errh:
            output_text = str(errh)
        except requests.exceptions.RequestException as err:
            output_text = str(err)
        except Exception as e:
            output_text = str(e)
    else: # Claude
        
        API_URL = "https://api.anthropic.com/v1/messages"
        headers = {
            "x-api-key": settings.CLAUDE_TOKEN,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json"
        }
        data = {
            "model": model_name,
            "max_tokens": 8192,
            "messages": messages
        }
        try:
            response = requests.post(API_URL, headers=headers, json=data)
            status_code = response.status_code
            response.raise_for_status()
            
            result = response.json()
            output_text = result['content'][0]['text']
            
        except requests.exceptions.HTTPError as errh:
            output_text = str(errh)
        except requests.exceptions.RequestException as err:
            output_text = str(err)
        except Exception as e:
            output_text = str(e)

    return output_text, status_code