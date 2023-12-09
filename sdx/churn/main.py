from pyspark.sql import SparkSession
from tools.injection import CSVLoader
from tools.preprocess import TextProcessor

def create_spark_session():
    """
    Create and return a SparkSession.
    """
    spark = SparkSession.builder \
        .appName('Churn') \
        .getOrCreate()
    return spark

def main():
    """
    Main function for the pipeline.
    """
    
    spark = create_spark_session()
    csv_loader = CSVLoader(spark)
    csv_loader.inject()
    csv_loader.data.df.show()
    processor = TextProcessor()
    processor.remove_stop_words()
    processor.data.df_stop.show()
    processor.apply_tf_idf()
    processor.data.df_tfidf.show()
    csv_loader.close()

if __name__ == "__main__":
    main()