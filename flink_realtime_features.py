from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.functions import KeyedProcessFunction
from pyflink.common.typeinfo import Types
from pyflink.common.serialization import SimpleStringSchema
from pyflink.datastream.connectors import FlinkKafkaConsumer, FlinkKafkaProducer
from pyflink.common import Row
import json
from collections import deque

env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)
env.set_stream_time_characteristic("ProcessingTime")

# Include Kafka JAR (adjust path if needed)
env.get_config().set_string("pipeline.jars", "file:///opt/flink/lib/flink-connector-kafka-1.17.1.jar")

consumer_props = {'bootstrap.servers': 'localhost:9092', 'group.id': 'flink-feature-group'}
producer_props = {'bootstrap.servers': 'localhost:9092'}

consumer = FlinkKafkaConsumer('transactions', SimpleStringSchema(), consumer_props)
producer = FlinkKafkaProducer('features', SimpleStringSchema(), producer_props)

class FeatureExtractor(KeyedProcessFunction):
    def open(self, ctx): self.state = {}

    def process_element(self, value, ctx):
        txn = json.loads(value)
        uid = txn["user_id"]
        amt = float(txn["amount"])
        country = txn["country"]
        present = txn["card_present"]

        if uid not in self.state:
            self.state[uid] = {
                "amounts": deque(maxlen=5),
                "countries": deque(maxlen=5),
                "flags": deque(maxlen=5)
            }

        self.state[uid]["amounts"].append(amt)
        self.state[uid]["countries"].append(country)
        self.state[uid]["flags"].append(present)

        prices = list(self.state[uid]["amounts"])
        avg = sum(prices) / len(prices)
        vol = (sum((x - avg)**2 for x in prices) / len(prices)) ** 0.5
        unique_countries = len(set(self.state[uid]["countries"]))
        flag_ratio = sum(self.state[uid]["flags"]) / len(self.state[uid]["flags"])

        feature = json.dumps({
            "user_id": uid,
            "avg_amt": avg,
            "volatility": vol,
            "country_switch": unique_countries,
            "card_present_ratio": flag_ratio
        })

        ctx.output(None, feature)

# Stream pipeline
source = env.add_source(consumer)
processed = source.key_by(lambda x: json.loads(x)["user_id"]).process(FeatureExtractor())
processed.add_sink(producer)

env.execute("Flink → Kafka Feature Pipeline")