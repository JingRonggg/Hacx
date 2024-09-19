# Hacx tryhards


## For Backend
- cd into Backend and follow the below steps
### Installing miniconda
- Follow this installation guide on https://docs.anaconda.com/miniconda/
- Then add conda to path https://www.geeksforgeeks.org/how-to-setup-anaconda-path-to-environment-variable/

### Creating conda env
- Run the following command in vscode terminal
```
conda env create -f environment.yml
```
- Then run
```
conda activate hacx
```
- This should install and run the env for hacx

```
npm install chart.js
```
- This should install visualisation tools
  

### Running the backend
- run
```
uvicorn src.api.backend:app --reload
```
- Backend is hosted on localhost:8000
- To see the docs, go to localhost:8000/localhost
