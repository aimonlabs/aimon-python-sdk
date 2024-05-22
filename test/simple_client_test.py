# Run python3 setup.py install --user
import pytest
from aimon import SimpleAimonRelyClient, Config


API_KEY = "YOUR API KEY HERE"
class TestSimpleAimonRelyClient:

    #  Sends an HTTP POST request to the Aimon Rely Hallucination Detection API with valid data and receives a valid response
    def test_valid_data_valid_response(self):
        config = Config({'hallucination': 'default'})
        client = SimpleAimonRelyClient(api_key=API_KEY, config=config)
        data_to_send = [{"context": "This is the context", "generated_text": "This is the context"}]
        response = client.detect(data_to_send)[0]
        assert "hallucination" in response
        assert "is_hallucinated" in response['hallucination']
        assert response['hallucination']["is_hallucinated"] == "False"
        assert "score" in response['hallucination']
        assert "sentences" in response['hallucination']
        assert len(response['hallucination']["sentences"]) == 1
        assert "This is the context" in response['hallucination']["sentences"][0]["text"]

    def test_valid_data_valid_response_user_query(self):
        config = Config({'hallucination': 'default'})
        client = SimpleAimonRelyClient(api_key=API_KEY, config=config)
        data_to_send = [{"context": "This is the context", "user_query": "This is the user query", "generated_text": "This is the context"}]
        response = client.detect(data_to_send)[0]
        assert "hallucination" in response
        assert "is_hallucinated" in response['hallucination']
        assert response['hallucination']["is_hallucinated"] == "False"
        assert "score" in response['hallucination']
        assert "sentences" in response['hallucination']
        assert len(response['hallucination']["sentences"]) == 1
        assert "This is the context" in response['hallucination']["sentences"][0]["text"]

    def test_valid_batch_data_valid_response(self):
        config = Config({'hallucination': 'default'})
        client = SimpleAimonRelyClient(api_key=API_KEY, config=config)
        data_to_send = [{"context": "This is the context", "generated_text": "This is the context"}, {"context": "This is the second context", "generated_text": "This is the second context"}]
        response = client.detect(data_to_send)
        for i in range(2):
            assert "hallucination" in response[i]
            assert "is_hallucinated" in response[i]['hallucination']
            assert response[i]['hallucination']["is_hallucinated"] == "False"
            assert "score" in response[i]['hallucination']
            assert "sentences" in response[i]['hallucination']
            assert len(response[i]['hallucination']["sentences"]) == 1
        assert "This is the context" in response[0]['hallucination']["sentences"][0]["text"]
        assert "This is the second context" in response[1]['hallucination']["sentences"][0]["text"]

    #  Sends an HTTP POST request to the Aimon Rely Hallucination Detection API with a single dict object containing a valid "context" and "generated_text" but with a very short text and receives a valid response
    def test_short_text_valid_response(self):
        config = Config({'hallucination': 'default'})
        client = SimpleAimonRelyClient(api_key=API_KEY, config=config)
        short_text = "Yes"
        data_to_send = [{"context": "This is the context", "generated_text": short_text}]
        response = client.detect(data_to_send)[0]
        assert "hallucination" in response
        assert "is_hallucinated" in response['hallucination']
        assert "score" in response['hallucination']
        assert response['hallucination']["score"] >= 0.48
        assert "sentences" in response['hallucination']
        assert len(response['hallucination']["sentences"]) == 1
        assert "Yes" in response['hallucination']["sentences"][0]["text"]

    #  Sends an HTTP POST request to the Aimon Rely Hallucination Detection API with a single dict object containing a valid "context" and "generated_text" but with a text containing special characters and receives a valid response
    def test_special_characters_valid_response(self):
        client = SimpleAimonRelyClient(api_key=API_KEY)
        special_text = "!@#$%^&*()_+"
        data_to_send = [{"context": "This is the context", "generated_text": special_text}]
        response = client.detect(data_to_send)[0]
        assert "hallucination" in response
        assert "is_hallucinated" in response['hallucination']
        assert response['hallucination']["is_hallucinated"] == "True"
        assert "score" in response['hallucination']
        assert response['hallucination']["score"] >= 0.5
        assert "sentences" in response['hallucination']
        assert len(response['hallucination']["sentences"]) == 1

    def test_valid_data_valid_response_conciseness(self):
        config = Config({'conciseness': 'default'})
        client = SimpleAimonRelyClient(api_key=API_KEY, config=config)
        data_to_send = [{
                            "context": "the abc have reported that those who receive centrelink payments made up half of radio rental's income last year. Centrelink payments themselves were up 20%.",
                            "generated_text": "those who receive centrelink payments made up half of radio rental's income last year. The Centrelink payments were 20% up."}]
        response = client.detect(data_to_send)[0]
        print(response["quality_metrics"])
        assert "quality_metrics" in response
        assert "results" in response["quality_metrics"]
        assert "conciseness" in response["quality_metrics"]["results"]
        assert "reasoning" in response["quality_metrics"]["results"]["conciseness"]
        assert "score" in response["quality_metrics"]["results"]["conciseness"]
        assert response["quality_metrics"]["results"]["conciseness"]["score"] >= 0.7

    def test_valid_data_valid_response_completeness(self):
        config = Config({'completeness': 'default'})
        client = SimpleAimonRelyClient(api_key=API_KEY, config=config)
        data_to_send = [{
                            "context": "the abc have reported that those who receive centrelink payments made up half of radio rental's income last year. Centrelink payments themselves were up 20%.",
                            "generated_text": "those who receive centrelink payments made up half of radio rental's income last year. The Centrelink payments were 20% up."}]
        response = client.detect(data_to_send)[0]
        assert "quality_metrics" in response
        print(response["quality_metrics"])
        assert "results" in response["quality_metrics"]
        assert "completeness" in response["quality_metrics"]["results"]
        assert "reasoning" in response["quality_metrics"]["results"]["completeness"]
        assert "score" in response["quality_metrics"]["results"]["completeness"]
        assert response["quality_metrics"]["results"]["completeness"]["score"] > 0.7

    def test_valid_data_valid_response_conciseness_completeness(self):
        config = Config({'conciseness': 'default', 'completeness': 'default'})
        client = SimpleAimonRelyClient(api_key=API_KEY, config=config)
        data_to_send = [{"context": "the abc have reported that those who receive centrelink payments made up half of radio rental's income last year. Centrelink payments themselves were up 20%.",
                         "generated_text": "those who receive centrelink payments made up half of radio rental's income last year. The Centrelink payments were 20% up."}]
        response = client.detect(data_to_send)[0]
        assert "quality_metrics" in response
        print(response["quality_metrics"])
        assert "results" in response["quality_metrics"]
        assert "completeness" in response["quality_metrics"]["results"]
        assert "reasoning" in response["quality_metrics"]["results"]["completeness"]
        assert "score" in response["quality_metrics"]["results"]["completeness"]
        assert response["quality_metrics"]["results"]["completeness"]["score"] > 0.7
        assert "quality_metrics" in response
        assert "results" in response["quality_metrics"]
        assert "conciseness" in response["quality_metrics"]["results"]
        assert "reasoning" in response["quality_metrics"]["results"]["conciseness"]
        assert "score" in response["quality_metrics"]["results"]["conciseness"]
        assert response["quality_metrics"]["results"]["conciseness"]["score"] > 0.7
