import requests
import time
from web3 import Web3
import json
from config import TOKEN, USER_ID, WALLET, SHARK_ID


class User:
    def __init__(self, user_id, keyboard):
        self.user_id = user_id
        self.reply_markup = keyboard

    def add_menu(self, element):
        self.reply_markup[user_id].setdefault('keyboard', []).append([element])

    def del_menu(self, element):
        for elem in range(0, len(self.reply_markup)):
            if self.reply_markup[elem][0] == element:
                del self.reply_markup[elem]
                break


class Bot:
    def __init__(self, token):
        self.token = token

    def get_message(self, offset=0):
        url = f'https://api.telegram.org/bot{self.token}/getUpdates?offset={offset}'
        try:
            response = requests.get(url=url).json()
            try:
                return response['result']
            except:
                #print(response)
                pass
        except requests.exceptions.ConnectionError:
            print("Connection refused")
            time.sleep(5)
    
    def send_message(self, chat_id, text, reply_markup=None):
        if reply_markup:
            url = f'https://api.telegram.org/bot{self.token}/sendMessage?chat_id={chat_id}&text={text}&reply_markup={json.dumps(reply_markup)}'
        else:
            url = f'https://api.telegram.org/bot{self.token}/sendMessage?chat_id={chat_id}&text={text}'
            
        response = requests.get(url=url).json()
        return response['result']['message_id']

    def edit_message(self, chat_id, message_id, textarea):
        url = f'https://api.telegram.org/bot{self.token}/editMessageText?chat_id={chat_id}&message_id={message_id}&text={textarea}&parse_mode=HTML'
        requests.get(url=url)


class Crypto:
    def __init__(self):
        self.url_eth = 'https://api.bscscan.com/api'
        self.bsc = 'https://bsc-dataseed.binance.org/'
        self.url_bnb = 'https://starsharks.com/go/api/market/exchange-rate'
        self.headers_bnb = {
            'content-type': 'application/json',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.174 YaBrowser/22.1.4.837 Yowser/2.5 Safari/537.36',
        }

        self.url_sharks = 'https://starsharks.com/go/api/market/sharks'
        self.headers_sharks = self.headers_bnb
        self.data_raw = '{"class":[],"stage":[],"star":0,"pureness":0,"hp":[0,200],"speed":[0,200],"skill":[0,200],"morale":[0,200],"body":[],"parts":[],"skill_id":[0,0,0,0],"full_energy":false,"page":1,"filter":"sell","sort":"PriceAsc","page_size":36}'

    def get_balance_wallet(self, web3, address, token_address):
        contract_address = web3.toChecksumAddress(token_address)  # Преобразует регистр в адресе
        api_endpoint = self.url_eth + '?module=contract&action=getabi&address=' + str(contract_address)
        r = requests.get(url=api_endpoint)
        response = r.json()
        abi = json.loads(response['result'])
        contract = web3.eth.contract(address=contract_address, abi=abi)
        balance = contract.functions.balanceOf(address).call()
        return web3.fromWei(balance, 'ether')

    def get_bnb_shark(self):
        response = requests.get(self.url_bnb, headers=self.headers_bnb)
        return response.json()['data']['bnb'], response.json()['data']['sea']

    def get_price_shark(self):
        response = requests.post(url=self.url_sharks, headers=self.headers_sharks, data=self.data_raw)
        return response.json()['data']['sharks'][0]['sheet']['sell_price']


def get_cost_rub(token_usd, headers):
    url = 'https://p2p.binance.com/bapi/c2c/v2/friendly/c2c/adv/search'

    data_raw_d = {
        "page": 1,
        "rows": 10,
        "payTypes": ["Tinkoff"],
        "asset": f"{token_usd}",
        "tradeType": "SELL",
        "fiat": "RUB",
        "publisherType": "merchant",
        "merchantCheck": 'false'
    }

    response = requests.post(url=url, headers=headers, data=str(data_raw_d))
    merchant_1 = float(response.json()['data'][0]['adv']['price'])
    merchant_2 = float(response.json()['data'][1]['adv']['price'])
    if merchant_1 >= merchant_2 + 1.5:
        return merchant_2
    else:
        return merchant_1


