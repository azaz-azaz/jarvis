import pyautogui


def pretty_input(input_text: str = "Input:", /) -> str | None:
    return pyautogui.prompt(input_text)


def pretty_alert(text: str = "Alert!"):
    pyautogui.alert(text, "JARVIS-RESPONSE", "Close")
