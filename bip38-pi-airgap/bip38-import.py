#!/usr/bin/env python3

import os
import sys
import time
import argparse

# bip38 package dependency:
from pybip38 import bip38decrypt

# Electrum scriptin API dependency:
sys.path.insert(0, 'Electrum-3.0.4/packages')
import imp
imp.load_module('electrum', *imp.find_module('Electrum-3.0.4/lib'))
from electrum.storage import WalletStorage
from electrum.wallet import Imported_Wallet
from electrum.keystore import Imported_KeyStore


WALLET_PATH = "/run/user/1000/wallet"


class Bip38Import(object):
    def __init__(self):
        self.existing_wallet = os.path.exists(WALLET_PATH)
        self.storage = WalletStorage(WALLET_PATH)
        k = Imported_KeyStore({})
        self.storage.put('keystore', k.dump())
        self.wallet = Imported_Wallet(self.storage)

    def decrypt(self, key, phrase):
        print("decrypting...")
        start = time.time()
        decrypted = bip38decrypt(phrase, key)
        if not decrypted:
            sys.exit("could not decrypt key with passphrase (invalid?)")
        print("decrypted key in %.8f seconds" % (time.time() - start))
        return decrypted

    def import_to_wallet(self, key):
        self.wallet.import_private_key(key, None)

    def get_addrs(self):
        return self.storage.get('addresses', {}).keys()

    def print_report(self):
        if self.existing_wallet:
            print("Added key to existing wallet electrum wallet at %s" %
                  WALLET_PATH)
        else:
            print("Finished creating wallet at %s" % WALLET_PATH)

        print("\nAddresses in wallet:")
        for a in self.get_addrs():
            print("\t%s" % a)
        print("\nThis wallet can be used with the Electrum cli's '-w' "
              "parameter:")
        print("\n\t$ ./electrum -w %s\n" % WALLET_PATH)

    def run(self, encrypted_key, passphrase):
        key = self.decrypt(encrypted_key, passphrase)
        self.import_to_wallet(key)
        self.print_report()


if __name__ == "__main__":
    description = ("Decrypts a bip38 key with a provided passphrase and "
                   "imports to the result into an Electrum wallet on tmpfs")
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('encrypted_key', type=str, help="bip38 encrypted key")
    parser.add_argument('passphrase', type=str,
                        help="decryption passphrase - wrap in quotes if "
                             "passphrase contains spaces")

    args = parser.parse_args()
    Bip38Import().run(args.encrypted_key, args.passphrase)
