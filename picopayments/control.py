# coding: utf-8
# Copyright (c) 2016 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


import pycoin
import json
import requests
from btctxstore import BtcTxStore
from requests.auth import HTTPBasicAuth
from pycoin.tx.script.tools import disassemble
from . import util
from . import scripts


# FIXME make fees per kb and auto adjust to market price
DEFAULT_TXFEE = 10000  # FIXME dont hardcode tx fee
DEFAULT_DUSTSIZE = 5430  # FIXME dont hardcode dust size
DEFAULT_TESTNET = False
DEFAULT_COUNTERPARTY_RPC_MAINNET_URL = "http://public.coindaddy.io:4000/api/"
DEFAULT_COUNTERPARTY_RPC_TESTNET_URL = "http://public.coindaddy.io:14000/api/"
DEFAULT_COUNTERPARTY_RPC_USER = "rpc"
DEFAULT_COUNTERPARTY_RPC_PASSWORD = "1234"


class Control(object):

    def __init__(self, asset, user=DEFAULT_COUNTERPARTY_RPC_USER,
                 password=DEFAULT_COUNTERPARTY_RPC_PASSWORD,
                 api_url=None, testnet=DEFAULT_TESTNET, dryrun=False,
                 fee=DEFAULT_TXFEE, dust_size=DEFAULT_DUSTSIZE):
        """Initialize payment channel controler.

        Args:
            asset (str): Counterparty asset name.
            user (str): Counterparty API username.
            password (str): Counterparty API password.
            api_url (str): Counterparty API url.
            testnet (bool): True if running on testnet, otherwise mainnet.
            dryrun (bool): If True nothing will be published to the blockchain.
            fee (int): The transaction fee to use.
            dust_size (int): The default dust size for counterparty outputs.
        """

        if testnet:
            default_url = DEFAULT_COUNTERPARTY_RPC_TESTNET_URL
        else:
            default_url = DEFAULT_COUNTERPARTY_RPC_MAINNET_URL

        self.fee = fee
        self.dust_size = dust_size
        self.api_url = api_url or default_url
        self.testnet = testnet
        self.user = user
        self.password = password
        self.asset = asset
        self.netcode = "BTC" if not self.testnet else "XTN"
        self.btctxstore = BtcTxStore(testnet=self.testnet, dryrun=dryrun)

    def _rpc_call(self, payload):
        headers = {'content-type': 'application/json'}
        auth = HTTPBasicAuth(self.user, self.password)
        response = requests.post(self.api_url, data=json.dumps(payload),
                                 headers=headers, auth=auth)
        response_data = json.loads(response.text)
        if "result" not in response_data:
            raise Exception("Counterparty rpc call failed! {0}".format(
                repr(response.text)
            ))
        return response_data["result"]

    def _create_tx(self, source_address, dest_address,
                   quantity, extra_btc=0):
        assert(extra_btc >= 0)
        return self._rpc_call({
            "method": "create_send",
            "params": {
                "source": source_address,
                "destination": dest_address,
                "quantity": quantity,
                "asset": self.asset,
                "regular_dust_size": extra_btc or self.dust_size,
                "fee": self.fee
            },
            "jsonrpc": "2.0",
            "id": 0,
        })

    def get_balance(self, address):
        result = self._rpc_call({
            "method": "get_balances",
            "params": {
                "filters": [
                    {'field': 'address', 'op': '==', 'value': address},
                    {'field': 'asset', 'op': '==', 'value': self.asset},
                ]
            },
            "jsonrpc": "2.0",
            "id": 0,
        })
        asset_balance = result[0]["quantity"]
        utxos = self.btctxstore.retrieve_utxos([address])
        btc_balance = sum(map(lambda utxo: utxo["value"], utxos))
        return asset_balance, btc_balance

    def deposit(self, payer_wif, payee_pubkey, spend_secret_hash,
                expire_time, quantity):

        payer_pubkey = util.b2h(util.wif2sec(payer_wif))
        script = scripts.compile_deposit_script(payer_pubkey, payee_pubkey,
                                                spend_secret_hash, expire_time)
        dest_address = util.script2address(script, self.netcode)
        payer_address = util.wif2address(payer_wif)

        # provide extra btc for future closing channel fees
        # change tx or recover + commit tx + payout tx or revoke tx
        extra_btc = (self.fee + self.dust_size) * 3

        rawtx = self._create_tx(payer_address, dest_address,
                                quantity, extra_btc=extra_btc)
        rawtx = self.btctxstore.sign_tx(rawtx, [payer_wif])
        self.btctxstore.publish(rawtx)
        return rawtx, disassemble(script)

    def recover(self, payer_wif, deposit_rawtx, deposit_script_text):

        # get channel info
        script = scripts.compile(deposit_script_text)
        channel_address = util.script2address(script, self.netcode)
        asset_balance, btc_balance = self.get_balance(channel_address)
        expire_time = scripts.get_deposit_expire_time(deposit_script_text)

        # create recover tx
        payer_address = util.wif2address(payer_wif)
        rawtx = self._create_tx(channel_address, payer_address, asset_balance,
                                extra_btc=btc_balance-self.fee)

        # prep for script compliance and signing
        tx = pycoin.tx.Tx.from_hex(rawtx)
        tx.version = 2  # enable relative lock-time, see bip68 & bip112
        for txin in tx.txs_in:
            txin.sequence = expire_time  # relative lock-time
            utxo_tx = self.btctxstore.service.get_tx(txin.previous_hash)
            tx.unspents.append(utxo_tx.txs_out[txin.previous_index])

        # sign
        hash160_lookup = pycoin.tx.pay_to.build_hash160_lookup(
            [util.wif2secretexponent(payer_wif)]
        )
        p2sh_lookup = pycoin.tx.pay_to.build_p2sh_lookup([script])
        tx.sign(hash160_lookup, p2sh_lookup=p2sh_lookup,
                spend_type="recover", spend_secret=None)

        # assert(tx.bad_signature_count() == 0) # FIXME patch pycoin so it works
        rawtx = tx.as_hex()
        self.btctxstore.publish(rawtx)
        return rawtx
