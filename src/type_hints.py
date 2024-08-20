from __future__ import annotations

from typing import TYPE_CHECKING, Any, Literal, TypedDict

if TYPE_CHECKING:
    import razorpay

    class Client(razorpay.client.Client):
        @property
        def payment(self) -> razorpay.resources.Payment: ...

        @property
        def refund(self) -> razorpay.resources.Refund: ...

        @property
        def order(self) -> razorpay.resources.Order: ...

        @property
        def invoice(self) -> razorpay.resources.Invoice: ...

        @property
        def payment_link(self) -> razorpay.resources.PaymentLink: ...

        @property
        def customer(self) -> razorpay.resources.Customer: ...

        @property
        def card(self) -> razorpay.resources.Card: ...

        @property
        def token(self) -> razorpay.resources.Token: ...

        @property
        def transfer(self) -> razorpay.resources.Transfer: ...

        @property
        def virtual_account(self) -> razorpay.resources.VirtualAccount: ...

        @property
        def addon(self) -> razorpay.resources.Addon: ...

        @property
        def plan(self) -> razorpay.resources.Plan: ...

        @property
        def subscription(self) -> razorpay.resources.Subscription: ...

        @property
        def qrcode(self) -> razorpay.resources.Qrcode: ...

        @property
        def registration_link(self) -> razorpay.resources.RegistrationLink: ...

        @property
        def settlement(self) -> razorpay.resources.Settlement: ...

        @property
        def item(self) -> razorpay.resources.Item: ...

        @property
        def fund_account(self) -> razorpay.resources.FundAccount: ...

        @property
        def account(self) -> razorpay.resources.Account: ...

        @property
        def stakeholder(self) -> razorpay.resources.Stakeholder: ...

        @property
        def product(self) -> razorpay.resources.Product: ...

        @property
        def iin(self) -> razorpay.resources.Iin: ...

        @property
        def webhook(self) -> razorpay.resources.Webhook: ...

        @property
        def document(self) -> razorpay.resources.Document: ...

        @property
        def dispute(self) -> razorpay.resources.Dispute: ...

        @property
        def utility(self) -> razorpay.utility.Utility: ...


class RazorPayOrderDict(TypedDict):
    id: str
    entity: Literal["order"]
    amount: int
    amount_paid: int
    amount_due: int
    currency: Literal["INR"]
    receipt: None
    offer_id: None
    status: (
        Literal["created"]
        | Literal["paid"]
        | Literal["fulfilled"]
        | Literal["expired"]
        | Literal["cancelled"]
    )
    attempts: int
    notes: dict[str, Any]
    created_at: int
