import io
import subprocess
import sys
import webbrowser
import folium
import pyautogui
import Sets
import colorama
from datetime import datetime
from typing import Callable, Literal, Any
from dotdict import dotdict

colorama.init()

print(end=colorama.Fore.BLUE)

allowed_list_apps = dotdict(
    {
        'minecraft': r"C:\BRD\BRD\LaunchMinecraft.bat",
        'minecraft-preview': r"C:\BRD\BRD\LaunchMinecraftPreview.bat",
        'terraria': r"C:\Users\smesh\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Steam\Terraria.url",
        'steam': r"C:\Program Files (x86)\Steam\steam.exe",
        'spaceflight-simulator': r"C:\Users\smesh\AppData\Roaming\Microsoft\Windows\Start Menu\Programs\Steam\Spaceflight Simulator.url",
        "geometry-dash": r"C:\Games\Geometry Dash\GeometryDash.exe",
    }
)
pretty_allowed_list: str = ', '.join(allowed_list_apps.keys())


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
    

def fix_globals(glb: dict[str, Any]) -> dict[str, Any]:
    """
    Костыль, нужно переделать
    :param glb:
    :return:
    """
    for key in glb.keys():
        if not isinstance(glb[key], (int, bool, str, float, list)):
            glb[key] = None
    return glb


def get_current_datetime(kwargs) -> str:
    kwargs
    return str(datetime.now())


def open_location(kwargs) -> Literal["successful", "unsuccessful"]:
    try:
        fig = folium.Map((kwargs['x'], kwargs['y']))
        name = f"{kwargs['x']}--{kwargs['y']}" if kwargs.get('name') is None else kwargs['name']
        filename = f'{Sets.path}\\folium\\map-{name}.html'
        fig.save(filename)
        if kwargs['show']:
            webbrowser.open(filename)
    except Exception as e:
        print(e)
        return "unsuccessful"
    return "successful"


def cmd(kwargs) -> str:
    stdin = kwargs['stdin']
    text = 'cd ' + Sets.path + '&' + stdin
    enc = 'oem'
    
    stdout = subprocess.run(text, shell=True, capture_output=True, text=True, encoding=enc).stdout
    stderr = subprocess.run(text, shell=True, capture_output=True, text=True, encoding=enc).stderr
    if stderr is not None:
        return "stderr:\n" + stderr
    return "stdout:\n" + stdout


def open_app(kwargs) -> str:
    name: str = kwargs["name"]
    app_path = allowed_list_apps.get(name.lower())
    if app_path is None:
        print(f"###\n###open_app_log: name {name} not found in {pretty_allowed_list}")
        return f"name {name} not found in {pretty_allowed_list}"
    else:
        out = subprocess.run(app_path)
        try:
            assert out.stderr is None
        except AssertionError:
            raise AssertionError(out.stderr)
        return "success"


def python_interpreter(kwargs) -> str:
    show_result_in_alert = True
    
    glb = {}
    text = kwargs['content']
    old_stdout = sys.stdout
    new_stdout = io.StringIO()
    sys.stdout = new_stdout
    error_message = None
    try:
        exec(text, {}, glb)
        glb = fix_globals(glb)
    except Exception as e:
        error_message = str(e)
    sys.stdout = old_stdout
    stdout_str = new_stdout.getvalue().strip()
    result = "###OUT:" + (("\n" + stdout_str) if stdout_str else 'NO') + f"\n###GLOBALS: {glb}"
    prt_inp = f"###INPUT:\n{text}"
    if not stdout_str and not error_message and not glb:
        eval_result = eval(text, locals(), {})
        if not eval_result:
            return "Your code must print or write to variables anything"
        return "Used python eval, result:\n" + str(eval_result)
    if error_message is not None:
        result += '\n###ERR:\n' + error_message
    if show_result_in_alert:
        pyautogui.alert(f"{prt_inp}\n{result}", "Jarvis's code interpreter", "Close")
    return result


GetCurrentDatetime = UsableFunction(
    get_current_datetime,
    """Returns current date and time""",
    []
)
OpenLocation = UsableFunction(
    open_location,
    """Opens location in the world map""",
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
        Prop(
            'show',
            'boolean',
            'Indicates whether the result should be displayed on screen',
            True,
        ),
        Prop(
            'name',
            'string',
            'File name in English to save',
            True,  # need to be False, but if it is True, filename generator is not ready yet
        )
    ]
)
CmdPrompt = UsableFunction(
    cmd,
    """Execute any command in cmd
If you want to execute chain of commands, you MUST write command1&command2&command3 etc
Returns stdout or stderr
You start directory is {Sets.path}""",
    [
        Prop(
            'stdin',
            'string',
            """Std input""",
            True,
        )
    ]
)
OpenApp = UsableFunction(
    open_app,
    f"""Opens one of my games/programs""",
    [
        Prop(
            'name',
            'string',
            f"""Name of the game. Allowed values: {pretty_allowed_list}""",
            True,
        )
    ]
)
PythonExec = UsableFunction(
    python_interpreter,
    """Execute any python code, returns output, errors and global variables""",
    [
        Prop(
            'content',
            'string',
            """Code to execute, python syntax""",
            True
        ),
    ]
)

all_functions = [
    GetCurrentDatetime,
    OpenLocation,
    CmdPrompt,
    OpenApp,
    PythonExec,
]

tools = [
    {
        "type": "function",
        "function": cl.dict,
    }
    for cl in all_functions
]

available_tools = {av.function.__name__: av.function for av in all_functions}

if __name__ != '__main__':
    print("JARVIS SUBSYSTEM ACTIVATED")
