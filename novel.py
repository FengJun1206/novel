import requests
from bs4 import BeautifulSoup


def get_html(url):
    """
    获取网页源代码
    :param url: url
    :return: 网页源代码
    """
    try:
        r = requests.get(url, timeout=20)
        if r.status_code == 200:
            r.encoding = 'utf-8'
            return r.text
    except:
        return '爬取失败'


def parse_html(html):
    """
    解析源代码，获取每一章 url以及章节名
    :param html: 源代码
    :return: 每一章 url，章节名
    """
    try:
        url_list = []       # 全部章节 url 列表
        soup = BeautifulSoup(html, 'lxml')
        title = soup.find('h1').text    # 小说名
        dd = soup.find_all('dd')        # 获取全部章节 url
        for d in dd:
            base_url = 'https://www.qu.la/book/4140/' + d.a['href']
            url_list.append(base_url)

        return url_list, title
    except:
        return '解析失败'


def test(url_list, title):
    """
    获取每章内容，并存储成文件
    :param url_list: 章节 url 列表
    :param title: 小说名
    :return:
    """
    try:
        url_list = url_list[12:]
        for url in url_list:
            html = get_html(url).replace('<br/>', '\n')     # 替换 <br/>

            soup = BeautifulSoup(html, 'lxml')

            h1 = soup.find('h1').text  # 每章名字
            content = soup.find('div', id='content').text  # 每章内容

            with open('H:\\%s.txt' % title, 'a', encoding='utf-8') as f:
                f.write(h1 + '\n\n')
                f.write(content)
                print('当前小说：%s 当前章节：%s 已下载完毕' % (title, h1))
    except:
        pass


def main():
    url = 'https://www.qu.la/book/3137/'
    html = get_html(url)
    url_list, title = parse_html(html)
    test(url_list, title)


if __name__ == '__main__':
    main()
