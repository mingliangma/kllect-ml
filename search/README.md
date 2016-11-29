# Video Data Index and Search

The Elasticsearch cluster is currently hosted on the following three instances:

1. 54.175.64.170
2. 54.210.216.186
3. 54.175.41.130

You can take a look at your current index via this URL:
http://54.175.41.130:9200/_plugin/head/

It should looks something like this:
![alt tag](https://github.com/mingliangma/kllect-ml/blob/search/search/2016-11-28%2023_12_58-elasticsearch-head.png)


# About this Repository

This repository currently contains the Docker files and source code for the `Video Data Index and Search` microservices. The service now supports the following functinality:
* `reindex`: A full reindexing of all the video data currently in the MongoDB to ElasticSearch. You should **avoid using** this microservice as much as possible, in favor of the incremental index/delete of video data if you are dealing with a small amount of change, e.g., daily update your searchable video index. The reason why you should avoid using this service is simply because of the unnecessary time spent on processing those data that remain the same. **However, this service is fully automated in a way that there would be no down time experienced even if the reindexing process takes a long time.**
* `index_videos`: Incrementally **index** a list of new videos. This service will simply add this new list of videos into the existing Elasticsearch index to make them searchable.
* `delete_videos`: Incrementally **remove** a list of old videos. This service will simply remove this list of videos from the existing Elasticsearch index so they are no longer searchable.
* `search_videos`: Given the specified search criteria, this service will return a list of videos sorted by their relevancy score.


## Content
* [Docker building instructions] (#docker-building-instructions)
  1. [Build the Reindex docker] (#build-the-reindex-docker)
  2. [Build the RESTful APIs docker] (#build-the-restful-apis-docker)
 
* [Test if the APIs work properly] (#test-if-the-apis-work-properly)
* How to use the Services
  1. [How to use the Reindex Service] (#how-to-use-the-reindex-service)
  2. [How to use the Index New Videos API] (#how-to-use-the-index-new-videos-api)
  3. [How to use the Delete Old Videos API] (#how-to-use-the-delete-old-videos-api)
  4. [How to use the Search Videos API] (#how-to-use-the-search-videos-api)

## Docker building instructions

### Build the Reindex docker

In the current folder:

  `docker build -t kllect:reindex -f Dockerfile-reindex .` (don't forget the last period)


If everything works out right, run the following command to launch the container. **WARNING**: This will start the complete reindex process.

        docker run -t kllect:reindex


### Build the RESTful APIs docker

In the current folder:

  `docker build -t kllect:search -f Dockerfile-search .` (don't forget the last period)


If everything works out right, run the following command to launch the container. Let's map the container's exposed port to the same port on the host.

        docker run --name kllectsearch -p :5012:5012 -t kllect:search
        
## Kllect Docker registry

** Please update **

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
* Run a RESTful API test to test the `search_videos` API:

   ```
   curl -H "Content-Type: application/json" -X POST -d '{"keyword" : "apple"}' http://localhost:5012/search_videos
   ```

The expected result should be:
   ```json
   {
  "results": [
    {
      "article_url": "https://youtu.be/rXfyccUvukc", 
      "category": "technology", 
      "comment_count": 777, 
      "description": "THE NEW Apple Watch Series 2, we got it for $4 on black friday :)\n\u25b6Infinite Warfare: HOW TO AIM BETTER:\nhttps://www.youtube.com/watch?v=TlYGNBPNbns\n\u25b6Infinite Warfare How To LEVEL UP FAST:\nhttps://www.youtube.com/watch?v=yLhZ1U8ij7M\n\u25b6SELLING Infinite Warfare at GAMESTOP (Day Of RELEASE)\nhttps://www.youtube.com/watch?v=eRG0OywM_XY\n\nFOLLOW ME HERE:\n\u25b6 Twitter: https://twitter.com/HollowPoiint\n\u25b6Twitch: https://Twitch.tv/HollowPoiint\n\u25b6 FaceBook: https://Facebook.com/HollowPoiint\n\u25b6 Instagram: http://instagram.com/HollowPoiint\n\nEVERYTHING I use to GAME:\n\u25b6Kontrol Freek:\nhttps://www.kontrolfreek.com/?a_aid=Hollow\n(USE Code \"Hollow\" For 10% OFF)\n\u25b6SCUF Gaming: \nhttps://scufgaming.com/\n(USE Code \"Hollow For OFF)\n\u25b6ASTRO (My HEADSETS)\nhttp://tinyurl.com/hmosn72\n\u25b6GFUEL:\nhttp://gfuel.com/\n(USE Code \"Hollow\" For 10% OFF)\n\u25b6Ironside Computers - GET Your CUSTOM PC HERE:\nhttp://ironsidecomputers.com/page.php?load=index\n\n\n\u266c Music \u266c\nhttps://soundcloud.com/ukiyoau\nhttps://soundcloud.com/jeff-kaale\n\u25b6Music courtesy of www.epidemicsound.com\n\n\u265b Join The Team: \u265b\n\u23aa\u24c8\u24ca\u24b7\u24c8\u24b8\u24c7\u24be\u24b7\u24ba\u23aa ..Not Later.. NOW \n\u25b6Subscribe: http://urlmin.com/subscribe0\n\n\n\u2622 Game On \u2622\n\u2013\u2013\u2013\u2013\u2013\u2013\u2013\u2013\u2013\u2013\u2013\u2013\nVideo Uploaded By HollowPoiint", 
      "dislike_count": 209, 
      "duration": 616, 
      "extraction_method": "most_popular", 
      "favorite_count": 0, 
      "image_url": "https://i.ytimg.com/vi/rXfyccUvukc/mqdefault.jpg", 
      "is_video": true, 
      "like_count": 3354, 
      "parse_date": "2016-11-27T22:02:26.551000", 
      "popularity": 4.7533608761433515, 
      "publish_date": "2016-11-26T15:33:06", 
      "publisher": "HollowPoiint", 
      "publisherId": "UCmp5y07YIV6i2jPX4x82hVQ", 
      "raw_tags": [
        "NEW APPLE WATCH", 
        "NEW APPLE WATCH SERIES 2", 
        "NEW APPLE WATCH $4", 
        "BUYING APPLE WATCH FOR $4", 
        "BUYING APPLE WATCH", 
        "APPLE WATCH", 
        "APPLE WATCH $4", 
        "APPLE", 
        "WATCH", 
        "CHEAPEST APPLE WATCH", 
        "WORLDS CHEAPEST APPLE WATCH", 
        "BOUGHT NEW APPLE WATCH", 
        "BLACK FRIDAY", 
        "VLOG", 
        "VLOGING"
      ], 
      "raw_tags_text": "NEW APPLE WATCH NEW APPLE WATCH SERIES 2 NEW APPLE WATCH $4 BUYING APPLE WATCH FOR $4 BUYING APPLE WATCH APPLE WATCH APPLE WATCH $4 APPLE WATCH CHEAPEST APPLE WATCH WORLDS CHEAPEST APPLE WATCH BOUGHT NEW APPLE WATCH BLACK FRIDAY VLOG VLOGING", 
      "site_name": "youtube.com", 
      "srcId": "rXfyccUvukc", 
      "tagged_date": "2016-11-27T22:02:26.592000", 
      "tags": [
        "wearable_tech"
      ], 
      "title": "Buying NEW Apple Watch for $4", 
      "video_id": "583b57f212eca7090ffafa73", 
      "view_count": 56670, 
      "youtube_url": "https://youtu.be/rXfyccUvukc"
    }
  ], 
  "size": 1, 
  "start": 0, 
  "status": 200, 
  "total": 1772
}
   ```

* Run a RESTful API test to test the `index_videos` API:

  **WARNING: Running this API would cause a dummy video being inserted into the ElasticSearch index. Please make sure to run the following `delete_videos` API test to remove this dummy video.**
 
   ```
   curl -H "Content-Type: application/json" -X POST -d '{"input" : [{"_id" : "testtest", "title" : "a test video"}]}' http://localhost:5012/index_videos
   ```

The expected result should be:
   ```json
   {
  "batches": [
    {
      "batch_id": 0, 
      "input_ids": [
        "testtest"
      ], 
      "skips": [], 
      "success": true
    }
  ], 
  "status": 200, 
  "success": true, 
  "total_skips": 0
}
   ```
   
* Run a RESTful API test to test the `delete_videos` API:

   ```
   curl -H "Content-Type: application/json" -X POST -d '{"input" : [{"_id" : "testtest"}]}' http://localhost:5012/delete_videos
   ```

The expected result should be:
   ```json
   {
  "batches": [
    {
      "batch_id": 0, 
      "fails": [], 
      "input_ids": [
        "testtest"
      ], 
      "success": true, 
      "successes": [
        "testtest"
      ]
    }
  ], 
  "status": 200, 
  "success": true, 
  "total_fails": 0, 
  "total_successes": 1
}
   ```


## How to use the Services
### How to use the Reindex Service
  Simply run the `kllect-reindex` docker with the following command:
  
      docker run -t kllect:reindex
      
  As state in the beginning, you should avoid using this service if you are dealing with a small amount of new data each time, because indexing the whole set of video data takes significant amount of time. However, this service is fully automated in a way that there would be no down time experienced even if the reindexing process takes a long time. Therefore, running this docker does not cause any damage, just a waste of bandwidth and instance machine time.
  
### How to use the Index New Videos API
      
  - **URL:** `http://{Your host's IP address}:5012/index_videos`
  - **Method:** `POST`
  - **Request format:** `JSON`
  - **Request parameters:**

    | Parameter | Required | Description |
    | :--------- | :---------: | ----------- |
    | `input`   | Y | A **list** containing all the input videos to be indexed. Each element in the `input` list needs to be in the same format as the data stored in MongoDB. The maximum number of elements in the `input` list is set as 2,000.|


  - **Response format:** `JSON`
  - **Response:**

    | Parameter | Description |
    | :---------| :--------- |
    | `batches` | The input data will be indexed in mini-batches, each of which contains 500 videos. This field contains a **list** of response detail for each batch, including the input video ids (to identify the data in each mini-batch), and whether this batch was successfully indexed or not. See below for the format of this field.|
    | `success` | Indicates whether the whole process succeeded or not. Not that each individual mini-batch might have encountered errors on its own. Please check the response detail in the `batches` field.|
    | `total_skips` | The total number of malformed videos which were skipped (not indexed) across the batches. |


  - **`batches` parameter format:** Each element in the `batches` parameter will be of the following `JSON` format:

    | Parameter | Description |
    | :--------- | :--------- |
    | `batch_id` | The **identifier** of the batch, starting from 0. |
    | `input_ids` | The list of `_id`s of the videos being partitioned into this batch. |
    | `success` | Indicates whether this batch succeeded or not. |
    | `skips` | The list of `_id`s of the malformed videos which were skipped in this batch. |


### How to use the Delete Old Videos API

  - **URL:** `http://{Your host's IP address}:5012/delete_videos`
  - **Method:** `POST`
  - **Request format:** `JSON`
  - **Request parameters:**

    | Parameter | Required | Description |
    | :--------- | :---------: | ----------- |
    | `input`   | Y | A **list** containing all the input videos to be deleted. Each element in the `input` list needs to contain at least an `_id` field (all other extra fields will be ignored). The maximum number of elements in the `input` list is set as 2,000.|


  - **Response format:** `JSON`
  - **Response:**

    | Parameter | Description |
    | :---------| :--------- |
    | `batches` | The input data will be indexed in mini-batches, each of which contains 500 videos. This field contains a **list** of response detail for each batch, including the input video ids (to identify the data in each mini-batch), and whether this batch was successfully indexed or not. See below for the format of this field.|
    | `success` | Indicates whether the whole process succeeded or not. Not that each individual mini-batch might have encountered errors on its own. Please check the response detail in the `batches` field.|
    | `total_successes` | The total number of videos which were successfully indexed across the batches. |
    | `total_fails` | The total number of videos which were **not** indexed across the batches. These are those input videos which were not found in the existing index. Nothing happened for these videos.|


  - **`batches` parameter format:** Each element in the `batches` parameter will be of the following `JSON` format:

    | Parameter | Description |
    | :--------- | :--------- |
    | `batch_id` | The **identifier** of the batch, starting from 0. |
    | `input_ids` | The list of `_id`s of the videos being partitioned into this batch. |
    | `success` | Indicates whether this batch succeeded or not. |
    | `successes` | The list of `_id`s of the videos which were successfully indexed in this batch. |
    | `fails` | The list of `_id`s of the videos which were **not** indexed in this batch. |
    
    
### [How to use the Search Videos API

  - **URL:** `http://{Your host's IP address}:5012/search_videos`
  - **Method:** `POST`
  - **Request format:** `JSON`
  - **Request parameters:**

    | Parameter | Required | Description |
    | :--------- | :---------: | ----------- |
    | `keyword`   | N | A search keyword, e.g., `apple` or `apple macbook`. If supplied, the search engine will return only those videos whose t**itle, description, raw_tags, or tags** matches **at least one word** in the search keyword (if it happens to be phrase). If not supplied, the search engine will return all videos, but ranked according to other speicifed criteria. |
    | `start` | N | An integer, default 0, specifying from which position the items in the ranked search result will be returned as the result of this query. For example, `start=0` means include the items starting from the top search result, while `start=20` means include the items starting from the 21-th search result. This parameter, in combination with the `size` parameter, is to allow pagination of the search result page. |
    | `size` | N | An integer, default 20, specifying the maximum number of items returned in this query.  This parameter, in combination with the `size` parameter, is to allow pagination of the search result page. For example, `start=0, size=20` means this query will return the top 20 search results. Therefore, for example, if the user clicks `next page`, you can fire another query with `start=20, size=20` to fetch search results on the second page and so on. |
    | `preferences`  | N | A list of preferences, in terms of **first-level** category w/o **second-level** tags with their corresponding relative weights, to influence the final ranking. For example, if the input preference has a high weight on tag `smartphones`, then search results with this tag will receive extra boosting. See below for the data format of this `preferences` field. |
    
    
- **`preferences` parameter format:** Each element in the `preferences` parameter will be of the following `JSON` format:

    | Parameter | Description |
    | :--------- | :--------- |
    | `tag` | The **first-level** video category plus **second-level** tags, e.g., `technology.smartphones` and `technology.internet of things`. In case second-level tag is not supplied in this parameter, e.g., `technology` only, the query will equally boost all technology videos.|
    | `weight` | The relative importance of this preference, as a user can specify multiple preferences. The weight will be normalized  to sum up as 1 in the backend, so only their relative values matter. |

  - **Response format:** `JSON`
  - **Response:**

    | Parameter | Description |
    | :---------| :--------- |
    | `results` | The list of search results ranked by their relevancy to the search criteria.|
    | `size` | Echo the `size` parameter in the request. |
    | `start` | Echo the `start` parameter in the request. |
    | `total` | The total number of result found matching the search criteria. So you can do proper pagination. |
    
