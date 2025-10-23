import os
import requests
import logging
#import asyncio
from time import sleep
from random import randint
from bs4 import BeautifulSoup
#from playwright.async_api import async_playwright

logger = logging.getLogger('arXivDownloader')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()

formatter = logging.Formatter(
    fmt='[%(levelname)s] %(asctime)s %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
handler.setFormatter(formatter)

logger.addHandler(handler)

UA='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36 Edg/141.0.0.0'

def is_file_valid_pdf(fpath):
    if not os.path.exists(fpath):
        return False, "文件不存在"
    file_size = os.path.getsize(fpath)
    if file_size == 0:
        return False, "文件为空"
    try:
        with open(fpath, 'rb') as f:
            if f.read(4) != b'%PDF':
                return False, "不是有效的PDF文件"
    except Exception as e:
        return False, f"读取文件失败: {e}"
    return True, f"文件有效，大小: {file_size} 字节"

def download_pdf_from_url(url,fname,timeout=50000,user_agent=UA):
    session = requests.Session()
    session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'application/pdf, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8'
    })
    try:
        resp = session.get(url, stream=True,timeout=timeout)
        resp.raise_for_status()
        with open(fname, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        is_valid, message = is_file_valid_pdf(fname)
        if is_valid:
            return True,f"下载成功: {fname}"
        else:
            os.remove(fname)  #删除无效文件
            return False,f"文件验证失败: {message}"
    except Exception as e:
        return False,f"下载失败: {e}"

def find_title_and_urls_from_html(content):
    soup = BeautifulSoup(content,'html.parser')
    all_divs = soup.find_all('div',class_='ant-card-body')
    v=[]
    for div in all_divs:
        title,link = '',''
        try:
            pa2 = div.find_all('div',class_='pa2')[0]
            title = pa2.find_all('span',class_='__Latex__')[0].text
            links = pa2.find_all('a',href=True)
            for L in links:
                href = L.get('href')
                if 'arxiv.org/abs' in href:
                    link = 'https:'+href if href.startswith('//') else href
                    break
            if link == '':
                links = div.find_all('a',href=True)
                for L in links:
                    href = L.get('href')
                    if 'inspirehep.net/files' in href:
                        link = 'https:'+href if href.startswith('//') else href
                        break
        except:
            pass
        if title != '' and link != '':
            link = link.replace('abs','pdf')
            v.append((title,link))
    return v

def download_papers_in_page(page_filename='page.html',save_dir='./papers'):
    if not os.path.exists(save_dir):
        os.mkdir(save_dir)
    with open('page.html','rb') as f:
        content = f.read().decode('utf-8')
        v=find_title_and_urls_from_html(content)
        for title,url in v:
            windows_forbidden_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
            windows_replace_chars   = ['[', ']', '$', '#', '%', '`',  '^', '@', '~']
            fname=title.replace(' ','_')+'.pdf'
            for old,new in zip(windows_forbidden_chars,windows_replace_chars):
                fname = fname.replace(old,new)
            logger.info(f'Downloading <<{title}>> from {url} as {fname} into {save_dir}/{fname}...')
            success,reason = download_pdf_from_url(url=url,fname=f'{save_dir}/{fname}')
            if success:
                logger.info(f'Successfully downloaded {fname}!')
            else:
                logger.error(f'Failed to download {fname}, reason: {reason}')
            sleep(randint(1,3))

'''
async def fetch(base_url):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(base_url,timeout=180000)
            await page.wait_for_selector('#root',state='visible',timeout=180000)
            content = page.content()
            soup = BeautifulSoup(content,'html.parser')
            print(content)
        finally:
            await browser.close()
'''

if __name__ == '__main__':
    download_papers_in_page()
    #asyncio.run(fetch())