from bs4 import BeautifulSoup
from selenium import webdriver
from pywebio.input import *
from pywebio.output import *
from pywebio.platform import start_server, config
from selenium.webdriver.common.by import By


class Spider:
    def __init__(self):
        # 创建浏览器对象
        self.browser = webdriver.Chrome()

    def crawl_scores(self, name, psw):
        url = 'https://cas.jou.edu.cn/lyuapServer/login?service=http%3A%2F%2Fportal.jou.edu.cn%2Fc%2Fportal%2Flogin' \
              '%3Fredirect%3D%252F-s1%26p_l_id%3D70131 '
        self.browser.get(url)
        self.browser.implicitly_wait(3)
        username = self.browser.find_element(By.ID, 'username')
        username.send_keys(name)
        password = self.browser.find_element(By.ID, 'password')
        password.send_keys(psw)
        login_button = self.browser.find_element(By.NAME, 'login')
        login_button.submit()
        source_code = self.browser.page_source.encode('utf-8').decode()
        self.browser.quit()
        soup = BeautifulSoup(source_code, 'html5lib')
        data = []
        for i, tr in enumerate(soup.find_all('tr')):
            if i != 0:
                tds = tr.find_all('td')
                if tds:
                    data.append(
                        {'id': tds[0].contents[0], 'academic_year': tds[1].contents[0], 'semester': tds[2].contents[0],
                         'course': tds[3].contents[0], 'score': tds[4].contents[0], 'credits': tds[5].contents[0]})
        return data


@config(title="JOU成绩查询")
def main():
    put_markdown('# JOU成绩查询')
    info = input_group('输入信息', [
        input('学号', type=NUMBER, name='id', required=True),
        input('密码', type=PASSWORD, name='psw', required=True)
    ])
    with put_loading():
        spider = Spider()
        data = spider.crawl_scores(info['id'], info['psw'])
        with use_scope('scores'):
            put_table(tdata=[
                [
                    put_text(item['id']), put_text(item['academic_year']), put_text(item['semester']),
                    put_text(item['course']), put_text(item['score']), put_text(item['credits'])
                ] for item in data
            ], header=['学号', '学年', '学期', '课程', '分数', '学分'])


if __name__ == '__main__':
    start_server(main, port=80)
