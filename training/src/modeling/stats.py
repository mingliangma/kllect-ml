import json
import collections
import config



def check_expand():
    unique_id = []
    with open('mturk_data_160715_cleaned_expaned.json', 'r') as input_file:
        for line in input_file:
            r = json.loads(line)
            if r['id'] not in unique_id:
                unique_id.append(r['id'])
            else:
                print r['id']
    print len(unique_id)

def label_list():
    unique_label = set()
    label_number = {}
    label_list = {}
    label_list['Others'] = 0
    with open('mturk_data_160715_cleaned_expaned.json', 'r') as input_file:
        for line in input_file:
            r = json.loads(line)
            unique_label.add(r['ml_label'])
            if r['ml_label'] not in label_number:
                label_number[r['ml_label']] = 1
            else:
                label_number[r['ml_label']] += 1
    print len(unique_label)
    print unique_label

    for i, r in enumerate(label_number):
        if r in config.predefined_technology_labels:
            label_list[r] = label_number[r]
        else:
            label_list['Others'] += label_number[r]

    for i, r in enumerate(label_list):
        print ('%s: %s' %(r, label_list[r]))




if __name__ == '__main__':
    # check_expand()
    label_list()