from dataclasses import dataclass
from pyspark.ml.feature import Tokenizer, StopWordsRemover, HashingTF, IDF
import pytzen as zen

@dataclass
class TextProcessor(zen.ProtoType):

    def remove_stop_words(self) -> None:
        """
        Removes stop words from the DataFrame.
        """
        self.log('Removing stop words from the DataFrame.')
        tokenizer = Tokenizer(
            inputCol=self.config.input_col, 
            outputCol=self.config.output_col)
        tokenized_df = tokenizer.transform(self.data.df)
        remover = StopWordsRemover(
            inputCol='words', 
            outputCol='filtered_words')
        self.df_stop = remover.transform(tokenized_df)

    def apply_tf_idf(self) -> None:
        """
        Applies TF-IDF transformation on the DataFrame.
        """
        self.log('Applying TF-IDF transformation on the DataFrame.')
        hashing_tf = HashingTF(
            inputCol=self.config.output_col, 
            outputCol='raw_features', 
            numFeatures=self.config.num_features)
        featurized_df = hashing_tf.transform(self.data.df_stop)

        idf = IDF(inputCol='raw_features', outputCol='features')
        idf_model = idf.fit(featurized_df)
        self.df_tfidf = idf_model.transform(featurized_df)