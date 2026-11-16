"""The nightly job: count the day's payments that match no order."""


def run_nightly_job(store, day):
    order_ids = store.order_ids()
    return len([payment for payment in store.payments(day) if payment["order_id"] not in order_ids])
