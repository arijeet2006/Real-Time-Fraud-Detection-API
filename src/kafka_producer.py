from kafka import KafkaProducer
import json


producer = KafkaProducer(
    bootstrap_servers="kafka:29092",
    value_serializer=lambda value: json.dumps(value).encode("utf-8"),
)


def send_transaction(transaction: dict):
    producer.send(
        "transactions",
        value=transaction,
    )

    producer.flush()