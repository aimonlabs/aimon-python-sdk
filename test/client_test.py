# Run python3 setup.py install --user
import pytest
from aimon import Client, Config


API_KEY = "YOUR API KEY"
class TestSimpleAimonRelyClient:

    #  Sends an HTTP POST request to the Aimon Rely Hallucination Detection API with valid data and receives a valid response
    def test_valid_data_valid_response(self):
        config = Config({'hallucination': 'default'})
        client = Client(api_key=API_KEY, email="preetam@aimon.ai")
        data_to_send = [{"context": "This is the context", "generated_text": "This is the context"}]
        response = client.detect(data_to_send, config=config)[0]
        assert "hallucination" in response
        assert "is_hallucinated" in response['hallucination']
        assert response['hallucination']["is_hallucinated"] == "False"
        assert "score" in response['hallucination']
        assert "sentences" in response['hallucination']
        assert len(response['hallucination']["sentences"]) == 1
        assert "This is the context" in response['hallucination']["sentences"][0]["text"]

    def test_valid_data_valid_response_user_query(self):
        config = Config({'hallucination': 'default'})
        client = Client(api_key=API_KEY, email="preetam@aimon.ai")
        data_to_send = [{"context": "This is the context", "user_query": "This is the user query", "generated_text": "This is the context"}]
        response = client.detect(data_to_send, config=config)[0]
        assert "hallucination" in response
        assert "is_hallucinated" in response['hallucination']
        assert response['hallucination']["is_hallucinated"] == "False"
        assert "score" in response['hallucination']
        assert "sentences" in response['hallucination']
        assert len(response['hallucination']["sentences"]) == 1
        assert "This is the context" in response['hallucination']["sentences"][0]["text"]

    def test_valid_batch_data_valid_response(self):
        config = Config({'hallucination': 'default'})
        client = Client(api_key=API_KEY, email="preetam@aimon.ai")
        data_to_send = [{"context": "This is the context", "generated_text": "This is the context"}, {"context": "This is the second context", "generated_text": "This is the second context"}]
        response = client.detect(data_to_send, config=config)
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
        client = Client(api_key=API_KEY, email="preetam@aimon.ai")
        short_text = "Yes"
        data_to_send = [{"context": "This is the context", "generated_text": short_text}]
        response = client.detect(data_to_send, config=config)[0]
        assert "hallucination" in response
        assert "is_hallucinated" in response['hallucination']
        assert "score" in response['hallucination']
        assert response['hallucination']["score"] >= 0.45
        assert "sentences" in response['hallucination']
        assert len(response['hallucination']["sentences"]) == 1
        assert "Yes" in response['hallucination']["sentences"][0]["text"]

    #  Sends an HTTP POST request to the Aimon Rely Hallucination Detection API with a single dict object containing a valid "context" and "generated_text" but with a text containing special characters and receives a valid response
    def test_special_characters_valid_response(self):
        client = Client(api_key=API_KEY, email="preetam@aimon.ai")
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

    def test_valid_data_valid_response_hallucination_v0_2(self):
        config = Config({'hallucination_v0.2': 'default'})
        client = Client(api_key=API_KEY, email="preetam@aimon.ai")
        data_to_send = [{"context": "This is the context", "generated_text": "This is the context"}]
        response = client.detect(data_to_send, config=config)[0]
        assert "hallucination_v0.2" in response
        assert "is_hallucinated" in response['hallucination_v0.2']
        assert response['hallucination_v0.2']["is_hallucinated"] == "False"
        assert "score" in response['hallucination_v0.2']
        assert "sentences" in response['hallucination_v0.2']
        assert len(response['hallucination_v0.2']["sentences"]) == 1
        assert "This is the context" in response['hallucination_v0.2']["sentences"][0]["text"]

    def test_valid_data_valid_response_user_query_hallucination_v0_2(self):
        config = Config({'hallucination_v0.2': 'default'})
        client = Client(api_key=API_KEY, email="preetam@aimon.ai")
        data_to_send = [{"context": "This is the context", "user_query": "This is the user query", "generated_text": "This is the context"}]
        response = client.detect(data_to_send, config=config)[0]
        assert "hallucination_v0.2" in response
        assert "is_hallucinated" in response['hallucination_v0.2']
        # assert response['hallucination_v0.2']["is_hallucinated"] == "False"
        assert "score" in response['hallucination_v0.2']
        assert "sentences" in response['hallucination_v0.2']
        # assert len(response['hallucination_v0.2']["sentences"]) == 1
        # assert "This is the context" in response['hallucination_v0.2']["sentences"][0]["text"]

    def test_valid_batch_data_valid_response_hallucination_v0_2(self):
        config = Config({'hallucination_v0.2': 'default'})
        client = Client(api_key=API_KEY, email="preetam@aimon.ai")
        data_to_send = [{"context": "This is the context", "generated_text": "This is the context"}, {"context": "This is the second context", "generated_text": "This is the second context"}]
        response = client.detect(data_to_send, config=config)
        for i in range(2):
            assert "hallucination_v0.2" in response[i]
            assert "is_hallucinated" in response[i]['hallucination_v0.2']
            # assert response[i]['hallucination_v0.2']["is_hallucinated"] == "False"
            assert "score" in response[i]['hallucination_v0.2']
            assert "sentences" in response[i]['hallucination_v0.2']
            # assert len(response[i]['hallucination_v0.2']["sentences"]) == 1
        # assert "This is the context" in response[0]['hallucination_v0.2']["sentences"][0]["text"]
        # assert "This is the second context" in response[1]['hallucination_v0.2']["sentences"][0]["text"]

    #  Sends an HTTP POST request to the Aimon Rely Hallucination Detection API with a single dict object containing a valid "context" and "generated_text" but with a very short text and receives a valid response
    def test_short_text_valid_response_hallucination_v0_2(self):
        config = Config({'hallucination_v0.2': 'default'})
        client = Client(api_key=API_KEY, email="preetam@aimon.ai")
        short_text = "Yes"
        data_to_send = [{"context": "This is the context", "generated_text": short_text}]
        response = client.detect(data_to_send, config=config)[0]
        assert "hallucination_v0.2" in response
        assert "is_hallucinated" in response['hallucination_v0.2']
        assert "score" in response['hallucination_v0.2']
        assert 0.0 <= response['hallucination_v0.2']["score"] <= 1.0
        assert "sentences" in response['hallucination_v0.2']
        # assert len(response['hallucination_v0.2']["sentences"]) == 1
        # assert "Yes" in response['hallucination_v0.2']["sentences"][0]["text"]

    #  Sends an HTTP POST request to the Aimon Rely Hallucination Detection API with a single dict object containing a valid "context" and "generated_text" but with a text containing special characters and receives a valid response
    def test_special_characters_valid_response_hallucination_v0_2(self):
        config = Config({'hallucination_v0.2': 'default'})
        client = Client(api_key=API_KEY, email="preetam@aimon.ai")
        special_text = "!@#$%^&*()_+"
        data_to_send = [{"context": "This is the context", "generated_text": special_text}]
        response = client.detect(data_to_send, config=config)[0]
        assert "hallucination_v0.2" in response
        assert "is_hallucinated" in response['hallucination_v0.2']
        assert response['hallucination_v0.2']["is_hallucinated"] == "True"
        assert "score" in response['hallucination_v0.2']
        assert response['hallucination_v0.2']["score"] >= 0.5
        assert "sentences" in response['hallucination_v0.2']
        # assert len(response['hallucination_v0.2']["sentences"]) == 1

    def test_valid_data_valid_response_conciseness(self):
        config = Config({'conciseness': 'default'})
        client = Client(api_key=API_KEY, email="preetam@aimon.ai")
        data_to_send = [{
                            "context": "the abc have reported that those who receive centrelink payments made up half of radio rental's income last year. Centrelink payments themselves were up 20%.",
                            "generated_text": "those who receive centrelink payments made up half of radio rental's income last year. The Centrelink payments were 20% up."}]
        response = client.detect(data_to_send, config=config)[0]
        assert "conciseness" in response
        assert "reasoning" in response["conciseness"]
        assert "score" in response["conciseness"]
        assert response["conciseness"]["score"] >= 0.7

    def test_valid_data_valid_response_completeness(self):
        config = Config({'completeness': 'default'})
        client = Client(api_key=API_KEY, email="preetam@aimon.ai")
        data_to_send = [{
                            "context": "the abc have reported that those who receive centrelink payments made up half of radio rental's income last year. Centrelink payments themselves were up 20%.",
                            "generated_text": "those who receive centrelink payments made up half of radio rental's income last year. The Centrelink payments were 20% up."}]
        response = client.detect(data_to_send, config=config)[0]
        assert "completeness" in response
        assert "reasoning" in response["completeness"]
        assert "score" in response["completeness"]
        assert response["completeness"]["score"] > 0.7

    def test_valid_data_valid_response_instruction_adherence(self):
        config = Config({'instruction_adherence': 'default'})
        client = Client(api_key=API_KEY, email="preetam@aimon.ai")
        data_to_send = [{
            "context": "the abc have reported that those who receive centrelink payments made up half of radio rental's income last year. Centrelink payments themselves were up 20%.",
            "generated_text": "those who receive centrelink payments made up half of radio rental's income last year. The Centrelink payments were 20% up.",
            "instructions": "1. You are helpful chatbot. 2. You are friendly and polite. 3. The number of sentences in your response should not be more than two."
        }]
        response = client.detect(data_to_send, config=config)[0]
        assert "instruction_adherence" in response
        assert "results" in response["instruction_adherence"]
        assert len(response["instruction_adherence"]["results"]) == 3
        assert "instruction" in response["instruction_adherence"]["results"][2]
        assert "examples" in response["instruction_adherence"]["results"][2]
        assert "detailed_explanation" in response["instruction_adherence"]["results"][2]
        assert "adherence" in response["instruction_adherence"]["results"][2]
        # print(response)
        # assert response["instruction_adherence"]["results"][2]["adherence"] is True

    def test_valid_data_valid_response_conciseness_completeness(self):
        config = Config({'conciseness': 'default', 'completeness': 'default'})
        client = Client(api_key=API_KEY, email="preetam@aimon.ai")
        data_to_send = [{"context": "the abc have reported that those who receive centrelink payments made up half of radio rental's income last year. Centrelink payments themselves were up 20%.",
                         "generated_text": "those who receive centrelink payments made up half of radio rental's income last year. The Centrelink payments were 20% up."}]
        response = client.detect(data_to_send, config=config)[0]
        assert "completeness" in response
        assert "reasoning" in response["completeness"]
        assert "score" in response["completeness"]
        assert response["completeness"]["score"] > 0.7
        assert "conciseness" in response
        assert "reasoning" in response["conciseness"]
        assert "score" in response["conciseness"]
        assert response["conciseness"]["score"] > 0.7