Let's run the project build in the terminal with the following command: docker compose -f docker-compose.dev.yml build, creating the image will take some time. After creating an image with containers, the build must be launched, this is done with the following command: docker compose -f docker-compose.dev.yml up. I'm using the -f flag because this file contains the name docker-compose.dev.yml and is the dev version, if the file name were docker-compose.yml, I could just run it with the command: docker compose build -- up.
To get into the terminal of a container with django, you can enter the following command: docker exec -it django sh, where django is the name of any container.