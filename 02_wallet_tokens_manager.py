"""
Script for managing tokens on your wallets
"""

from sys import stderr, exit
from time import sleep

from web3 import Web3
from loguru import logger


logger.remove()
logger.add(stderr, format="<white>{time:HH:mm:ss}</white> | <level>{level: <8}</level> | "
                          "<white>{message}</white>")


def batch_collect_native_coins(_private_keys_from: list, _public_key_to: str, _gas_price_gwei: int):
    """
    Collecting native coins from provided private keys to main wallet using defined gas price
    :param _private_keys_from: list of private keys
    :param _public_key_to: collecting address
    :param _gas_price_gwei: gas price in GWEI
    """

    for _i, _key in enumerate(_private_keys_from):
        logger.info(f"{_i + 1} : processing account")
        sleep(0.1)

        try:
            acct = web3.eth.account.privateKeyToAccount(_key)
            nonce = web3.eth.getTransactionCount(acct.address)
        except Exception as e:
            logger.error(f"{_i + 1} : failed to connect, skipping. Reason: {e}")
            continue

        try:
            native_coin_balance = web3.eth.getBalance(acct.address)
            native_coin_balance_human = web3.fromWei(native_coin_balance, 'ether')
        except Exception as e:
            logger.error(f"{_i + 1} : {acct.address} : failed to check balance, skipping. Reason: {e}")
            continue

        logger.info(f"{_i + 1} : {acct.address} : balance {native_coin_balance_human}")

        gas_limit = 21000
        gas_price_wei = web3.toWei(_gas_price_gwei, 'gwei')
        amount_to_send = native_coin_balance - (gas_price_wei * gas_limit)

        if amount_to_send <= 0:
            logger.info(f"{_i + 1} : {acct.address} : nothing to send, skipping")
            continue

        transaction = {
            'chainId': web3.eth.chainId,
            'nonce': nonce,
            'to': Web3.toChecksumAddress(_public_key_to),
            'value': amount_to_send,
            'gas': gas_limit,
            'gasPrice': gas_price_wei
        }

        transaction_sent = False
        for i in range(5):
            try:
                signed_tx = web3.eth.account.sign_transaction(transaction, private_key=acct.privateKey)
                tx_hash = web3.eth.sendRawTransaction(signed_tx.rawTransaction)
                logger.success(f'{_i + 1} : {acct.address} : transaction sent. Hash: {web3.toHex(tx_hash)}')
                transaction_sent = True
                break
            except:
                sleep(0.2)
                continue

        if not transaction_sent:
            logger.error(f"{_i + 1} : {acct.address} : failed to send transaction, skipping. Reason: {e}")


if __name__ == "__main__":
    # create web3 object and connect to provider
    blockchain_name = 'Polygon'
    provider = 'https://polygon-rpc.com'
    web3 = Web3(Web3.HTTPProvider(provider))
    web3.eth.account.enable_unaudited_hdwallet_features()

    if not web3.isConnected():
        logger.error('Failed to connect to node, quitting')
        exit()
    else:
        logger.success(f'Connected to node: {provider}')

    # collect user data
    logger.info('Please make sure you have updated private keys file in directory "data/02_private_keys.txt"')

    sleep(0.1)
    public_key_to = input(f'Enter main wallet address for {blockchain_name} network (to collect funds): ')
    if not web3.isAddress(public_key_to):
        logger.error('You have provided wrong address, quitting')
        exit()
    else:
        logger.success(f'All funds will be collected on the wallet {public_key_to}')

    sleep(0.1)
    try:
        gas_price_gwei = int(input('Enter gas price (gwei) for all transactions: '))
    except ValueError:
        logger.error('Wrong gas price, quitting')
        exit()

    sleep(0.1)
    confirm_action = input(f'Are you sure you want to continue? (y/n): ')
    if confirm_action.lower() == 'n':
        logger.info('User cancelled operation, quitting')
        exit()
    elif confirm_action.lower() == 'y':
        logger.info('User confirmed operation, starting')

        with open(f'data/02_private_keys.txt') as file:
            private_keys_from = [line.rstrip() for line in file]
        batch_collect_native_coins(private_keys_from, public_key_to, gas_price_gwei)
    else:
        logger.error('Wrong entry, quitting')
        exit()
