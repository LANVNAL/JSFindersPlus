# 检测js文件中的敏感信息
# todo: 优化匹配，中文
# todo: 跳过一些默认js的匹配

import re

def detect_sensitive_data(js_code):
    patterns = {
        'API Key': r'[\w]{8}-[\w]{4}-[\w]{4}-[\w]{4}-[\w]{12}',  # API Key 格式为8-4-4-4-12的字符串
        'Token': r'[A-Za-z0-9]{32}',  # 32位字母数字组合的 Token
        '手机号': r'(?:\+?86)?1[3-9]\d{9}',  # 中国大陆手机号
        '人员姓名密码': r'(?:username|user|name|用户名|账号|姓名|名字)[\s:：]*([^\s:：]{6,20})[\s:：]*(?:密码|pwd|password)[\s:：]*([^\s:：]{6,20})',  # 匹配人员姓名和密码
        '姓名': r'(?:username|user|name|姓名|名字)[\s:：]*([^\s:：]{1,20})',  # 匹配人员姓名
        '密码': r'(?:密码|pwd|password)[\s:：]*([^\s:：]{6,20})',  # 匹配密码
        '邮箱地址': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b',  # 匹配邮箱地址
        '注释姓名': r'\/\/[^\n]*?([^\x00-\xff]{2,5})',  # 匹配注释中的姓名（2-5个非ASCII字符）
        '注释姓名拼音': r'\/\/[^\n]*?([A-Za-z]+\s[A-Za-z]+)',  # 匹配注释中的姓名拼音
        '注释手机号': r'\/\/[^\n]*?(\b(?:\+?86)?1[3-9]\d{9}\b)',  # 匹配注释中的手机号
        '注释邮箱': r'\/\/[^\n]*?(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b)',  # 匹配注释中的邮箱地址
        '信用卡号': r'\b(?:\d{4}[ -]?){3}(?:\d{4})\b',  # 匹配信用卡号
        '身份证号': r'\b\d{17}[\dXx]\b',  # 匹配身份证号（18位）
        '银行账号': r'\b\d{16,19}\b',  # 匹配银行账号（16-19位数字）
        '社会保险号': r'\b\d{3}-\d{2}-\d{4}\b',  # 匹配社会保险号
        '日期': r'\b\d{4}[./-]\d{1,2}[./-]\d{1,2}\b',  # 匹配日期（YYYY-MM-DD、YYYY/MM/DD、YYYY.MM.DD）
        'IP地址': r'\b(?:\d{1,3}\.){3}\d{1,3}\b',  # 匹配IP地址
        # 添加更多的模式...
    }

    sensitive_data = {}

    for data_type, pattern in patterns.items():
        matches = re.findall(pattern, js_code)
        if matches:
            sensitive_data[data_type] = matches

    return sensitive_data

if __name__ == '__main__':
    # 测试数据
    js_content = """
    var apiKey = '123e4567-e89b-12d3-a456-426655440000';
    var token = 'abcdef1234567890';
    var user = {
        username: 'john_doe',
        password: 'secret123'
    };
    // osadi
    // 张明 pipaids.sd@qq.cn
    var phone = '+8613012345678';
    var email = 'test@example.com';
    var creditCard = '1234 5678 9012 3456';
    var idCard = '110101199001011234';
    var bankAccount = '1234567890123456';
    var socialSecurityNumber = '123-45-6789';
    var date = '2023/08/14';
    var ipAddress = '192.168.0.1';
    """

    sensitive_data = detect_sensitive_data(js_content)

    if sensitive_data:
        print("检测到敏感数据泄露:")
        for data_type, data in sensitive_data.items():
            print(f"{data_type}: {data}")
    else:
        print("未检测到敏感数据泄露")