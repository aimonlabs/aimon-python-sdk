import os
import pytest
import logging
import json
import time
from datetime import datetime
from aimon import Client, APIStatusError

def parse_datetime(dt_str):
    """Parse datetime string in various formats to ensure compatibility with Pydantic."""
    if not dt_str or not isinstance(dt_str, str):
        return dt_str
    try:
        # Try to parse RFC 1123 format (e.g., 'Mon, 28 Apr 2025 19:40:50 GMT')
        formats = [
            '%a, %d %b %Y %H:%M:%S GMT',  # RFC 1123 format
            '%Y-%m-%dT%H:%M:%S.%fZ',      # ISO 8601 format
            '%Y-%m-%dT%H:%M:%SZ',         # ISO 8601 without microseconds
        ]
        for fmt in formats:
            try:
                return datetime.strptime(dt_str, fmt)
            except ValueError:
                continue
        return dt_str  # Return original if parsing fails
    except Exception:
        return dt_str  # Return original on any error

class TestLowLevelAPIWithRealService:
    """Test the low-level API client functions with the real AIMon service."""

    def setup_method(self, method):
        """Setup method for each test."""
        self.api_key = os.getenv("AIMON_API_KEY")
        if not self.api_key:
            pytest.skip("AIMON_API_KEY environment variable not set")

        self.logger = logging.getLogger(f"test_low_level_{method.__name__}")
        
        # Create a real client
        self.client = Client(auth_header=f"Bearer {self.api_key}")
        
        # Create unique names for resources to avoid conflicts
        self.timestamp = int(time.time())
        self.prefix = f"test_ll_{self.timestamp}"
        self.model_name = f"{self.prefix}_model"
        self.app_name = f"{self.prefix}_app"
        self.dataset_name = f"{self.prefix}_dataset.csv"
        self.collection_name = f"{self.prefix}_collection"
        self.evaluation_name = f"{self.prefix}_evaluation"
        
        self.temp_files_to_remove = []

    def teardown_method(self, method):
        """Cleanup temporary files created during tests."""
        for file_path in self.temp_files_to_remove:
            try:
                os.remove(file_path)
                self.log_info(f"Cleaned up temporary file: {file_path}")
            except OSError as e:
                self.log_info(f"Error removing temporary file {file_path}: {e}")
        self.temp_files_to_remove.clear()


    @pytest.fixture(autouse=True)
    def _setup_logging(self, caplog):
        """Setup logging with caplog fixture."""
        caplog.set_level(logging.INFO)
        self.caplog = caplog

    def log_info(self, title, data=""):
        """Log data to the test log."""
        if isinstance(data, dict) or isinstance(data, list):
            try:
                formatted_data = json.dumps(data, indent=2, default=str)
                self.logger.info(f"{title}: {formatted_data}")
            except Exception as e:
                self.logger.info(f"{title}: {data} (JSON formatting failed: {e})")
        elif data:
            self.logger.info(f"{title}: {data}")
        else:
             self.logger.info(title)

    def create_temp_dataset_file(self, filename_suffix=""):
        """Creates a temporary CSV file for dataset upload."""
        dataset_content = """context_docs,user_query,output
"Document 1 context","Query 1","Output 1"
"Document 2 context","Query 2","Output 2"
"""
        temp_file_path = f"{self.prefix}_temp_dataset{filename_suffix}.csv"
        with open(temp_file_path, 'w') as f:
            f.write(dataset_content)
        self.temp_files_to_remove.append(temp_file_path) # Register for cleanup
        self.log_info(f"Created temporary dataset file: {temp_file_path}")
        return temp_file_path

    # --- Test Methods ---

    def test_user_validate(self):
        """Test client.users.validate with a valid API key."""
        self.log_info("Starting test: User Validate")
        try:
            validation_response = self.client.users.validate(self.api_key)
            self.log_info("Validation Response", validation_response.model_dump())
            assert validation_response.id is not None
            assert validation_response.email is not None
        except Exception as e:
            self.log_info("Test error", str(e))
            pytest.fail(f"User validation failed: {e}")
        self.log_info("Test completed successfully: User Validate")

    def test_user_validate_invalid_key(self):
        """Test client.users.validate with an invalid API key."""
        self.log_info("Starting test: User Validate Invalid Key")
        invalid_client = Client(auth_header="Bearer invalid_key")
        with pytest.raises(APIStatusError) as exc_info:
             invalid_client.users.validate("invalid_key")
        self.log_info(f"Received expected error for invalid key: {exc_info.value}")
        assert exc_info.value.status_code == 401 # Expecting Unauthorized
        self.log_info("Test completed successfully: User Validate Invalid Key")
        
    def test_model_create_retrieve_list(self):
        """Test client.models.create, retrieve, and list."""
        self.log_info("Starting test: Model Create, Retrieve, List")
        
        # Create
        try:
            create_response = self.client.models.create(
                name=self.model_name,
                type="text",
                description=f"Test model {self.timestamp}"
            )
            self.log_info("Create Response", create_response.model_dump())
            assert create_response.name == self.model_name
            model_id = create_response.id
        except Exception as e:
            self.log_info("Model creation failed", str(e))
            pytest.fail(f"Model creation failed: {e}")

        # Retrieve
        try:
            retrieve_response = self.client.models.retrieve(name=self.model_name, type="text")
            self.log_info("Retrieve Response", retrieve_response.model_dump())
            assert retrieve_response.id == model_id
            assert retrieve_response.name == self.model_name
        except Exception as e:
            self.log_info("Model retrieval failed", str(e))
            pytest.fail(f"Model retrieval failed: {e}")

        # List (and check if our model type is present)
        try:
            list_response = self.client.models.list()
            # Response is List[str] containing model type names
            self.log_info("List Response (Model Types)", list_response)
            # Check if the type we created with ('text') is in the list
            found = "text" in list_response 
            assert found, f"Model type 'text' not found in list: {list_response}"
        except Exception as e:
            self.log_info("Model listing failed", str(e))
            pytest.fail(f"Model listing failed: {e}")
            
        self.log_info("Test completed successfully: Model Create, Retrieve, List")

    def test_application_create_retrieve_delete(self):
        """Test client.applications.create, retrieve, and delete."""
        self.log_info("Starting test: Application Create, Retrieve, Delete")
        
        # Prerequisite: Create a model
        try:
             model = self.client.models.create(name=self.model_name, type="text", description=f"Prereq model {self.timestamp}")
             self.log_info(f"Prerequisite model created: {model.name} (ID: {model.id})")
        except Exception as e:
             pytest.skip(f"Skipping application test due to model creation failure: {e}")

        app_id = None
        # Create
        try:
            create_response = self.client.applications.create(
                name=self.app_name,
                model_name=self.model_name,
                stage="evaluation",
                type="qa"
            )
            self.log_info("Create Response", create_response.model_dump())
            assert create_response.name == self.app_name
            assert create_response.api_model_name == self.model_name
            app_id = create_response.id
            app_version = create_response.version
        except Exception as e:
            self.log_info("Application creation failed", str(e))
            pytest.fail(f"Application creation failed: {e}")

        # Retrieve
        try:
            retrieve_response = self.client.applications.retrieve(
                name=self.app_name, 
                stage="evaluation", 
                type="qa"
            )
            self.log_info("Retrieve Response", retrieve_response.model_dump())
            assert retrieve_response.id == app_id
            assert retrieve_response.name == self.app_name
        except Exception as e:
            self.log_info("Application retrieval failed", str(e))
            pytest.fail(f"Application retrieval failed: {e}")

        # Delete
        try:
            delete_response = self.client.applications.delete(
                name=self.app_name, 
                version=str(app_version), # API expects string version
                stage="evaluation"
            )
            self.log_info("Delete Response", delete_response.model_dump())
            assert delete_response.message == "Application deleted successfully."
        except Exception as e:
            self.log_info("Application deletion failed", str(e))
            # Don't fail the test for deletion failure, but log it. Cleanup might fail.
            self.logger.warning(f"Application deletion failed: {e}")

        # Try retrieving again to confirm deletion (should fail)
        try:
            with pytest.raises(APIStatusError) as exc_info:
                 self.client.applications.retrieve(
                     name=self.app_name,
                     stage="evaluation",
                     type="qa"
                 )
            self.log_info(f"Received expected error after delete: {exc_info.value}")
            assert exc_info.value.status_code == 404 # Expecting Not Found
        except Exception as e:
             pytest.fail(f"Unexpected error trying to retrieve deleted application: {e}")
            
        self.log_info("Test completed successfully: Application Create, Retrieve, Delete")

    def test_dataset_create_retrieve_by_name(self):
        """Test client.datasets.create and retrieve by name (list)."""
        self.log_info("Starting test: Dataset Create, Retrieve by Name")
        
        # Create temp file
        temp_file_path = self.create_temp_dataset_file()

        # Create Dataset
        created_dataset_sha = None
        try:
            with open(temp_file_path, 'rb') as f:
                dataset_args = json.dumps({
                    "name": self.dataset_name,
                    "description": f"Test dataset {self.timestamp}"
                })
                create_response = self.client.datasets.create(
                    file=f,
                    json_data=dataset_args
                )
            self.log_info("Create Response", create_response.model_dump())
            assert create_response.name == self.dataset_name
            assert create_response.sha is not None
            created_dataset_sha = create_response.sha
        except Exception as e:
            self.log_info("Dataset creation failed", str(e))
            pytest.fail(f"Dataset creation failed: {e}")

        # Retrieve by name using list(name=...)
        try:
            # Add a small delay in case creation is eventually consistent
            time.sleep(2) 
            # Call list with the required name argument
            retrieved_dataset = self.client.datasets.list(name=self.dataset_name) 
            self.log_info("Retrieve by Name (List) Response", retrieved_dataset.model_dump())
            # Assert the SHA of the retrieved dataset matches the created one
            assert retrieved_dataset.sha == created_dataset_sha 
        except Exception as e:
            self.log_info("Dataset retrieval by name (list) failed", str(e))
            pytest.fail(f"Dataset retrieval by name (list) failed: {e}")

        self.log_info("Test completed successfully: Dataset Create, Retrieve by Name")

    def test_dataset_collection_create_retrieve(self):
        """Test client.datasets.collection.create and retrieve."""
        self.log_info("Starting test: Dataset Collection Create, Retrieve")
        
        # Prerequisite: Create two datasets
        dataset_shas = []
        for i in range(2):
            temp_file_path = self.create_temp_dataset_file(filename_suffix=f"_{i}")
            dataset_base_name = f"{self.prefix}_dataset_{i}.csv"
            try:
                with open(temp_file_path, 'rb') as f:
                    dataset = self.client.datasets.create(
                        file=f,
                        name=dataset_base_name,
                        description=f"Test dataset {i}"
                    )
                    dataset_shas.append(dataset.sha)
                    self.log_info(f"Prerequisite dataset {i} created: {dataset_base_name} (SHA: {dataset.sha})")
            except Exception as e:
                pytest.skip(f"Skipping collection test due to dataset creation failure: {e}")
        
        if len(dataset_shas) < 2:
             pytest.skip("Skipping collection test as prerequisite datasets couldn't be created.")

        collection_id = None
        # Create Collection
        try:
            create_response = self.client.datasets.collection.create(
                name=self.collection_name,
                dataset_ids=dataset_shas,
                description=f"Test collection {self.timestamp}"
            )
            self.log_info("Create Response", create_response.model_dump())
            assert create_response.name == self.collection_name
            assert create_response.id is not None
            collection_id = create_response.id
        except Exception as e:
            self.log_info("Collection creation failed", str(e))
            pytest.fail(f"Collection creation failed: {e}")

        # Retrieve Collection
        try:
            # Add a small delay if needed
            time.sleep(1) 
            # Retrieve using name instead of id
            retrieve_response = self.client.datasets.collection.retrieve(name=self.collection_name) 
            self.log_info("Retrieve Response", retrieve_response.model_dump())
            assert retrieve_response.id == collection_id
            assert retrieve_response.name == self.collection_name
            assert set(retrieve_response.dataset_ids) == set(dataset_shas)
        except Exception as e:
            self.log_info("Collection retrieval failed", str(e))
            pytest.fail(f"Collection retrieval failed: {e}")

        self.log_info("Test completed successfully: Dataset Collection Create, Retrieve")

    def test_evaluation_create_retrieve(self):
        """Test client.evaluations.create and retrieve."""
        self.log_info("Starting test: Evaluation Create, Retrieve")

        # Prerequisites: model, application, dataset collection
        try:
            model = self.client.models.create(name=self.model_name, type="text", description=f"Prereq model {self.timestamp}")
            app = self.client.applications.create(name=self.app_name, model_name=model.name, stage="evaluation", type="qa")
            
            temp_file_path = self.create_temp_dataset_file()
            with open(temp_file_path, 'rb') as f:
                dataset = self.client.datasets.create(
                    file=f,
                    name=self.dataset_name,
                    description=f"Prereq dataset {self.timestamp}"
                )
            
            # Add description to collection create call
            collection = self.client.datasets.collection.create(name=self.collection_name, dataset_ids=[dataset.sha], description=f"Prereq collection {self.timestamp}") 
            self.log_info("Prerequisites created", {"model": model.id, "app": app.id, "collection": collection.id})
        except Exception as e:
            pytest.skip(f"Skipping evaluation test due to prerequisite creation failure: {e}")

        evaluation_id = None
        # Create Evaluation
        try:
            create_response = self.client.evaluations.create(
                name=self.evaluation_name,
                application_id=app.id,
                model_id=model.id,
                dataset_collection_id=collection.id
            )
            self.log_info("Create Response", create_response.model_dump())
            assert create_response.name == self.evaluation_name
            assert create_response.id is not None
            evaluation_id = create_response.id
        except Exception as e:
            self.log_info("Evaluation creation failed", str(e))
            pytest.fail(f"Evaluation creation failed: {e}")

        # Retrieve Evaluation
        try:
             # Add a small delay if needed
            time.sleep(1)
            # Retrieve using name instead of id, returns a list
            retrieve_response_list = self.client.evaluations.retrieve(name=self.evaluation_name)
            self.log_info("Retrieve Response List", retrieve_response_list)
            
            # Expecting one evaluation with this unique name
            assert isinstance(retrieve_response_list, list) and len(retrieve_response_list) == 1
            retrieved_evaluation = retrieve_response_list[0]
            
            # Log the specific evaluation object
            self.log_info("Retrieved Evaluation Object", retrieved_evaluation.model_dump())
            
            assert retrieved_evaluation.id == evaluation_id
            assert retrieved_evaluation.name == self.evaluation_name
        except Exception as e:
            self.log_info("Evaluation retrieval failed", str(e))
            pytest.fail(f"Evaluation retrieval failed: {e}")

        self.log_info("Test completed successfully: Evaluation Create, Retrieve")


    def test_evaluation_run_create(self):
        """Test client.evaluations.run.create."""
        self.log_info("Starting test: Evaluation Run Create")

        # Prerequisites: model, application, dataset collection, evaluation
        try:
            model = self.client.models.create(name=self.model_name, type="text", description=f"Prereq model {self.timestamp}")
            app = self.client.applications.create(name=self.app_name, model_name=model.name, stage="evaluation", type="qa")
            temp_file_path = self.create_temp_dataset_file()
            with open(temp_file_path, 'rb') as f:
                dataset = self.client.datasets.create(
                    file=f,
                    name=self.dataset_name,
                    description=f"Prereq dataset {self.timestamp}"
                )
            # Add description to collection create call
            collection = self.client.datasets.collection.create(name=self.collection_name, dataset_ids=[dataset.sha], description=f"Prereq collection {self.timestamp}") 
            evaluation = self.client.evaluations.create(
                name=self.evaluation_name,
                application_id=str(app.id),  # Convert to string to avoid Pydantic warnings
                model_id=str(model.id),      # Convert to string to avoid Pydantic warnings
                dataset_collection_id=str(collection.id)  # Convert to string to avoid Pydantic warnings
            )
            self.log_info("Prerequisites created", {"evaluation": evaluation.id})
        except Exception as e:
            pytest.skip(f"Skipping evaluation run test due to prerequisite creation failure: {e}")
            
        # Create Evaluation Run
        try:
            metrics_config = {'hallucination': {'detector_name': 'default'}, 'toxicity': {'detector_name': 'default'}}
            
            # Handle creation_time and completed_time if they come as string responses
            creation_time = None
            completed_time = None
            
            # When creating an evaluation run, use the helper to handle date strings
            create_response = self.client.evaluations.run.create(
                evaluation_id=str(evaluation.id),  # Convert to string to avoid Pydantic warnings
                metrics_config=metrics_config,
                creation_time=creation_time,
                completed_time=completed_time
            )
            
            # Post-process the response if needed
            if hasattr(create_response, 'creation_time') and isinstance(create_response.creation_time, str):
                create_response.creation_time = parse_datetime(create_response.creation_time)
                
            if hasattr(create_response, 'completed_time') and isinstance(create_response.completed_time, str):
                create_response.completed_time = parse_datetime(create_response.completed_time)
                
            self.log_info("Create Run Response", create_response.model_dump())
            assert create_response.evaluation_id == str(evaluation.id)  # Convert to string for comparison
            assert create_response.id is not None
            self.log_info("Create Run Response. metrics config?", create_response)
            # assert 'hallucination' in create_response.metrics_config 
        except Exception as e:
            self.log_info("Evaluation run creation failed", str(e))
            pytest.fail(f"Evaluation run creation failed: {e}")
            
        self.log_info("Test completed successfully: Evaluation Run Create")


    def test_analyze_create(self):
        """Test client.analyze.create with a basic payload."""
        self.log_info("Starting test: Analyze Create")
        
        # Prerequisites: Application (can be dev or prod)
        try:
             model = self.client.models.create(name=self.model_name, type="text", description=f"Prereq model {self.timestamp}")
             app = self.client.applications.create(name=self.app_name, model_name=model.name, stage="production", type="qa")
             self.log_info(f"Prerequisite app created: {app.name} (ID: {app.id}, Version: {app.version})")
        except Exception as e:
             pytest.skip(f"Skipping analyze test due to prerequisite creation failure: {e}")

        # Analyze Create
        try:
            analyze_payload = {
                "application_id": app.id,
                "version": app.version,
                "context_docs": ["Test context document."],
                "output": "Test output generated by LLM.",
                "user_query": "Test user query.",
                "config": {'hallucination': {'detector_name': 'default'}} # Optional config
            }
            # The analyze endpoint expects a list of payloads
            create_response = self.client.analyze.create(body=[analyze_payload]) 
            self.log_info("Analyze Create Response", create_response.model_dump())
            assert create_response.status == 200
            assert "successfully sent" in create_response.message.lower()
        except Exception as e:
            self.log_info("Analyze create failed", str(e))
            pytest.fail(f"Analyze create failed: {e}")

        self.log_info("Test completed successfully: Analyze Create")

    def test_inference_detect(self):
        """Test client.inference.detect with a basic payload."""
        self.log_info("Starting test: Inference Detect")

        # Inference Detect
        try:
            detect_payload = {
                "context": ["This is the context for the inference test."],
                "generated_text": "This is the generated text to check for issues.",
                "user_query": "What was generated?",
                "config": {
                    'hallucination': {'detector_name': 'default'},
                    'toxicity': {'detector_name': 'default'}
                }
            }
            # Pass the payload as a list to the 'body' argument
            detect_response_list = self.client.inference.detect(body=[detect_payload]) 
            
            # Log the raw response list structure
            self.log_info("Raw Inference Detect Response List", detect_response_list)
            
            # Response is a list, get the first item's result
            assert isinstance(detect_response_list, list) and len(detect_response_list) > 0
            detect_result = detect_response_list[0].result
            
            # Log the actual result object
            if hasattr(detect_result, 'model_dump'):
                 result_dict = detect_result.model_dump()
            elif isinstance(detect_result, dict):
                 result_dict = detect_result # Already a dict
            else:
                 result_dict = str(detect_result) # Fallback

            self.log_info("Inference Detect Result Object", result_dict)
            print("Inference Detect Result Object", result_dict)
            
            # Assertions on the result object
            assert hasattr(detect_result, 'hallucination')
            assert hasattr(detect_result, 'toxicity')
            assert 'score' in detect_result.hallucination
            assert 'score' in detect_result.toxicity

        except Exception as e:
            self.log_info("Inference detect failed", str(e))
            pytest.fail(f"Inference detect failed: {e}")

        self.log_info("Test completed successfully: Inference Detect") 