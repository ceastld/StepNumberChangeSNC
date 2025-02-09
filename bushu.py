# -*- coding: utf8 -*-

import requests,time,re,json,random
import os

TG_BOT_TOKEN = ""           # telegram bot token 自行申请
TG_USER_ID = ""             # telegram 用户ID

def telegram_bot(title, content):
    print("\n")
    tg_bot_token = TG_BOT_TOKEN
    tg_user_id = TG_USER_ID
    if "TG_BOT_TOKEN" in os.environ and "TG_USER_ID" in os.environ:
        tg_bot_token = os.environ["TG_BOT_TOKEN"]
        tg_user_id = os.environ["TG_USER_ID"]
    if not tg_bot_token or not tg_user_id:
        print("Telegram推送的tg_bot_token或者tg_user_id未设置!!\n取消推送")
        return
    print("Telegram 推送开始")
    send_data = {"chat_id": tg_user_id, "text": title +
                 '\n\n'+content, "disable_web_page_preview": "true"}
    response = requests.post(
        url='https://api.telegram.org/bot%s/sendMessage' % (tg_bot_token), data=send_data)
    print(response.text)

now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
headers = {
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; MI 6 MIUI/20.6.18)'
        }

#获取登录code
def get_code(location):
    code_pattern = re.compile("(?<=access=).*?(?=&)")
    code = code_pattern.findall(location)[0]
    return code

#登录
def login(user,password):
    url1 = "https://api-user.huami.com/registrations/" + user + "/tokens"
    headers = {
        "Content-Type":"application/x-www-form-urlencoded;charset=UTF-8",
    "User-Agent":"Mozilla/5.0 (iPhone; CPU iPhone OS 14_7_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2"
        }
    data1 = {
        "client_id":"HuaMi",
        "password":f"{password}",
        "redirect_uri":"https://s3-us-west-2.amazonaws.com/hm-registration/successsignin.html",
        "token":"access"
        }
    r1 = requests.post(url1,data=data1,headers=headers,allow_redirects=False)
    location = r1.headers["Location"]
    try:
        code = get_code(location)
    except:
        return 0,0
    #print("access_code获取成功！")ste
    #print(code)

    url2 = "https://account.huami.com/v2/client/login"
    data2 = {
            "allow_registration=": "false",
            "app_name": "com.xiaomi.hm.health",
            "app_version": "6.3.5",
            "code": f"{code}",
            "country_code": "CN",
            "device_id": "2C8B4939-0CCD-4E94-8CBA-CB8EA6E613A1",
            "device_model": "phone",
            "dn": "api-user.huami.com%2Capi-mifit.huami.com%2Capp-analytics.huami.com",
            "grant_type": "access_token",
            "lang": "zh_CN",
            "os_version": "1.5.0",
            "source": "com.xiaomi.hm.health",
            "third_name": "email",
        } 
    r2 = requests.post(url2,data=data2,headers=headers).json()
    login_token = r2["token_info"]["login_token"]
    #print("login_token获取成功！")
    #print(login_token)
    userid = r2["token_info"]["user_id"]
    #print("userid获取成功！")
    #print(userid)

    return login_token,userid

