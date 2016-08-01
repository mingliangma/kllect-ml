# Video Content Classification


This repository currently contains the Docker files, source code, and data for the `Video Content Classification` microservice. The service now supports the second-level tag classification for `Technology` videos.


## Content
* [Docker building instructions] (#docker-building-instructions)
* [Test if the APIs work properly] (#test-if-the-apis-work-properly)
* [How to use the API] (#how-to-use-the-api)


## Docker building instructions

In the current folder:

1. `docker build -t kllect:python_image -f Dockerfile-image .` (don't forget the last period)
2. `docker build -t kllect:python_pkgs -f Dockerfile-pkgs .`
3. `docker build -t kllect:python_code -f Dockerfile-code .`
4. `docker build -t kllect:video_content_classification -f Dockerfile-deploy .`



If everything works out right, run the following command to launch the container. Let's map the container's exposed port to the same port on the host.

        docker run -p :5011:5011 -t kllect:video_content_classification



## Test if the APIs work properly
* Run a RESTful API test:
  
   ```
   curl -H "Content-Type: application/json" -X POST -d '{"category":"Technology", "data":[{"id":1, "title":"Apple new gadget","description":"Watch out for this newest and coolest Apple watch"}]}' http://localhost:5011/content_classification
   ```

The expected result should be:
   ```json
   {
     "results": [
       {
           "id": 1, 
           "predictions": [
              "Others"
            ]
    	}]
    }
   ```


## How to use the API
  - **URL:** `http://{Your host's IP address}:5011/content_classification`
  - **Method:** `POST`
  - **Request format:** `JSON`
  - **Request parameters:**

    | Parameter | Required | Description |
    | :--------- | :---------: | ----------- |
    | `category`     | Y | The **first-level category** of the video. Currently, only `Technology` category is supported. |
    | `data`   | Y | A **list** containing all the input videos for classification. Each element in the `data` list needs to be in a certain form. Details see below.|


  Each element in the `data` parameter needs to be of the following `JSON` format:

    | Parameter | Required | Description |
    | :--------- | :---------: | ----------- |
    | `id`     | Y | The **identifier** of the video, will be returned as part of the response. This ID won't be used to link any external data source, only for the purpose of identifying the document being requested. |
    | `title`   | N | The **title** of the video. |
    | `description` | N | The **description** of the video. |
    | `extraction_method`   | N | The **extraction_method** of the video, in the same sense as the `extraction_method` field in the MongoDB, such as `search_by_funny`. |
    | `raw_tags` | N | The list of **raw tags** of the video as gathered from Youtube. |

    
    - **Response format:** `JSON`
    - **Response:**
    
    | Parameter | Description |
    | :--------- | :--------- |
    | `results` | The list of prediction results returned. Each element in the `results` list would be in a certain form. Details see below.|


  Each element in the `results` parameter will be of the following `JSON` format:

    | Parameter | Description |
    | :--------- | :--------- |
    | `id` | The **identifier** of the video, will be returned as part of the response. This would be used to identify each video in the request. Note, in the case where some input videos are not in the valid format, as specified in the `data` parameter part, those videos will not be present in the response, i.e., their `id`s are missing in the response. Also, the order of the videos in the response is not guaranteed to be the same as in the request. |
    | `predictions` | The list of predicted **tags** of the video. |

