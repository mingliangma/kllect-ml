# Video Data Index and Search

The Elasticsearch cluster is currently hosted on the following three instances:
1. 54.175.64.170
2. 54.175.64.170
3. 54.175.64.170



This repository currently contains the Docker files and source code for the `Video Data Index and Search` microservices. The service now supports the following functinality:
* `reindex`: A full reindexing of all the video data currently in the MongoDB to ElasticSearch. You should **avoid using** this microservice as much as possible, in favor of the incremental index/delete of video data if you are dealing with a small amount of change, e.g., daily update your searchable video index. The reason why you should avoid using this service is simply because of the unnecessary time spent on processing those data that remain the same. **However, this service is fully automated in a way that there would be no down time experienced even if the reindexing process takes a long time.**
* `index_videos`: Incrementally **index** a list of new videos. This service will simply add this new list of videos into the existing Elasticsearch index to make them searchable.
* `delete_videos`: Incrementally **remove** a list of old videos. This service will simply remove this list of videos from the existing Elasticsearch index so they are no longer searchable.
* `search_videos`: Given the specified search criteria, this service will return a list of videos sorted by their relevancy score.


## Content
* [Docker building instructions] (#docker-building-instructions)
* [Test if the APIs work properly] (#test-if-the-apis-work-properly)
* How to use the API
  1. [How to use the Category Classifcation API] (#how-to-use-the-category-classification-api)
  2. [How to use the Tag Classifcation API] (#how-to-use-the-tag-classification-api)
  3. [How to use the Full Classifcation API] (#how-to-use-the-full-classification-api)

## Docker building instructions

In the current folder:

1. `docker build -t kllect/ml:latest .` (don't forget the last period)


If everything works out right, run the following command to launch the container. Let's map the container's exposed port to the same port on the host.

        docker run --name kllectml -p :5011:5011 -t kllect/ml:latest

## Kllect Docker registry
Docker registry is hosted on Docker Hub. If Ming (owner) hasn't add you to Kllect organization, please him to do so.

Login with your personal Docker ID and password to push and pull images from Docker Hub:
```
docker login

# push a new image to this repository
docker push kllect/ml:lastest

# pull the latest image from this repository
docker pull kllect/ml:lastest
```

## Docker continuous integration continuous delivery

Auto deployment is setup in Docker Cloud - Services so that when a new GitHub commit is detected, a new docker image will be built, and deployed to AWS EC2 Instance.

## Test if the APIs work properly
* Run a RESTful API test to test first-level video category classification:

   ```
   curl -H "Content-Type: application/json" -X POST -d '{"data":[{"id":1, "title":"Thinnest Smartphone In The World! (Vivo X5 Max)", "description":"Unboxing and overview of the thinnest smartphone in the world in the Vivo X5 Max. This phone measures in at just 4.75mm thick, beating out the Oppo R5 (4.85mm) for the title of world’s thinnest phone. Places I hang out: Facebook: http://www.facebook.com/phonebuff Google+: http://www.google.com/+PhoneBuff Instagram: http://instagram.com/phonebuff Twitter: http://twitter.com/phonebuff", "raw_tags":["thinnest phone", "vivo x5 max", "vivo", "x5 max", "thinnest phone in the world", "phonebuff"]}]}' http://localhost:5011/category_classification
   ```

The expected result should be:
   ```json
   {
     "results": [
       {
           "categories": [
              "Technology"
            ],
          "id": 1
    	}]
    }
   ```

* Run a RESTful API test to test second-level tag classification:

   ```
   curl -H "Content-Type: application/json" -X POST -d '{"category":"Technology", "data":[{"id":1, "title":"Thinnest Smartphone In The World! (Vivo X5 Max)", "description":"Unboxing and overview of the thinnest smartphone in the world in the Vivo X5 Max. This phone measures in at just 4.75mm thick, beating out the Oppo R5 (4.85mm) for the title of world’s thinnest phone. Places I hang out: Facebook: http://www.facebook.com/phonebuff Google+: http://www.google.com/+PhoneBuff Instagram: http://instagram.com/phonebuff Twitter: http://twitter.com/phonebuff", "raw_tags":["thinnest phone", "vivo x5 max", "vivo", "x5 max", "thinnest phone in the world", "phonebuff"]}]}' http://localhost:5011/tag_classification
   ```

The expected result should be:
   ```json
   {
     "results": [
       {
           "id": 1,
           "tags": [
              "Smartphones"
            ]
    	}]
    }
   ```

* Run a RESTful API test to test full classification:

   ```
   curl -H "Content-Type: application/json" -X POST -d '{"data":[{"id":1, "title":"Thinnest Smartphone In The World! (Vivo X5 Max)", "description":"Unboxing and overview of the thinnest smartphone in the world in the Vivo X5 Max. This phone measures in at just 4.75mm thick, beating out the Oppo R5 (4.85mm) for the title of world’s thinnest phone. Places I hang out: Facebook: http://www.facebook.com/phonebuff Google+: http://www.google.com/+PhoneBuff Instagram: http://instagram.com/phonebuff Twitter: http://twitter.com/phonebuff", "raw_tags":["thinnest phone", "vivo x5 max", "vivo", "x5 max", "thinnest phone in the world", "phonebuff"]}]}' http://localhost:5011/full_classification
   ```

The expected result should be:
   ```json
   {
     "results": [
       {
           "full_predictions": [
              {
                "category": "Technology",
                "tags": [
                  "Smartphones"
                ]
              }
            ],
          "id": 1
    	}]
    }
   ```


## How to use the API
### How to use the Category Classification API
  - **URL:** `http://{Your host's IP address}:5011/category_classification`
  - **Method:** `POST`
  - **Request format:** `JSON`
  - **Request parameters:**

    | Parameter | Required | Description |
    | :--------- | :---------: | ----------- |
    | `data`   | Y | A **list** containing all the input videos for classification. Each element in the `data` list needs to be in a certain form. Details see below.|


  - **`data` parameter format:** Each element in the `data` parameter needs to be of the following `JSON` format:

    | Parameter | Required | Description |
    | :--------- | :---------: | ----------- |
    | `id`     | Y | The **identifier** of the video, will be returned as part of the response. This ID won't be used to link any external data source, only for the purpose of identifying the document being requested. |
    | `title`   | N | The **title** of the video. |
    | `description` | N | The **description** of the video. |
    | `raw_tags` | N | The list of **raw tags** of the video as gathered from Youtube.|


  - **Response format:** `JSON`
  - **Response:**

    | Parameter | Description |
    | :---------| :--------- |
    | `results` | The list of prediction results returned. Each element in the `results` list would be in a certain form. Details see below.|


  - **`results` parameter format:** Each element in the `results` parameter will be of the following `JSON` format:

    | Parameter | Description |
    | :--------- | :--------- |
    | `id` | The **identifier** of the video, will be returned as part of the response. This would be used to identify each video in the request. Note, in the case where some input videos are not in the valid format, as specified in the `data` parameter part, those videos will not be present in the response, i.e., their `id`s are missing in the response. Also, the order of the videos in the response is not guaranteed to be the same as in the request. |
    | `categories` | The list of predicted **categories** of the video. |


### How to use the Tag Classification API
  - **URL:** `http://{Your host's IP address}:5011/tag_classification`
  - **Method:** `POST`
  - **Request format:** `JSON`
  - **Request parameters:**

    | Parameter | Required | Description |
    | :--------- | :---------: | ----------- |
    | `category`     | Y | The **first-level category** of the video. Currently, only `Technology` category is supported. |
    | `data`   | Y | A **list** containing all the input videos for classification. Each element in the `data` list needs to be in a certain form. The same as the `data` parameter in the `Category Classification` API.|


  - **Response format:** `JSON`
  - **Response:**

    | Parameter | Description |
    | :---------| :--------- |
    | `results` | The list of prediction results returned. Each element in the `results` list would be in a certain form. Details see below.|


  - **`results` parameter format:** Each element in the `results` parameter will be of the following `JSON` format:

    | Parameter | Description |
    | :--------- | :--------- |
    | `id` | The **identifier** of the video, will be returned as part of the response. This would be used to identify each video in the request. Note, in the case where some input videos are not in the valid format, as specified in the `data` parameter part, those videos will not be present in the response, i.e., their `id`s are missing in the response. Also, the order of the videos in the response is not guaranteed to be the same as in the request. |
    | `tags` | The list of predicted **tags** of the video. |


### How to use the Full Classification API
  - **URL:** `http://{Your host's IP address}:5011/full_classification`
  - **Method:** `POST`
  - **Request format:** `JSON`
  - **Request parameters:**

    | Parameter | Required | Description |
    | :--------- | :---------: | ----------- |
    | `data`   | Y | A **list** containing all the input videos for classification. Each element in the `data` list needs to be in a certain form. The same as the `data` parameter in the `Category Classification` API.|


  - **Response format:** `JSON`
  - **Response:**

    | Parameter | Description |
    | :---------| :--------- |
    | `results` | The list of prediction results returned. Each element in the `results` list would be in a certain form. Details see below.|


  - **`results` parameter format:** Each element in the `results` parameter will be of the following `JSON` format:

    | Parameter | Description |
    | :--------- | :--------- |
    | `id` | The **identifier** of the video, will be returned as part of the response. This would be used to identify each video in the request. Note, in the case where some input videos are not in the valid format, as specified in the `data` parameter part, those videos will not be present in the response, i.e., their `id`s are missing in the response. Also, the order of the videos in the response is not guaranteed to be the same as in the request. |
    | `full_predictions` | The **list** of predicted **categories** and the associated **tags** of the video. Details see below.|


  - **`full_predictions` output format:** Each element in the `full_predictions` output field will contain the following `JSON` format:

    | Parameter |Description |
    | :--------- | ----------- |
    | `category`   | The predicted **category** of the video. Currently, we only support `Technology` vs. `Others`.|
    | `tags` | The list of second-level tags associated the category of interest. At this moment, we only support second-level tags for the `Technology` category.|
