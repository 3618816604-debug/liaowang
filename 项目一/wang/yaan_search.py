import requests
from bs4 import BeautifulSoup
import logging

# 配置日志，使用Flask应用的日志配置
# 不添加basicConfig，避免与Flask日志冲突
logger = logging.getLogger(__name__)

class YaanGovSearch:
    def __init__(self):
        """初始化搜索工具"""
        self.base_url = "https://www.yaan.gov.cn"
        self.search_url = f"{self.base_url}/search.html"
        self.headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6",
            "cache-control": "max-age=0",
            "host": "www.yaan.gov.cn",
            "upgrade-insecure-requests": "1",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36 Edg/142.0.0.0",
            "referer": self.base_url
        }
        # 不设置初始Cookie，让服务器返回新的Cookie
        self.cookies = {}
        
        # 不使用代理直接请求
        self.proxies = None
    
    def search(self, keyword):
        """执行搜索，返回搜索结果"""
        try:
            # 构建搜索URL
            # 对关键词进行URL编码
            encoded_keyword = requests.utils.quote(keyword)
            url = f"{self.search_url}?q={encoded_keyword}"
            logger.info(f"正在搜索: {keyword}")
            logger.info(f"编码后的关键词: {encoded_keyword}")
            logger.info(f"请求URL: {url}")
            
            # 创建Session对象，禁用自动重定向
            session = requests.Session()
            session.headers.update(self.headers)
            session.cookies.update(self.cookies)
            
            # 发送请求，禁用自动重定向
            logger.info("发送搜索请求（禁用自动重定向）...")
            response = session.get(url, timeout=15, allow_redirects=False, proxies=self.proxies)
            
            # 检查响应状态
            logger.info(f"状态码: {response.status_code}")
            logger.info(f"响应头: {dict(response.headers)}")
            
            # 安全记录Cookie信息，避免Cookie冲突错误
            try:
                cookies_dict = {}  # 用于存储不重复的Cookie
                for cookie in session.cookies:
                    cookies_dict[cookie.name] = cookie.value
                logger.info(f"Cookie: {cookies_dict}")
            except Exception as cookie_e:
                logger.info(f"Cookie记录失败: {str(cookie_e)}")
            
            # 如果是302重定向，尝试获取重定向URL并直接访问
            if response.status_code == 302:
                redirect_url = response.headers.get('Location', '')
                logger.info(f"重定向URL: {redirect_url}")
                
                if redirect_url:
                    # 处理相对URL
                    if not redirect_url.startswith('http'):
                        if redirect_url.startswith('/'):
                            redirect_url = f"{self.base_url}{redirect_url}"
                        else:
                            redirect_url = f"{self.base_url}/{redirect_url}"
                    
                    logger.info(f"处理后的重定向URL: {redirect_url}")
                    
                    # 发送重定向请求，禁用自动重定向
                    redirect_response = session.get(redirect_url, timeout=15, allow_redirects=False, proxies=self.proxies)
                    logger.info(f"重定向请求状态码: {redirect_response.status_code}")
                    logger.info(f"重定向响应头: {dict(redirect_response.headers)}")
                    
                    if redirect_response.status_code == 200:
                        logger.info("重定向请求成功")
                        # 保存响应内容到文件
                        with open('search_response.html', 'w', encoding='utf-8') as f:
                            f.write(redirect_response.text)
                        logger.info("响应内容已保存到search_response.html")
                        return self.parse_result(redirect_response.text)
                    else:
                        logger.error(f"重定向请求失败，状态码: {redirect_response.status_code}")
                        # 保存响应内容到文件
                        with open('search_response.html', 'w', encoding='utf-8') as f:
                            f.write(redirect_response.text)
            elif response.status_code == 200:
                logger.info("搜索请求成功")
                # 保存响应内容到文件
                with open('search_response.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                logger.info("响应内容已保存到search_response.html")
                return self.parse_result(response.text)
            else:
                logger.error(f"搜索请求失败，状态码: {response.status_code}")
                # 保存响应内容到文件
                with open('search_response.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                logger.info("响应内容已保存到search_response.html")
            return []
        except Exception as e:
            logger.error(f"搜索过程中发生错误: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    def parse_result(self, html_content):
        """解析搜索结果HTML，提取有用信息"""
        results = []
        try:
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 定位搜索结果列表，根据实际页面结构调整选择器
            search_items = soup.select('.sou-ul02 li')  # 搜索结果列表项选择器
            
            for item in search_items:
                # 提取标题和链接
                title_tag = item.select_one('h1 a')  # 标题链接选择器
                if not title_tag:
                    continue
                
                title = title_tag.get_text(strip=True)
                link = title_tag.get('href', '')
                
                # 处理相对URL
                if link and not link.startswith('http'):
                    link = f"{self.base_url}{link}"
                
                # 提取内容
                content_tag = item.select_one('p span')  # 内容选择器
                content = content_tag.get_text(strip=True) if content_tag else ''
                
                # 提取发布时间和来源
                h2_tag = item.select_one('h2')  # 来源和时间容器
                if h2_tag:
                    # 提取来源
                    source = h2_tag.contents[0].strip() if h2_tag.contents else ''
                    
                    # 提取发布日期
                    date_tag = h2_tag.select_one('span:last-child')  # 发布日期选择器
                    publish_date = date_tag.get_text(strip=True) if date_tag else ''
                else:
                    source = ''
                    publish_date = ''
                
                # 添加到结果列表
                results.append({
                    'title': title,
                    'url': link,
                    'content': content,
                    'source': source,
                    'publish_date': publish_date
                })
            
            logger.info(f"共解析到 {len(results)} 条搜索结果")
        except Exception as e:
            logger.error(f"解析搜索结果时发生错误: {str(e)}")
        
        return results
    
    def save_results(self, results, keyword):
        """保存搜索结果到文件"""
        if not results:
            logger.warning("没有搜索结果可保存")
            return
        
        filename = f"yaan_search_results_{keyword}.txt"
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"雅安市政府网站搜索结果 - 关键词: {keyword}\n")
                f.write("=" * 60 + "\n\n")
                
                for i, result in enumerate(results, 1):
                    f.write(f"结果 {i}:\n")
                    f.write(f"标题: {result['title']}\n")
                    f.write(f"URL: {result['url']}\n")
                    f.write(f"内容: {result['content']}\n")
                    f.write(f"来源: {result['source']}\n")
                    f.write(f"发布日期: {result['publish_date']}\n")
                    f.write("-" * 60 + "\n")
            
            logger.info(f"搜索结果已保存到 {filename}")
        except Exception as e:
            logger.error(f"保存搜索结果时发生错误: {str(e)}")

if __name__ == "__main__":
    # 测试搜索功能
    searcher = YaanGovSearch()
    keyword = "雅西"
    results = searcher.search(keyword)
    
    if results:
        print(f"\n共找到 {len(results)} 条关于'{keyword}'的搜索结果：")
        for i, result in enumerate(results, 1):
            print(f"\n{i}. 标题: {result['title']}")
            print(f"   URL: {result['url']}")
            print(f"   内容: {result['content'][:100]}...")
            print(f"   发布日期: {result['publish_date']}")
        
        # 保存结果到文件
        searcher.save_results(results, keyword)
    else:
        print(f"未找到关于'{keyword}'的搜索结果")
