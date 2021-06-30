import logging
import json
import jsonpickle
import azure.functions as func
import requests
from azure.ai.textanalytics import TextAnalyticsClient
from azure.core.credentials import AzureKeyCredential
import os

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    try:
        body = json.dumps(req.get_json())
        
    except ValueError:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )
    
    if body:
        
        result = compose_response(body)
        return func.HttpResponse(result, mimetype="application/json")
    else:
        return func.HttpResponse(
             "Invalid body",
             status_code=400
        )

def compose_response(json_data):
    values = json.loads(json_data)['values']
    
    # Prepare the Output before the loop
    results = {}
    results["values"] = []
    
    for value in values:
        output_record = transform_value(value)
        if output_record != None:
            results["values"].append(output_record)
    logging.info(results)
    return json.dumps(results, ensure_ascii=False)


def authenticate_client(key,endpoint):
    ta_credential = AzureKeyCredential(key)
    text_analytics_client = TextAnalyticsClient(
            endpoint=endpoint, 
            credential=ta_credential)
    return text_analytics_client
## Perform an operation on a record
def transform_value(value):

    subscription_key = os.environ['CognitiveServicesKey'];
    endpoint = os.environ['CognitiveServicesEndpoint'];

    client = authenticate_client(subscription_key,endpoint)
    # try:
    #     recordId = value['recordId']
    # except AssertionError  as error:
    #     return None

    # Validate the inputs
    try:         
        assert ('data' in value), "'data' field is required."
        data = value['data']        
        assert ('text' in data), "'text' field is required in 'data' object."
        
    except AssertionError  as error:
        return (
            {
             "recordId": value['recordId'],
            "errors": [ { "message": "Error:" + error.args[0] }   ]       
            })

    try:
        # documents = {"documents": [
        #     {"id": "1", "language": "en",
        #         "text": value['data']['text1']}
        # ]}    
        opinion_json = sentiment_analysis_with_opinion_mining_example(client,value['data']['text'])
       
        print(opinion_json)
        # Here you could do something more interesting with the inputs
        
        aspect_arr = []
        # for document in opinion_json:
        
        #     for sentence in document.sentences:
        #         for mined_opinion in sentence.mined_opinions:
        #             aspect = mined_opinion.aspect
        #             aspect_arr.append({'name' : aspect.text, 'sentiment' : aspect.sentiment})
        
        temp_arr = {}
        for document in opinion_json:
            print(document.sentences)
            for sentence in document.sentences:
                for mined_opinion in sentence.mined_opinions:
                    aspect = mined_opinion.aspect
                    
                    temp_arr['aspect'] = aspect.text
                    temp_arr['sentiment'] = aspect.sentiment
                    
                    for opinion in mined_opinion.opinions:
                        temp_arr['opinion'] = opinion.text
                        aspect_arr.append(temp_arr) 
                        temp_arr = {}
    
        
    except:
        return (
            {
             "recordId": value['recordId'],
            "errors": [ { "message": "Could not complete operation for record." }   ]       
            })

    return ({
        
            "recordId": value['recordId'],
            # "language":"en",
            "data": {
                "text": aspect_arr
                    }
            })

def sentiment_analysis_with_opinion_mining_example(client,text):

    documents = [text]

    result = client.analyze_sentiment(documents, show_opinion_mining=True)
    doc_result = [doc for doc in result if not doc.is_error]
    
    # positive_reviews = [doc for doc in doc_result if doc.sentiment == "positive"]
    # negative_reviews = [doc for doc in doc_result if doc.sentiment == "negative"]

    # positive_mined_opinions = []
    # mixed_mined_opinions = []
    # negative_mined_opinions = []
    
    # for document in doc_result:
    #     print("Document Sentiment: {}".format(document.sentiment))
    #     print("Overall scores: positive={0:.2f}; neutral={1:.2f}; negative={2:.2f} \n".format(
    #         document.confidence_scores.positive,
    #         document.confidence_scores.neutral,
    #         document.confidence_scores.negative,
    #     ))
    #     for sentence in document.sentences:
    #         print("Sentence: {}".format(sentence.text))
    #         print("Sentence sentiment: {}".format(sentence.sentiment))
    #         print("Sentence score:\nPositive={0:.2f}\nNeutral={1:.2f}\nNegative={2:.2f}\n".format(
    #             sentence.confidence_scores.positive,
    #             sentence.confidence_scores.neutral,
    #             sentence.confidence_scores.negative,
    #         ))
    #         for mined_opinion in sentence.mined_opinions:
    #             aspect = mined_opinion.aspect
    #             print("......'{}' aspect '{}'".format(aspect.sentiment, aspect.text))
    #             print("......Aspect score:\n......Positive={0:.2f}\n......Negative={1:.2f}\n".format(
    #                 aspect.confidence_scores.positive,
    #                 aspect.confidence_scores.negative,
    #             ))
    #             for opinion in mined_opinion.opinions:
    #                 print("......'{}' opinion '{}'".format(opinion.sentiment, opinion.text))
    #                 print("......Opinion score:\n......Positive={0:.2f}\n......Negative={1:.2f}\n".format(
    #                     opinion.confidence_scores.positive,
    #                     opinion.confidence_scores.negative,
    #                 ))
    #         print("\n")
    #     print("\n")
    # jsonstr = {"data": {"data": json.loads(jsonpickle.encode(result, unpickable=False))}}
    # print(jsonstr)
    return result