# Job Level Classification


This repository currently contains the Docker files, source code, and data for the `Job Level Classification` microservice:


## Docker building instructions

In the current folder:

1. `docker build -t bi:pythonweb_v1 -f Dockerfile-image .` (don't forget the last period)
2. `docker build -t bi:jlc_pkgs_v1 -f Dockerfile-pkgs .`
3. `docker build -t bi:jlc_code_v1 -f Dockerfile-code .`
4. `docker build -t bi:jlc_job_level_classification_v1 -f Dockerfile-deploy .`



If everything works out right, run the following command to launch the container:

        docker run -e ENVIRONMENT=test bi:jlc_job_level_classification_v1


The environment variable `ENVIRONMENT` can also be set on the system level.


## Test if the APIs work properly
* Run a RESTful API test:
  
    `curl -H "Content-Type: application/json" -X POST -d '{"job_id" : 12345, "job_title" : "Sales Manager" , "noc_code" : "0611", "parse" : "<?xml version='1.0' encoding='utf-8'?>\n<JobDoc>\n<posting canonversion='2' dateversion='2' iso8601='2016-05-12' present='736098' xml:space='preserve'><duties>Test</duties></posting>\n\n<skillrollup version='1'>\n</skillrollup>\n\n<special>\n<bgtldlanguage>0514</bgtldlanguage>\n<bgtldcountry>000</bgtldcountry>\n</special>\n</JobDoc>\n" }' http://{Your container's IP address}:5011/career_level_prediction`

The expected result should be:
   ```json
   {
          "job_level": "Junior/Entry",
          "probability": 0.8440564241785155
   }
   ```


