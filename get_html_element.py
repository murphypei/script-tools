import urllib.request
from bs4 import BeautifulSoup


response = urllib.request.urlopen('http://www.mmjpg.com/')
if response:
    # 获取页面内容
    html_content = response.read().decode('utf-8')
    # 将获取到的内容转换成BeautifulSoup格式，并将html.parser作为解析器
    soup = BeautifulSoup(html_content, 'html.parser')
    # 格式化打印输出html
    # print(soup.prettify())
    # 获取元素节点
    tag_elements = soup.find('div', attrs={"class": "subnav"}).find_all('a')
    hrefs = [e.get('href') for e in tag_elements]
    tags = [e.string for e in tag_elements]
    print(hrefs)
    print(tags)
