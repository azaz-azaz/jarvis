import ast
import json
import os
import requests
import Sets
import nexus
import keys
from pprint import pprint
from datetime import datetime
from random import choice
from dotdict import dotdict, superlist


def check_valid(ip_port: str):
    try:
        txt = requests.get(
            "https://api.openai.com/",
            # proxies={"https": "65.109.152.88	8888".replace('	', ':')},
            proxies={"https": ip_port.replace('	', ':')},
            timeout=4
        ).text
        
        return "(){var b=a.getElement" not in txt
    except Exception:
        return False


def convert_to_python_syntax(raw_text: str) -> str:
    for pack in (
        (' true', ' True'),
        (' false', ' False'),
        (' null', ' None'),
        ('|\n', '\n'),
    ):
        raw_text = raw_text.replace(*pack)
    return raw_text
    

proxies = {"https": "65.109.152.88	8888".replace('	', ':')}
while not check_valid(proxies["https"]):
    print("p", end='')
print()
url = 'https://api.openai.com/v1/chat/completions'
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {keys.openai_token}"
}
tools = nexus.tools
available_functions = nexus.available_tools
generate_filename = lambda: (str(datetime.now()).replace(' ', '_').replace(':', '-') +
                             ''.join([choice('qwertyuiopasdfghjklzxcvbnm') for _ in range(4)]))

languages = {
    "cpp": "cpp",
    "c++": "cpp",
    "c": "c",
    "python": "py",
    "css": "css",
    "html": "html",
    "javascript": "js",
    "js": "js",
}


class Bot:
    def __init__(
            self,
            sys_message: str = None,
            /,
            model: str = None,
            *,
            history: list[dict[str, str]] = None,
            silent_startup: bool = False
    ):
        self.sys_message: str = sys_message
        self.messages: list[dict[str, str]] = history if history is not None else self.get_empty_history()
        self.model = model if model else "gpt-3.5-turbo"
        if not silent_startup:
            print("JARVIS SYSTEM ACTIVATED")
    
    def get_empty_history(self):
        return list() if self.sys_message is None else [{"role": "system", "content": self.sys_message}]
    
    def set_empty_history(self):
        self.messages = self.get_empty_history()
    
    def add_user_message(self, message: dict[str, str]) -> None:
        self.messages.append(message)
    
    @staticmethod
    def _do_request(data: dict) -> dotdict:
        print("sending...",)
        pprint(data)
        print("received", end=' ')
        response = requests.request(
            method="POST",
            headers=headers,
            url=url,
            data=json.dumps(data),
            proxies=proxies
        )
        pprint(response.json())
        try:
            assert response.status_code == 200
        except AssertionError:
            raise AssertionError("oai code ==", response.status_code)
        return dotdict(response.json())
    
    def get_response(
            self,
            prompt,
            /,
            *,
            temperature: float = 0,
            presence_penalty: float = 0,
            frequency_penalty: float = 0,
            tool_choice: str = None,
            tools_: dict = None,
    
    ) -> dotdict:
        self.add_user_message({"role": "user", "content": prompt})
        if tools_ is None and tool_choice is None:
            return self._do_request(
                dict(
                    model=self.model,
                    messages=self.messages,
                    temperature=temperature,
                    presence_penalty=presence_penalty,
                    frequency_penalty=frequency_penalty,
                )
            )
        return self._do_request(
            dict(
                model=self.model,
                messages=self.messages,
                temperature=temperature,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
                tools=tools_,
                tool_choice=tool_choice,
            )
        )
    
    def get_simple_response(
            self,
            prompt,
            /,
            *,
            temperature: float = 0,
            presence_penalty: float = 0,
            frequency_penalty: float = 0
    
    ) -> str:
        return self.get_response(
            prompt,
            temperature=temperature,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
        ).choices[0].message.content
    
    def get_tool_using_response(
            self,
            prompt,
            /,
            *,
            temperature: float = 0,
            presence_penalty: float = 0,
            frequency_penalty: float = 0
    ) -> str:
        first_response = self.get_response(
            prompt,
            tool_choice="auto",
            tools_=tools,
            temperature=temperature,
            presence_penalty=presence_penalty,
            frequency_penalty=frequency_penalty,
        )
        if first_response.choices[0].message.content is not None:
            # no function calls, simple response
            self.messages.append(first_response.choices[0].message)
            return first_response.choices[0].message.content
        # function calls presents
        self.messages.append(
            first_response.choices[0].message
        )
        tool_calls: superlist = first_response.choices[0].message.tool_calls
        assert isinstance(tool_calls, superlist)
        for tool_call in tool_calls:
            tool_call = dotdict(tool_call)
            # calls handling
            f_name = tool_call.function.name
            f_to_call = available_functions[f_name]
            # print("received function call, name =", f_name)
            # print("raw args:", tool_call.function.arguments)
            to_eval: str = convert_to_python_syntax(
                tool_call.function.arguments
            )
            try:
                f_args = ast.literal_eval(
                    to_eval
                )
            except Exception:
                print("Error with decoding of", to_eval)
                try:
                    f_args = ast.literal_eval('{' + to_eval + '}')
                except ValueError:
                    raise ValueError("Error with decoding of " + to_eval)
                except SyntaxError:
                    raise SyntaxError("Error with decoding of " + to_eval)
            f_response = f_to_call(kwargs=f_args)
            
            self.messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": f_name,
                    "content": f_response,
                }
            )
        second_response = self._do_request(
            {
                "model": self.model,
                "messages": self.messages,
            }
        )
        return second_response.choices[0].message.content
    
    def get_pretty_response(
            self,
            prompt,
            /,
            *,
            temperature: float = 0,
            presence_penalty: float = 0,
            frequency_penalty: float = 0
    ) -> str:
        raw_text = self.get_tool_using_response(
            prompt, temperature=temperature, presence_penalty=presence_penalty, frequency_penalty=frequency_penalty
        )
        # print("received response, rawtext:\n",raw_text)
        splited = raw_text.split('```')
        comments = []
        code_fragments = []
        for i in range(len(splited)):
            if i % 2:
                code_fragments.append(splited[i])
            else:
                comments.append(splited[i])
        res = '\n\n...code...\n\n'.join(comments)
        for code_fragment in code_fragments:
            splited = code_fragment.splitlines()
            name = generate_filename()
            suffix = languages.get(splited[0])
            
            filename = Sets.path + '\\code\\' + name + '.' + ('txt' if suffix is None else suffix)
            with open(filename, mode='w', encoding='utf-8') as f:
                f.write(code_fragment.split('\n', maxsplit=1)[1])
                print("файл сохранен", filename)
            os.startfile(filename)
        return res
