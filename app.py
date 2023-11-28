import streamlit as st
import os
from langchain.llms import VertexAI
from google.cloud import bigquery
import pandas as pd
import logging
from langchain_experimental.agents.agent_toolkits import create_pandas_dataframe_agent
from langchain.agents.agent_types import AgentType
from vertexai.language_models import TextGenerationModel

from langchain.schema.output_parser import StrOutputParser
from langchain.prompts import PromptTemplate
from diagrams import Cluster, Diagram
import uuid
from PIL import Image

import graphviz as pgv

st.session_state.project_id='ayyappan-gke'; #os.environ['GOOGLE_CLOUD_PROJECT']
df = pd.DataFrame()

#main invoke
def process_prompt():

    llm = VertexAI(
    model_name="text-bison@001",
    max_output_tokens=256,
    temperature=0.1,
    top_p=0.8,
    top_k=40,
    verbose=True,
    )

    template = """
    Given the user question below, classify it as either being about `billing`, `releasenotes`, 'diagram' or `other`.
    {query}

    Respond in one word
    """

    prompt = PromptTemplate(
        input_variables=["location"],
        template=template,
    )

    final_prompt = prompt.format(query=st.session_state.user_query)

    output =llm(final_prompt)

    if output == "billing":
        process_billing_prompt()
    elif output == "releasenotes":
        process_releasenotes_prompt()
    elif output == "diagram":
        process_diagram_prompt()
    else:
        st.chat_message("assistant").write("Sorry, I don't understand.")

#architecture diagram related
def process_diagram_prompt():
    print("diagram")
    sql=design_bq_query();
    st.chat_message("assistant").write("Here are the results:")
    data=run_query(sql);
  

    g = pgv.Graph(format='png', node_attr={'style':'rounded','shape':'record','image': 'cloud_generic.png','fixedsize':'false'}, 
                  edge_attr={'style':'invis'})
    

    # Group the DataFrame by 'col1' and 'col2'
    grouped_df = data.groupby(['project', 'location'])
  
    # Iterate over the groups
    for name, group in grouped_df:
        service = group['service'].unique()
        #print(name[0], name[1])
        with g.subgraph(name=f'cluster_{name[0]}'.lower()) as proj:
            proj.attr(style='rounded', color='lightgrey',label=name[0])
            with proj.subgraph(name=f'cluster_{name[1]}'.lower()) as loc:
                loc.attr(style='rounded', color='lightblue',label=name[1])
                locList=[]
                for s in service:
                    locHex =f'{uuid.uuid4().hex}'
                    loc.node(locHex, label=f'{s}')
                    locList.append(locHex)
                
                pos=0
                if(len(locList)>1):
                    while pos < len(locList) - 1:
                        g.edge(locList[pos],locList[pos+1])
                        pos = pos+1


    filename=f'gcp_relationships{uuid.uuid4().hex}'
    g.render(filename)
    image = Image.open(filename+'.png')
    st.image(image,caption='Enterprise Architecture Diagram based on usage')
    os.remove(filename)
    os.remove(filename+'.png')
    

def design_bq_query():
    user_query = st.session_state.user_query
    st.chat_message("user").write(user_query)
    dataset = 'billingexport' #os.environ['BILLING_DATASET']
    table = 'gcp_billing_export_v1_0127B5_2FBACD_34F0C6'  #os.environ['BILLING_TABLE']
    billing_uri=f"{dataset}.{table}"
    logging.error(user_query)

    with open("billing-schema.json", "r") as f:
        schema = f.read()

    #Lets few shot example model to help construct the query correctly to avoid unnest errors
    with open("billing-prompt.txt", "r") as f:
        prompt = f.read()
    
    template = prompt.format(schema=schema, question=user_query, dataset=billing_uri)

    #using Codey for Code Generation ( code-bison ) is the name of the model that supports code generation from Google
    #https://cloud.google.com/vertex-ai/docs/generative-ai/model-reference/code-generation
    llm = VertexAI(model_name="code-bison", max_output_tokens=2048)

    # in case it decides to spit out markdown-formatted SQL instead of straight SQL
    sql = llm(prompt = template).replace("```", "").replace("sql", "")
    return sql
    
#billing related 
def process_billing_prompt():
    
    # generate query from user text format request
    sql =design_bq_query()
    # st.chat_message("assistant").write("Running the following query... \n```\n{}\n```".format(sql))

    # run the query and display the results
    st.chat_message("assistant").write("Here are the results:")
    #st.write();
    rows=run_query(sql)
    if 'month' in rows.columns:
        rows.set_index('month', inplace=True)
    if 'day' in rows.columns:
        rows.set_index('day', inplace=True)
    if 'year' in rows.columns:
        rows.set_index('year', inplace=True)
    st.bar_chart(rows)


def load_data():
    
    llm = VertexAI()

    # Load release notes from a public dataset from BigQuery to dataframe
    sql = """
        SELECT release_note_type, product_name,product_version_name,
        published_at,description FROM `bigquery-public-data.google_cloud_release_notes.release_notes`
    """
    #change to run_query(bq_query)
    client = bigquery.Client(st.session_state.project_id)
    st.session_state.releasenotes_df = client.query(sql).to_dataframe()

    st.session_state.releasenotes_agent = create_pandas_dataframe_agent(
        llm,
        st.session_state.releasenotes_df,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,   # "zero-shot-react-description",
        verbose=False,
        handle_parsing_errors=True)
        #return_intermediate_steps=True)


def process_releasenotes_prompt():
    st.chat_message("user").write(st.session_state.user_query)
    print(st.session_state.releasenotes_df)
    #as a paragraph no longer than 10 lines
    query = f' {st.session_state.user_query}'

    try:
        st.chat_message("assistant").write(st.session_state.releasenotes_agent.run(query))
    except Exception as e:
        st.chat_message("assistant").write(e)


# Run the BQ query
def run_query(bq_query):
    res = []

    # Perform a query.
    # remove the unformatted quote from the query
    query = bq_query.replace('`', '')
    if 'SELECT' not in query:
        # if the result was not a query, send it back to the customer - it's probably already what they asked for
        rows = [query]
    else:
        try:
            client = bigquery.Client(st.session_state.project_id)
            query_job = client.query(query)
            logging.error(query)
            rows = query_job.to_dataframe()
        except Exception as e:
            logging.error(e)
            rows = pd.DataFrame({'Error message': e},index=[0])
   
    return rows


#load data
load_data()

user_query = st.chat_input("How can I help you", on_submit=process_prompt, key="user_query")