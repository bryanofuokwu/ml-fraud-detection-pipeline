from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import *

spark = SparkSession.builder \
    .appName("SparkFeatureAggregator") \
    .getOrCreate()

schema = StructType([
    StructField("user_id", StringType()),
    StructField("avg_amt", FloatType()),
    StructField("volatility", FloatType()),
    StructField("country_switch", IntegerType()),
    StructField("card_present_ratio", FloatType())
])

raw_df = spark.read \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "features") \
    .option("startingOffsets", "earliest") \
    .load()

parsed_df = raw_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*")

agg_df = parsed_df.groupBy("user_id").agg({
    "avg_amt": "avg",
    "volatility": "avg",
    "card_present_ratio": "avg"
})

agg_df.write.mode("overwrite").csv("/tmp/daily_aggregates")
