
import requests
import time

Cookie = "ga=GA1.2.2127752435.1619423430; _gid=GA1.2.542154346.1619423430; MEIQIA_TRACK_ID=1rhLZxyDfzFWEQsCBcilbeWzSXd; auth_token=eyJldCI6MTYyMDY0NDQ2MywiZ2lkIjo2NCwidWlkIjozNjM0ODh9.lU+p7d0O6bcgeEOHJSKHYkIHKqUYX/7FsgH7c2FkG9hKz993Mxq++NRV0Ax37WMAfYRFxDxpNJm32AYfBO61+EwArbsO3ecpV8t4KPxtaoBCuVa+u/bwq6CqsUnj+NCtuL2U/aAtwfL2QGtv7t+pyhLiGOk3TgVEe4RTumn9jPHQ3R95e9YZWVJxiEGFblD8JEcEEFgdU/A7T8Ph9P2J3zqB5uAPUHyHpc3S1tjVogrVI8lccn2LMMjDcMVK5qxotD3WXLDzTJngYY84Qc90fvdB2ZNFXVQn1WbUWvk4An52hVOOCG1X+xhCTugG0A4jLYWHxjY68AGDuj54f2dbDQ==; lang=zh"
def https_get(url, data):
    Number_of_attempts = 0
    while True:
        try:
            header = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'close',
                'Cookie': Cookie
            }
            response = requests.get(url, headers=header, data=data, stream=True, timeout=20)
            break
        except Exception as e:
            Number_of_attempts += 1
            if Number_of_attempts > 10:
                response = ""
                break
            time.sleep(3)
    return response
def https_post(url, data):
    Number_of_attempts = 0
    while True:
        try:
            # 请求头
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:54.0) Gecko/20100101 Firefox/54.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Connection': 'close',
                'Cookie': Cookie
            }
            # 开始请求
            response = requests.post(url, data=data, headers=headers, timeout=20)
            break
        except Exception as e:
            print()
            Number_of_attempts += 1
            if Number_of_attempts > 10:
                response = []
                break
            time.sleep(3)
    return response
r = https_get("https://www.hpool.com/api/assets/totalassets", [])
print(r.content)
