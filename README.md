# Instructed to Bias

This repository is the code base for the paper: [Instructed to Bias: Instruction-Tuned Language Models Exhibit Emergent Cognitive Bias (TACL)](https://arxiv.org/abs/2308.00225). 

## Requirements

* Python version >= 3.11

View requirments.txt file for more information.

## Getting started
```bash
git clone https://github.com/itay1itzhak/InstructedToBias.git
cd InstructedToBias
pip install requirements.txt -r
```

## Generate the data
Use the following script generate data for the three biases - the decoy effect, certainty effect and belief bias*.
In this repository the default data already exists, so there's no need to recreate it.

\* Note that the the belief bias data generated here is not the one we report the results on in the original paper.
This data is a recreation of the data created by [Dasgupta et al. (2022)](https://arxiv.org/abs/2207.07051) which we used for the results in our paper.

```BIAS_NAME = {'decoy','certainty','false_belief'}.```

```bash
python Data_generation/generate_samples.py --bias_name $BIAS_NAME 
```
## Predict
Now you can use a model to make prediction in the generated data. We support the models used in the original paper from the GPT3/3.5/4 and the T5/Flan-T5 models families.
Additional models can be easily supported by adding a new predictor file for your model that inherits from the Predictor class (see 'Predict/t5_predict.py' for example).

We'll use T5-Small and Flan-T5-Small as an example.
```$MODELS = 't5-v1_1-small,flan-t5-small'```

In order to predict using OpenAI API models, make sure to create an .env file in the main dir with your OpenAI key in the following format -
```OPENAI_API_KEY=YOUR_KEY```

```bash
python run_predict.py --bias_name $BIAS_NAME --all_models $MODELS
```

## Results analysis
Run the analysis script to create a .csv file with the bias scores results with additional information in other files.
The results will be saved in The respected predictions dirs.

\* Note that for the decoy analysis, you'll need to set ```BIAS_NAME=decoy_expensive``` or ```BIAS_NAME=decoy_cheaper``` for the respected biases analysis.
```bash
python run_analysis.py --bias_name $BIAS_NAME --all_models $MODELS
```

Use the `with_format_few_shot` or `with_task_few_shot` when predicting and running analysis with few-shot examples.

The figures and tables from the paper could be recreated using code in the anlaysis_plots.ipynb Jupyter notebook.

## License

Instructed to Bias is MIT-licensed.
