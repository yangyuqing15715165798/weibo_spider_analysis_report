import requests
import json
import time
import os
import re
import argparse
from datetime import datetime

class WeiboCrawler:
    def __init__(self, cookie=None):
        """
        初始化微博爬虫
        :param cookie: 用户登录的cookie字符串
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9',
            'Referer': 'https://weibo.com/',
            'Origin': 'https://weibo.com',
        }
        
        if cookie:
            self.headers['Cookie'] = cookie
        
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def get_user_info(self, user_id):
        """
        获取用户基本信息
        :param user_id: 用户ID
        :return: 用户信息字典
        """
        url = f'https://weibo.com/ajax/profile/info?uid={user_id}'
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') == 1 and 'data' in data:
                    return data['data']['user']
            return None
        except Exception as e:
            print(f"获取用户信息失败: {e}")
            return None
    
    def get_user_weibos(self, user_id, page=1, count=20):
        """
        获取用户的微博列表
        :param user_id: 用户ID
        :param page: 页码
        :param count: 每页微博数量
        :return: 微博列表
        """
        url = f'https://weibo.com/ajax/statuses/mymblog?uid={user_id}&page={page}&feature=0'
        try:
            response = self.session.get(url)
            if response.status_code == 200:
                data = response.json()
                if data.get('ok') == 1 and 'data' in data:
                    return data['data']['list'], data['data']['total']
            return [], 0
        except Exception as e:
            print(f"获取微博列表失败: {e}")
            return [], 0
    
    def clean_text(self, text):
        """
        清理文本内容，去除HTML标签等
        :param text: 原始文本
        :return: 清理后的文本
        """
        if not text:
            return ""
        # 去除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        # 替换特殊字符
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&amp;', '&')
        # 去除多余空格和换行
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    def format_weibo(self, weibo):
        """
        格式化微博内容
        :param weibo: 微博数据
        :return: 格式化后的微博文本
        """
        created_at = datetime.strptime(weibo['created_at'], '%a %b %d %H:%M:%S %z %Y').strftime('%Y-%m-%d %H:%M:%S')
        text = self.clean_text(weibo.get('text', ''))
        
        formatted = f"[{created_at}]\n"
        formatted += f"{text}\n"
        
        # 添加转发内容
        if 'retweeted_status' in weibo and weibo['retweeted_status']:
            retweeted = weibo['retweeted_status']
            retweeted_user = retweeted.get('user', {}).get('screen_name', '未知用户')
            retweeted_text = self.clean_text(retweeted.get('text', ''))
            formatted += f"\n转发 @{retweeted_user}: {retweeted_text}\n"
        
        # 添加图片链接
        if 'pic_ids' in weibo and weibo['pic_ids']:
            formatted += "\n图片链接:\n"
            for pic_id in weibo['pic_ids']:
                pic_url = f"https://wx1.sinaimg.cn/large/{pic_id}.jpg"
                formatted += f"{pic_url}\n"
        
        formatted += "-" * 50 + "\n"
        return formatted
    
    def crawl_user_weibos(self, user_id, max_pages=None):
        """
        爬取用户的所有微博
        :param user_id: 用户ID
        :param max_pages: 最大爬取页数，None表示爬取全部
        :return: 所有微博内容的列表
        """
        user_info = self.get_user_info(user_id)
        if not user_info:
            print(f"未找到用户 {user_id} 的信息")
            return []
        
        screen_name = user_info.get('screen_name', user_id)
        print(f"开始爬取用户 {screen_name} 的微博")
        
        all_weibos = []
        page = 1
        total_pages = float('inf')
        
        while (max_pages is None or page <= max_pages) and page <= total_pages:
            print(f"正在爬取第 {page} 页...")
            weibos, total = self.get_user_weibos(user_id, page)
            
            if not weibos:
                break
                
            all_weibos.extend(weibos)
            
            # 计算总页数
            if total > 0:
                total_pages = (total + 19) // 20  # 每页20条，向上取整
            
            page += 1
            # 防止请求过快
            time.sleep(1)
        
        print(f"共爬取到 {len(all_weibos)} 条微博")
        return all_weibos, screen_name
    
    def save_weibos_to_file(self, user_id, max_pages=None):
        """
        爬取用户微博并保存到文件
        :param user_id: 用户ID
        :param max_pages: 最大爬取页数
        :return: 保存的文件路径
        """
        weibos, screen_name = self.crawl_user_weibos(user_id, max_pages)
        if not weibos:
            return None
        
        # 创建文件名
        filename = f"{user_id}_weibos.txt"
        
        # 写入文件
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"用户: {screen_name} (ID: {user_id})\n")
            f.write(f"爬取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"微博数量: {len(weibos)}\n")
            f.write("=" * 50 + "\n\n")
            
            for weibo in weibos:
                formatted = self.format_weibo(weibo)
                f.write(formatted)
        
        print(f"微博内容已保存到文件: {filename}")
        return filename

def main():
    parser = argparse.ArgumentParser(description='微博爬虫 - 爬取指定用户的微博')
    parser.add_argument('user_id', help='微博用户ID')
    parser.add_argument('--cookie', help='登录cookie字符串', default=None)
    parser.add_argument('--max-pages', type=int, help='最大爬取页数', default=None)
    parser.add_argument('--cookie-file', help='包含cookie的文件路径', default=None)
    
    args = parser.parse_args()
    
    cookie = args.cookie
    
    # 如果提供了cookie文件，从文件读取cookie
    if args.cookie_file and not cookie:
        try:
            with open(args.cookie_file, 'r', encoding='utf-8') as f:
                cookie = f.read().strip()
        except Exception as e:
            print(f"读取cookie文件失败: {e}")
    
    crawler = WeiboCrawler(cookie=cookie)
    crawler.save_weibos_to_file(args.user_id, args.max_pages)

if __name__ == "__main__":
    main()