import unittest
import picopayments
import json


ASSET = "A14456548018133352000"
USER = "rpc"
PASSWORD = "1234"
API_URL = "http://127.0.0.1:14000/api/"
TESTNET = True
DRYRUN = True


PAYER_BEFORE = {
  "payer_wif": "cSthi1Ye1sbHepC5s8rNukQBAKLCyct6hLg6MCH9Ybk1cKfGcPb2",
  "deposit_script_hex": (
    "63522102a73443bc32f5fec6a551f71af75311b0876686156d16d367562d3d29987792d5"
    "2103c7b09d53bdb0ef9cfea06c1e6f2192e6a91cdeac209402bc36c1c368021a861152ae"
    "6763a9144cc776751eb4d41f23feaf94697cb7ec2fe597a4882102a73443bc32f5fec6a5"
    "51f71af75311b0876686156d16d367562d3d29987792d5ac6703ffff00b2752102a73443"
    "bc32f5fec6a551f71af75311b0876686156d16d367562d3d29987792d5ac6868"
  ),
  "commits_active": [],
  "deposit_rawtx": (
    "0100000001d85205661d29fec2e5ede0dbb8eaa0e55655c7b14b1aeac9b0e72dae01596f"
    "63000000006b483045022100e631d8b259bd09ba8956a96e6e471e9938ddad1fa831bb12"
    "ffa690f2d0d2640002202cf3bcc376225e1861443608cad549d63a76b636225630946942"
    "205dfd8f4672012102a73443bc32f5fec6a551f71af75311b0876686156d16d367562d3d"
    "29987792d5ffffffff03d2b400000000000017a9145c6f176aa8bab82688c8b07562595a"
    "622d7b889a8700000000000000001e6a1c6c4d9b5afac6415f4eff0ec371c5d8155b5821"
    "76fa9e12aed0cc84645e310200000000001976a914a5efd9bcdc152be40dc2390607a806"
    "b32cf2902c88ac00000000"
  ),
  "timeout_rawtx": None,
  "payee_wif": None,
  "commits_revoked": [],
  "change_rawtx": None,
  "spend_secret": None,
  "commits_pending": []
}

PAYEE_BEFORE = {
  "payer_wif": None,
  "deposit_script_hex": (
    "63522102a73443bc32f5fec6a551f71af75311b0876686156d16d367562d3d29987792d5"
    "2103c7b09d53bdb0ef9cfea06c1e6f2192e6a91cdeac209402bc36c1c368021a861152ae"
    "6763a9144cc776751eb4d41f23feaf94697cb7ec2fe597a4882102a73443bc32f5fec6a5"
    "51f71af75311b0876686156d16d367562d3d29987792d5ac6703ffff00b2752102a73443"
    "bc32f5fec6a551f71af75311b0876686156d16d367562d3d29987792d5ac6868"
  ),
  "commits_active": [],
  "deposit_rawtx": (
    "0100000001d85205661d29fec2e5ede0dbb8eaa0e55655c7b14b1aeac9b0e72dae01596f"
    "63000000006b483045022100e631d8b259bd09ba8956a96e6e471e9938ddad1fa831bb12"
    "ffa690f2d0d2640002202cf3bcc376225e1861443608cad549d63a76b636225630946942"
    "205dfd8f4672012102a73443bc32f5fec6a551f71af75311b0876686156d16d367562d3d"
    "29987792d5ffffffff03d2b400000000000017a9145c6f176aa8bab82688c8b07562595a"
    "622d7b889a8700000000000000001e6a1c6c4d9b5afac6415f4eff0ec371c5d8155b5821"
    "76fa9e12aed0cc84645e310200000000001976a914a5efd9bcdc152be40dc2390607a806"
    "b32cf2902c88ac00000000"
  ),
  "timeout_rawtx": None,
  "payee_wif": "cVmyYsHfeJWmCFy7N6DUeC4aXMS8vRR57aW7eGmpFVLfSHWjZ4jc",
  "commits_revoked": [],
  "change_rawtx": None,
  "spend_secret": (
    "d688fc3400f9feb6f8c409b804c75deaa5fa1635bf252d5d5de262a5c63cb5e5"
  ),
  "commits_pending": []
}

