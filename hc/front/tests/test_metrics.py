from __future__ import annotations

from django.test.utils import override_settings
from django.utils.timezone import now
from hc.api.models import Check
from hc.test import BaseTestCase


class MetricsTestCase(BaseTestCase):
    def setUp(self) -> None:
        super().setUp()
        self.project.api_key_readonly = "R" * 32
        self.project.save()

        self.check = Check(project=self.project, name="Alice Was Here")
        self.check.tags = "foo"
        self.check.save()

        key = "R" * 32
        self.url = f"/projects/{self.project.code}/metrics/{key}"
        self.auth_url = f"/projects/{self.project.code}/metrics/"

    def test_it_works(self) -> None:
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)

        alice_spec = '{name="Alice Was Here", tags="foo", unique_key="%s"}'
        alice_spec = alice_spec % self.check.unique_key

        self.assertContains(r, f"hc_check_up{alice_spec} 1")
        self.assertContains(r, f"hc_check_started{alice_spec} 0")
        self.assertContains(r, 'hc_tag_up{tag="foo"} 1')
        self.assertContains(r, "hc_checks_total 1")

    def test_it_accepts_hashed_ro_key(self) -> None:
        key = self.project.set_api_key_readonly()
        self.project.save()
        r = self.client.get(f"/projects/{self.project.code}/metrics/{key}")
        self.assertEqual(r.status_code, 200)

    def test_it_rejects_hashed_rw_key(self) -> None:
        key = self.project.set_api_key()
        self.project.save()
        r = self.client.get(f"/projects/{self.project.code}/metrics/{key}")
        self.assertEqual(r.status_code, 403)

    def test_authenticated_request_requires_bearer_token(self) -> None:
        r = self.client.get(self.auth_url)
        self.assertEqual(r.status_code, 401)

    def test_authenticated_request_accepts_bearer_token(self) -> None:
        headers = {"Authorization": "Bearer " + "R" * 32}
        r = self.client.get(self.auth_url, headers=headers)
        self.assertEqual(r.status_code, 200)

    def test_it_escapes_newline(self) -> None:
        self.check.name = "Line 1\nLine2"
        self.check.tags = "A\\C"
        self.check.save()

        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "Line 1\\nLine2")
        self.assertContains(r, "A\\\\C")

    def test_it_checks_api_key_length(self) -> None:
        r = self.client.get(self.url + "R")
        self.assertEqual(r.status_code, 400)

    def test_it_checks_api_key(self) -> None:
        rw_key = "X" * 32
        url = f"/projects/{self.project.code}/checks/metrics/{rw_key}"
        r = self.client.get(url)
        self.assertEqual(r.status_code, 403)

    @override_settings(PROMETHEUS_ENABLED=False)
    def test_it_requires_prometheus_enabled(self) -> None:
        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 404)

    def test_it_reports_hc_check_started(self) -> None:
        self.check.last_start = now()
        self.check.save()

        r = self.client.get(self.url)
        self.assertEqual(r.status_code, 200)

        alice_spec = '{name="Alice Was Here", tags="foo", unique_key="%s"}'
        alice_spec = alice_spec % self.check.unique_key

        self.assertContains(r, f"hc_check_up{alice_spec} 1")
        self.assertContains(r, f"hc_check_started{alice_spec} 1")
