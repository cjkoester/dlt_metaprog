# Databricks notebook source
# MAGIC %md
# MAGIC ## Create Synthetic Source Data 

# COMMAND ----------

# MAGIC %pip install dbldatagen==0.3.5

# COMMAND ----------

import dbldatagen as dg

# COMMAND ----------

dbutils.widgets.text("catalog", "", "01 Catalog")

# COMMAND ----------

# DBTITLE 1,Create Dataspec for Data Generator
# https://databrickslabs.github.io/dbldatagen/public_docs/generating_cdc_data.html

def create_dataspec(row_count, partitions):
    partitions_requested = partitions
    data_rows = row_count
    spark.conf.set("spark.sql.shuffle.partitions", "auto")
    uniqueCustomers = row_count

    dataspec = (
        dg.DataGenerator(
            spark,
            rows=data_rows,
            partitions=partitions_requested,
            randomSeedMethod="hash_fieldname",
        )
        .withIdOutput()
        .withColumn("str1", "string", template=r"\\w")
        .withColumn("str2", "string", template=r"\\w")
        .withColumn(
            "event_date",
            "date",
            begin="2020-01-01",
            end="2022-12-31",
            interval="1 day",
            random=True,
        )
    )

    return dataspec

# COMMAND ----------

catalog = dbutils.widgets.get('catalog')
schema = 'dlt_metaprog'

spark.sql(f'use catalog {catalog}')
spark.sql(f'create schema if not exists {schema}')

# Set partitions to 1x or 2x number of cores
dataspec = create_dataspec(row_count=1_000_000, partitions=32)
dataspec.build().createOrReplaceTempView('src_vw')
display(spark.sql('select * from src_vw'))

# COMMAND ----------

for i in range(8):
    spark.sql(f'create or replace table {schema}.src_table_{i+1} as select * from src_vw')