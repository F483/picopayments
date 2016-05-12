# coding: utf-8
# Copyright (c) 2016 Fabian Barkhau <fabian.barkhau@gmail.com>
# License: MIT (see LICENSE file)


from picopayments import util
from picopayments import control
from picopayments.channel.base import Base
from threading import RLock


class Payer(Base):

    def __init__(self, asset, user=control.DEFAULT_COUNTERPARTY_RPC_USER,
                 password=control.DEFAULT_COUNTERPARTY_RPC_PASSWORD,
                 api_url=None, testnet=control.DEFAULT_TESTNET, dryrun=False,
                 auto_update_interval=0):

        # TODO validate input

        self.control = control.Control(
            asset, user=user, password=password, api_url=api_url,
            testnet=testnet, dryrun=dryrun, fee=control.DEFAULT_TXFEE,
            dust_size=control.DEFAULT_DUSTSIZE
        )

        self.mutex = RLock()
        if auto_update_interval > 0:
            self.interval = auto_update_interval
            self.start()

    def can_change_recover(self):
        with self.mutex:
            return (
                # we know the payer wif
                self.payer_wif is not None and

                # deposit was made
                self.deposit_rawtx is not None and
                self.deposit_script_hex is not None and

                # we know the spend secret
                self.spend_secret is not None
            )

    def can_timeout_recover(self):
        with self.mutex:
            return (
                # we know the payer wif
                self.payer_wif is not None and

                # deposit was made
                self.deposit_rawtx is not None and
                self.deposit_script_hex is not None and

                # deposit expired
                self.is_deposit_expired() and

                # not already recovering
                not self.is_closing()
            )

    def update(self):
        with self.mutex:

            # If deposit expired recover the coins!
            if self.can_timeout_recover():
                self.timeout_recover()

            # If spend secret exposed recover the coins!
            if self.can_change_recover():
                self.change_recover()

    def deposit(self, payer_wif, payee_pubkey, spend_secret_hash,
                expire_time, quantity):
        """Create deposit for given quantity.

        Args:
            payer_wif: TODO doc string
            payee_pubkey: TODO doc string
            spend_secret_hash: TODO doc string
            expire_time: TODO doc string
            quantity: In satoshis

        Returns:
            Transaction ID for the created deposit.

        Raises:
            ValueError if invalid quantity
            IllegalStateError if not called directly after initialization.
            InsufficientFunds if not enough funds to cover requested quantity.
        """

        # TODO validate input
        # TODO validate pubkeys on blockchain (required by counterparty)

        with self.mutex:
            self.clear()
            self.payer_wif = payer_wif
            self.payer_pubkey = util.b2h(util.wif2sec(self.payer_wif))
            self.payee_pubkey = payee_pubkey
            rawtx, script, address = self.control.deposit(
                self.payer_wif, self.payee_pubkey,
                spend_secret_hash, expire_time, quantity
            )
            self.deposit_rawtx = rawtx
            self.deposit_script_hex = util.b2h(script)
            info = {
                "asset": self.control.asset,
                "quantity": quantity,
                "rawtx": rawtx,
                "txid": util.gettxid(rawtx),
                "script": util.b2h(script),
                "address": address
            }
            return info

    def timeout_recover(self):
        with self.mutex:
            script = util.h2b(self.deposit_script_hex)
            self.timeout_rawtx = self.control.timeout_recover(
                self.payer_wif, self.deposit_rawtx, script
            )

    def change_recover(self):
        with self.mutex:
            script = util.h2b(self.deposit_script_hex)
            self.change_rawtx = self.control.change_recover(
                self.payer_wif, self.deposit_rawtx,
                script, self.spend_secret
            )