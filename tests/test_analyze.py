import os
import pytest
import logging
import time
import json
import warnings

from aimon.decorators.evaluate import AnalyzeEval, AnalyzeProd, Application, Model
from aimon import Client

class TestAnalyzeWithRealService:
    def setup_method(self, method):
        self.api_key = os.getenv("AIMON_API_KEY")
        if not self.api_key:
            pytest.skip("AIMON_API_KEY environment variable not set")
        self.logger = logging.getLogger("test_analyze_real")
        self.client = Client(auth_header=f"Bearer {self.api_key}")
        self.timestamp = int(time.time())
        self.app_name = f"test_app_analyze_{self.timestamp}"
        self.model_name = f"test_model_analyze_{self.timestamp}"
        self.dataset_name = f"test_dataset_analyze_{self.timestamp}"
        self.collection_name = f"test_collection_analyze_{self.timestamp}"
        self.evaluation_name = f"test_evaluation_analyze_{self.timestamp}"

    @pytest.fixture(autouse=True)
    def _setup_logging(self, caplog):
        caplog.set_level(logging.INFO)
        self.caplog = caplog

    def log_info(self, title, data):
        if isinstance(data, dict):
            try:
                formatted_data = json.dumps(data, indent=2, default=str)
                self.logger.info(f"{title}: {formatted_data}")
            except:
                self.logger.info(f"{title}: {data}")
        else:
            self.logger.info(f"{title}: {data}")

    def create_test_data(self, minimal_headers=False, empty=False):
        self.log_info("Creating test data", {
            "App Name": self.app_name,
            "Model Name": self.model_name,
            "Dataset Name": self.dataset_name,
            "Collection Name": self.collection_name
        })
        # Create model
        model = self.client.models.create(
            name=self.model_name,
            type="text",
            description=f"Test model created at {self.timestamp}"
        )
        # Create dataset content
        if empty:
            dataset_content = "context_docs,user_query,prompt,output\n"
        elif minimal_headers:
            dataset_content = "context_docs,user_query\n\"The capital of France is Paris.\",\"What is the capital of France?\"\n"
        else:
            dataset_content = (
                "context_docs,user_query,prompt,output\n"
                "\"The capital of France is Paris.\",\"What is the capital of France?\",\"You are a helpful assistant.\",\"Paris is the capital of France.\"\n"
                "\"Python is a programming language.\",\"Tell me about Python.\",\"You are a helpful assistant.\",\"Python is a versatile programming language.\"\n"
            )
        temp_file_path = f"temp_dataset_analyze_{self.timestamp}.csv"
        with open(temp_file_path, 'w') as f:
            f.write(dataset_content)
        with open(temp_file_path, 'rb') as f:
            dataset_args = json.dumps({
                "name": self.dataset_name,
                "description": "Test dataset for AnalyzeEval"
            })
            dataset = self.client.datasets.create(
                file=f,
                json_data=dataset_args
            )
        collection = self.client.datasets.collection.create(
            name=self.collection_name,
            dataset_ids=[dataset.sha],
            description="Test collection for AnalyzeEval"
        )
        os.remove(temp_file_path)
        self.log_info("Created dataset", {"ID": dataset.sha})
        self.log_info("Created collection", {"ID": collection.id})
        return {"dataset_id": dataset.sha, "collection_id": collection.id}

    def test_analyze_eval_with_real_service(self):
        test_data = self.create_test_data()
        headers = ["context_docs", "user_query", "prompt"]
        config = {'hallucination': {'detector_name': 'default'}}
        application = Application(name=self.app_name)
        model = Model(name=self.model_name, model_type="text")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            dec = AnalyzeEval(
                application=application,
                model=model,
                evaluation_name=self.evaluation_name,
                dataset_collection_name=self.collection_name,
                headers=headers,
                api_key=self.api_key,
                config=config
            )
            @dec
            def dummy_func(context_docs, user_query, prompt):
                return f"output: {context_docs[0]}, {user_query}, {prompt}"
            results = dummy_func()
            assert isinstance(results, list)
            assert len(results) == 2
            for output, response in results:
                assert output.startswith("output:")
                assert hasattr(response, 'status') or hasattr(response, 'hallucination')
            assert any("deprecated" in str(warn.message).lower() for warn in w)

    def test_analyze_eval_multiple_detectors(self):
        test_data = self.create_test_data()
        headers = ["context_docs", "user_query", "prompt"]
        config = {
            'hallucination': {'detector_name': 'default'},
            'toxicity': {'detector_name': 'default'}
        }
        application = Application(name=self.app_name)
        model = Model(name=self.model_name, model_type="text")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            dec = AnalyzeEval(
                application=application,
                model=model,
                evaluation_name=self.evaluation_name+"_multi",
                dataset_collection_name=self.collection_name,
                headers=headers,
                api_key=self.api_key,
                config=config
            )
            @dec
            def dummy_func(context_docs, user_query, prompt):
                return f"output: {context_docs[0]}, {user_query}, {prompt}"
            results = dummy_func()
            assert isinstance(results, list)
            assert len(results) == 2
            for output, response in results:
                assert output.startswith("output:")
                assert hasattr(response, 'status') or hasattr(response, 'hallucination')
                # Do not check for hallucination/toxicity fields, just log response
                print(f"RESPONSE: {response}")
            assert any("deprecated" in str(warn.message).lower() for warn in w)

    def test_analyze_eval_minimal_headers(self):
        test_data = self.create_test_data(minimal_headers=True)
        headers = ["context_docs", "user_query"]
        config = {'hallucination': {'detector_name': 'default'}}
        application = Application(name=self.app_name)
        model = Model(name=self.model_name, model_type="text")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            dec = AnalyzeEval(
                application=application,
                model=model,
                evaluation_name=self.evaluation_name+"_minimal",
                dataset_collection_name=self.collection_name,
                headers=headers,
                api_key=self.api_key,
                config=config
            )
            @dec
            def dummy_func(context_docs, user_query):
                return f"output: {context_docs[0]}, {user_query}"
            results = dummy_func()
            assert isinstance(results, list)
            assert len(results) == 1
            output, response = results[0]
            assert output.startswith("output:")
            assert hasattr(response, 'status') or hasattr(response, 'hallucination')
            assert any("deprecated" in str(warn.message).lower() for warn in w)

    def test_analyze_eval_missing_header_error(self):
        test_data = self.create_test_data(minimal_headers=True)
        headers = ["context_docs", "user_query", "prompt"]  # prompt missing in data
        config = {'hallucination': {'detector_name': 'default'}}
        application = Application(name=self.app_name)
        model = Model(name=self.model_name, model_type="text")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            dec = AnalyzeEval(
                application=application,
                model=model,
                evaluation_name=self.evaluation_name+"_missing",
                dataset_collection_name=self.collection_name,
                headers=headers,
                api_key=self.api_key,
                config=config
            )
            @dec
            def dummy_func(context_docs, user_query, prompt):
                return f"output: {context_docs[0]}, {user_query}, {prompt}"
            results = dummy_func()
            assert isinstance(results, list)
            assert len(results) == 1
            output, response = results[0]
            assert hasattr(response, 'status') and response.status == 400
            assert "prompt" in getattr(response, 'error', '')
            assert any("deprecated" in str(warn.message).lower() for warn in w)

    def test_analyze_prod_iterable_types(self):
        application = Application(name=self.app_name, stage="production")
        model = Model(name=self.model_name, model_type="text")
        config = {'hallucination': {'detector_name': 'default'}}
        for values in (["context", "generated_text", "user_query"], ("context", "generated_text", "user_query")):
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                dec = AnalyzeProd(
                    application=application,
                    model=model,
                    values_returned=values,
                    api_key=self.api_key,
                    config=config
                )
                @dec
                def dummy_func(context, generated_text, user_query):
                    return context, generated_text, user_query
                context = "The capital of France is Paris."
                generated_text = "Paris is the capital of France."
                user_query = "What is the capital of France?"
                result = dummy_func(context, generated_text, user_query)
                assert isinstance(result, tuple)
                assert len(result) == 4
                assert result[0] == context
                assert result[1] == generated_text
                assert result[2] == user_query
                response = result[3]
                assert hasattr(response, 'status') or hasattr(response, 'hallucination')
                assert any("deprecated" in str(warn.message).lower() for warn in w)

    def test_analyze_prod_invalid_values_returned(self):
        application = Application(name=self.app_name, stage="production")
        model = Model(name=self.model_name, model_type="text")
        with pytest.raises(ValueError, match="values_returned must be specified and be an iterable"):
            AnalyzeProd(
                application=application,
                model=model,
                values_returned=None,
                api_key=self.api_key
            )
        with pytest.raises(ValueError, match="values_returned must be specified and be an iterable"):
            AnalyzeProd(
                application=application,
                model=model,
                values_returned=123,
                api_key=self.api_key
            )

    def test_analyze_eval_empty_dataset(self):
        test_data = self.create_test_data(empty=True)
        headers = ["context_docs", "user_query", "prompt"]
        config = {'hallucination': {'detector_name': 'default'}}
        application = Application(name=self.app_name)
        model = Model(name=self.model_name, model_type="text")
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            dec = AnalyzeEval(
                application=application,
                model=model,
                evaluation_name=self.evaluation_name+"_empty",
                dataset_collection_name=self.collection_name,
                headers=headers,
                api_key=self.api_key,
                config=config
            )
            @dec
            def dummy_func(context_docs, user_query, prompt):
                return f"output: {context_docs}, {user_query}, {prompt}"
            results = dummy_func()
            assert isinstance(results, list)
            assert len(results) == 0
            assert any("deprecated" in str(warn.message).lower() for warn in w) 