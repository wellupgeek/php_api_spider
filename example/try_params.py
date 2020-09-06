import requests
from urllib.parse import quote, unquote

headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.83 Safari/537.36"}
# p = {"wd":"我的世界"}
# url = "http://www.baidu.com/s"
# response = requests.get(url, params=p, headers=headers)
# print(response.status_code)
# get_url = response.request.url
# print(get_url)
# print(unquote(get_url, "utf-8"))
# print(response.content.decode())

url = "https://www.baidu.com/s?wd={}".format("我的世界")
r = requests.get(url, headers=headers)
print(r.status_code)
print(r.request.url)