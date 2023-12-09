from dataclasses import dataclass
from pyspark.sql import SparkSession, DataFrame
import pytzen as zen

@dataclass
class CSVLoader(zen.ProtoType):
    spark: SparkSession
    header: bool = True
    infer_schema: bool = True

    def load_as_dataframe(self) -> DataFrame:
        """
        Loads a CSV file as a Spark DataFrame.

        Returns:
            DataFrame loaded from the CSV file.
        """
        self.df = self.data.spark.read.csv(
            self.config.file_path,
            header=self.data.header,
            inferSchema=self.data.infer_schema,
            sep=self.config.delimiter
        )

    def retrive_data_info(self) -> None:
        """
        Retrives the schema of the CSV file.
        """
        schema_dict = {field.name: field.dataType.simpleString() 
                       for field in self.data.df.schema.fields}
        self.store('data_schema', schema_dict)
        num_rows = self.data.df.count()
        num_columns = len(self.data.df.columns)
        self.store('data_shape', {'rows': num_rows, 'columns': num_columns})

    def inject(self) -> None:
        """
        Injects the CSV file into the pipeline.
        """
        self.log('Injecting CSV file into the pipeline.')
        self.load_as_dataframe()
        self.retrive_data_info()