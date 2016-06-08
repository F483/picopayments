import json
import unittest
import picopayments


ASSET = "A14456548018133352000"
USER = "rpc"
PASSWORD = "1234"
API_URL = "http://127.0.0.1:14000/api/"
TESTNET = True
DRYRUN = True


FIXTURES = json.load(open("tests/fixtures.json"))
SPEND_SECRET = FIXTURES["test_change"]["payee_state"]["spend_secret"]
PAYER_STATE = FIXTURES["test_change"]["payer_state"]
PAYER_RECOVERED_CHANGE = FIXTURES["test_change"]["payer_recovered_change"]


class TestRecoverChange(unittest.TestCase):

    def setUp(self):
        self.payer = picopayments.Channel(
            ASSET, api_url=API_URL, testnet=TESTNET, dryrun=DRYRUN
        )
        self.maxDiff = None

    def test_recover_change(self):
        result = self.payer.payer_update(PAYER_STATE)  # recover change
        self.assertEqual(result["channel_state"], PAYER_RECOVERED_CHANGE)


if __name__ == "__main__":
    unittest.main()
