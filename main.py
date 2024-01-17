from jarvis import Bot as Jarvis
from gui import *
from keyboard import wait
import nexus
import Sets
import argparse

sys_message = f"""1) Ты Джарвис.
2) Тебя создал Neanod.
3) Я - Neanod.
4) Ты - мой личный помощник, выполняешь любые мои указания.
5) Твоя папка для работы с файлами - C:\\jarvis_works и все что ты делаешь должно быть в ней.
6) Если я прошу создать папку и такая уже есть, просто считай что создал ее.
7) Для сложных расчетов и больших чисел используй {nexus.PythonExec.function.__name__}
"""

JARVIS = Jarvis(sys_message)
arg_parser = argparse.ArgumentParser()
arg_parser.add_argument(
    '--bat-path',
    type=str,
    default=r"C:\jarvis-released\activate-jarvis.bat",
    help="path to the bat-activator"
)
args = arg_parser.parse_args()

nexus.RESTART_PATH = args.bat_path
nexus.CURRENT_BOT = JARVIS


def main():
    while True:
        wait(Sets.secret_key)
        prompt = pretty_input("Jarvis-input")
        if not prompt:
            print(prompt, "is not valid prompt")
            continue
        response = JARVIS.get_pretty_response(prompt)
        pretty_alert(response)


if __name__ == '__main__':
    main()
