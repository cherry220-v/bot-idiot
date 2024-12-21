from g4f.client import Client as G4FClient
from g4f import models
import re
import multiprocessing

def answer(text: str, prompt: str, model: str = 'gpt-4o', data: str = "", limit: int = 60, timeout:int = 100) -> str | None:
    def send_request(result_queue):
        try:
            client = G4FClient()
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": f'{prompt}\n{text};'
                    }
                ]
            )
            result_queue.put({'result': response.choices[0].message.content})
        except Exception as e:
            result_queue.put({'error': str(e)})

    i = 1

    while i <= 15:
        result_queue = multiprocessing.Queue()
        send_request(result_queue)
        result = result_queue.get() if not result_queue.empty() else None

        if result is None:
            pass
        elif 'error' in result:
            pass
        else:
            res = result['result']
            clear_text = re.sub(r"[A-Za-z]", "", res)
            clear_text = re.sub(r'\s+', ' ', clear_text.strip())

            if len(clear_text) > limit:
                res = res.strip()
                index = res.find('.ai')

                if index > 0:
                    res = res[index+3:]
                    return res
                else:
                    return res
            else:
                pass

        i += 1

    return None