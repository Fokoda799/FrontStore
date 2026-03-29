from time import sleep

from celery import shared_task


@shared_task()
def notify_costumers(message):
    print("Sending messages...")
    print(message)
    sleep(10)
    print("Messages sent!")
