import dlt

def load_table(spark, task):    
    @dlt.expect_all_or_drop(task['expectations'])
    @dlt.table(name=f"{task['tgt_table']}", comment=f"{task['tgt_table']}")
    def src_query():
        return spark.readStream.format("delta").table(
            f"{task['src_catalog']}.{task['src_schema']}.{task['src_table']}"
        )