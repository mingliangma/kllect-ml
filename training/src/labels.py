labels = {
    'Technology' : {
        't1' : 'Internet of Things',
        't2' : 'Artificial Intelligence',
        't3' : 'Big Data',
        't4' : 'Computer Science',
        't5' : 'Driverless Cars',
        't6' : 'Drone',
        't7' : 'Wearable Tech',
        't8' : 'Manufacturing',
        't9' : 'NanoTech',
        't10' : 'Battery',
        't11' : 'BioTech',
        't12' : 'Virtual Reality and Augmented Reality',
        't13' : 'Smartphones',
        't14' : 'Social Networks',
        't15' : 'Ecommerce'
    }
}

inv_labels = {}
for k in labels:
    inv_labels[k] = {}
    for sub_k, v in labels[k].items():
        inv_labels[k][v] = sub_k