"""
Script for withdrawing assets from Binance account
Binance API docs: https://binance-docs.github.io/apidocs/spot/en/#change-log
Python connector: https://github.com/binance/binance-connector-python
"""

import json
from sys import stderr, exit
from random import randint, uniform
from time import sleep

from binance.spot import Spot
from loguru import logger
from pyfiglet import Figlet


logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | <white>{message}</white>")


f = Figlet(font='5lineoblique')
print(f.renderText('Busher'))
print('Telegram channel: @CryptoKiddiesClub')
print('Telegram chat: @CryptoKiddiesChat\n')


def create_binance_client(_binance_api_key: str, _binance_api_secret: str, _proxy: str = None, ) -> Spot:
    if _proxy:
        proxies = {'https': _proxy}
        _client = Spot(key=_binance_api_key, secret=_binance_api_secret, show_header=False,
                       proxies=proxies)
    else:
        _client = Spot(key=_binance_api_key, secret=_binance_api_secret, show_header=False)

    return _client


def start_batch_withdrawal(_wallet_addresses: list, _config: dict):
    for i, wallet in enumerate(_wallet_addresses):
        amount = round(uniform(_config["withdraw_min_amount"], _config["withdraw_max_amount"]), 2)
        logger.info(f'{wallet} - sending {amount} {_config["withdraw_coin_ticker"]}')

        try:
            response = client.withdraw(coin=_config["withdraw_coin_ticker"], amount=amount, address=wallet,
                                       network=_config["withdraw_network"])
            if response["id"]:
                logger.info(f'{wallet} - sent tokens, id: {response["id"]}')
            else:
                logger.error(f'{wallet} - failed to send tokens, response: {response}')

        except Exception as e:
            logger.error(f'{wallet} - failed to send tokens')

        if i < len(_wallet_addresses) - 1:
            delay = randint(_config["withdraw_min_delay_sec"], _config["withdraw_max_delay_sec"])
            logger.info(f'Sleeping {round(delay / 60, 2)} minutes')
            sleep(delay)


if __name__ == "__main__":
    with open('data/01_config.json', 'r') as f:
        config = json.loads(f.read())

    with open(f'data/01_wallet_addresses.txt') as file:
        wallet_addresses = [line.rstrip() for line in file]

    client = create_binance_client(config["binance_api_key"], config["binance_api_secret"], config["binance_proxy"])

    confirm_action = input(f'Going to withdraw {config["withdraw_min_amount"]} - {config["withdraw_max_amount"]} '
                           f'{config["withdraw_coin_ticker"]} in {config["withdraw_network"]} network to '
                           f'{len(wallet_addresses)} different wallets with delay {config["withdraw_min_delay_sec"]} - '
                           f'{config["withdraw_max_delay_sec"]} seconds\n'
                           f'Are you sure? (y/n): ')

    if confirm_action.lower() == 'n':
        logger.info('User cancelled operation, quitting')
        exit()
    elif confirm_action.lower() == 'y':
        logger.info('User confirmed operation, starting')
        start_batch_withdrawal(wallet_addresses, config)
        logger.info('Finished batch withdrawal')
    else:
        logger.error('Wrong entry, quitting')
        exit()