#主函数
def main(user, passwd, step):
    user = str(user)
    password = str(passwd)
    step = str(step)
    if user == '' or password == '':
        print ("用户名或密码填写有误！")
        return

    if step == '':
        print ("已设置为随机步数（20000-29999）")
        step = str(random.randint(20000,29999))
    login_token = 0
    login_token,userid = login(user,password)
    if login_token == 0:
        print("登陆失败！")
        return "login fail!"

    t = get_time()

    app_token = get_app_token(login_token)

    today = time.strftime("%F")

    data_json = open('data.txt','r').read()
    finddate = re.compile(r'.*?date%22%3A%22(.*?)%22%2C%22data.*?')
    findstep = re.compile(r'.*?ttl%5C%22%3A(.*?)%2C%5C%22dis.*?')
    data_json = re.sub(finddate.findall(data_json)[0], today, str(data_json))
    data_json = re.sub(findstep.findall(data_json)[0], step, str(data_json))

    url = f'https://api-mifit-cn.huami.com/v1/data/band_data.json?&t={t}'
    head = {
        "apptoken": app_token,
        "Content-Type": "application/x-www-form-urlencoded"
        }

    data = f'userid={userid}&last_sync_data_time=1597306380&device_type=0&last_deviceid=DA932FFFFE8816E7&data_json={data_json}'

    response = requests.post(url, data=data, headers=head).json()
    #print(response)
    result = f"{user[:4]}****{user[-4:]}: [{now}] 修改步数（{step}）"+ response['message']
    print(f"修改步数({step})"+response['message'])
    qqtalk = 'https://qmsg.zendee.cn/send/KYE?msg=' + "修改步数：" + step + "  " + response[
        'message'] + '&qq=QQ'
    requests.get(qqtalk)
    return result
#修改上方的KYE和QQ
# qqtalk = 'https://qmsg.zendee.cn/send/输入你的kye?msg=' + "修改步数：" + step + "  " + response[
#        'message'] + '&qq=输入你的qq号'
#获取时间戳
# def get_time():
#     url = 'http://worldtimeapi.org/api/timezone/Asia/Shanghai'
#     response = requests.get(url, headers=headers)
#     response.raise_for_status()
#     data = response.json()
#     t = str(data['unixtime'])+'000'
#     return t
from datetime import datetime

def get_time():
    local_time = datetime.now().timestamp()
    t = str(int(local_time)) + '000'
    return t


#获取app_token
def get_app_token(login_token):
    url = f"https://account-cn.huami.com/v1/client/app_tokens?app_name=com.xiaomi.hm.health&dn=api-user.huami.com%2Capi-mifit.huami.com%2Capp-analytics.huami.com&login_token={login_token}"
    response = requests.get(url,headers=headers).json()
    app_token = response['token_info']['app_token']
    #print("app_token获取成功！")
    #print(app_token)
    return app_token

def main_handler(event, context):
    # 用户名（单用户的格式为 13800138000 ，多用户用#隔开，例如13800138000#13800138000#13800138000）
    user = "1950946176@qq.com"
    # 登录密码（用#隔开，例如123456#123456#123456）
    passwd = "Ldy20020519"
    # 要修改的步数，直接输入想要修改的步数值，留空为随机步数20000至29999之间
    step = "5555"

    user_list = user.split('#')
    passwd_list = passwd.split('#')
    setp_array = step.split('-')

    if len(user_list) == len(passwd_list):
        push = ''
        for line in range(0,len(user_list)):
            if len(setp_array) == 2:
                step = str(random.randint(int(setp_array[0]),int(setp_array[1])))
            elif str(step) == '0':
                step = ''
            push += main(user_list[line], passwd_list[line], step) + '\n'
        telegram_bot("小米运动", push)
    else:
        print('用户名和密码数量不对')

if __name__ == '__main__':
    # 用户名（单用户的格式为 13800138000 ，多用户用#隔开，例如13800138000#13800138000#13800138000）
    user = "1950946176@qq.com"
    # 登录密码（用#隔开，例如123456#123456#123456）
    passwd = "Ldy20020519"
    # 要修改的步数，直接输入想要修改的步数值，留空为随机步数20000至29999之间
    import random
    step = random.randint(300,700)
    
    try:
        data = json.loads(open('bushu.json','r').read())
        if data['time']:
            last_time = datetime.fromisoformat(data['time'])
            if last_time.date() == datetime.today().date():
                step += int(data['step'])
    except:
        pass

    json.dump({'step':step,'time':datetime.now().isoformat()},open('bushu.json','w'))
    
    step = min(700, step)+random.randint(0,300)
    main(user, passwd, step)