import webbrowser
from datetime import datetime
from pprint import pprint
from typing import Callable, Literal
import folium


class Prop:
    def __init__(self, name: str, type_: Literal["number", "string"], doc: str, required: bool):
        self.doc = doc
        self.type_ = type_
        self.name = name
        self.required = required
    
    @property
    def dict(self):
        return {
            "type": self.type_,
            "description": self.doc,
        }
    
    def __str__(self):
        return self.name


class UsableFunction:
    def __init__(
            self,
            function: Callable[[dict], ...],
            doc: str,
            props: list[Prop]
    ):
        self.props = props
        self.doc = doc
        self.function = function
    
    def get_parameters(self) -> dict:
        required: list[str] = list()
        for prop in self.props:
            if prop.required:
                required.append(str(prop))
        return {
            "type": "object",
            "properties": {param.name: param.dict for param in self.props},
            "required": required
        }
    
    @property
    def dict(self):
        return {
            "name": self.function.__name__,
            "description": self.doc,
            "parameters": self.get_parameters(),
        }


def get_current_datetime(kwargs) -> str:
    return str(datetime.now())


def open_location(kwargs) -> None:
    fig = folium.Map((kwargs['x'], kwargs['y']))
    filename = f'C:/jarvis_works/folium/map{kwargs['x']}--{kwargs['y']}.html'
    fig.save(filename)
    webbrowser.open(filename)


GetCurrentDatetime = UsableFunction(
    get_current_datetime,
    """Returns current date and time""",
    []
)
OpenLocation = UsableFunction(
    open_location,
    """Opens location in the world map, doesnt return anything""",
    [
        Prop(
            'x',
            'number',
            """X position""",
            True
        ),
        Prop(
            'y',
            'number',
            """Y position""",
            True
        ),
    ]
)


all_functions = [
    GetCurrentDatetime,
    OpenLocation,
]

tools = [
    {
        "type": "function",
        "function": cl.dict,
    }
    for cl in all_functions
]

available_tools = {av.function.__name__: av.function for av in all_functions}


if __name__ == '__main__':
    open_location({'x': 30.7128, 'y': -74.006})

