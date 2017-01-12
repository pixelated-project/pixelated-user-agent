from twisted.trial import unittest

from pixelated.bitmask_libraries.certs import LeapCertificate
from pixelated.config import leap_config
from mock import MagicMock


class CertsTest(unittest.TestCase):

    def setUp(self):
        leap_config.leap_home = '/some/leap/home'

        self.provider = MagicMock(server_name=u'test.leap.net')

    def test_set_cert_and_fingerprint_sets_cert(self):
        LeapCertificate.set_cert_and_fingerprint('some cert', None)

        certs = LeapCertificate(self.provider)

        self.assertIsNone(certs.LEAP_FINGERPRINT)
        self.assertEqual('some cert', certs.provider_web_cert)

    def test_set_cert_and_fingerprint_sets_fingerprint(self):
        LeapCertificate.set_cert_and_fingerprint(None, 'fingerprint')

        certs = LeapCertificate(self.provider)

        self.assertEqual('fingerprint', LeapCertificate.LEAP_FINGERPRINT)
        self.assertFalse(certs.provider_web_cert)

    def test_set_cert_and_fingerprint_when_none_are_passed(self):
        LeapCertificate.set_cert_and_fingerprint(None, None)

        certs = LeapCertificate(self.provider)

        self.assertIsNone(certs.LEAP_FINGERPRINT)
        self.assertEqual(True, certs.provider_web_cert)
