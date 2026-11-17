import unittest

from payment_factory import (
    BankTransferProcessor,
    CreditCardProcessor,
    PaymentFactory,
    PaymentProcessor,
    PayPalProcessor,
)


class TestPaymentFactory(unittest.TestCase):
    def setUp(self):
        self.factory = PaymentFactory()

    def test_factory_returns_correct_types(self):
        self.assertIsInstance(self.factory.get_processor("credit_card"), CreditCardProcessor)
        self.assertIsInstance(self.factory.get_processor("bank_transfer"), BankTransferProcessor)
        self.assertIsInstance(self.factory.get_processor("paypal"), PayPalProcessor)

    def test_unknown_type_raises(self):
        with self.assertRaises(ValueError):
            self.factory.get_processor("bitcoin")

    def test_credit_card_fee(self):
        result = self.factory.get_processor("credit_card").process(
            100.0, {"card_number": "1234567890123456", "cvv": "123"}
        )
        self.assertTrue(result["success"])
        self.assertAlmostEqual(result["fee"], 2.9)
        self.assertAlmostEqual(result["amount"], 102.9)

    def test_credit_card_invalid(self):
        result = self.factory.get_processor("credit_card").process(
            100.0, {"card_number": "123", "cvv": "123"}
        )
        self.assertFalse(result["success"])

    def test_bank_transfer_fee(self):
        result = self.factory.get_processor("bank_transfer").process(
            100.0, {"iban": "FR7630006000011234567890189"}
        )
        self.assertAlmostEqual(result["fee"], 1.5)

    def test_paypal_fee(self):
        result = self.factory.get_processor("paypal").process(100.0, {"email": "a@b.com"})
        self.assertAlmostEqual(result["fee"], 3.7)

    def test_register_new_method(self):
        class ApplePayProcessor(PaymentProcessor):
            def validate(self, details):
                return True

            def process(self, amount, details):
                return {"success": True, "method": "apple_pay", "amount": amount, "fee": 0.0}

        self.factory.register("apple_pay", ApplePayProcessor)
        result = self.factory.get_processor("apple_pay").process(50.0, {})
        self.assertEqual(result["method"], "apple_pay")


if __name__ == "__main__":
    unittest.main()
