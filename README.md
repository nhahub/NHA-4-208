# National Mental Health & Substance Use Data Analytics Platform
### End-to-End Scalable Data Pipeline, Semantic Modeling, and AI-Driven Exploration

---

## 📌 Project Overview
This repository contains an enterprise-grade data analytics and engineering platform designed to process, model, and visualize nationwide mental health and substance use trends in the United States. Utilizing multi-year public-use microdata from the **Substance Abuse and Mental Health Services Administration (SAMHSA)**, the platform establishes an optimized, high-performance architecture bridging advanced local preprocessing, modern cloud data lake solutions, robust semantic modeling, and intuitive self-service intelligence.

The system scales efficiently to handle millions of records across disparate national health surveys, transforming raw and heavily encoded categorical datasets into decision-ready insights for healthcare policymakers, clinicians, and health analysts.

---

## 🚀 Key Objectives
1. **High-Performance Engineering:** Establish a high-throughput processing pipeline using **Polars** to ingest and clean large-scale multi-year datasets, achieving over **80% storage compression** via optimization to Apache Parquet formats.
2. **Robust Cloud Integration:** Deploy an agile, cost-effective Data Lake architecture using **AWS S3** for structured storage and **Amazon Athena** for serverless ad-hoc query execution.
3. **Macro-Level Data Cohesion:** Resolve the absolute absence of shared patient identifiers across different behavioral studies by designing a centralized **Star Schema semantic layer** anchored on aggregate space-time dimensions (State and Year).
4. **Interactive Enterprise BI:** Deliver a dynamic portfolio of interactive, enterprise-ready **Power BI dashboards** leveraging **Composite Models (DirectQuery + Import)** to guarantee responsive query performance over massive underlying datasets.
5. **Generative AI Querying:** Implement a specialized **AI Text-to-SQL Bot** that democratizes data exploration, enabling users to query the AWS Athena Data Lake using natural language.

---

## 🗺️ System Architecture & Data Pipeline
The overall data lifecycle is built upon a linear, scalable pipeline designed to bypass local memory bottlenecks and cloud cost inefficiencies:

```text
  [ Raw Public Data (SAMHSA) ]
               │
               ▼  (Local Pipeline: Polars / Feature Selection / Null Masking)
  [ Parquet Columnar Compression ]
               │
               ▼  (Secure Migration via Boto3 / AWS CLI)
  [ AWS S3 Structured Buckets ]
               │
               ▼  (Data Lake Cataloging & Type Alignment: BIGINT/DOUBLE)
  [ Amazon Athena External Tables & Decoded Views ]
        ───────┴───────
       │               │
       ▼ (DirectQuery)  ▼ (Boto3 SDK Orchestration)
  [ Power BI ]    [ AI Text-to-SQL Bot ] ◄─── (Natural Language Input)
```

**Local Preprocessing Layer:** Implemented in Python using Polars (LazyFrames) to seamlessly process large multi-year files. This step automates features selection, filters out invalid rows, and aligns variable structures. Missing or suppressed records (historically marked as -9, -8, or unknown indicators in SAMHSA codebooks) are strictly mapped to proper database NULL types.

**Columnar Compression & Storage:** Output files are converted into heavily compressed Apache Parquet files, shrinking storage requirements by more than 80%, substantially reducing cloud data transfer costs.

**Cloud Data Lake & Cataloging:** Data is organized in AWS S3 buckets with intuitive folder partitioning. Amazon Athena serves as the serverless relational engine. External schemas are explicitly defined to address schema evolution or type mismatches (e.g., handling double-precision values emitted by pandas/polars pipelines into matching Athena types).

---

## 🗂️ Project Scope & Data Sources
The project explicitly ingests and synthesizes historical datasets spanning 2021 to 2023:

