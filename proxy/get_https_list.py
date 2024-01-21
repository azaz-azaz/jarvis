import requests
import ast
from typing import Literal
from prettytable import prettytable


PROTOCOL = "http"
with open("banned_list", "r") as file:
    banned_list: list[str] = list(map(lambda string: string[:-1], file.readlines()))


def get_proxies_1(
        url="https://raw.githubusercontent.com/jetkai/proxy-list/main/online-proxies/json/proxies.json",
) -> dict:
    response = requests.get(url)
    assert response.status_code == 200
    content = response.text
    return ast.literal_eval(content)


def get_proxies_2(
        url="https://raw.githubusercontent.com/TheSpeedX/SOCKS-List/master/http.txt",
) -> list:
    response = requests.get(url)
    assert response.status_code == 200
    content = response.text.split()
    return content


def get_proxies_3():
    with open("temp.txt", "r") as f:
        lines = f.readlines()
    return lines
    

def check_valid_with_google(ip, port) -> bool:
    try:
        resp_code = requests.get("https://8.8.8.8", proxies={PROTOCOL: ip + ':' + port}, timeout=0.1).status_code
    except Exception as e:
        return e
    return resp_code


def check_valid_oai(ip_port: str):
    if ip_port in banned_list:
        return False, 403
    try:
        response = requests.get(
            "https://api.openai.com/",
            proxies={PROTOCOL: ip_port},
            timeout=6,
        )
        if response.status_code == 403:
            banned_list.append(ip_port)
        with open("banned_list", "a") as f:
            f.write(ip_port + '\n')
        return "(){var b=a.getElement" not in response.text, response.status_code
    except Exception:
        return False, 0


def pretty_table_print():
    # actual_list: dict[Literal["http", "https", "socks4", "socks5"], list[str]] = get_proxies()
    # listing = actual_list[PROTOCOL]
    listing = get_proxies_2()
    names = ["ip", "port", "protocol://ip:port", "google dns code", "openai valid"]
    table = prettytable.PrettyTable(names)
    for x in range(0, len(listing), 15):
        try:
            l = listing[x:x+15]
        except IndexError:
            break
        for proxy in l:
            ip: str
            port: str
            ip, port = proxy.split(':')
            full_name = PROTOCOL + "://" + proxy
            is_valid = check_valid_with_google(ip, port)
            is_valid_oai = '-' if not is_valid else check_valid_oai(proxy)
            table.add_row([ip, port, full_name, is_valid, is_valid_oai])
        print(str(table))
        table.clear()
        table.field_names = names


def get_actual_1_proxy(silent: bool = False) -> dict[Literal["http", "https"], str]:
    listing = get_proxies_2()
    for v in listing:
        oai = check_valid_oai(v)
        if not oai[0]:
            if not silent:
                print(v, oai[1])
            continue
        # found
        if not silent:
            print("found", v)
        return {PROTOCOL: v}
    
        
if __name__ == '__main__':
    print(get_actual_1_proxy())
    