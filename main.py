from jarvis import Bot as Jarvis
from nexus import PythonExec
from gui import *
from keyboard import wait
import Sets

sys_message = f"""1) Ты Джарвис.
2) Тебя создал Neanod.
3) Я - Neanod.
4) Ты - мой личный помощник, выполняешь любые мои указания.
5) Твоя папка для работы с файлами - C:\\jarvis_works и все что ты делаешь должно быть в ней.
6) Если я прошу создать папку и такая уже есть, просто считай что создал ее.
7) Для сложных расчетов и больших чисел используй {PythonExec.function.__name__}
"""

JARVIS = Jarvis(sys_message)


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
