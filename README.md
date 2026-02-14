# AlphaStream: Real-Time Fraud & Geospatial Pipeline

**AlphaStream** is a cloud-native data engineering project that simulates, ingests, and analyzes high-frequency financial transactions in real-time. The system is built on **Google Cloud Platform (GCP)** and utilizes a **Medallion Architecture** to transform raw JSON events into actionable fraud alerts using geospatial and time-series analytics.

---

## 🏗️ Architecture Overview

The pipeline follows a modern data lakehouse pattern:
1.  **Ingestion Layer**: A custom Python simulator generates synthetic transaction data (JSON) and streams it to **Google Cloud Storage (GCS)**.
2.  **Raw Layer (Bronze)**: Data is exposed to BigQuery via **BigLake External Tables**, utilizing **Metadata Caching** for high-performance querying of unstructured data.
3.  **Silver Layer**: Raw JSON is parsed, cleaned, and materialized into structured tables, including the conversion of Lat/Long coordinates into **GEOGRAPHY** objects.
4.  **Gold Layer**: Advanced analytics are performed using **SQL Window Functions** to detect fraud patterns:
    * **Impossible Travel**: Identifying transactions occurring too far apart in too short a time.
    * **High Velocity**: Identifying customers exceeding a **$13,000/hour** spending threshold.

---

## 🛠️ Technology Stack

* **Language:** Python (Simulator & Data Generation)
* **Infrastructure:** Google Cloud Storage (GCS)
* **Data Warehouse:** BigQuery & BigLake
* **Analytics:** Google Standard SQL (Geospatial & Window Functions)
* **Visualization:** Looker Studio

---

## 📊 The Medallion Pipeline

### 1. Bronze Layer (Raw Ingestion)
To ensure the pipeline could scale and handle unstructured data efficiently, I implemented **BigLake**. This allowed for a single source of truth in GCS while enabling BigQuery features like metadata caching.

### 2. Silver Layer (Cleaning & Structuring)
In this layer, I transformed raw coordinates into spatial points using `ST_GEOGPOINT`. This is critical for calculating distances between transactions.

### 3. Gold Layer (Fraud Intelligence)
This layer contains the core business logic. I used a combination of `LAG()` for geospatial comparison and `SUM() OVER` for rolling time-windows.

**The "High-Velocity" Threshold:**
The system flags any customer whose rolling 60-minute spend exceeds **$13,000**, providing real-time risk mitigation.

---

## 🚀 Fraud Detection Logic

### Impossible Travel
Calculates the speed required to travel between the current and previous transaction locations. If the speed exceeds **800 km/h** (the speed of a commercial jet), a flag is raised.

$$Speed = \frac{ST\_DISTANCE(location, prev\_location) / 1000}{timestamp\_diff\_hours}$$

### Spend Velocity
Uses a 1-hour look-back window to aggregate spending per unique `customer_id`.

```sql
SUM(amount) OVER (
  PARTITION BY customer_id 
  ORDER BY timestamp 
  RANGE BETWEEN 3600 PRECEDING AND CURRENT ROW
)