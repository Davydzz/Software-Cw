# Deutsche Bank Feedback System

The aim of this system is implementing a mood retrieval system that will make use of machine learning in the form of language processing. This input data will then be displayed to the presenter via a series of graphs and concise visualisations.


## Running

Type:
```bash
make
```

If the makefile doesn't work, follow these instructions:

## Installation

Use the package manager [pip3](https://pip.pypa.io/en/stable/) to install NLTK.

```bash
pip3 install nltk
```

Install Flask

```bash
pip3 install flask
```

## Running

First instantiate the database

```bash
python3 createDB.py
```

Then run

```bash
flask run

```

or 

```bash
py -m flask run

```


Click on the provided to link to get redirected to the webpage.



## License
[MIT](https://choosealicense.com/licenses/mit/)
