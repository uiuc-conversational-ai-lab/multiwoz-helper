# !/usr/bin/env python3
# conding=utf-8

import sys
import json

from mwzeval.metrics import Evaluator


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--mwz_ver", dest='mwz_ver', required=False, default="2.2", choices=['2.0', '2.1', '2.2', '2.4'], help="Set MultiWOZ version for DST.")
    parser.add_argument("-m", "--mode", dest='mode', required=False, default="test", choices=['train', 'dev', 'test'], help="Set dataset mode (train/dev/test).")
    parser.add_argument("-b", "--bleu", dest='bleu', action="store_true", default=False, help="If set, BLEU is evaluated.")
    parser.add_argument("-s", "--success", dest='success', action="store_true", default=False, help="If set, inform and success rates are evaluated.")
    parser.add_argument("-r", "--richness", dest='richness', action="store_true", default=False, help="If set, various lexical richness metrics are evaluated.")
    parser.add_argument("-d", "--dst", dest='dst', action="store_true", default=False, help="If set, JGA and Slot-F1 is evaluated for DST.")
    parser.add_argument("-f", "--fuzzy_ratio", dest='fuzzy_ratio', type=int, required=False, default=95, help="Fuzzy ratio to compare slot values.")
    parser.add_argument("-i", "--input", type=str, required=True, help="Input JSON file path.")
    parser.add_argument("-o", "--output", type=str, default="evaluation_results.json", help="Output file path, here will be the final report.")
    args = parser.parse_args()

    if not args.bleu and not args.success and not args.richness and not args.dst:
        sys.stderr.write('error: Missing argument, at least one of -b, -s, -r, and -d must be used!\n')
        parser.print_help()
        sys.exit(1)

    with open(args.input, 'r') as f:
        input_data = json.load(f)

    #Fixing dialog_id format
    inp_data = {}
    for dialog_id in input_data:
        did = dialog_id.split(".json")[0].lower()
        inp_data[did] = input_data[dialog_id]

    e = Evaluator(args.mwz_ver, args.mode, args.bleu, args.success, args.richness, args.dst, args.fuzzy_ratio)
    results = e.evaluate(inp_data)

    for metric, values in results.items():
        if values is not None:
            print(f"====== {metric.upper()} ======")
            for k, v in values.items():
                print(f"{k.ljust(15)}{v}")
            print("")

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
