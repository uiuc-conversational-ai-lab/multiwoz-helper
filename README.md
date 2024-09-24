# MultiWOZ Helper
A code repository for creating and evaluating MultiWOZ data, with support for multiple versions (2.0, 2.1, 2.2, and 2.4). The scripts are based on the following repositories:
1. [MultiWOZ Benchmark](https://github.com/budzianowski/multiwoz)
2. [MultiWOZ Evaluation](https://github.com/Tomiinek/MultiWOZ_Evaluation)

## Install dependencies
python 3.12 or later
```console
❱❱❱ pip install -r requirements.txt
```

## Create data for Dialogue Sate Tracking (DST)
```console
❱❱❱ python create_data.py --mwz_ver=<version>
```

## Create delexicalized data
```console
❱❱❱ python create_delex_data.py --mwz_ver=<version>
```

## Evaluate
```console
❱❱❱ python evaluate.py -v=<version> -m=<mode> -b -s -r -d -i=<input_file.json> -o=<output_file.json>
```
The default values for version and mode are 2.4 and test, respectively. The <input_file.json> must include generated responses and/or belief states. For sample input files, refer to the [`predictions`](predictions) folder.
