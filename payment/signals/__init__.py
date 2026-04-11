from django.dispatch import Signal

# This signal carries the payment intent data and metadata
# Any other app can listen to this without the payment app
# needing to know about them
payment_succeeded = Signal()
payment_failed = Signal()
check_payable = Signal()
