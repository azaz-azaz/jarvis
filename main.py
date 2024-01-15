from jarvis import Bot as Jarvis
from gui import *
from keyboard import wait
import Sets

sys_message = \
    """
1) Ты Джарвис.
2) Тебя создал Neanod.
3) Я - Neanod.
4) Ты - мой личный помощник, выполняешь любые мои указания.
"""

JARVIS = Jarvis(sys_message)


while True:
    wait(Sets.secret_key)
    prompt = pretty_input("Jarvis-input")
    if prompt is None:
        continue
    response = JARVIS.get_pretty_response(prompt)
    pretty_alert(response)
