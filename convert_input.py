import os
import json
import re
import argparse
from tqdm import tqdm
from utils import delexicalize
from utils.nlp import normalize

def convert_utterance(utt, dic, bs):
    sent = re.sub(r"\(http.*?\)","",utt)
    sent = re.sub(r"\[User.*\]","",sent)
    sent = re.sub(r"\[Assistant.*\]","",sent)
    sent = sent.replace("[","")
    sent = sent.replace("]","")
    sent = sent.replace("\\u00a", "")
    sent = sent.replace("\\u00A", "")
    sent = sent.replace("\"", "")
    sent = normalize(sent)
    
    words = sent.split()
    sent = delexicalize.delexicalise(' '.join(words), dic)

    # changes to numbers only here
    digitpat = re.compile(r'\d+')
    sent = re.sub(digitpat, '[value_count]', sent)

    return sent

def main(args):
    input_path = args.input

    with open(input_path, 'r') as f:
        input_data = json.load(f)

    dic = delexicalize.prepareSlotValuesIndependent()

    output = {}
    for dialog_id in tqdm(input_data):
        did = dialog_id.split(".json")[0].lower()
        output[did] = []
        for i, turn in enumerate(input_data[dialog_id]):
            bs = {}
            if "state" in turn:
                bs = turn["state"]
            if "response" in turn:
                utt = turn["response"]
                delex_utt = convert_utterance(utt, dic, bs)
                turn["response"] = delex_utt
            output[did].append(turn)

    with open(args.output, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", type=str, required=True, help="Input JSON file path.")
    parser.add_argument("-o", "--output", type=str, default="evaluation_results.json", help="Output file path, here will be the final report.")
    args = parser.parse_args()
    main(args)