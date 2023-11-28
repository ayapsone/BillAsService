pip install virtualenv
virtualenv bill-env
source bill-env/bin/activate
pip install -r requirements.txt


must
gcloud auth application-default login

streamlit run app.py

install graphviz on your machine separately, pip install is not enough for the streamlit app to run it has to be in the os package
