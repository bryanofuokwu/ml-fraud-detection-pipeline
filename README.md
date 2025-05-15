# ──────────────────────────────────────────────────────
# README.md — How to Run the End-to-End ML Pipeline
# ──────────────────────────────────────────────────────

## 📌 Project: Real-Time ML Feature Pipeline

```
Kafka → Flink (real-time features) → Kafka → Spark (batch aggregation) → Airflow (orchestration)
```

---

## ⚙️ Prerequisites

- Docker + Docker Compose
- Python 3.8+
- Java 8+ (for PyFlink)
- Apache Spark (CLI or Dockerized)

---

## 🚀 Quick Start Instructions

### 1. Clone Repo & Start All Services

```bash
git clone <this_repo_url>
cd ml-pipeline

# Start Kafka, Zookeeper, Flink, Airflow
docker compose up -d
```


### 2. Start Kafka Producer (Simulates Transactions)

```bash
pip install kafka-python
python kafka_producer.py
```

You’ll see output like:
```
Sent: {'user_id': 'u1', 'amount': 123.45, ...}
```


### 3. Run Flink Job to Generate Features

```bash
pip install apache-flink==1.17
python flink_realtime_features.py --jarfile flink-connector-kafka-1.17.1.jar
```

This consumes transactions and writes real-time features to the `features` Kafka topic.


### 4. Run Spark Batch Processor

```bash
spark-submit spark_batch_processor.py
```

This reads features from Kafka and writes daily aggregates to:
```
/tmp/daily_aggregates/
```


### 5. Launch Airflow and Trigger DAG

Airflow UI: http://localhost:8080 (user: `admin`, pass: `admin`)

Enable and trigger the `daily_spark_job` DAG to run Spark on schedule.

---

## 📂 Output Sample
```
user_id, avg(avg_amt), avg(volatility), avg(card_present_ratio)
u1, 132.4, 23.1, 0.6
u2, 145.7, 17.9, 0.4
```

---

## ✅ Summary
- Real-time feature pipeline powered by Kafka + Flink
- Batch ML aggregation using Spark
- Airflow automates the workflow daily
