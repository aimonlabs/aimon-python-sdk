# Run python3 setup.py install --user
import pytest
from aimon import Client

API_KEY = "YOUR_API_KEY"

class TestSimpleAimonRelyClient:

    def test_valid_data_valid_response(self):
        client = Client(auth_header=f"Bearer {API_KEY}")
        data_to_send = [{
            "context": "This is the context", 
            "generated_text": "This is the context", 
            "config": {'hallucination': {'detector_name': 'default'}}
        }]
        response = client.inference.detect(body=data_to_send)[0]
        assert response.hallucination is not None
        assert response.hallucination["is_hallucinated"] == "False"
        assert "score" in response.hallucination
        assert "sentences" in response.hallucination
        assert len(response.hallucination["sentences"]) == 1
        assert response.hallucination["sentences"][0]["text"] == "This is the context"

    def test_valid_data_valid_response_user_query(self):
        client = Client(auth_header=f"Bearer {API_KEY}")
        data_to_send = [{
            "context": "This is the context", 
            "user_query": "This is the user query", 
            "generated_text": "This is the context", 
            "config": {'hallucination': {'detector_name': 'default'}}
        }]
        response = client.inference.detect(body=data_to_send)[0]
        assert response.hallucination is not None
        assert response.hallucination["is_hallucinated"] == "False"
        assert "score" in response.hallucination
        assert "sentences" in response.hallucination
        assert len(response.hallucination["sentences"]) == 1
        assert response.hallucination["sentences"][0]["text"] == "This is the context"

    def test_valid_batch_data_valid_response(self):
        client = Client(auth_header=f"Bearer {API_KEY}")
        data_to_send = [
            {
                "context": "This is the context", 
                "generated_text": "This is the context", 
                "config": {'hallucination': {'detector_name': 'default'}}
            },
            {
                "context": "This is the second context", 
                "generated_text": "This is the second context", 
                "config": {'hallucination': {'detector_name': 'default'}}
            }
        ]
        response = client.inference.detect(body=data_to_send)
        for item in response:
            assert item.hallucination is not None
            assert item.hallucination["is_hallucinated"] == "False"
            assert "score" in item.hallucination
            assert "sentences" in item.hallucination
            assert len(item.hallucination["sentences"]) == 1
        assert response[0].hallucination["sentences"][0]["text"] == "This is the context"
        assert response[1].hallucination["sentences"][0]["text"] == "This is the second context"

    def test_short_text_valid_response(self):
        client = Client(auth_header=f"Bearer {API_KEY}")
        short_text = "Yes"
        data_to_send = [{
            "context": "This is the context", 
            "generated_text": short_text, 
            "config": {'hallucination': {'detector_name': 'default'}}
        }]
        response = client.inference.detect(body=data_to_send)[0]
        assert response.hallucination is not None
        assert "is_hallucinated" in response.hallucination
        assert "score" in response.hallucination
        assert response.hallucination["score"] >= 0.45
        assert "sentences" in response.hallucination
        assert len(response.hallucination["sentences"]) == 1
        assert response.hallucination["sentences"][0]["text"] == "Yes"

    def test_special_characters_valid_response(self):
        client = Client(auth_header=f"Bearer {API_KEY}")
        special_text = "!@#$%^&*()_+"
        data_to_send = [{
            "context": "This is the context", 
            "generated_text": special_text, 
            "config": {'hallucination': {'detector_name': 'default'}}
        }]
        response = client.inference.detect(body=data_to_send)[0]
        assert response.hallucination is not None
        assert response.hallucination["is_hallucinated"] == "True"
        assert "score" in response.hallucination
        assert response.hallucination["score"] >= 0.5
        assert "sentences" in response.hallucination
        assert len(response.hallucination["sentences"]) == 1

    def test_valid_data_valid_response_hallucination_v0_2(self):
        client = Client(auth_header=f"Bearer {API_KEY}")
        data_to_send = [{
            "context": "This is the context", 
            "generated_text": "This is the context", 
            "config": {'hallucination_v0.2': {'detector_name': 'default'}}
        }]
        response = client.inference.detect(body=data_to_send)[0]
        hallucination_v02 = getattr(response, 'hallucination_v0.2', None)
        assert hallucination_v02 is not None
        assert hallucination_v02["is_hallucinated"] == "False"
        assert "score" in hallucination_v02
        assert "sentences" in hallucination_v02
        assert len(hallucination_v02["sentences"]) == 1
        assert hallucination_v02["sentences"][0]["text"] == "This is the context"

    def test_valid_data_valid_response_user_query_hallucination_v0_2(self):
        client = Client(auth_header=f"Bearer {API_KEY}")
        data_to_send = [{
            "context": "This is the context", 
            "user_query": "This is the user query", 
            "generated_text": "This is the context", 
            "config": {'hallucination_v0.2': {'detector_name': 'default'}}
        }]
        response = client.inference.detect(body=data_to_send)[0]
        hallucination_v02 = getattr(response, 'hallucination_v0.2', None)
        assert hallucination_v02 is not None
        assert hallucination_v02["is_hallucinated"] == "False"
        assert "score" in hallucination_v02
        assert "sentences" in hallucination_v02
        # assert len(hallucination_v02["sentences"]) == 1
        # assert hallucination_v02["sentences"][0]["text"] == "This is the context"

    def test_valid_batch_data_valid_response_hallucination_v0_2(self):
        client = Client(auth_header=f"Bearer {API_KEY}")
        data_to_send = [
            {
                "context": "This is the context", 
                "generated_text": "This is the context", 
                "config": {'hallucination_v0.2': {'detector_name': 'default'}}
            },
            {
                "context": "This is the second context", 
                "generated_text": "This is the second context", 
                "config": {'hallucination_v0.2': {'detector_name': 'default'}}
            }
        ]
        response = client.inference.detect(body=data_to_send)
        for item in response:
            hallucination_v02 = getattr(item, 'hallucination_v0.2', None)
            assert hallucination_v02 is not None
            assert hallucination_v02["is_hallucinated"] == "False"
            assert "score" in hallucination_v02
            assert "sentences" in hallucination_v02
            # assert len(hallucination_v02["sentences"]) == 1
        # assert response[0]['hallucination_v0.2']["sentences"][0]["text"] == "This is the context"
        # assert response[1]['hallucination_v0.2']["sentences"][0]["text"] == "This is the second context"

    def test_short_text_valid_response_hallucination_v0_2(self):
        client = Client(auth_header=f"Bearer {API_KEY}")
        short_text = "Yes"
        data_to_send = [{
            "context": "This is the context", 
            "user_query": "summarization", 
            "generated_text": short_text, 
            "config": {'hallucination_v0.2': {'detector_name': 'default'}}
        }]
        response = client.inference.detect(body=data_to_send)[0]
        hallucination_v02 = getattr(response, 'hallucination_v0.2', None)
        assert hallucination_v02 is not None
        assert "score" in hallucination_v02
        assert 0.0 <= hallucination_v02["score"] <= 1.0
        assert "sentences" in hallucination_v02
        # assert len(hallucination_v02["sentences"]) == 1
        # assert hallucination_v02["sentences"][0]["text"]

    def test_special_characters_valid_response_hallucination_v0_2(self):
        client = Client(auth_header=f"Bearer {API_KEY}")
        special_text = "!@#$%^&*()_+"
        data_to_send = [{
            "context": "This is the context", 
            "user_query": "summarization", 
            "generated_text": special_text, 
            "config": {'hallucination_v0.2': {'detector_name': 'default'}}
        }]
        response = client.inference.detect(body=data_to_send)[0]
        hallucination_v02 = getattr(response, 'hallucination_v0.2', None)
        assert hallucination_v02 is not None
        assert hallucination_v02["is_hallucinated"] == "True"
        assert "score" in hallucination_v02
        assert hallucination_v02["score"] >= 0.5
        assert "sentences" in hallucination_v02
        # assert len(hallucination_v02["sentences"]) == 1

    def test_valid_data_valid_response_conciseness(self):
        client = Client(auth_header=f"Bearer {API_KEY}")
        data_to_send = [{
            "context": "the abc have reported that those who receive centrelink payments made up half of radio rental's income last year. Centrelink payments themselves were up 20%.",
            "generated_text": "those who receive centrelink payments made up half of radio rental's income last year. The Centrelink payments were 20% up.",
            "config": {'conciseness': {'detector_name': 'default'}}
        }]
        response = client.inference.detect(body=data_to_send)[0]
        assert response.conciseness is not None
        assert "reasoning" in response.conciseness
        assert "score" in response.conciseness
        assert response.conciseness["score"] >= 0.7

    def test_valid_data_valid_response_completeness(self):
        client = Client(auth_header=f"Bearer {API_KEY}")
        data_to_send = [{
            "context": "the abc have reported that those who receive centrelink payments made up half of radio rental's income last year. Centrelink payments themselves were up 20%.",
            "generated_text": "those who receive centrelink payments made up half of radio rental's income last year. The Centrelink payments were 20% up.",
            "config": {'completeness': {'detector_name': 'default'}}
        }]
        response = client.inference.detect(body=data_to_send)[0]
        assert response.completeness is not None
        assert "reasoning" in response.completeness
        assert "score" in response.completeness
        assert response.completeness["score"] > 0.7

    def test_valid_data_valid_response_instruction_adherence(self):
        client = Client(auth_header=f"Bearer {API_KEY}")
        data_to_send = [{
            "context": "the abc have reported that those who receive centrelink payments made up half of radio rental's income last year. Centrelink payments themselves were up 20%.",
            "generated_text": "those who receive centrelink payments made up half of radio rental's income last year. The Centrelink payments were 20% up.",
            "instructions": "1. You are helpful chatbot. 2. You are friendly and polite. 3. The number of sentences in your response should not be more than two.",
            "config": {'instruction_adherence': {'detector_name': 'default'}}
        }]
        response = client.inference.detect(body=data_to_send)[0]
        assert response.instruction_adherence is not None
        assert "results" in response.instruction_adherence
        assert len(response.instruction_adherence["results"]) == 3
        assert "instruction" in response.instruction_adherence["results"][2]
        assert "detailed_explanation" in response.instruction_adherence["results"][2]
        assert "adherence" in response.instruction_adherence["results"][2]
        # print(response)
        # assert response.instruction_adherence["results"][2]["adherence"] is True

    def test_valid_data_valid_response_conciseness_completeness(self):
        client = Client(auth_header=f"Bearer {API_KEY}")
        data_to_send = [{
            "context": "the abc have reported that those who receive centrelink payments made up half of radio rental's income last year. Centrelink payments themselves were up 20%.",
            "generated_text": "those who receive centrelink payments made up half of radio rental's income last year. The Centrelink payments were 20% up.",
            "config": {'conciseness': {'detector_name': 'default'}, 'completeness': {'detector_name': 'default'}}
        }]
        response = client.inference.detect(body=data_to_send)[0]
        assert response.completeness is not None
        assert "reasoning" in response.completeness
        assert "score" in response.completeness
        assert response.completeness["score"] > 0.7
        assert response.conciseness is not None
        assert "reasoning" in response.conciseness
        assert "score" in response.conciseness
        assert response.conciseness["score"] > 0.7
