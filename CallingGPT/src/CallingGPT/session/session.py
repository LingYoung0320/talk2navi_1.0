from ..entities.namespace import Namespace
import openai
import logging
import json


class Session:

    namespace: Namespace = None

    messages: list[dict] = []

    model: str = "ft:gpt-4o-2024-08-06:sun-yat-sen-university::AK0BjAyV"

    def __init__(self, modules: list, model: str = "ft:gpt-4o-2024-08-06:sun-yat-sen-university::AK0BjAyV"):
        self.namespace = Namespace(modules)
        self.model = model

    def ask(self, msg: str) -> dict:
        # copy messages

        messages = self.messages.copy()

        messages.append(
            {
                "role": "user",
                "content": msg
            }
        )
        while True:

            args = {
                "model": self.model,
                "messages": messages,
            }

            if len(self.namespace.functions_list) > 0:
                args['functions'] = self.namespace.functions_list
                args['function_call'] = "auto"

            resp = openai.ChatCompletion.create(
                **args
            )

            logging.debug("Response: {}".format(resp))
            reply_msg = resp["choices"][0]['message']

            yield reply_msg

            ret = {}

            if 'function_call' in reply_msg:

                fc = reply_msg['function_call']
                args = json.loads(fc['arguments'])
                call_ret = self._call_function(fc['name'], args)

                messages.append({
                    "role": "function",
                    "name": fc['name'],
                    "content": str(call_ret)
                })

                self.messages = messages.copy()
            else:
                messages.append({
                    "role": "assistant",
                    "content": reply_msg['content']
                })

                self.messages = messages.copy()

                break

    def _call_function(self, function_name: str, args: dict):
        return self.namespace.call_function(function_name, args)
    