def message_text(address, headers, message_id, user_id):
    web3 = Web3(Web3.HTTPProvider(crypto.bsc))
    balance_bnb = web3.eth.get_balance(address)
    bnb_balance = web3.fromWei(balance_bnb, 'ether')
    bot.edit_message(user_id, message_id, 'In Process 1/6')
    time.sleep(5)
    sea_balance = float(
        '{:.2f}'.format(crypto.get_balance_wallet(web3, address, '0x26193C7fa4354AE49eC53eA2cEBC513dc39A10aa')))
    bot.edit_message(user_id, message_id, 'In Process 2/6')
    time.sleep(5)
    busd_balance = float('{:.2f}'.format(crypto.get_balance_wallet(web3, address, '0xe9e7cea3dedca5984780bafc599bd69add087d56')))
    time.sleep(5)
    snft = int(crypto.get_balance_wallet(web3, address, '0x416f1D70c1C22608814d9f36c492EfB3Ba8cad4c')*pow(10,18))
    bot.edit_message(user_id, message_id, 'In Process 3/6')
    bnb, sea = crypto.get_bnb_shark()
    bot.edit_message(user_id, message_id, 'In Process 4/6')
    time.sleep(1)
    price = crypto.get_price_shark()
    bot.edit_message(user_id, message_id, 'In Process 5/6')

    b = str(float(bnb) * float(price))
    price_min_shark = str(float('{:.2f}'.format(float(b))))
    token_sea = str(float("{:.2f}".format(sea)))
    price_box = str(float(token_sea) * 500)
    mine_sea = str(float(token_sea) * 14.3625)
    mine_sea_14 = str(float(token_sea) * 13.405)
    dollars = float("{:.2f}".format(busd_balance+(sea_balance * sea)))
    busd_rub = get_cost_rub('BUSD', headers)
    usdt_rub = get_cost_rub('USDT', headers)
    bot.edit_message(user_id, message_id, 'In Process 6/6')

    if busd_rub > usdt_rub:
        roi = str(int(busd_rub * dollars)) + ' / 20000'
    else:
        roi = str(int(usdt_rub * dollars)) + ' / 20000'

    purpose = f'{roi} Руб.\n{sea_balance} / 500 SEA'

    textarea = '''
<b>------------------------------------</b>
<b>|                 🦊 Metamask 🦊                |
------------------------------------</b>
{bnb_text} BNB
{busd_text} BUSD
{sea_text} SEA
<b>------------------------------------</b>
🏧 $ | BUSD | USDT 🏧
{dollars} $
{busd_balance} Руб. | {busd} Руб.
{usdt_balance} Руб. | {usdt} Руб.
<b>------------------------------------</b>
📌 Purpose 📌
{purpose}
<b>------------------------------------</b>
<b>|                🦈 StarSharks 🦈                |
------------------------------------</b>
💹 Market 💹
{price_min_shark} BUSD
{price} BNB

🎁 MysteryBox 🎁
~{price_box} BUSD
<b>------------------------------------</b>
🪙 Token 🪙
{bnb} BNB
{sea} SEA
<b>------------------------------------</b>
💧 Mining 💧
15 SEA ~ {mine_sea} $
14 SEA ~ {mine_sea_14} $
<b>------------------------------------</b>
'''.format(bnb_text='{:.4f}'.format(bnb_balance), bnb=bnb, sea_text=sea_balance, sea=token_sea,
           busd_text=busd_balance, dollars=dollars,
           price_min_shark=price_min_shark, price=price, price_box=price_box,
           mine_sea="{:.2f}".format(float(mine_sea)), mine_sea_14="{:.2f}".format(float(mine_sea_14)),
           busd_balance=int(busd_rub * dollars), usdt_balance=int(usdt_rub * dollars),
           busd=busd_rub, usdt=usdt_rub, purpose=purpose)

    return textarea


