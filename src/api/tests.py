from content_classification_api import topic_classifier

if __name__ == '__main__':
    from pymongo import MongoClient
    import config

    uri = "mongodb://%s:%s@%s:%s/%s?authMechanism=SCRAM-SHA-1" % (config.username,
                                                                  config.password,
                                                                  config.mongodb_host,
                                                                  config.mongodb_port,
                                                                  config.db)

    client = MongoClient(uri)
    col = client[config.db][config.result_col]

    i = 0
    batch_data = [ {
        "id" : 1,
        "title" : "Apple new gadget",
        "description" : "Watch out for this newest and coolest Apple watch"
        }]

    labels = []
    batch_size = 5
    predictions = []
    for data in batch_data:
        predictions.extend(topic_classifier.predict(batch_data))

    for prediction in predictions:
        print prediction

        # classifier = category2classifier['Technology']
    # for video in col.find({'ml_label': {'$exists': True}}):
    #     labels.append(video['ml_label'])
    #     video['id'] = str(video['_id'])
    #
    #     batch_data.append(video)
    #
    #     if len(batch_data) == batch_size:
    #         print 'Predicting for group #%d...' % (i // batch_size)
    #
    #         predictions.extend(classifier.predict(batch_data))
    #         batch_data = []
    #         break
    #
    #     i += 1
    #
    # if len(batch_data):
    #     predictions.extend(classifier.predict(batch_data))
    #
    # for prediction in predictions:
    #     print prediction
