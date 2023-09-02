from random import choice

import requests
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

from core.utils import str_to_file, logger
from string import ascii_lowercase, digits

from core.utils import MailUtils

from inputs.config import (
    MOBILE_PROXY,
    MOBILE_PROXY_CHANGE_IP_LINK
)


class Vold(MailUtils):
    referral = None

    def __init__(self, email: str, imap_pass: str, proxy: str = None):
        super().__init__(email, imap_pass)
        self.proxy = Vold.get_proxy(proxy)

        self.headers = {
            'Accept': 'application/json',
            'Accept-Language': 'uk-UA,uk;q=0.9',
            'Cache-Control': 'no-cache',
            'Connection': 'keep-alive',
            'Content-Type': 'application/json',
            'Origin': 'https://referlist.co',
            'Referer': 'https://referlist.co/',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'cross-site',
            'User-Agent': UserAgent().random,
            'sec-ch-ua': '"Chromium";v="116", "Not)A;Brand";v="24", "Google Chrome";v="116"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
        }

        self.session = requests.Session()

        self.session.headers.update(self.headers)
        self.session.proxies.update({'https': self.proxy, 'http': self.proxy})

    @staticmethod
    def get_proxy(proxy: str):
        if MOBILE_PROXY:
            Vold.change_ip()
            proxy = MOBILE_PROXY

        if proxy is not None:
            return f"http://{proxy}"

    @staticmethod
    def change_ip():
        requests.get(MOBILE_PROXY_CHANGE_IP_LINK)

    def enter_waitlist(self):
        url = 'https://referlist.herokuapp.com/api/addtowaitlist'

        json_data = {
            'email': self.email,
            'referralSource': Vold.referral,
            'waitlistName': 'vold',
        }

        res = self.session.post(url, json=json_data)

        return res.json()

    def verify_email(self):
        verify_link = self.get_verify_link()
        return self.approve_email(verify_link)

    def get_verify_link(self):
        result = self.get_msg(subject="Confirm your email for Vold",
                              from_="no-reply@waitlist.referlistmailer.co", limit=3)
        html = result["msg"]
        soup = BeautifulSoup(html, 'lxml')
        a = soup.select_one('td > div > a')
        return a["href"]

    def approve_email(self, verify_link: str):
        url = "https://referlist.herokuapp.com/api/verify"

        json_data = {
            'token': verify_link.split("?token=")[1],
        }

        response = self.session.post(url, json=json_data)

        return "verified" == response.json()["type"]

    def logs(self, file_name: str):
        file_msg = f"{self.email}|{self.proxy}"
        str_to_file(f"./logs/{file_name}.txt", file_msg)
        logger.success(f"{self.email} | Register")

    @staticmethod
    def generate_password(k=10):
        return ''.join([choice(ascii_lowercase + digits) for _ in range(k)])
