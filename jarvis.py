import ast
import json
import os
import requests
import Sets
import nexus
from datetime import datetime
from random import choice
from dotdict import dotdict, superlist

proxies = {"https": "65.109.152.88	8888".replace('	', ':')}
url = 'https://api.openai.com/v1/chat/completions'
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer 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"
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
    ):
        self.sys_message: str = sys_message
        self.messages: list[dict[str, str]] = history if history is not None else self.get_empty_history()
        self.model = model if model else "gpt-3.5-turbo"
        print("JARVIS SYSTEM ACTIVATED")
    
    def get_empty_history(self):
        return list() if self.sys_message is None else [{"role": "system", "content": self.sys_message}]
    
    def set_empty_history(self):
        self.messages = self.get_empty_history()
    
    def add_user_message(self, message: dict[str, str]) -> None:
        self.messages.append(message)
    
    @staticmethod
    def do_request(data: dict) -> dotdict:
        return dotdict(
            requests.request(
                method="POST",
                headers=headers,
                url=url,
                data=json.dumps(data),
                proxies=proxies
            ).json()
        )
    
    def get_response(
            self,
            prompt,
            /,
            *,
            temperature: float = 0,
            presence_penalty: float = 0,
            frequency_penalty: float = 0,
            tool_choice: str = None,
            tools: dict = None,
    
    ) -> dotdict:
        self.add_user_message({"role": "user", "content": prompt})
        if tools is None and tool_choice is None:
            return self.do_request(
                dict(
                    model=self.model,
                    messages=self.messages,
                    temperature=temperature,
                    presence_penalty=presence_penalty,
                    frequency_penalty=frequency_penalty,
                )
            )
        return self.do_request(
            dict(
                model=self.model,
                messages=self.messages,
                temperature=temperature,
                presence_penalty=presence_penalty,
                frequency_penalty=frequency_penalty,
                tools=tools,
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
            tools=tools,
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
            f_args = ast.literal_eval(tool_call.function.arguments)
            f_response = f_to_call(kwargs=f_args)
            
            self.messages.append(
                {
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": f_name,
                    "content": f_response,
                }
            )
        second_response = self.do_request(
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
        print("received response, rawtext:\n",raw_text)
        splited = raw_text.split('```')
        comments = []
        code_fragments = []
        for i in range(len(splited)):
            if i % 2:
                code_fragments.append(splited[i])
            else:
                comments.append(splited[i])
        res = '\nCODE IN IDE\n'.join(comments)
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

