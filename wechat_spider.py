import json
import time
from datetime import datetime
from login import gzhlogin
import os
import requests
import csv
import urllib3
urllib3.disable_warnings()

# Disable proxy settings
os.environ['http_proxy'] = ''
os.environ['https_proxy'] = ''

class WeChatSpider:
    def __init__(self):
        # 初始化一个新的 session
        self.session = requests.Session()
        self.token = None
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",
            'Accept': 'application/json, text/plain, */*',
        }
        
        # 设置 session 的属性
        self.session.headers.update(self.headers)
        self.session.proxies = {
            'http': None,
            'https': None
        }
        self.session.verify = False
    
    def login(self):
        """登录微信公众平台"""
        print("正在登录微信公众平台...")
        self.session = gzhlogin()  # 使用登录后的 session 替换初始 session
        if self.session:
            # 确保登录后的 session 也有正确的设置
            self.session.headers.update(self.headers)
            self.session.proxies = {
                'http': None,
                'https': None
            }
            self.session.verify = False
            self._update_token()
        return self.session is not None

    def _update_token(self):
        """更新token"""
        try:
            response = self.session.get('https://mp.weixin.qq.com/')
            self.token = response.url.split('token=')[1]
        except Exception as e:
            print(f"获取token失败: {e}")
            self.token = None

    def search_gzh(self, query, begin=0, count=5):
        """搜索公众号"""
        if not self.token:
            self._update_token()
            if not self.token:
                return None

        search_url = 'https://mp.weixin.qq.com/cgi-bin/searchbiz'
        params = {
            'action': 'search_biz',
            'begin': begin,
            'count': count,
            'query': query,
            'token': self.token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': 1
        }

        try:
            response = self.session.get(search_url, params=params)
            result = response.json()
            
            if result['base_resp']['ret'] == 0:
                return result
            else:
                print(f"搜索失败: {result['base_resp']['err_msg']}")
                return None
        except Exception as e:
            print(f"搜索请失败: {e}")
            return None

    def get_articles(self, fakeid, begin=0, count=5):
        """获取公众号文章列表"""
        if not self.token:
            self._update_token()
            if not self.token:
                return None

        url = 'https://mp.weixin.qq.com/cgi-bin/appmsg'
        params = {
            'action': 'list_ex',
            'begin': begin,
            'count': count,
            'fakeid': fakeid,
            'type': '9',
            'token': self.token,
            'lang': 'zh_CN',
            'f': 'json',
            'ajax': '1'
        }

        try:
            response = self.session.get(url, params=params)
            result = response.json()
            
            if result.get('base_resp', {}).get('ret') == 0:
                return result
            else:
                print(f"获取文章列表失败: {result.get('base_resp', {}).get('err_msg')}")
                return None
        except Exception as e:
            print(f"请求失败: {e}")
            return None

    def print_gzh_info(self, gzh_info):
        """打印公众号信息"""
        if not gzh_info or 'list' not in gzh_info:
            print("未找到相关公众号")
            return []
        
        print(f"\n找到 {len(gzh_info['list'])} 个公众号：")
        for idx, gzh in enumerate(gzh_info['list'], 1):
            print("-" * 50)
            print(f"序号: {idx}")
            print(f"昵称: {gzh['nickname']}")
            print(f"微信号: {gzh['alias']}")
            print(f"简介: {gzh['signature']}")
        
        return gzh_info['list']

    def print_article_info(self, articles_info):
        """打印文章信息"""
        if not articles_info or 'app_msg_list' not in articles_info:
            print("未找到文章")
            return
        
        print(f"\n找到文章总数: {articles_info.get('total', 0)}")
        
        print("\n文章列表：")
        for idx, article in enumerate(articles_info['app_msg_list'], 1):
            print("-" * 50)
            print(f"序号: {idx}")
            print(f"标题: {article['title']}")
            print(f"作者: {article.get('author', '未知')}")
            print(f"摘要: {article.get('digest', '无')}")
            print(f"链接: {article['link']}")
            print(f"发布时间: {datetime.fromtimestamp(article['create_time'])}")

    def export_to_csv(self, articles_info, gzh_name):
        """导出文章信息到CSV文件"""
        if not articles_info or 'app_msg_list' not in articles_info:
            print("没有文章可以导出")
            return

        # 创建输出目录
        output_dir = 'exports'
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        # 生成文件名
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = os.path.join(output_dir, f'{gzh_name}_{timestamp}.csv')

        # 准备CSV数据
        articles_data = []
        for article in articles_info['app_msg_list']:
            articles_data.append({
                '标题': article['title'],
                '作者': article.get('author', '未知'),
                '摘要': article.get('digest', ''),
                '链接': article['link'],
                '发布时间': datetime.fromtimestamp(article['create_time']).strftime('%Y-%m-%d %H:%M:%S'),
                '封面图': article.get('cover', '')
            })

        # 写入CSV文件
        try:
            with open(filename, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=articles_data[0].keys())
                writer.writeheader()
                writer.writerows(articles_data)
            print(f"\n文章信息已导出到: {filename}")
            print(f"共导出 {len(articles_data)} 篇文章")
        except Exception as e:
            print(f"导出CSV文件失败: {e}")

    def handle_article_list(self, selected_gzh, articles):
        """处理文章列表"""
        while True:
            self.print_article_info(articles)
            print("\n操作选项：")
            print("1. 获取更多文章")
            print("2. 导出文章信息到CSV")
            print("0. 返回上级菜单")
            
            try:
                choice = input("请选择操作 (0-2): ").strip()
                
                if choice == '0':
                    break
                elif choice == '1':
                    # 获取更多文章
                    begin = len(articles['app_msg_list'])
                    more_articles = self.get_articles(selected_gzh['fakeid'], begin=begin)
                    if more_articles and 'app_msg_list' in more_articles:
                        articles['app_msg_list'].extend(more_articles['app_msg_list'])
                        articles['total'] = more_articles.get('total')
                        print("\n已加载更多文章")
                    else:
                        print("\n没有更多文章了")
                elif choice == '2':
                    # 导出到CSV
                    self.export_to_csv(articles, selected_gzh['nickname'])
                else:
                    print("输入无效，请重新选择")
            except ValueError:
                print("输入无效，请输入数字")

def main():
    spider = WeChatSpider()
    
    # 登录
    if not spider.login():
        print("登录失败")
        return

    while True:
        print("\n" + "="*50)
        print("1. 搜索公众号")
        print("2. 退出程序")
        choice = input("请选择操作 (1-2): ").strip()
        
        if choice == '2':
            break
        elif choice == '1':
            query = input("\n请输入要搜索的公众号名称: ").strip()
            if not query:
                continue
                
            # 搜索公众号
            gzh_list = spider.search_gzh(query)
            if not gzh_list:
                continue
                
            gzh_accounts = spider.print_gzh_info(gzh_list)
            if not gzh_accounts:
                continue
            
            # 选择公众号
            while True:
                try:
                    idx = int(input("\n请输入要查看的公众号序号 (0返回): "))
                    if idx == 0:
                        break
                    if 1 <= idx <= len(gzh_accounts):
                        selected_gzh = gzh_accounts[idx-1]
                        print(f"\n已选择: {selected_gzh['nickname']}")
                        
                        # 获取文章列表
                        articles = spider.get_articles(selected_gzh['fakeid'])
                        if articles:
                            spider.handle_article_list(selected_gzh, articles)
                        break
                    else:
                        print("序号无效，请重新输入")
                except ValueError:
                    print("输入无效，请输入数字")
        else:
            print("输入无效，请重新选择")

if __name__ == "__main__":
    main() 