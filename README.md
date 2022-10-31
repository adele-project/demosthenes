# Demosthenes

Repository of the Demosthenes corpus, a novel corpus for argument mining in legal documents composed of 40 decisions of the Court of Justice of the European Union on matters of fiscal state aid.
The corpus is annotated at three hierarchical levels: the argumentative elements, their types, and their argument schemes.


## Citation

If you use this repository, dataset, or code, please cite our work as:

*Giulia Grundler, Piera Santin, Andrea Galassi, Federico Galli, Francesco Godano, Francesca Lagioia, Elena Palmieri, Federico Ruggeri, Giovanni Sartor, and Paolo Torroni. 2022. Detecting Arguments in CJEU Decisions on Fiscal State Aid. In Proceedings of the 9th Workshop on Argument Mining, pages 143–157, Online and in Gyeongju, Republic of Korea. International Conference on Computational Linguistics. URL: https://aclanthology.org/2022.argmining-1.14.*

```
@inproceedings{grundler-etal-2022-detecting,
    title = "Detecting Arguments in {CJEU} Decisions on Fiscal State Aid",
    author = "Grundler, Giulia  and
      Santin, Piera  and
      Galassi, Andrea  and
      Galli, Federico  and
      Godano, Francesco  and
      Lagioia, Francesca  and
      Palmieri, Elena  and
      Ruggeri, Federico  and
      Sartor, Giovanni  and
      Torroni, Paolo",
    booktitle = "Proceedings of the 9th Workshop on Argument Mining",
    month = oct,
    year = "2022",
    address = "Online and in Gyeongju, Republic of Korea",
    publisher = "International Conference on Computational Linguistics",
    url = "https://aclanthology.org/2022.argmining-1.14",
    pages = "143--157",
}
```


## Repository structure

* the demosthenes_dataset folder contains the tagged documents in xml format
* xmlToJson.py is a python script that converts the dataset into json format
* create_df.py is a python script that generates two dataframes: the first one contains the annotated sentences with their attributes, while the second contains all the documents' sentences and it is used for the AD task
* argumentmining.py defines the functions that perform the classification tasks
* run_experiments.py calls the argumentmining.py functions with the desired parameters


## How to run the experiments

* run xmlToJson.py to convert the xml dataset into the required json format
* run create_df.py to create the dataframes
* open run_experiments.py to choose the tasks, embeddings and classifiers, or run it as it is to get the complete set of experiments