def position_shark(shark_id, headers, message_id, user_id):
    def req_page(page):
        url = 'https://starsharks.com/go/api/market/sharks'
        data_raw = '{"page":' + str(page) + ',"filter":"rent","sort":"PriceAsc","page_size":36}'
        response = requests.post(url=url, headers=headers, data=str(data_raw))

        return response.json()['data']

    headers = {'content-type': 'application/json',
               'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.174 YaBrowser/22.1.5.810 Yowser/2.5 Safari/537.36', }

    response = req_page(1)
    total_page = int(response['total_page'])

    for i in range(len(response['sharks'])):
        if int(response['sharks'][i]['sheet']['shark_id']) == int(shark_id):
            print(f"Page 1 / {total_page} [{i + 1}]")

    time.sleep(1)

    url_my_shark = f'https://starsharks.com/go/api/market/shark-detail?shark_id={shark_id}&account='
    response_my_shark = requests.get(url=url_my_shark, headers=headers)
    time_my_shark = response_my_shark.json()['data']['sheet']['updated_at']

    array = [int(total_page * 0.25), int(total_page * 0.5), int(total_page * 0.75), total_page]
    time.sleep(1)

    temp = req_page(array[0])['sharks'][0]['sheet']['updated_at']  # время акулы в шаге
    if time_my_shark > temp:
        time.sleep(1)
        temp = req_page(array[1])['sharks'][0]['sheet']['updated_at']  # время акулы в шаге
        if time_my_shark > temp:
            time.sleep(1)
            temp = req_page(array[2])['sharks'][0]['sheet']['updated_at']  # время акулы в шаге
            if time_my_shark > temp:

                for k in range(array[3], 0, -1):
                    time.sleep(1)
                    response = req_page(k)
                    for j in range(len(response['sharks'])):
                        if int(response['sharks'][j]['sheet']['shark_id']) == int(shark_id):
                            return f"Page {k} / {total_page} [{j + 1}]"

                    bot.edit_message(user_id, message_id, f'In Process {k}/{total_page}')
            else:
                for k in range(array[2], 0, -1):
                    time.sleep(1)
                    response = req_page(k)
                    for j in range(len(response['sharks'])):
                        if int(response['sharks'][j]['sheet']['shark_id']) == int(shark_id):
                            return f"Page {k} / {total_page} [{j + 1}]"

                    bot.edit_message(user_id, message_id, f'In Process {k}/{total_page}')
        else:
            for k in range(array[1], 0, -1):
                time.sleep(1)
                response = req_page(k)
                for j in range(len(response['sharks'])):
                    if int(response['sharks'][j]['sheet']['shark_id']) == int(shark_id):
                        return f"Page {k} / {total_page} [{j + 1}]"

                bot.edit_message(user_id, message_id, f'In Process {k}/{total_page}')
    else:
        for k in range(array[0], 0, -1):
            time.sleep(1)
            response = req_page(k)
            for j in range(len(response['sharks'])):
                if int(response['sharks'][j]['sheet']['shark_id']) == int(shark_id):
                    return f"Page {k} / {total_page} [{j + 1}]"

            bot.edit_message(user_id, message_id, f'In Process {k}/{total_page}')

    return 'Акула с таким id не найдена'


def time_rent_shark(shark_id, headers):
    url = f'https://starsharks.com/go/api/market/rent-sale-list?shark_id={shark_id}'
    response = requests.get(url=url, headers=headers)
    time = response.json()['data']['rent'][0]['created_at'].split()[1]

    if int(time[0:2]) + 6 >= 24:
        time = '0' + str(int(time[0:2]) + 6 - 24) + time[2:]
    else:
        time = str(int(time[0:2]) + 6) + time[2:]

    return time


def main(update_id, user):
    headers = {
        'content-type': 'application/json',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.174 YaBrowser/22.1.5.810 Yowser/2.5 Safari/537.36',
    }
    while True:
        time.sleep(2)
        messages = bot.get_message(update_id)
        for message in messages:
            if update_id < message['update_id']:
                update_id = message['update_id']

                text = message['message']['text']

                user_id = int(message['message']['from']['id'])

                if user_id == user.user_id:
                    if text.split()[0] == '/start':
                        bot.send_message(user_id, 'Ready', user.reply_markup)
                    
                    elif len(text) == 42:
                        message_id = bot.send_message(user_id, 'In Process...')
                        print(1)
                        bot.edit_message(user_id, message_id, message_text(text, headers, message_id, user_id))
                        print(2)

                    elif text.split()[0] == '/add' and len(text.split()) == 2:
                        user.add_menu(text.split()[1])
                        bot.send_message(user_id, f'Menu Edit!', user.reply_markup)

                    elif text.split()[0] == '/del' and len(text.split()) == 2:
                        user.del_menu(text.split()[1])
                        bot.send_message(user_id, f'Menu Edit!', user.reply_markup)

                    elif len(text) == 6:
                        message_id = bot.send_message(user_id, 'In Process...')
                        bot.edit_message(user_id, message_id, position_shark(text, headers, message_id, user_id))

                    elif text.split()[0] == '/time' and len(text.split()) == 2:
                        bot.send_message(user_id, time_rent_shark(text.split()[1], headers))
                    
                    else:
                        bot.send_message(user_id, 'Error commands...')


if __name__ == '__main__':

    print('Start')
    bot = Bot(TOKEN)
    crypto = Crypto()
    user_id = USER_ID
    SHARK_TIME = []
    for item in SHARK_ID:
        SHARK_TIME.append('/time {}'.format(item))
    
    
    keyboard = {user_id: {'keyboard': [[WALLET],
                                        SHARK_ID,
                                        SHARK_TIME
                                      ], 'resize_keyboard': True},
            }
    
    user = User(user_id, keyboard)
    bot.send_message(user.user_id, 'StartUp', user.reply_markup)
    update_id = bot.get_message()[-1]['update_id']
    main(update_id, user)

