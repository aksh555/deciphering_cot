# Logistic Regression

- `text_cot_train_table.tsv` - train table statistics where `correct` indicates whether GPT-4 solved the example correctly. Logistic rgeression model is fitted on this data in `regression.ipynb`. Obtained by running [eval.py](https://github.com/aksh555/deciphering_cot/eval.py) and `create_train_table.py`
- `text_cot_test_table.tsv` - test table statistics
- `text_cot_test_table_results.tsv` - test table statistics with predictions from the LR model.