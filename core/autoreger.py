import time
from concurrent.futures import ThreadPoolExecutor

from core.utils import shift_file, logger
from core.utils.file_to_list import file_to_list
from core.vold import Vold

from inputs.config import (
    REFERRAL, THREADS, CUSTOM_DELAY, EMAILS_FILE_PATH, PROXIES_FILE_PATH
)


class AutoReger:
    def __init__(self):
        self.success = 0
        self.custom_user_delay = None

    @staticmethod
    def get_accounts():
        emails = file_to_list(EMAILS_FILE_PATH)
        proxies = file_to_list(PROXIES_FILE_PATH)

        min_accounts_len = len(emails)

        accounts = []

        for i in range(min_accounts_len):
            accounts.append((*emails[i].split(":")[:2], proxies[i] if len(proxies) > i else None))

        return accounts

    @staticmethod
    def remove_account():
        return shift_file(EMAILS_FILE_PATH), shift_file(PROXIES_FILE_PATH)

    def start(self):
        referral_link = REFERRAL

        Vold.referral = referral_link.split('?ref=')[-1]

        threads = THREADS

        self.custom_user_delay = CUSTOM_DELAY

        accounts = AutoReger.get_accounts()

        with ThreadPoolExecutor(max_workers=threads) as executor:
            executor.map(self.register, accounts)

        if self.success:
            logger.success(f"Successfully registered {self.success} accounts :)")
        else:
            logger.warning(f"No accounts registered :(")

    def register(self, account: tuple):
        vold = Vold(*account)
        is_ok = False

        try:
            time.sleep(self.custom_user_delay)

            if vold.enter_waitlist():
                is_ok = vold.verify_email()
        except Exception as e:
            logger.error(f"Error {e}")

        AutoReger.remove_account()

        if is_ok:
            vold.logs("success")
            self.success += 1
        else:
            vold.logs("fail")

    @staticmethod
    def is_file_empty(path: str):
        return not open(path).read().strip()
