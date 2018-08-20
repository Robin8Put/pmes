import unittest

from ecdsa import BadSignatureError

from bip32keys.bip32keys import Bip32Keys
from qtum_utils.qtum import Qtum


class TestUM(unittest.TestCase):

    def setUp(self):
        pass

    def test_valid_signature(self):
        message = 'aaa'
        public_key = '040646d16f7bb84333446266a7237eed33866b3478caad3da040e0ca63e7b3f1c01f8c8ee50d8a57e2b9c35b48efdce495f0075560790bb8a87749b92ad8600239'
        signature = '304402201c1ee66e98a67e4da411eacc2388b4e33cfd6da37a11340119e2cb2c76064aa0022049c00a810b896445f7508d0499845eaf3b904661cd427e0a19ab54a50e9012ad'
        self.assertTrue(Qtum.verify_message(message, signature, public_key))

    def test_der(self):
        message = 'aaa'
        signature = '3045022016cdbe36a5653336ff74a28cde1092c76886306b0fb9a86bbcd3b8ec15679a5602210091393fb0d4c43a461ff522ebfd8f22ef8ad412f51f29602ba7ca339c37880772'
        public_key = '0406838688de86e85a2a10f1c0986eeef3dadd7e8cf7bd8491dc9557132f75b655c9eb00d5fed251c7def677e1b67c49f5d4cff690282fcbd9fe97be29f4fef843'

        self.assertTrue(Qtum.verify_message(message, signature, public_key))

    def test_valid_signature2(self):
        message = 'aaa'
        public_key = '0646d16f7bb84333446266a7237eed33866b3478caad3da040e0ca63e7b3f1c01f8c8ee50d8a57e2b9c35b48efdce495f0075560790bb8a87749b92ad8600239'
        signature = '304402201c1ee66e98a67e4da411eacc2388b4e33cfd6da37a11340119e2cb2c76064aa0022049c00a810b896445f7508d0499845eaf3b904661cd427e0a19ab54a50e9012ad'
        self.assertTrue(Qtum.verify_message(message, signature, public_key))

    def test_valid_signature3(self):
        message = 'aaa'
        public_key = '030646d16f7bb84333446266a7237eed33866b3478caad3da040e0ca63e7b3f1c0'
        signature = '304402201c1ee66e98a67e4da411eacc2388b4e33cfd6da37a11340119e2cb2c76064aa0022049c00a810b896445f7508d0499845eaf3b904661cd427e0a19ab54a50e9012ad'
        self.assertTrue(Qtum.verify_message(message, signature, public_key))

    def test_valid_signature4(self):
        message = 'Simple message'
        public_key = '995d52cbc1c5b96eebeeae16383dd7c41dd409fe9eef6e13a7ca2807911dd45fbd18005bfa2272e91b9f0ebd702226db3e5f7f17531087f3ac54c51bae100d6d'
        signature = '1d7cb366aa960c837bdaf7423054f8a8eb9f1dfd20ae277482f51231b1865eb24fd2bd336f6687a0e8854c600dce2f18606dfd5429f8551077bb4f6ab53b832a'
        self.assertTrue(Qtum.verify_message(message, signature, public_key))

    def test_invalid_signature_message(self):
        message = 'CORRUPTED'
        public_key = '040646d16f7bb84333446266a7237eed33866b3478caad3da040e0ca63e7b3f1c01f8c8ee50d8a57e2b9c35b48efdce495f0075560790bb8a87749b92ad8600239'
        signature = '304402201c1ee66e98a67e4da411eacc2388b4e33cfd6da37a11340119e2cb2c76064aa0022049c00a810b896445f7508d0499845eaf3b904661cd427e0a19ab54a50e9012ad'
        with self.assertRaises(BadSignatureError):
            Qtum.verify_message(message, signature, public_key)


    def test_invalid_signature(self):
        message = 'aaa'
        public_key = '040646d16f7bb84333446266a7237eed33866b3478caad3da040e0ca63e7b3f1c01f8c8ee50d8a57e2b9c35b48efdce495f0075560790bb8a87749b92ad8600239'
        signature = '304402201c1ee66e98a67e4da4'+'CORRUPTED'+'8b4e33cfd6da37a11340119e2cb2c76064aa0022049c00a810b896445f7508d0499845eaf3b904661cd427e0a19ab54a50e9012ad'
        with self.assertRaises(Exception):
            Qtum.verify_message(message, signature, public_key)

    def test_sig_formats(self):
        message = 'aaa'
        public_key = '040646d16f7bb84333446266a7237eed33866b3478caad3da040e0ca63e7b3f1c01f8c8ee50d8a57e2b9c35b48efdce495f0075560790bb8a87749b92ad8600239'
        signature = '1c1ee66e98a67e4da411eacc2388b4e33cfd6da37a11340119e2cb2c76064aa049c00a810b896445f7508d0499845eaf3b904661cd427e0a19ab54a50e9012ad'
        self.assertTrue(Qtum.verify_message(message, signature, public_key))

    def test_pubkey_formats(self):
        message = 'aaa'
        public_key = '0646d16f7bb84333446266a7237eed33866b3478caad3da040e0ca63e7b3f1c01f8c8ee50d8a57e2b9c35b48efdce495f0075560790bb8a87749b92ad8600239'
        signature = '304402201c1ee66e98a67e4da411eacc2388b4e33cfd6da37a11340119e2cb2c76064aa0022049c00a810b896445f7508d0499845eaf3b904661cd427e0a19ab54a50e9012ad'
        self.assertTrue(Qtum.verify_message(message, signature, public_key))

    def test_valid_verify(self):
        message = 'aaa'
        public_key = '040646d16f7bb84333446266a7237eed33866b3478caad3da040e0ca63e7b3f1c01f8c8ee50d8a57e2b9c35b48efdce495f0075560790bb8a87749b92ad8600239'
        signature = '304402201c1ee66e98a67e4da411eacc2388b4e33cfd6da37a11340119e2cb2c76064aa0022049c00a810b896445f7508d0499845eaf3b904661cd427e0a19ab54a50e9012ad'
        self.assertTrue(Qtum.verify_message(message, signature, public_key))

    def test_sing_verify(self):
        q = Qtum('1232131234324324324234321231')
        public_key = q.get_uncompressed_public_key()
        private_key = q.get_private_key()
        message = 'hello'

        signature = Qtum.sign_message(message, private_key)
        self.assertTrue(Qtum.verify_message(message, signature, public_key))

    def test_sing_verify_invalid(self):
        q = Qtum('1232131234324324324234321231')
        public_key = q.get_uncompressed_public_key()
        private_key = q.get_private_key()
        message = 'hello'

        signature = Qtum.sign_message(message, private_key)
        message = 'corrupted'
        with self.assertRaises(BadSignatureError):
            Qtum.verify_message(message, signature, public_key)

    def test_addresses(self):
        entropy = "3123213213213123312c3kjifj3"
        private_key = "7a6be1df9cc5d88edce5443ef0fce246123295dd82afae9a57986543272157cc"
        wif = "L1KgWtY57mSggocxDVSDRGvLVCRYuQfj8ur7cHvuv6UkgJmXweti"
        public_key = "021ad7138370ef5e93fb243aff3373e2b92383818dfc20022841b655e0cd6c618c"
        uncompressed_public_key = "041ad7138370ef5e93fb243aff3373e2b92383818dfc20022841b655e0cd6c618cd578261c78e1adfe205c3ade8b81e1722d6058be9155eee55468fbb04b62040e"
        qtum_address = "QLonXSbmVhECBV3fqN3L7H9LJn8jUS3m9k"
        q = Qtum("3123213213213123312c3kjifj3")
        self.assertEqual(q.get_private_key(), private_key)
        self.assertEqual(q.get_wif(), wif)
        self.assertEqual(q.get_public_key(), public_key)
        self.assertEqual(q.get_uncompressed_public_key(), uncompressed_public_key)
        self.assertEqual(q.get_qtum_address(), qtum_address)
        self.assertEqual(q.private_key_to_wif(private_key), wif)
        self.assertEqual(q.wif_to_private_key(wif), private_key)

    def test_valid_address_to_hex(self):
        address = 'qHmBaB5dWsxWtMh3MNh6B427L47DWavgJD'
        hex_address = '023b5269b46be13e6ac5c3f122ed263e9fa78114'

        self.assertEqual(Qtum.address_to_hex(address), hex_address)
        self.assertEqual(Qtum.hex_to_qtum_address(hex_address, mainnet=False), address)

    def test_init_from_private_key(self):
        private_key = '5907a2e9e917fbb8ab93a4d309184d1fe2cd55030f1e616620ef794e6a5b0df5'
        public_key = '0356fd892d76117935853466db2bf0ac5d0eb9138bfa78c3b25d68f1b64f9a5106'
        uncompressed_public_key = '0456fd892d76117935853466db2bf0ac5d0eb9138bfa78c3b25d68f1b64f9a51068a6b2f8b4c80c32f6e898d06b765c3a95a2eb372dcbbf2d086bce89b4f256dcb'
        wif = 'cQZmGLJZAMpNY36YFKbH6gygW2eBDULpokkeTYdPg41fo4BqycEc'
        qtum_address = 'qgNj57RLaEsLQUpD5JZxZ6tREonrfp5z2i'
        hex_address = 'fa46f119b82df651edb8a7bff2172dccc7cfac9a'

        q = Qtum({'private_key': private_key}, mainnet=False)

        self.assertEqual(q.get_public_key(), public_key)
        self.assertEqual(q.get_uncompressed_public_key(), uncompressed_public_key)
        self.assertEqual(q.get_qtum_address(),qtum_address)
        self.assertEqual(q.get_hex_address(), hex_address)
        self.assertEqual(q.get_wif(), wif)
        self.assertEqual(q.get_private_key(), private_key)

    def test_init_from_wif(self):
        private_key = '5907a2e9e917fbb8ab93a4d309184d1fe2cd55030f1e616620ef794e6a5b0df5'
        public_key = '0356fd892d76117935853466db2bf0ac5d0eb9138bfa78c3b25d68f1b64f9a5106'
        uncompressed_public_key = '0456fd892d76117935853466db2bf0ac5d0eb9138bfa78c3b25d68f1b64f9a51068a6b2f8b4c80c32f6e898d06b765c3a95a2eb372dcbbf2d086bce89b4f256dcb'
        wif = 'cQZmGLJZAMpNY36YFKbH6gygW2eBDULpokkeTYdPg41fo4BqycEc'
        qtum_address = 'qgNj57RLaEsLQUpD5JZxZ6tREonrfp5z2i'
        hex_address = 'fa46f119b82df651edb8a7bff2172dccc7cfac9a'

        q = Qtum({'wif': wif}, mainnet=False)

        self.assertEqual(q.get_public_key(), public_key)
        self.assertEqual(q.get_uncompressed_public_key(), uncompressed_public_key)
        self.assertEqual(q.get_qtum_address(),qtum_address)
        self.assertEqual(q.get_hex_address(), hex_address)
        self.assertEqual(q.get_wif(), wif)
        self.assertEqual(q.get_private_key(), private_key)

    def test_valid_address(self):
        wif = 'cQZmGLJZAMpNY36YFKbH6gygW2eBDULpokkeTYdPg41fo4BqycEc'
        q = Qtum({'wif': wif}, mainnet=False)

        self.assertTrue(Qtum.verify_address(q.get_qtum_address()))

    def test_valid_predefined_address(self):
        self.assertTrue(Qtum.verify_address('qZiXFyqVf9vxf6iu47AdfU1FVaHyULUP7e'))

    def test_invalid_address(self):
        with self.assertRaises(Exception):
            self.assertFalse(Qtum.verify_address('qAiXFyqVf9vxf6iu47AdfU1FVaHyULUP7e'))

    def test_valid_qtum_address(self):
        self.assertTrue(Qtum.verify_qtum_address('qZiXFyqVf9vxf6iu47AdfU1FVaHyULUP7e', mainnet=False))

    # valid checksum but invalid length
    def test_tricky_qtum_address(self):
        with self.assertRaises(Exception):
            self.assertFalse(Qtum.verify_address('6JnZeT4rMWNrapEKqCLjNGFJRfKyALEm5'))

    def test_shared_key(self):
        keys = Bip32Keys({'entropy': '3123213213213123312c3kjifj3'})
        keys2 = Bip32Keys({'entropy': 'fdjsofjioej9fsdfjdskfdsjkhfdsj'})
        self.assertEqual(keys2.get_shared_key(keys.get_public_key()),
                         keys.get_shared_key(keys2.get_public_key()),
                         )


if __name__ == '__main__':
    unittest.main()
