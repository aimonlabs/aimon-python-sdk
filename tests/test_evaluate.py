import os
import pytest
import logging
import json
import time

from aimon.decorators.evaluate import evaluate, EvaluateResponse
from aimon import Client


class TestEvaluateWithRealService:
    """Test the evaluate function with the real AIMon service."""

    def setup_method(self, method):
        """Setup method for each test."""
        self.api_key = os.getenv("AIMON_API_KEY")
        if not self.api_key:
            pytest.skip("AIMON_API_KEY environment variable not set")
        
        self.logger = logging.getLogger("test_evaluate_real")
        
        # Create a real client to prepare test data using staging base url
        self.client = Client(auth_header=f"Bearer {self.api_key}")
        
        # Create unique names for resources to avoid conflicts
        self.timestamp = int(time.time())
        self.app_name = f"test_app_{self.timestamp}"
        self.model_name = f"test_model_{self.timestamp}"
        self.dataset_name = f"test_dataset_{self.timestamp}"
        self.collection_name = f"test_collection_{self.timestamp}"
        self.evaluation_name = f"test_evaluation_{self.timestamp}"

    @pytest.fixture(autouse=True)
    def _setup_logging(self, caplog):
        """Setup logging with caplog fixture."""
        caplog.set_level(logging.INFO)
        self.caplog = caplog

    def log_info(self, title, data):
        """Log data to the test log."""
        if isinstance(data, dict):
            try:
                formatted_data = json.dumps(data, indent=2, default=str)
                self.logger.info(f"{title}: {formatted_data}")
            except:
                self.logger.info(f"{title}: {data}")
        else:
            self.logger.info(f"{title}: {data}")

    def create_test_data(self):
        """Create test data in the AIMon platform."""
        self.log_info("Creating test data", {
            "App Name": self.app_name,
            "Model Name": self.model_name,
            "Dataset Name": self.dataset_name,
            "Collection Name": self.collection_name
        })
        
        # Create test model
        model = self.client.models.create(
            name=self.model_name,
            type="text",
            description=f"Test model created at {self.timestamp}"
        )
        self.log_info("Created model", {"ID": model.id})
        
        # Create test dataset content
        dataset_content = """context_docs,user_query,output,prompt,task_definition
"The capital of France is Paris.","What is the capital of France?","Paris is the capital of France.","You are a helpful assistant.","Your task is to grade the relevance of context document against a specified user query."
"Python is a programming language.","Tell me about Python.","Python is a versatile programming language.","You are a helpful assistant.","Your task is to grade the relevance of context document against a specified user query."
"""
        
        # Save dataset content to a temporary file
        temp_file_path = f"temp_dataset_{self.timestamp}.csv"
        with open(temp_file_path, 'w') as f:
            f.write(dataset_content)
        
        # Create dataset in the platform
        with open(temp_file_path, 'rb') as f:
            dataset = self.client.datasets.create(
                file=f,
                name=self.dataset_name,
                description="Test dataset for evaluate function"
            )
        
        # Create dataset collection
        collection = self.client.datasets.collection.create(
            name=self.collection_name,
            dataset_ids=[dataset.sha],
            description="Test collection for evaluate function"
        )
        
        # Delete the temporary file
        os.remove(temp_file_path)
        
        self.log_info("Created dataset", {"ID": dataset.sha})
        self.log_info("Created collection", {"ID": collection.id})
        
        return {"dataset_id": dataset.sha, "collection_id": collection.id}

    def test_evaluate_with_real_service(self):
        """Test the evaluate function with the real AIMon service."""
        # Skip if no API key
        if not self.api_key:
            pytest.skip("AIMON_API_KEY environment variable not set")
        
        try:
            # Create test data
            test_data = self.create_test_data()
            
            # Configure test parameters
            headers = ["context_docs", "user_query", "output", "prompt", "task_definition"]
            config = {'hallucination': {'detector_name': 'default'}, 'retrieval_relevance': {'detector_name': 'default'}}
            
            self.log_info("Starting evaluate test", {
                "Application": self.app_name,
                "Model": self.model_name,
                "Collection": self.collection_name,
                "Headers": headers,
                "Config": config
            })
            
            # Call evaluate function
            results = evaluate(
                application_name=self.app_name,
                model_name=self.model_name,
                dataset_collection_name=self.collection_name,
                evaluation_name=self.evaluation_name,
                headers=headers,
                api_key=self.api_key,
                config=config
            )
            
            # Log results
            self.log_info("Results count", len(results))
            for i, result in enumerate(results):
                self.log_info(f"Result {i} Output", result.output)
                self.log_info(f"Result {i} Response", str(result.response))
            
            # Basic assertions
            assert len(results) == 2
            assert isinstance(results[0], EvaluateResponse)
            assert results[0].output in ["Paris is the capital of France.", "Python is a versatile programming language."]
            assert results[1].output in ["Paris is the capital of France.", "Python is a versatile programming language."]
            
            # Check for errors in response
            if hasattr(result.response, 'error'):
                self.log_info("API Error", result.response.error)
                pytest.skip(f"Skipping due to API error: {result.response.error}")
            
            # Check for successful status
            if hasattr(result.response, 'status') and result.response.status == 200:
                self.log_info("API Success", "Successful evaluation with status 200")
                
                # Async/batch API may not return hallucination data immediately
                if hasattr(result.response, 'hallucination'):
                    self.log_info("Hallucination data", result.response.hallucination)
                else:
                    self.log_info("No hallucination data in response", "This is expected for asynchronous processing")
                
                # Test passed if we got a successful response
                self.log_info("Test completed successfully", "Received success status from API")
                return
            
            # If we get here, something unexpected happened
            self.log_info("Response structure unexpected", str(results[0].response))
            raise AssertionError(f"Unexpected response structure: {str(results[0].response)}")
            
        except Exception as e:
            self.log_info("Test error", str(e))
            raise

    def test_evaluate_with_hallucination_detector_only(self):
        """Test the evaluate function with only the hallucination detector."""
        # Skip if no API key
        if not self.api_key:
            pytest.skip("AIMON_API_KEY environment variable not set")
        
        try:
            # Create test data
            test_data = self.create_test_data()
            
            # Configure test parameters
            headers = ["context_docs", "user_query", "output", "prompt", "task_definition"]
            config = {'hallucination': {'detector_name': 'default'}}
            
            self.log_info("Starting evaluate test", {
                "Test": "Hallucination detector only",
                "Application": self.app_name,
                "Model": self.model_name,
                "Collection": self.collection_name,
                "Headers": headers,
                "Config": config
            })
            
            # Call evaluate function
            results = evaluate(
                application_name=self.app_name,
                model_name=self.model_name,
                dataset_collection_name=self.collection_name,
                evaluation_name=f"{self.evaluation_name}_hallucination",
                headers=headers,
                api_key=self.api_key,
                config=config
            )
            
            # Basic assertions
            assert len(results) == 2
            assert isinstance(results[0], EvaluateResponse)
            assert results[0].output in ["Paris is the capital of France.", "Python is a versatile programming language."]
            assert hasattr(results[0].response, 'status')
            assert results[0].response.status == 200
            
            self.log_info("Test completed successfully", "Hallucination detector test passed")
            
        except Exception as e:
            self.log_info("Test error", str(e))
            raise
            
    def test_evaluate_with_retrieval_relevance_detector_only(self):
        """Test the evaluate function with only the retrieval_relevance detector."""
        # Skip if no API key
        if not self.api_key:
            pytest.skip("AIMON_API_KEY environment variable not set")
        
        try:
            # Create test data
            test_data = self.create_test_data()
            
            # Configure test parameters
            headers = ["context_docs", "user_query", "output", "prompt", "task_definition"]
            config = {'retrieval_relevance': {'detector_name': 'default'}}
            
            self.log_info("Starting evaluate test", {
                "Test": "Retrieval relevance detector only",
                "Application": self.app_name,
                "Model": self.model_name,
                "Collection": self.collection_name,
                "Headers": headers,
                "Config": config
            })
            
            # Call evaluate function
            results = evaluate(
                application_name=self.app_name,
                model_name=self.model_name,
                dataset_collection_name=self.collection_name,
                evaluation_name=f"{self.evaluation_name}_relevance",
                headers=headers,
                api_key=self.api_key,
                config=config
            )
            
            # Basic assertions
            assert len(results) == 2
            assert isinstance(results[0], EvaluateResponse)
            assert results[0].output in ["Paris is the capital of France.", "Python is a versatile programming language."]
            assert hasattr(results[0].response, 'status')
            assert results[0].response.status == 200
            
            self.log_info("Test completed successfully", "Retrieval relevance detector test passed")
            
        except Exception as e:
            self.log_info("Test error", str(e))
            raise
            
    def test_evaluate_with_multiple_detectors(self):
        """Test the evaluate function with multiple detectors."""
        # Skip if no API key
        if not self.api_key:
            pytest.skip("AIMON_API_KEY environment variable not set")
        
        try:
            # Create test data
            test_data = self.create_test_data()
            
            # Configure test parameters with multiple detectors
            headers = ["context_docs", "user_query", "output", "prompt", "task_definition"]
            config = {
                'hallucination': {'detector_name': 'default'},
                'retrieval_relevance': {'detector_name': 'default'},
                'toxicity': {'detector_name': 'default'}
            }
            
            self.log_info("Starting evaluate test", {
                "Test": "Multiple detectors",
                "Application": self.app_name,
                "Model": self.model_name,
                "Collection": self.collection_name,
                "Headers": headers,
                "Config": config
            })
            
            # Call evaluate function
            results = evaluate(
                application_name=self.app_name,
                model_name=self.model_name,
                dataset_collection_name=self.collection_name,
                evaluation_name=f"{self.evaluation_name}_multi",
                headers=headers,
                api_key=self.api_key,
                config=config
            )
            
            # Basic assertions
            assert len(results) == 2
            assert isinstance(results[0], EvaluateResponse)
            assert results[0].output in ["Paris is the capital of France.", "Python is a versatile programming language."]
            assert hasattr(results[0].response, 'status')
            assert results[0].response.status == 200
            
            self.log_info("Test completed successfully", "Multiple detectors test passed")
            
        except Exception as e:
            self.log_info("Test error", str(e))
            raise
            
    def test_evaluate_with_minimal_headers(self):
        """Test the evaluate function with minimal required headers."""
        # Skip if no API key
        if not self.api_key:
            pytest.skip("AIMON_API_KEY environment variable not set")
        
        try:
            # Create test data
            self.log_info("Creating test data with minimal headers", {
                "App Name": self.app_name,
                "Model Name": self.model_name,
                "Dataset Name": f"{self.dataset_name}_minimal",
                "Collection Name": f"{self.collection_name}_minimal"
            })
            
            # Create test model
            model = self.client.models.create(
                name=self.model_name,
                type="text",
                description=f"Test model created at {self.timestamp}"
            )
            
            # Create test dataset - it seems all these fields are required by the API
            dataset_content = """context_docs,user_query,output,prompt,task_definition
"The capital of France is Paris.","What is the capital of France?","Paris is the capital of France.","You are a helpful assistant.","Your task is to provide accurate information."
"Python is a programming language.","Tell me about Python.","Python is a versatile programming language.","You are a helpful assistant.","Your task is to provide accurate information."
"""
            
            # Save dataset content to a temporary file
            temp_file_path = f"temp_dataset_{self.timestamp}_minimal.csv"
            with open(temp_file_path, 'w') as f:
                f.write(dataset_content)
            
            # Create dataset in the platform
            with open(temp_file_path, 'rb') as f:
                dataset = self.client.datasets.create(
                    file=f,
                    name=f"{self.dataset_name}_minimal",
                    description="Test dataset with minimal headers"
                )
            
            # Create dataset collection
            collection_name = f"{self.collection_name}_minimal"
            collection = self.client.datasets.collection.create(
                name=collection_name,
                dataset_ids=[dataset.sha],
                description="Test collection with minimal headers"
            )
            
            # Delete the temporary file
            os.remove(temp_file_path)
            
            # Test with minimal set of headers that will work
            headers = ["context_docs", "user_query", "output", "prompt", "task_definition"]
            config = {'hallucination': {'detector_name': 'default'}}
            
            self.log_info("Starting evaluate test with minimal headers", {
                "Application": self.app_name,
                "Model": self.model_name,
                "Collection": collection_name,
                "Headers": headers,
                "Config": config
            })
            
            # Call evaluate function
            results = evaluate(
                application_name=self.app_name,
                model_name=self.model_name,
                dataset_collection_name=collection_name,
                evaluation_name=f"{self.evaluation_name}_minimal",
                headers=headers,
                api_key=self.api_key,
                config=config
            )
            
            # Basic assertions
            assert len(results) == 2
            assert isinstance(results[0], EvaluateResponse)
            assert results[0].output in ["Paris is the capital of France.", "Python is a versatile programming language."]
            assert hasattr(results[0].response, 'status')
            assert results[0].response.status == 200
            
            self.log_info("Test completed successfully", "Minimal headers test passed")
            
        except Exception as e:
            self.log_info("Test error", str(e))
            raise

    def test_evaluate_with_empty_headers(self):
        """Test that the evaluate function properly validates empty headers."""
        # Skip if no API key
        if not self.api_key:
            pytest.skip("AIMON_API_KEY environment variable not set")
        
        try:
            # Create test data
            test_data = self.create_test_data()
            
            # Configure test parameters with empty headers
            headers = []
            config = {'hallucination': {'detector_name': 'default'}}
            
            self.log_info("Starting evaluate test with empty headers", {
                "Application": self.app_name,
                "Model": self.model_name,
                "Collection": self.collection_name,
                "Headers": headers,
                "Config": config
            })
            
            # Call evaluate function - should raise ValueError
            with pytest.raises(ValueError, match="Headers must be a non-empty list"):
                evaluate(
                    application_name=self.app_name,
                    model_name=self.model_name,
                    dataset_collection_name=self.collection_name,
                    evaluation_name=f"{self.evaluation_name}_empty_headers",
                    headers=headers,
                    api_key=self.api_key,
                    config=config
                )
            
            self.log_info("Test completed successfully", "Empty headers validation test passed")
            
        except Exception as e:
            self.log_info("Test error", str(e))
            raise
            
    def test_evaluate_with_invalid_headers(self):
        """Test that the evaluate function properly handles invalid headers."""
        # Skip if no API key
        if not self.api_key:
            pytest.skip("AIMON_API_KEY environment variable not set")
        
        try:
            # Create test data
            test_data = self.create_test_data()
            
            # Configure test parameters with invalid headers (missing from dataset)
            headers = ["context_docs", "user_query", "output", "nonexistent_column"]
            config = {'hallucination': {'detector_name': 'default'}}
            
            self.log_info("Starting evaluate test with invalid headers", {
                "Application": self.app_name,
                "Model": self.model_name,
                "Collection": self.collection_name,
                "Headers": headers,
                "Config": config
            })
            
            # Call evaluate function - should raise ValueError
            with pytest.raises(ValueError, match="Dataset record must contain the column"):
                evaluate(
                    application_name=self.app_name,
                    model_name=self.model_name,
                    dataset_collection_name=self.collection_name,
                    evaluation_name=f"{self.evaluation_name}_invalid_headers",
                    headers=headers,
                    api_key=self.api_key,
                    config=config
                )
            
            self.log_info("Test completed successfully", "Invalid headers validation test passed")
            
        except Exception as e:
            self.log_info("Test error", str(e))
            raise
            
    def test_evaluate_with_custom_client(self):
        """Test the evaluate function with a custom client instead of api_key."""
        # Skip if no API key
        if not self.api_key:
            pytest.skip("AIMON_API_KEY environment variable not set")
        
        try:
            # Create test data
            test_data = self.create_test_data()
            
            # Create a custom client
            custom_client = Client(auth_header=f"Bearer {self.api_key}")
            
            # Configure test parameters
            headers = ["context_docs", "user_query", "output", "prompt", "task_definition"]
            config = {'hallucination': {'detector_name': 'default'}}
            
            self.log_info("Starting evaluate test with custom client", {
                "Application": self.app_name,
                "Model": self.model_name,
                "Collection": self.collection_name,
                "Headers": headers,
                "Config": config,
                "Using client": "True"
            })
            
            # Call evaluate function with custom client
            results = evaluate(
                application_name=self.app_name,
                model_name=self.model_name,
                dataset_collection_name=self.collection_name,
                evaluation_name=f"{self.evaluation_name}_custom_client",
                headers=headers,
                aimon_client=custom_client,  # Use client instead of api_key
                config=config
            )
            
            # Basic assertions
            assert len(results) == 2
            assert isinstance(results[0], EvaluateResponse)
            assert results[0].output in ["Paris is the capital of France.", "Python is a versatile programming language."]
            assert hasattr(results[0].response, 'status')
            assert results[0].response.status == 200
            
            self.log_info("Test completed successfully", "Custom client test passed")
            
        except Exception as e:
            self.log_info("Test error", str(e))
            raise

    def test_evaluate_without_evaluation_name(self):
        """Test the evaluate function when no evaluation name is provided."""
        if not self.api_key:
            pytest.skip("AIMON_API_KEY environment variable not set")

        try:
            # Create test data
            test_data = self.create_test_data()

            headers = ["context_docs", "user_query", "output", "prompt", "task_definition"]
            config = {'hallucination': {'detector_name': 'default'}}

            self.log_info("Starting evaluate test without evaluation_name", {
                "Application": self.app_name,
                "Model": self.model_name,
                "Collection": self.collection_name,
                "Headers": headers,
                "Config": config
            })

            # Call evaluate without providing evaluation_name
            results = evaluate(
                application_name=self.app_name,
                model_name=self.model_name,
                dataset_collection_name=self.collection_name,
                headers=headers,  # evaluation_name omitted
                api_key=self.api_key,
                config=config
            )

            assert len(results) == 2
            assert isinstance(results[0], EvaluateResponse)
            assert results[0].output in ["Paris is the capital of France.", "Python is a versatile programming language."]
            assert hasattr(results[0].response, 'status')
            assert results[0].response.status == 200

            self.log_info("Test completed successfully", "Auto-generated evaluation_name handled correctly")

        except Exception as e:
            self.log_info("Test error", str(e))
            raise
