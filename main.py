import argparse
import html
import os
import sys
from itertools import groupby

import requests
import urllib3

import config
from JSFinder import find_by_url, giveresult
from Utils import extract_ip_or_url


normal_rsp = ""
def parse_args():
    parser = argparse.ArgumentParser(epilog='\tExample: \r\npython ' + sys.argv[0] + " -u http://www.baidu.com")
    parser.add_argument("-u", "--url", help="Target Domain")
    parser.add_argument("-nc", "--new_cookie", help="The new website cookie")
    parser.add_argument("-oc", "--original_cookie", help="The original website cookie")
    parser.add_argument("-p", "--same_rsp", help="Pass if same with this Resopnse")
    return parser.parse_args()

def init():
    '''
    初始化，检查输出目录，不存在则创建
    获取normal_rsp原始响应数据，判断是否指定定cookie和url
    :return:
    '''
    os.makedirs(config.Report_output_path, exist_ok=True)  # 创建目录（如果不存在）
    global normal_rsp
    original_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Cookie': args.original_cookie,
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    if args.same_rsp:
        normal_rsp = requests.get(args.same_rsp, headers=original_headers, verify=False).content
    else:
        normal_rsp = requests.get(args.url, headers=original_headers, verify=False).content


def check_urls_auth(urls):
    '''
    对于提取的urls，获取请求状态码
    :param urls: 包含url的list
    :return: 保存url和状态码的字典
    '''
    # 构造请求头
    new_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
        'Cookie': args.new_cookie,
        'Cache-Control': 'no-cache',
        'Pragma': 'no-cache'
    }
    # 创建一个空的字典，用于保存url和状态码对应关系
    url_status_dict = {}
    for url in urls:
        # print(url)
        if check_type(url) != "pass":
            try:
                # 处理一些请求异常导致退出问题
                response = requests.get(url, headers=new_headers, verify=False)
            except:
                continue
            status_code = response.status_code

            if response.content == normal_rsp:
                status = "status code: {} , 是否重复: {} , 响应长度: {}".format(status_code, "是", len(response.content))
                is_repeat = "是"
            else:
                status = "status code: {} , 是否重复: {} , 响应长度: {}".format(status_code, "否", len(response.content))
                is_repeat = "否"
            response_length = len(response.content)
            url_status_dict[url] = [status_code, response_length, is_repeat]
        else:
            continue
    return url_status_dict


def check_type(url):
    '''
    静态资源是否记录，做个判断条件，同时可以配置开关
    :param url: url
    :return: pass表示可以继续
    '''
    if config.static_resources_log:
        (path, file_ext) = os.path.splitext(url)
        # print(file_ext)
        if file_ext != '' and file_ext in config.static_resources_type:
            return "pass"
        else:
            return
    else:
        return
def format_print(result):
    # 按照状态码进行聚类，输出url和状态码
    # for status_code, group in groupby(sorted(result.items()), lambda x: x[1]):
    #     print(f'Status Code: {status_code}')
    #     for url, status_code in sorted(group):
    #         print(f'  {url:<30} {status_code}')

    # 美观地输出结果
    print('----------------------------------------')
    print('Formatted Output:')
    for status_code, group in groupby(sorted(result.items(), key=lambda x: x[1][0]), lambda x: x[1][0]):
        print(f'Status Code: {status_code}')
        for url, status_code in sorted(group, key=lambda x: x[0]):
            print(f'  {url:<30} {status_code}')


def make_table_row(data, is_duplicate):
    row_html = '<tr style="color: red">' if is_duplicate else '<tr>'
    for item in data:
        row_html += f'<td>{html.escape(str(item))}</td>'
    row_html += '</tr>'
    return row_html

def save_result(result):
    # 构造 HTML 文件的头部和尾部信息
    html_head = '<html><head><title>Domain</title></head><body>'
    html_tail = '</body></html>'

    # 构造表格的表头和表尾信息
    table_head = '<table><tr><th>URL</th><th>状态码</th><th>响应长度</th><th>是否重复</th></tr>'
    table_tail = '</table>'

    # 按照状态码进行聚类，输出每个状态码对应的表格
    output_html = html_head
    for status_code, group in groupby(sorted(result.items(), key=lambda x: x[1][0]), lambda x: x[1][0]):
        output_html += f'<h2>Status Code: {status_code}</h2>'
        output_html += table_head
        output_html += make_table_row(('URL', '状态码', '响应长度', '是否重复'), False)
        for url, (status_code, content_length, is_duplicate) in sorted(group, key=lambda x: x[0]):
            output_html += make_table_row((url, status_code, content_length, is_duplicate), is_duplicate == '否')
        output_html += table_tail

    # 添加 HTML 文件尾部信息，将结果输出到文件中
    output_html += html_tail
    domain = extract_ip_or_url(args.url)
    filename = domain + ".html"
    with open(config.Report_output_path + filename, 'w', encoding='utf-8') as f:
        f.write(output_html)
    print("报告保存在：{}".format(config.Report_output_path + filename))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    urllib3.disable_warnings()
    args = parse_args()
    init()
    if args.new_cookie:
        print("Set New Cookie: {}".format(args.new_cookie))
    if args.original_cookie:
        print("Set Original Cookie: {}".format(args.original_cookie))
    # 设置响应对比的基准
    # todo: 设置两组cookie，进行对比用

    urls = find_by_url(args.url)
    result = check_urls_auth(urls)
    # format_print(result)
    # print(urls)
    save_result(result)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
