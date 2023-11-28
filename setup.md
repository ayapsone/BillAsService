## Use virtual env to run this generative app

pip install virtualenv
virtualenv bill-env
source bill-env/bin/activate
pip install -r requirements.txt


## graphviz is a little weird 
1. library it expects the installer to be in the machine
2. So install graphviz on your machine separately, pip install is not enough for the streamlit app to run it has to be in the os package
3. https://graphviz.org/download/
4. for strealit app to be deployed you need to have the package.txt file as well but its not required for local testing




## This app uses default credential for demo purpose change the code to use service account
### service account should only have read access to billing data to avoid sql injection
gcloud auth application-default login


## To run the app do the following
streamlit run app.py