### ✔️ Included Datasets
- **NSDUH (National Survey on Drug Use and Health):** Focuses on population-level prevalence of mental illness, major depressive episodes (MDE), serious psychological distress (Kessler-6 scores), suicidal ideation, and substance use patterns.
- **MH-CLD (Mental Health Client-Level Data):** Captures clinical data from state-reporting facilities, providing diagnostic profiles (clinical classifications like depression, schizophrenia, bipolar disorder, anxiety), clinical counts, and demographics at care admission.
- **TEDS-A (Treatment Episode Data Set - Admissions):** Tracks substance use treatment center admissions, recording substance profiles (alcohol, opioids, cocaine, methamphetamines), primary administrative delivery routes, and frequencies of use.

### ❌ Excluded Datasets (Technical Justifications)
- **TEDS-D (Discharges):** Excluded due to systemic, corrupt data files on the public provider portal that could not be deterministically parsed or structurally resolved.
- **N-SUMHSS (National Survey of Substance Abuse and Mental Health Services):** Excluded because it functions strictly as facility-level capacity data and completely lacks client/patient-level attributes.
- **DAWN & URS:** Excluded because the raw granular microdata is legally classified and restricted from public use.

---

## 📐 Data Modeling & Star Schema
Because these public datasets are completely anonymous, they do not share a common primary key (Patient_ID). To achieve multidimensional analytics across separate studies, a Star Schema was created to join these datasets macroscopically.

The three massive transaction tables function as Fact Tables, which connect to centrally maintained, optimized Dimension Tables via strict 1-to-Many (1:*) relationships:

- **Dim_State:** Standardized census FIPS state codes and geographical identifiers.
- **Dim_Year:** Chronological calendar year structures.

This modeling paradigm allows a single slicer interaction in Power BI (e.g., filtering for State: Texas and Year: 2022) to instantly filter and align metrics across NSDUH, MH-CLD, and TEDS-A simultaneously.

---

## 📊 Business Intelligence Dashboards (Power BI)
The data platform exposes a highly professional, multi-layered dashboard design. To maintain exceptional response times, a Composite Model Architecture was deployed: Dimension tables are fully loaded via Import Mode into local RAM for instantaneous filter processing, while massive fact data remains connected directly via DirectQuery to Amazon Athena, execution queries on-demand.

### 🔹 1. MH-CLD Clinical Care Profiling Dashboard
**Focus:** Visualizes primary, secondary, and tertiary psychiatric diagnoses alongside inpatient and outpatient facility utilization rates.
**Path to Visual:** `MH-CLD/MHCLD-PBI-Photos/mhcld-photo1.jpeg`

### 🔹 2. NSDUH Sociodemographic Disparities & Prevalence Dashboard
**Focus:** Tracks macro-level national trends regarding mental illness prevalence across distinct demographic brackets (age, sex, income, race, and education levels).
**Path to Visual:** `NSDUH/NSDUH-PBI-Photos/nsduh-photo1.jpeg`

### 🔹 3. TEDS-A Treatment & Substance Use Admission Profiling
**Focus:** Monitors administrative care ingestion, substance profiles, route-of-administration patterns, and dual-diagnosis vulnerabilities.
**Path to Visual:** `TEDS-A/TEDSA-PBI-Photos/tedsa-photo1.JPG`

---

## 🤖 AI Text-to-SQL Bot
To abstract complex SQL structures away from end-users, an interactive Natural Language AI Agent was built inside the repository.

- **Core Engine:** Utilizes an LLM provider orchestrated via an application tier to accept free-form English queries (e.g., "Show me the total number of clients diagnosed with depression in California during 2023").
- **Execution Architecture:** Generates optimized Amazon Athena dialect SQL statements, passes credentials via a secure Boto3 SDK client wrapper, executes the query on the AWS Data Lake in the background, and formats the output data dynamically for the end-user.
- **Interface App:** Delivered via a clean, lightweight interactive layout.
**Path to Interface Visual:** `AI-Bot/WhatsApp Image 2026-07-13 at 5.15.29 PM.jpeg`
  ├── AI-Bot/
