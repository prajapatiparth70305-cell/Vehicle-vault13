from django.test import TestCase, override_settings
from django.contrib.auth import get_user_model

from .models import EMIHistory


@override_settings(EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend')
class SuccessPageTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='tester',
            email='tester@example.com',
            password='secret123',
        )

    def test_success_page_accepts_missing_total_emi(self):
        self.client.force_login(self.user)

        response = self.client.get('/core/success/', {
            'payment_id': 'pay_test_123',
            'amount': '1000',
        })

        self.assertEqual(response.status_code, 200)
        self.assertTrue(EMIHistory.objects.filter(user=self.user, payment_id='pay_test_123').exists())

        emi = EMIHistory.objects.get(user=self.user, payment_id='pay_test_123')
        self.assertEqual(emi.total_emi, 1)
