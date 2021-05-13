from wxpusher.wxpusher import WxPusher
uids=['UID_cwOvXzL0KY8k7iezszCiLluH3Dza']
def send_message(message):
    res = WxPusher.send_message(message,token='AT_eEk0qk5whArWSWIUfwgm2aBoyiJyOl2W',
        #uids=uids,
        topic_ids=[481],
        url='https://www.12306.cn/index/',
    )
    return res
if __name__ == '__main__':
    message_id=send_message("zabbix报警Test123567")
    print(message_id)