│   ├── ai_engine.py             # LLM Text-to-SQL logic & context injection
│   ├── athena_utils.py          # Boto3 client initialization and AWS connections
│   └── WhatsApp Image 2026-07-13 at 5.15.29 PM.jpeg  # AI Bot App Interface Visual
├── MH-CLD/
│   ├── MHCLD-PBI-Photos/
│   │   └── mhcld-photo1.jpeg    # Clinical Care Profiling Dashboard Screenshot
│   └── athena_mhcld_views.sql   # SQL scripts for MH-CLD data modeling & decoding
├── NSDUH/
│   ├── NSDUH-PBI-Photos/
│   │   └── nsduh-photo1.jpeg    # National Prevalence Dashboard Screenshot
│   └── athena_nsduh_views.sql   # Athena external tables and type alignment SQL
├── TEDS-A/
│   ├── TEDSA-PBI-Photos/
│   │   └── tedsa-photo1.JPG     # Admission Analysis Dashboard Screenshot
│   └── athena_tedsa_views.sql   # SQL scripts mapping substance abuse and routes
├── preprocessing/
│   └── ingestion_pipeline.py    # Polars ETL and Parquet compression scripts
├── WhatsApp Image 2026-07-13 at 1.31.26 AM.jpeg     # Central Star Schema Model Diagram
├── Mental_Health_Project_Documentation.pdf         # Comprehensive Project Report
└── README.md                    # System Documentation (This File)

---

## 🛠️ Getting Started & Installation

### Prerequisite Configurations
- **AWS Identity Setup:** Create an IAM User with explicit access permissions: `AmazonAthenaFullAccess` and `AmazonS3ReadOnlyAccess`. Generate and save your `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`.
- **Local Environment:** Ensure Python 3.10+ is installed alongside your preferred virtual environment framework.
- **Power BI Driver:** Install the official Amazon Athena ODBC Driver locally to support DirectQuery execution.

### Local Setup Steps
```bash
# 1. Clone the repository
git clone https://github.com/your-username/mental-health-analytics.git
cd mental-health-analytics

# 2. Initialize a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows use: .\venv\Scripts\Activate.ps1

# 3. Install required application dependencies
pip install polars pandas boto3 streamlit google-generativeai
```

### Running the AI Text-to-SQL Application
```bash
cd AI-Bot
streamlit run ai_engine.py
```

---

## 🏆 Key Performance Indicators (KPIs) Achieved
- **Storage Optimization (KPI-1):** Achieved >80% compression on raw analytical files, transitioning multi-gigabyte structures into highly indexed columnar .parquet blocks.
- **Data Integrity (KPI-2):** 100% conversion of ambiguous invalid survey responses (-9 flags) into standardized structural database NULL representations.
- **Model Optimization (KPI-3):** Successfully implemented a star schema across 3 multi-million row surveys with zero direct many-to-many relationships.
- **Performance (KPI-4):** Reduced dashboard calculation lag using a composite data model (DirectQuery for heavy fact views + Import for geographic dimensions).

---

## 👥 Team Information & Roles

**Mohammed Mahmoud Abdelrazek** – Project Lead & Data Architect
Defined the overall engineering strategy, enforced preprocessing pipelines, designed the central Star Schema architecture, and authored the system documentation.

**Shaza Yousef** – BI Analyst (NSDUH)
Engineered demographic analytics models and designed the interactive National Prevalence Dashboard.

**Habiba Mohammed** – BI Analyst (MH-CLD)
Developed the Clinical Care Profiling Dashboard and structured diagnostic profiling logic.

**Khadija Osama** – BI Analyst (TEDS-A)
Constructed treatment episode tracking metrics and managed semantic visualizations for care ingestion patterns.

**Mohannad Mohammed** – AI & Data Engineering Associate
Constructed the serverless infrastructure catalogs on AWS Athena and developed the Text-to-SQL AI bot engine.

---


---

## 📁 Repository Structure
