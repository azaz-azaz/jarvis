import pyautogui


def pretty_input(input_text: str = "Input:", /) -> str | None:
    return pyautogui.prompt(input_text, "JARVIS INPUT", "Скинуть ядерку на 64.529366° 40.542775°")


def pretty_alert(text: str = "Alert!"):
    pyautogui.alert(text, "JARVIS-RESPONSE", "Close", None)
