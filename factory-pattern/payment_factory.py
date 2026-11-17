from abc import ABC, abstractmethod


class PaymentProcessor(ABC):
    """Blueprint: every payment processor must implement these methods."""

    @abstractmethod
    def validate(self, details: dict) -> bool:
        """Return True if the payment details are valid."""

    @abstractmethod
    def process(self, amount: float, details: dict) -> dict:
        """Process the payment and return a result dict."""


class CreditCardProcessor(PaymentProcessor):
    FEE_RATE = 0.029  # 2.9%

    def validate(self, details: dict) -> bool:
        card_number = details.get("card_number")
        cvv = details.get("cvv")
        return bool(card_number) and len(card_number) == 16 and bool(cvv) and len(cvv) == 3

    def process(self, amount: float, details: dict) -> dict:
        if not self.validate(details):
            card_number = details.get("card_number")
            if not card_number or len(card_number) != 16:
                return {"success": False, "error": "Invalid card number"}
            return {"success": False, "error": "Invalid CVV"}

        fee = amount * self.FEE_RATE
        return {
            "success": True,
            "method": "credit_card",
            "amount": amount + fee,
            "fee": fee,
        }


class BankTransferProcessor(PaymentProcessor):
    FLAT_FEE = 1.50

    def validate(self, details: dict) -> bool:
        iban = details.get("iban")
        return bool(iban) and len(iban) >= 15

    def process(self, amount: float, details: dict) -> dict:
        if not self.validate(details):
            return {"success": False, "error": "Invalid IBAN"}

        fee = self.FLAT_FEE
        return {
            "success": True,
            "method": "bank_transfer",
            "amount": amount + fee,
            "fee": fee,
        }


class PayPalProcessor(PaymentProcessor):
    FEE_RATE = 0.034  # 3.4%
    FIXED_FEE = 0.30

    def validate(self, details: dict) -> bool:
        email = details.get("email")
        return bool(email) and "@" in email

    def process(self, amount: float, details: dict) -> dict:
        if not self.validate(details):
            return {"success": False, "error": "Invalid PayPal email"}

        fee = amount * self.FEE_RATE + self.FIXED_FEE
        return {
            "success": True,
            "method": "paypal",
            "amount": amount + fee,
            "fee": fee,
        }


class PaymentFactory:
    """Middleman: turns a string into the right processor instance."""

    def __init__(self):
        self._processors = {
            "credit_card": CreditCardProcessor,
            "bank_transfer": BankTransferProcessor,
            "paypal": PayPalProcessor,
        }

    def register(self, payment_type: str, processor_cls) -> None:
        """Add a new payment method without modifying existing code."""
        self._processors[payment_type] = processor_cls

    def get_processor(self, payment_type: str) -> PaymentProcessor:
        processor_cls = self._processors.get(payment_type)
        if processor_cls is None:
            raise ValueError(f"Unknown payment type: {payment_type}")
        return processor_cls()


if __name__ == "__main__":
    factory = PaymentFactory()

    processor = factory.get_processor("credit_card")
    print(processor.process(100.0, {"card_number": "1234567890123456", "expiry": "12/25", "cvv": "123"}))

    processor = factory.get_processor("bank_transfer")
    print(processor.process(100.0, {"iban": "FR7630006000011234567890189", "bic": "BNPAFRPP"}))

    processor = factory.get_processor("paypal")
    print(processor.process(100.0, {"email": "user@example.com"}))

    try:
        factory.get_processor("bitcoin")
    except ValueError as e:
        print({"success": False, "error": str(e)})
