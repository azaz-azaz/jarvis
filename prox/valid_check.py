from typing import Literal
import requests
import prettytable
import keys


text = """159.65.180.117:10009
167.172.238.6:10008
104.129.192.175:10957
159.223.144.108:3128
138.197.20.244:10000
138.197.16.249:10009
138.197.92.54:10005
162.243.184.16:10003
159.65.176.77:10010
64.225.8.118:10001
138.197.16.249:10006
64.225.8.142:10004
35.225.16.82:2387
159.65.180.117:10005
64.225.8.142:10003
64.225.4.81:10009
68.183.48.146:10009
64.225.8.118:10003
150.136.38.91:80
64.189.106.6:3129
167.172.238.15:10007
64.225.4.17:10011
64.225.8.132:10000
167.172.238.15:10008
139.180.39.201:8080
139.180.39.200:8080
64.225.8.179:10001
159.65.186.46:10005
167.172.238.6:10006
137.184.6.37:3128
23.225.72.123:3501
66.29.156.100:80
198.23.176.76:3128
67.217.61.162:80
68.183.144.115:10003"""


class Api:
	key: str = keys.openai_token


def check_valid_via_google(ip: str, port: str, /) -> bool | Exception:
	try:
		code: int = requests.get(
			"https://8.8.8.8",
			timeout=0.2
		).status_code
		return code == 200
	except Exception as e:
		return e


def check_valid_via_openai(ip: str, port: str, /) -> Literal["<code>", "<error>"]:
	try:
		response = requests.post(
			"https://api.openai.com/v1/engines/davinci/completions",
			headers={
				"Content-Type": "application/json",
				"Authorization": f"Bearer {Api.key}"
			},
			json={
				"prompt": "Hello, World!",
				"max_tokens": 5
			},
			proxies={
				"https": ip + ':' + port
			},
			timeout=35
		)
		return str(response.status_code)
	except Exception as e:
		return str(e)


def check_valid(
	listed: tuple[str],
) -> Literal["Non-valid", "<status code>"]:
	prox: str
	for prox in listed:
		ip: str
		port: str
		ip, port = prox.split(':', maxsplit=1)
		# check via google dns
		if not check_valid_via_google(ip, port):
			yield "Non-valid"
		# check via openai
		yield check_valid_via_openai(ip, port)

	
def main():
	table = prettytable.PrettyTable(field_names=["Number", "Ip:port", "Valid", "OAI-code"])
	proxies_raw = text.splitlines()
	i = 0
	for res in check_valid(proxies_raw):
		number = i + 1
		ip_port = proxies_raw[i]
		is_valid_google = "Yes" if res != "Non-valid" else "No"
		openai_code = "-" if is_valid_google == "No" else res
		table.add_row(
			(
				number,
				ip_port,
				is_valid_google,
				openai_code,
			)
		)
		i += 1
		print(ip_port, ':', openai_code)
	table.title = "Valid checking"
	print(table)


if __name__ == '__main__':
	main()
