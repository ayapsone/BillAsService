# BillChat

## Streamlit App for Answering Customer Questions with Vertex AI and BigQuery

This Streamlit app utilizes Vertex AI and BigQuery to answer customer questions about billing, release notes, and diagrams. 

**Key functionalities:**

* Classifies user queries as "billing", "releasenotes", "diagram", or "other".
* Generates SQL queries based on user queries to retrieve relevant data from BigQuery.
* Leverages Vertex AI models for:
    * Code generation (billing-prompt.txt) to construct appropriate SQL queries for user questions.
    * Understanding and responding to user questions about release notes (releasenotes_agent).
* Visualizes billing data using bar charts.
* Generates architecture diagrams based on resource usage.

**Main components:**

* `process_prompt`: Main function triggered by user input. Classifies the query and invokes appropriate processing functions.
* `process_billing_prompt`: Generates SQL query based on user query and retrieves data from BigQuery. Visualizes the data using a bar chart.
* `process_releasenotes_prompt`: Uses a pre-trained model to understand the user query and respond with relevant information from the release notes dataframe.
* `process_diagram_prompt`: Generates a diagram representing the relationships between project, location, and service based on billing data.
* `design_bq_query`: Uses a code generation model to create an SQL query based on the user's query and schema information.
* `load_data`: Loads release notes data from BigQuery and initializes a pre-trained model for response generation.
* `run_query`: Executes a provided SQL query and returns the results as a dataframe.

**Overall, this app demonstrates how to combine Vertex AI and BigQuery to build a powerful and insightful customer support tool.**

**Additional Notes:**

* The app utilizes pre-trained models for billing prompt generation and release notes response generation. You may need to modify the model names and configuration based on your specific needs.
* The SQL queries used in the app are for illustrative purposes and may need to be adjusted depending on your BigQuery schema.
* The app provides a basic interface for interacting with the models and visualizing data. You can extend it further to include additional features and functionalities.



