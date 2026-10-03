from kafka import KafkaConsumer
import json

from src.redis_client import record_transaction
from src.predict import predict_fraud


consumer = KafkaConsumer(
    "transactions",
    bootstrap_servers="kafka:29092",
    auto_offset_reset="earliest",
    enable_auto_commit=True,
    group_id="fraud-detection-group",
    value_deserializer=lambda value: json.loads(
        value.decode("utf-8")
    ),
)


def consume_transactions():

    for message in consumer:

        transaction = message.value

        customer_id = transaction["cc_num"]

        tx_count_1h = record_transaction(
            customer_id
        )

        transaction["tx_count_1h"] = tx_count_1h

        transaction.pop("cc_num")

        result = predict_fraud(
            transaction
        )

        print(
            "Fraud Result:",
            result
        )


if __name__ == "__main__":
    consume_transactions()