from __future__ import annotations

from unittest import skipIf
from unittest.mock import call, Mock, patch

from django.test import TestCase
from django.test.utils import override_settings

from hc.lib.s3 import get_object, GetObjectError

try:
    from minio import InvalidResponseError, S3Error
    from urllib3.exceptions import InvalidHeader, ProtocolError

    have_minio = True
except ImportError:
    have_minio = False


@skipIf(not have_minio, "minio not installed")
@override_settings(S3_BUCKET="dummy-bucket")
class S3TestCase(TestCase):
    @patch("hc.lib.s3.statsd")
    @patch("hc.lib.s3._client")
    def test_get_object_handles_nosuchkey(self, client: Mock, statsd: Mock) -> None:
        e = S3Error("NoSuchKey", "b", "c", "d", "e", Mock())
        client.get_object.return_value.read = Mock(side_effect=e)
        self.assertIsNone(get_object("dummy-code", 1))
        # Should not increase the error counter for NoSuchKey responses
        self.assertEqual(statsd.incr.mock_calls, [call("hc.lib.s3.getObject")])

    @patch("hc.lib.s3.statsd")
    @patch("hc.lib.s3._client")
    def test_get_object_handles_s3error(self, client: Mock, statsd: Mock) -> None:
        e = S3Error("DummyError", "b", "c", "d", "e", Mock())
        client.get_object.return_value.read = Mock(side_effect=e)
        with self.assertRaises(GetObjectError):
            get_object("dummy-code", 1)
        client.get_object.assert_called_once()
        statsd.incr.assert_called_once()

    @patch("hc.lib.s3._client")
    def test_get_object_handles_urllib_exceptions(self, client: Mock) -> None:
        for e in [ProtocolError, InvalidHeader]:
            client.get_object.reset_mock()
            client.get_object.return_value.read = Mock(side_effect=e)
            with self.assertRaises(GetObjectError):
                get_object("dummy-code", 1)
            client.get_object.assert_called_once()

    @patch("hc.lib.s3._client")
    def test_get_object_handles_invalidresponseerror(self, client: Mock) -> None:
        e = InvalidResponseError(123, "text/plain", None)
        client.get_object.return_value.read = Mock(side_effect=e)
        with self.assertRaises(GetObjectError):
            get_object("dummy-code", 1)
        client.get_object.assert_called_once()

    @override_settings(S3_BUCKET=None)
    @patch("hc.lib.s3._client")
    def test_get_object_handles_no_s3_configuration(self, client: Mock) -> None:
        self.assertIsNone(get_object("dummy-code", 1))
        client.get_object.assert_not_called()
