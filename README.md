# APLES 
>New model and planning module only.


### Instructions

- clone this repo and cd under APLES folder
- `docker compose up -d`

You can attach vscode to the running container or run

`docker exec -it <<aples_container>> bash`

To execute the experiments:

```

python aples.py

python plot_scalability.py

python calculate_heterogeneity.py

```
When you finished:

`docker compose down`

