import re
import os
import matplotlib.pyplot as plt
from datetime import datetime
import jieba
import jieba.analyse
from collections import Counter
import numpy as np
from wordcloud import WordCloud
import matplotlib.font_manager as fm
from matplotlib.font_manager import FontProperties
import pandas as pd
from matplotlib.dates import DateFormatter
import seaborn as sns

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号

class WeiboAnalyzer:
    def __init__(self, file_path):
        """
        初始化微博分析器
        :param file_path: 微博数据文件路径
        """
        self.file_path = file_path
        self.weibos = []
        self.user_info = {}
        self.load_data()
        
    def load_data(self):
        """
        加载微博数据
        """
        with open(self.file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 提取用户信息
        if lines and "用户:" in lines[0]:
            user_info_match = re.match(r'用户: (.*) \(ID: (.*)\)', lines[0])
            if user_info_match:
                self.user_info['name'] = user_info_match.group(1)
                self.user_info['id'] = user_info_match.group(2)
        
        if len(lines) > 2 and "微博数量:" in lines[2]:
            count_match = re.match(r'微博数量: (\d+)', lines[2])
            if count_match:
                self.user_info['count'] = int(count_match.group(1))
        
        # 提取微博内容
        current_weibo = None
        for line in lines:
            # 新微博的开始
            if re.match(r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\]', line):
                if current_weibo:
                    self.weibos.append(current_weibo)
                
                date_match = re.match(r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]', line)
                if date_match:
                    date_str = date_match.group(1)
                    content = line[len(date_str) + 3:].strip()
                    
                    current_weibo = {
                        'date': datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S'),
                        'content': content,
                        'images': [],
                        'is_retweet': False,
                        'retweet_content': '',
                        'retweet_user': ''
                    }
            
            # 图片链接
            elif line.strip().startswith('https://wx1.sinaimg.cn/'):
                if current_weibo:
                    current_weibo['images'].append(line.strip())
            
            # 转发内容
            elif current_weibo and line.strip().startswith('转发 @'):
                current_weibo['is_retweet'] = True
                retweet_match = re.match(r'转发 @(.*): (.*)', line.strip())
                if retweet_match:
                    current_weibo['retweet_user'] = retweet_match.group(1)
                    current_weibo['retweet_content'] = retweet_match.group(2)
            
            # 继续添加内容
            elif current_weibo and not line.strip() == '-' * 50 and not line.strip() == '=' * 50:
                current_weibo['content'] += ' ' + line.strip()
        
        # 添加最后一条微博
        if current_weibo:
            self.weibos.append(current_weibo)
        
        print(f"成功加载 {len(self.weibos)} 条微博")
    
    def time_distribution_analysis(self):
        """
        分析微博发布时间分布
        """
        if not self.weibos:
            print("没有微博数据可分析")
            return
        
        # 提取日期和时间
        dates = [weibo['date'].date() for weibo in self.weibos]
        hours = [weibo['date'].hour for weibo in self.weibos]
        weekdays = [weibo['date'].weekday() for weibo in self.weibos]
        
        # 创建日期DataFrame
        df = pd.DataFrame({
            'date': dates,
            'hour': hours,
            'weekday': weekdays
        })
        
        # 按日期统计
        date_counts = df['date'].value_counts().sort_index()
        
        # 按小时统计
        hour_counts = df['hour'].value_counts().sort_index()
        
        # 按星期几统计
        weekday_counts = df['weekday'].value_counts().sort_index()
        weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
        
        # 创建图表
        fig, axes = plt.subplots(3, 1, figsize=(12, 15))
        
        # 日期分布图
        axes[0].plot(date_counts.index, date_counts.values, marker='o')
        axes[0].set_title('微博发布日期分布')
        axes[0].set_xlabel('日期')
        axes[0].set_ylabel('微博数量')
        axes[0].grid(True)
        
        # 小时分布图
        axes[1].bar(hour_counts.index, hour_counts.values)
        axes[1].set_title('微博发布时间段分布')
        axes[1].set_xlabel('小时')
        axes[1].set_ylabel('微博数量')
        axes[1].set_xticks(range(0, 24))
        axes[1].grid(True)
        
        # 星期几分布图
        axes[2].bar([weekday_names[i] for i in weekday_counts.index], weekday_counts.values)
        axes[2].set_title('微博发布星期分布')
        axes[2].set_xlabel('星期')
        axes[2].set_ylabel('微博数量')
        axes[2].grid(True)
        
        plt.tight_layout()
        plt.savefig('time_distribution.png')
        plt.close()
        
        print("时间分布分析完成，结果已保存为 time_distribution.png")
    
    def content_analysis(self):
        """
        分析微博内容
        """
        if not self.weibos:
            print("没有微博数据可分析")
            return
        
        # 合并所有微博内容
        all_content = ' '.join([weibo['content'] for weibo in self.weibos])
        
        # 使用jieba进行分词
        jieba.analyse.set_stop_words('stopwords.txt')  # 如果有停用词表
        words = jieba.cut(all_content)
        
        # 过滤掉单个字符和数字
        filtered_words = [word for word in words if len(word) > 1 and not word.isdigit()]
        
        # 统计词频
        word_counts = Counter(filtered_words)
        
        # 提取关键词
        keywords = jieba.analyse.extract_tags(all_content, topK=50, withWeight=True)
        
        # 创建词云
        wordcloud = WordCloud(
            font_path='simhei.ttf',  # 设置中文字体
            width=800,
            height=400,
            background_color='white'
        ).generate_from_frequencies(dict(word_counts))
        
        # 绘制词云图
        plt.figure(figsize=(10, 6))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('微博内容词云')
        plt.savefig('wordcloud.png')
        plt.close()
        
        # 绘制关键词条形图
        plt.figure(figsize=(12, 8))
        keywords_dict = dict(keywords[:20])
        plt.barh(list(reversed(list(keywords_dict.keys()))), 
                list(reversed(list(keywords_dict.values()))))
        plt.title('微博内容关键词TOP20')
        plt.xlabel('权重')
        plt.tight_layout()
        plt.savefig('keywords.png')
        plt.close()
        
        print("内容分析完成，结果已保存为 wordcloud.png 和 keywords.png")
    
    def quote_analysis(self):
        """
        分析微博中引用的人物
        """
        if not self.weibos:
            print("没有微博数据可分析")
            return
        
        # 定义可能被引用的人物列表
        famous_people = [
            '曾国藩', '尼采', '荣格', '苏格拉底', '马云', '武志红', 
            '阿德勒', '王安石', '苏东坡', '海德格尔', '左宗棠', '宗萨'
        ]
        
        # 统计每个人物被引用的次数
        quotes = {person: 0 for person in famous_people}
        
        for weibo in self.weibos:
            content = weibo['content']
            for person in famous_people:
                if person in content:
                    quotes[person] += 1
        
        # 过滤掉未被引用的人物
        quotes = {k: v for k, v in quotes.items() if v > 0}
        
        # 按引用次数排序
        sorted_quotes = dict(sorted(quotes.items(), key=lambda item: item[1], reverse=True))
        
        # 绘制引用人物条形图
        plt.figure(figsize=(10, 6))
        plt.bar(sorted_quotes.keys(), sorted_quotes.values())
        plt.title('微博中引用人物统计')
        plt.xlabel('人物')
        plt.ylabel('引用次数')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('quotes.png')
        plt.close()
        
        print("引用人物分析完成，结果已保存为 quotes.png")
    
    def image_analysis(self):
        """
        分析微博中的图片使用情况
        """
        if not self.weibos:
            print("没有微博数据可分析")
            return
        
        # 统计带图片的微博数量
        weibos_with_images = [weibo for weibo in self.weibos if weibo['images']]
        image_counts = [len(weibo['images']) for weibo in weibos_with_images]
        
        # 计算统计数据
        total_weibos = len(self.weibos)
        weibos_with_images_count = len(weibos_with_images)
        percentage = weibos_with_images_count / total_weibos * 100 if total_weibos > 0 else 0
        
        # 绘制饼图
        plt.figure(figsize=(8, 8))
        plt.pie([weibos_with_images_count, total_weibos - weibos_with_images_count], 
                labels=['带图片微博', '纯文字微博'], 
                autopct='%1.1f%%',
                startangle=90)
        plt.title('微博图片使用情况')
        plt.axis('equal')
        plt.savefig('image_usage.png')
        plt.close()
        
        # 绘制图片数量分布
        if image_counts:
            plt.figure(figsize=(10, 6))
            counter = Counter(image_counts)
            plt.bar(counter.keys(), counter.values())
            plt.title('微博图片数量分布')
            plt.xlabel('图片数量')
            plt.ylabel('微博数量')
            plt.xticks(range(1, max(image_counts) + 1))
            plt.grid(axis='y')
            plt.savefig('image_count.png')
            plt.close()
        
        print("图片使用分析完成，结果已保存为 image_usage.png 和 image_count.png")
    
    def generate_report(self):
        """
        生成分析报告
        """
        # 执行所有分析
        self.time_distribution_analysis()
        self.content_analysis()
        self.quote_analysis()
        self.image_analysis()
        
        # 生成HTML报告
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>微博数据分析报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1, h2 {{ color: #1DA1F2; }}
                .section {{ margin-bottom: 30px; }}
                img {{ max-width: 100%; border: 1px solid #ddd; }}
            </style>
        </head>
        <body>
            <h1>微博数据分析报告</h1>
            <div class="section">
                <h2>用户信息</h2>
                <p>用户名: {self.user_info.get('name', '未知')}</p>
                <p>用户ID: {self.user_info.get('id', '未知')}</p>
                <p>微博总数: {self.user_info.get('count', len(self.weibos))}</p>
                <p>分析微博数: {len(self.weibos)}</p>
            </div>
            
            <div class="section">
                <h2>时间分布分析</h2>
                <img src="time_distribution.png" alt="时间分布分析">
            </div>
            
            <div class="section">
                <h2>内容分析</h2>
                <h3>词云</h3>
                <img src="wordcloud.png" alt="词云">
                <h3>关键词</h3>
                <img src="keywords.png" alt="关键词">
            </div>
            
            <div class="section">
                <h2>引用人物分析</h2>
                <img src="quotes.png" alt="引用人物分析">
            </div>
            
            <div class="section">
                <h2>图片使用分析</h2>
                <img src="image_usage.png" alt="图片使用情况">
                <img src="image_count.png" alt="图片数量分布">
            </div>
        </body>
        </html>
        """
        
        with open('weibo_analysis_report.html', 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print("分析报告已生成: weibo_analysis_report.html")

def main():
    # 创建停用词文件（如果需要）
    stopwords = [
        '的', '了', '在', '是', '我', '有', '和', '就', '不', '人', '都', 
        '一', '一个', '上', '也', '很', '到', '说', '要', '去', '你', '会', 
        '着', '没有', '看', '好', '自己', '这', '那', '啊', '吧', '把', '给', 
        '但是', '但', '还', '可以', '这个', '这样', '这些', '因为', '所以', 
        '如果', '就是', '么', '什么', '只是', '只有', '这种', '那个', '他们'
    ]
    
    with open('stopwords.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(stopwords))
    
    # 分析微博数据
    analyzer = WeiboAnalyzer('1004524612_weibos.txt')
    analyzer.generate_report()

if __name__ == "__main__":
    main()