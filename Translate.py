from playsound import playsound
import requests
import json
import hashlib
import random
import os
import re
import execjs

class Transtate:
    def __init__(self):
        self._appid = '20201003000579661'
        self._key = 'CVer_8RORexp76w_EJ8l'

        self.trans_str = None
        self.trans_url = "https://fanyi.baidu.com/v2transapi"
        self.headers = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.100 Safari/537.36",
            # 必须带上cookie，否则请求返回的是错误信息
            "Cookie": "BAIDUID=AFB6E3FB47D3EEA8C525D02E728E0991:FG=1; BIDUPSID=AFB6E3FB47D3EEA8C525D02E728E0991; PSTM=1556177968; REALTIME_TRANS_SWITCH=1; FANYI_WORD_SWITCH=1; HISTORY_SWITCH=1; SOUND_SPD_SWITCH=1; SOUND_PREFER_SWITCH=1; MCITY=-131%3A; Hm_lvt_64ecd82404c51e03dc91cb9e8c025574=1556507678,1557287607,1557714510,1557972796; BDSFRCVID=xr-sJeCCxG3twro9YX2saOEfCZPT14fNd2s33J; H_BDCLCKID_SF=tR3fL-08abrqqbRGKITjhPrM2hKLbMT-027OKKO2b-oobfTyDRbHXULELn6TLT_J5eobot8bthF0HPonHj85j6bQ3J; PSINO=2; delPer=0; H_PS_PSSID=1450_28937_21095_18560_29064_28518_29098_28722_28963_28836_28584_26350; locale=zh; yjs_js_security_passport=5b9f340d92cf7400bd5ba82b49a65bc0520935cc_1558490261_js; Hm_lpvt_64ecd82404c51e03dc91cb9e8c025574=1558493551; to_lang_often=%5B%7B%22value%22%3A%22jp%22%2C%22text%22%3A%22%u65E5%u8BED%22%7D%2C%7B%22value%22%3A%22en%22%2C%22text%22%3A%22%u82F1%u8BED%22%7D%2C%7B%22value%22%3A%22zh%22%2C%22text%22%3A%22%u4E2D%u6587%22%7D%5D; from_lang_often=%5B%7B%22value%22%3A%22jp%22%2C%22text%22%3A%22%u65E5%u8BED%22%7D%2C%7B%22value%22%3A%22zh%22%2C%22text%22%3A%22%u4E2D%u6587%22%7D%2C%7B%22value%22%3A%22en%22%2C%22text%22%3A%22%u82F1%u8BED%22%7D%5D"
        }
        self.pattern = re.compile(r"window\['common'\]\W*?=\W*?{\W*?.*?token.*?:.*?'(\w+)',")
        self.pattern_gtk = re.compile(r"window.gtk\W*?=\W*?'(.*?)'")

    def __parse_url(self, data, url="https://fanyi.baidu.com/langdetect"):
        response = requests.post(url, data=data, headers=self.headers)
        return json.loads(response.content.decode())

    def __get_token_or_gtk(self, url="https://fanyi.baidu.com/translate"):
        response = requests.get(url, headers=self.headers)
        str = response.content.decode()
        token = self.pattern.search(str).group(1)
        gtk = self.pattern_gtk.search(str).group(1)
        return token, gtk

    def __get_sign(self, gtk):
        with open("./cs.js", 'r') as f:
            js_code = f.read()
        ctx = execjs.compile(js_code)
        return ctx.call("e", self.trans_str, gtk)


    def translate_dict(self):
        if self.trans_str != None:
            token, gtk = self.__get_token_or_gtk()
            lang_detect_data = {"query": self.trans_str}
            lang = self.__parse_url(lang_detect_data)["lan"]
            trans_data = {
                "query": self.trans_str,
                "from": "zh", "to": "en"
            } if lang == "zh" else \
                {
                "query": self.trans_str,
                "from": "en", "to": "zh"
            }

            sign = self.__get_sign(gtk)
            trans_data.update({"sign": sign, "token": token, "transtype": "translang", "simple_means_flag": 3})
            dict_response = self.__parse_url(trans_data, self.trans_url)

            return dict_response['trans_result']['data']




    def transtate(self,word,toLang):
        if self.trans_str != None:
            url = 'https://fanyi-api.baidu.com/api/trans/vip/translate'
            salt = random.randint(32768, 65536)
            sign = self._appid + word + str(salt) + self._key
            sign = hashlib.md5(sign.encode()).hexdigest()

            headers = {
                'Content-Type':'application/x-www-form-urlencoded'
            }
            data = {
                'q':word,
                'from':'auto',
                'to':toLang,
                'appid':self._appid,
                'salt':salt,
                'sign':sign
            }

            html = requests.post(url,data=data,headers=headers)
            content = json.loads(html.text)

            return content['trans_result'][0]['dst']

    def texttospeech(self):
        if self.trans_str != None:
            if not os.path.exists('cache'):
                os.mkdir('cache')
            file_name = 'cache/' + self.trans_str + ".mp3"
            file_name = file_name.replace("?",'') # ? 会有bug，去掉文件名里的 ？
            url = 'https://fanyi.baidu.com/gettts?lan=uk&text={0}&spd=3&source=web'.format(self.trans_str)
            html = requests.get(url)
            with open(file_name,'wb') as f:
                f.write(html.content)

        playsound(file_name)


if __name__ == "__main__":
    trant = Transtate()
    trant.trans_str = 'gay'
    a  = trant.translate_dict()
    print(a)