"""
Script for withdrawing assets from Binance account
Binance API docs: https://binance-docs.github.io/apidocs/spot/en/#change-log
Python connector: https://github.com/binance/binance-connector-python
"""

import json

from binance.spot import Spot


withdraw_to_wallets = [
    "",
    ""
]
withdraw_coin_ticker = "BUSD"
withdraw_amount = 12
withdraw_network = "BCS"

with open('config.json', 'r') as f:
    config = json.loads(f.read())


if config["binance_proxy"] != "":
    proxies = {'https': config["binance_proxy"]}
    client = Spot(key=config["binance_api_key"], secret=config["binance_api_secret"], show_header=True,
                  proxies=proxies)
else:
    client = Spot(key=config["binance_api_key"], secret=config["binance_api_secret"], show_header=True)


for wallet_address in withdraw_to_wallets:
    print(client.withdraw(coin=withdraw_coin_ticker, amount=withdraw_amount, address=wallet_address,
                          network=withdraw_network))
