import os
import json

def has_domain_predictions(data):
    for dialog in data.values():
        for turn in dialog:
            if "active_domains" not in turn:
                return False
    return True


def get_domain_estimates_from_state(data):

    for dialog in data.values():

        # Use an approximation of the current domain because the slot names used for delexicalization do not contain any
        # information about the domain they belong to. However, it is likely that the system talks about the same domain
        # as the domain that recently changed in the dialog state (which should be probably used for the possible lexicalization). 
        # Moreover, the usage of the domain removes a very strong assumption done in the original evaluation script assuming that 
        # all requestable slots are mentioned only and exactly for one domain (through the whole dialog).

        current_domain = None
        old_state = {}
        old_changed_domains = []

        for turn in dialog:
 
            # Find all domains that changed, i.e. their set of slot name, slot value pairs changed.
            changed_domains = []
            for domain in turn["state"]:
                domain_state_difference = set(turn["state"].get(domain, {}).items()) - set(old_state.get(domain, {}).items())
                if len(domain_state_difference) > 0:
                    changed_domains.append(domain)

            # Update the current domain with the domain whose state currently changed, if multiple domains were changed then:
            # - if the old current domain also changed, let the current domain be
            # - if the old current domain did not change, overwrite it with the changed domain with most filled slots
            # - if there were multiple domains in the last turn and we kept the old current domain & there are currently no changed domains, use the other old domain
            if len(changed_domains) == 0:
                if current_domain is None:
                    turn["active_domains"] = []
                    continue 
                else:
                    if len(old_changed_domains) > 1:
                        old_changed_domains = [x for x in old_changed_domains if x in turn["state"] and x != current_domain]
                        if len(old_changed_domains) > 0:
                            current_domain = old_changed_domains[0] 

            elif current_domain not in changed_domains:
                current_domain = max(changed_domains, key=lambda x: len(turn["state"][x]))

            old_state = turn["state"]
            old_changed_domains = changed_domains
            
            turn["active_domains"] = [current_domain]


def has_state_predictions(data):
    for dialog in data.values():
        for turn in dialog:
            if "state" not in turn:
                return False
    return True


def load_goals():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "data", "goals.json")) as f:
        return json.load(f)


def load_booked_domains():
    dir_path = os.path.dirname(os.path.realpath(__file__))
    with open(os.path.join(dir_path, "data", "booked_domains.json")) as f:
        return json.load(f)


def load_system_utterances(mwz_ver, mode):
    delex_path = os.path.join(f"mwz{mwz_ver}", f"{mode}_dials_delex.json")
    
    if(not os.path.exists(delex_path)):
        print(f"{delex_path} file does not exist. Create it by running the script create_delex_data.py")
        exit(0)
        
    with open(delex_path, 'r') as f:
        delex_data = json.load(f)

    references = {}
    for idx in delex_data:
        did = idx.split(".json")[0].lower()
        lst_sys = delex_data[idx]['sys']
        references[did] = delex_data[idx]['sys']
    return references

def load_belief_state(mwz_ver, mode):
    
    slot_detail = {'type': 'type', 'pricerange': 'pricerange', 'parking': 'parking', 'bookstay': 'stay', 'bookday': 'day', 
               'bookpeople': 'people', 'destination': 'destination', 'arriveby': 'arrive', 
               'departure': 'departure', 'internet': 'internet', 'stars': 'stars', 'area': 'area', 
               'leaveat': 'leave', 'booktime': 'time', 'food': 'food', 
               'name': 'name', 'day': 'day'}

    def get_formated_state(bs):
        bs_new = {}
        for i in range(len(bs)):
            sv = bs[i]['slots']
            for j in range(len(sv)):
                slot_key = sv[j][0]
                slot_key = slot_key.replace("book ","book")
                slot_value = sv[j][1]
                bs_new[slot_key] = slot_value

        bs_dict = {}
        for sk in bs_new:
            arr = sk.split("-")
            domain = arr[0]
            sl = arr[1].strip()
            if sl in slot_detail:
                slot = slot_detail[arr[1].strip()]
            else:
                slot = sl
            if domain not in bs_dict:
                bs_dict[domain] = {}
            bs_dict[domain][slot] = bs_new[sk]
        return bs_dict

    filename = os.path.join(f"mwz{mwz_ver}", f"{mode}_dials.json")
    if(not os.path.exists(filename)):
        print(f"{filename} file does not exist. Create it by running the script create_data.py")
        exit(0)
        
    with open(filename, "r") as f:
        data = json.load(f)

    belief_states = {}
    for i in range(len(data)):
        dt = data[i]
        did = dt["dialogue_idx"]
        idx = did.split(".json")[0].lower()
        belief_states[idx] = {}

        for j in range(len(dt['dialogue'])):
            bs = dt['dialogue'][j]['belief_state']
            belief_states[idx][j] = get_formated_state(bs)
            
    return belief_states