PAYER_AFTER = {
  "change_rawtx": None,
  "timeout_rawtx": None,
  "commits_pending": [],
  "commits_active": [
    [
      (
        "01000000017231934b8873769b325c090a99dd7e5a3d8708bf13e94f677228b90787"
        "631f0700000000fd4501483045022100ea61f098fdaf5b26f7b37b578ac0dcde84ae"
        "c1169aa45f84a876ff97075e29c602205ec1abeb2be0efb3891e4b1cc88cc687ab8d"
        "d3c0cf7f04202b6ff1be2fe523fd01483045022100ffffffffffffffffffffffffff"
        "fffffebaaedce6af48a03bbfd25e8cd036414002207fffffffffffffffffffffffff"
        "ffffff5d576e7357a4501ddfe92f46681b20a001514cb063522102a73443bc32f5fe"
        "c6a551f71af75311b0876686156d16d367562d3d29987792d52103c7b09d53bdb0ef"
        "9cfea06c1e6f2192e6a91cdeac209402bc36c1c368021a861152ae6763a9144cc776"
        "751eb4d41f23feaf94697cb7ec2fe597a4882102a73443bc32f5fec6a551f71af753"
        "11b0876686156d16d367562d3d29987792d5ac6703ffff00b2752102a73443bc32f5"
        "fec6a551f71af75311b0876686156d16d367562d3d29987792d5ac6868ffffffff03"
        "463c00000000000017a914b57a70f9301cfd13603fc36b3162b57340b3958b870000"
        "0000000000001e6a1c5144cf3299cdb4115af7e5b1a21ecac52fedaf164910f4fe4b"
        "eb0a877c5100000000000017a9145c6f176aa8bab82688c8b07562595a622d7b889a"
        "8700000000"
      ),
      (
        "6355b275a9144cc776751eb4d41f23feaf94697cb7ec2fe597a4882103c7b09d53bd"
        "b0ef9cfea06c1e6f2192e6a91cdeac209402bc36c1c368021a8611ac67a914bcc82b"
        "07e3c1317a52d7adbff1ef869d4e46ac35882102a73443bc32f5fec6a551f71af753"
        "11b0876686156d16d367562d3d29987792d5ac68"
      ),
      None
    ]
  ],
  "deposit_script_hex": (
    "63522102a73443bc32f5fec6a551f71af75311b0876686156d16d367562d3d29987792d5"
    "2103c7b09d53bdb0ef9cfea06c1e6f2192e6a91cdeac209402bc36c1c368021a861152ae"
    "6763a9144cc776751eb4d41f23feaf94697cb7ec2fe597a4882102a73443bc32f5fec6a5"
    "51f71af75311b0876686156d16d367562d3d29987792d5ac6703ffff00b2752102a73443"
    "bc32f5fec6a551f71af75311b0876686156d16d367562d3d29987792d5ac6868"
  ),
  "commits_revoked": [],
  "spend_secret": None,
  "payer_wif": "cSthi1Ye1sbHepC5s8rNukQBAKLCyct6hLg6MCH9Ybk1cKfGcPb2",
  "payee_wif": None,
  "deposit_rawtx": (
    "0100000001d85205661d29fec2e5ede0dbb8eaa0e55655c7b14b1aeac9b0e72dae01596f"
    "63000000006b483045022100e631d8b259bd09ba8956a96e6e471e9938ddad1fa831bb12"
    "ffa690f2d0d2640002202cf3bcc376225e1861443608cad549d63a76b636225630946942"
    "205dfd8f4672012102a73443bc32f5fec6a551f71af75311b0876686156d16d367562d3d"
    "29987792d5ffffffff03d2b400000000000017a9145c6f176aa8bab82688c8b07562595a"
    "622d7b889a8700000000000000001e6a1c6c4d9b5afac6415f4eff0ec371c5d8155b5821"
    "76fa9e12aed0cc84645e310200000000001976a914a5efd9bcdc152be40dc2390607a806"
    "b32cf2902c88ac00000000"
  )
}


REVOKE_SECRET_HASH = "bcc82b07e3c1317a52d7adbff1ef869d4e46ac35"


class TestCommit(unittest.TestCase):

    def setUp(self):
        self.payer = picopayments.channel.Payer(
            ASSET, api_url=API_URL, testnet=TESTNET, dryrun=DRYRUN
        )
        self.payee = picopayments.channel.Payee(
            ASSET, api_url=API_URL, testnet=TESTNET, dryrun=DRYRUN
        )
        self.maxDiff = None

    def tearDown(self):
        self.payer.stop()
        self.payee.stop()

    def test_request_commit(self):
        self.payee.load(PAYEE_BEFORE)
        amount, revoke_secret_hash = self.payee.request_commit(1)
        hash_bin = picopayments.util.h2b(revoke_secret_hash)
        self.assertEqual(len(hash_bin), 20)
        self.assertEqual(amount, 1)

    def test_commit(self):
        self.payer.load(PAYER_BEFORE)
        commit_rawtx, commit_script = self.payer.create_commit(
            1, REVOKE_SECRET_HASH, 5
        )
        # print(json.dumps(self.payer.save(), indent=2))
        self.assertEqual(self.payer.save(), PAYER_AFTER)


if __name__ == "__main__":
    unittest.main()
