import os
import time
import io
import boto3
import polars as pl
import streamlit as st  # استبدال dotenv بـ streamlit

# حذف سطر load_dotenv() لأنه لم يعد مستخدماً

# قراءة إعدادات قاعدة البيانات و S3 من البيئة أو استخدام القيم الافتراضية
DATABASE_NAME = os.getenv("ATHENA_DATABASE", "samhsa_master_db")
S3_BUCKET = os.getenv("ATHENA_S3_BUCKET", "samhsa-datalake-2021-2023-depi")
S3_OUTPUT_LOCATION = f"s3://{S3_BUCKET}/athena_results/"


def _get_clients():
    # جلب مفاتيح AWS مباشرة من Streamlit Secrets التي قمت بحفظها
    aws_id = st.secrets.get("AWS_ACCESS_KEY_ID")
    aws_secret = st.secrets.get("AWS_SECRET_ACCESS_KEY")
    region = st.secrets.get("AWS_REGION", "us-east-1")

    if not aws_id or not aws_secret:
        raise EnvironmentError(
            "AWS credentials not found. Set AWS_ACCESS_KEY_ID and "
            "AWS_SECRET_ACCESS_KEY in your Streamlit Secrets."
        )

    athena_client = boto3.client(
        "athena",
        region_name=region,
        aws_access_key_id=aws_id,
        aws_secret_access_key=aws_secret,
    )
    s3_client = boto3.client(
        "s3",
        region_name=region,
        aws_access_key_id=aws_id,
        aws_secret_access_key=aws_secret,
    )
    return athena_client, s3_client


def run_athena_query(query, poll_interval=1, timeout_seconds=120):
    """
    Executes a SQL query against Athena and returns the result as a Polars DataFrame.
    """
    athena, s3 = _get_clients()

    start_response = athena.start_query_execution(
        QueryString=query,
        QueryExecutionContext={"Database": DATABASE_NAME},
        ResultConfiguration={"OutputLocation": S3_OUTPUT_LOCATION},
    )
    execution_id = start_response["QueryExecutionId"]

    status = None
    state = "RUNNING"
    elapsed = 0
    while elapsed < timeout_seconds:
        status = athena.get_query_execution(QueryExecutionId=execution_id)
        state = status["QueryExecution"]["Status"]["State"]
        if state in ("SUCCEEDED", "FAILED", "CANCELLED"):
            break
        time.sleep(poll_interval)
        elapsed += poll_interval

    if state != "SUCCEEDED":
        if status is not None:
            reason = status["QueryExecution"]["Status"].get("StateChangeReason", "Unknown reason")
        else:
            reason = f"Query did not finish within {timeout_seconds}s"
        raise Exception(f"Athena query {state}: {reason}")

    output_location = status["QueryExecution"]["ResultConfiguration"]["OutputLocation"]
    without_scheme = output_location.replace("s3://", "", 1)
    bucket, key = without_scheme.split("/", 1)

    s3_object = s3.get_object(Bucket=bucket, Key=key)
    file_content = s3_object["Body"].read()

    if not file_content:
        return pl.DataFrame()

    try:
        return pl.read_csv(io.BytesIO(file_content), infer_schema_length=1000)
    except Exception:
        return pl.read_csv(io.BytesIO(file_content), infer_schema_length=0)
