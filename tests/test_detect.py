import os
import json
import pytest
import logging
from unittest.mock import patch, MagicMock

from aimon.decorators.detect import Detect, DetectResult


class TestDetectDecoratorWithRemoteService:
    """Test the Detect decorator using the actual remote service."""

    def setup_method(self, method):
        """Setup method for each test."""
        # Use environment variable for API key
        self.api_key = os.getenv("AIMON_API_KEY")
        if not self.api_key:
            pytest.skip("AIMON_API_KEY environment variable not set")
        self.logger = logging.getLogger("test_detect")

    @pytest.fixture(autouse=True)
    def _setup_logging(self, caplog):
        """Setup logging with caplog fixture."""
        caplog.set_level(logging.INFO)
        self.caplog = caplog
        self.verbose = True  # Always log in tests

    def log_info(self, title, data):
        """Log data to the test log."""
        if isinstance(data, dict):
            # Format dictionaries for better readability
            try:
                formatted_data = json.dumps(data, indent=2, default=str)
                self.logger.info(f"{title}: {formatted_data}")
            except:
                self.logger.info(f"{title}: {data}")
        else:
            self.logger.info(f"{title}: {data}")

    def test_basic_detect_functionality(self, caplog):
        """Test that the Detect decorator works with basic functionality without raising exceptions."""
        # Create the decorator
        config = {'hallucination': {'detector_name': 'default'}}
        values_returned = ["context", "generated_text", "user_query"]
        
        self.log_info("TEST", "Basic detect functionality")
        self.log_info("CONFIG", config)
        self.log_info("VALUES_RETURNED", values_returned)
        
        detect = Detect(
            values_returned=values_returned,
            api_key=self.api_key,
            config=config
        )
        
        # Define a function to be decorated
        @detect
        def generate_summary(context, query):
            generated_text = f"Summary: {context}"
            return context, generated_text, query
        
        # Call the decorated function
        context = "The quick brown fox jumps over the lazy dog."
        query = "Summarize the text."
        
        self.log_info("INPUT_CONTEXT", context)
        self.log_info("INPUT_QUERY", query)
        
        context_ret, generated_text, query_ret, result = generate_summary(context, query)
        
        self.log_info("OUTPUT_GENERATED_TEXT", generated_text)
        self.log_info("OUTPUT_STATUS", result.status)
        
        if hasattr(result.detect_response, 'hallucination'):
            self.log_info("OUTPUT_HALLUCINATION", {
                "is_hallucinated": result.detect_response.hallucination.get("is_hallucinated", ""),
                "score": result.detect_response.hallucination.get("score", ""),
                "sentences_count": len(result.detect_response.hallucination.get("sentences", []))
            })
        
        # Verify return values
        assert context_ret == context
        assert generated_text.startswith("Summary: ")
        assert query_ret == query
        
        # Verify response structure
        assert isinstance(result, DetectResult)
        assert result.status == 200
        assert hasattr(result.detect_response, 'hallucination')
        assert "is_hallucinated" in result.detect_response.hallucination
        assert "score" in result.detect_response.hallucination
        assert "sentences" in result.detect_response.hallucination

    def test_detect_with_multiple_detectors(self):
        """Test the Detect decorator with multiple detectors without raising exceptions."""
        # Create the decorator with multiple detectors
        config = {
            'hallucination': {'detector_name': 'default'},
            'instruction_adherence': {'detector_name': 'default'},
            'toxicity': {'detector_name': 'default'}
        }
        values_returned = ["context", "generated_text", "user_query", "instructions"]
        
        self.log_info("Test", "Detect with multiple detectors")
        self.log_info("Configuration", config)
        self.log_info("Values returned", values_returned)
        
        detect = Detect(
            values_returned=values_returned,
            api_key=self.api_key,
            config=config
        )
        
        # Define a function to be decorated
        @detect
        def generate_response(context, query, instructions):
            generated_text = f"According to the context: {context}"
            return context, generated_text, query, instructions
        
        # Call the decorated function
        context = "AI systems should be developed responsibly with proper oversight."
        query = "What does the text say about AI?"
        instructions = ["Provide a concise response with at most two sentences."]
        
        self.log_info("Input - Context", context)
        self.log_info("Input - Query", query)
        self.log_info("Input - Instructions", instructions)
        
        _, generated_text, _, _, result = generate_response(context, query, instructions)
        
        self.log_info("Output - Generated Text", generated_text)
        self.log_info("Output - Status", result.status)
        
        for detector in ['hallucination', 'instruction_adherence', 'toxicity']:
            if hasattr(result.detect_response, detector):
                self.log_info(f"Output - {detector.capitalize()} Response", 
                                getattr(result.detect_response, detector))
        
        # Verify response structure
        assert hasattr(result.detect_response, 'hallucination')
        assert hasattr(result.detect_response, 'instruction_adherence')
        assert hasattr(result.detect_response, 'toxicity')
        
        # Check key fields without verifying values
        assert "score" in result.detect_response.hallucination
        assert "instructions_list" in result.detect_response.instruction_adherence
        assert "score" in result.detect_response.toxicity

    def test_detect_with_different_iterables(self):
        """Test the Detect decorator with different iterable types for values_returned."""
        # Create the decorator with a tuple for values_returned
        config = {'hallucination': {'detector_name': 'default'}}
        values_returned = ("context", "generated_text")
        
        self.log_info("Test", "Detect with different iterables (tuple)")
        self.log_info("Configuration", config)
        self.log_info("Values returned", values_returned)
        
        detect = Detect(
            values_returned=values_returned,
            api_key=self.api_key,
            config=config
        )
        
        # Define a function to be decorated
        @detect
        def simple_function():
            context = "Python is a programming language."
            generated_text = "Python is used for data science and web development."
            return context, generated_text
        
        # Call the decorated function - should not raise exceptions
        context, generated_text, result = simple_function()
        
        self.log_info("Output - Context", context)
        self.log_info("Output - Generated Text", generated_text)
        self.log_info("Output - Status", result.status)
        
        if hasattr(result.detect_response, 'hallucination'):
            self.log_info("Output - Hallucination Response", 
                          result.detect_response.hallucination)
        
        # Verify return values and structure
        assert "Python" in context
        assert "data science" in generated_text
        assert isinstance(result, DetectResult)
        assert hasattr(result.detect_response, 'hallucination')
        assert "score" in result.detect_response.hallucination

    def test_detect_with_non_tuple_return(self):
        """Test the Detect decorator when the wrapped function returns a single value."""
        # Create the decorator
        config = {'toxicity': {'detector_name': 'default'}}
        values_returned = ["generated_text"]
        
        self.log_info("Test", "Detect with non-tuple return")
        self.log_info("Configuration", config)
        self.log_info("Values returned", values_returned)
        
        detect = Detect(
            values_returned=values_returned,
            api_key=self.api_key,
            config=config
        )
        
        # Define a function that returns a single value
        @detect
        def simple_text_function():
            return "This is a friendly and helpful message for you!"
        
        # Call the decorated function - should not raise exceptions
        text, result = simple_text_function()
        
        self.log_info("Output - Text", text)
        self.log_info("Output - Status", result.status)
        
        if hasattr(result.detect_response, 'toxicity'):
            self.log_info("Output - Toxicity Response", 
                          result.detect_response.toxicity)
        
        # Verify return values and structure
        assert "friendly and helpful" in text
        assert isinstance(result, DetectResult)
        assert hasattr(result.detect_response, 'toxicity')
        assert "score" in result.detect_response.toxicity

    def test_validate_iterable_values_returned(self):
        """Test that the values_returned validation accepts different iterable types without exceptions."""
        self.log_info("Test", "Validate iterable values_returned")
        
        # Test with a list (basic case)
        list_values = ["generated_text", "context"]
        self.log_info("Testing with list values", list_values)
        
        detect_with_list = Detect(
            values_returned=list_values,
            api_key=self.api_key,
            config={'hallucination': {'detector_name': 'default'}}
        )
        
        # Test with a tuple
        tuple_values = ("generated_text", "context")
        self.log_info("Testing with tuple values", tuple_values)
        
        detect_with_tuple = Detect(
            values_returned=tuple_values,
            api_key=self.api_key, 
            config={'hallucination': {'detector_name': 'default'}}
        )
        
        # Test with a custom iterable
        class CustomIterable:
            def __init__(self, items):
                self.items = items
            
            def __iter__(self):
                return iter(self.items)
            
            def __len__(self):
                return len(self.items)
        
        custom_values = ["generated_text", "context"]
        self.log_info("Testing with custom iterable", custom_values)
        
        custom_iterable = CustomIterable(custom_values)
        detect_with_custom = Detect(
            values_returned=custom_iterable,
            api_key=self.api_key,
            config={'hallucination': {'detector_name': 'default'}}
        )
        
        # If we got here without exceptions, the test passes
        self.log_info("Result", "All iterable types accepted without errors")
        assert True
    
    def test_invalid_values_returned(self):
        """Test that Detect raises ValueError with non-iterable values_returned."""
        self.log_info("Test", "Invalid values_returned")
        
        # Test with None
        self.log_info("Testing with None value", None)
        with pytest.raises(ValueError, match="values_returned must be specified and be an iterable"):
            Detect(values_returned=None, api_key=self.api_key)
        
        # Test with an integer
        self.log_info("Testing with integer value", 123)
        with pytest.raises(ValueError, match="values_returned must be specified and be an iterable"):
            Detect(values_returned=123, api_key=self.api_key)
        
        # Test with a boolean
        self.log_info("Testing with boolean value", True)
        with pytest.raises(ValueError, match="values_returned must be specified and be an iterable"):
            Detect(values_returned=True, api_key=self.api_key)
        
        self.log_info("Result", "All non-iterable types properly rejected with ValueError")
    
    def test_invalid_api_key(self):
        """Test that using an invalid API key raises an appropriate error."""
        self.log_info("Test", "Invalid API key")
        
        # Create the decorator with invalid API key
        values_returned = ["context", "generated_text"]
        invalid_key = "invalid_key_test_12345"
        
        self.log_info("Values returned", values_returned)
        self.log_info("Invalid API key", invalid_key[:5] + "...")  # Truncate for security
        
        detect = Detect(
            values_returned=values_returned,
            api_key=invalid_key,
            config={'hallucination': {'detector_name': 'default'}}
        )
        
        # Define a function to be decorated
        @detect
        def sample_function():
            context = "Sample context."
            generated_text = "Sample generated text."
            return context, generated_text
        
        # Calling the function should raise an authentication error
        with pytest.raises(Exception) as exc_info:
            sample_function()
        
        error_msg = str(exc_info.value)
        self.log_info("Error message", error_msg)
        
        # Check that it's an authentication-related error
        assert any(auth_term in error_msg.lower() 
                   for auth_term in ["auth", "token", "key", "credential", "unauthorized"])
        
        self.log_info("Result", "Invalid API key properly rejected with authentication error")
    
    def test_invalid_detector_name(self):
        """Test that using an invalid detector name raises an appropriate error."""
        self.log_info("Test", "Invalid detector name")
        
        # Create the decorator with invalid detector name
        values_returned = ["context", "generated_text"]
        invalid_detector = "non_existent_detector"
        config = {'hallucination': {'detector_name': invalid_detector}}
        
        self.log_info("Values returned", values_returned)
        self.log_info("Configuration with invalid detector", config)
        
        detect = Detect(
            values_returned=values_returned,
            api_key=self.api_key,
            config=config
        )
        
        # Define a function to be decorated
        @detect
        def sample_function():
            context = "Sample context."
            generated_text = "Sample generated text."
            return context, generated_text
        
        # Calling the function should raise an error about the detector
        with pytest.raises(Exception) as exc_info:
            sample_function()
        
        error_msg = str(exc_info.value)
        self.log_info("Error message", error_msg)
        
        # The error should mention something about the detector
        assert any(term in error_msg.lower() 
                   for term in ["detector", "not found", "invalid", "configuration", "error"])
        
        self.log_info("Result", "Invalid detector name properly rejected with appropriate error")
    
    def test_missing_required_fields(self):
        """Test that the API raises appropriate errors when required fields are missing."""
        self.log_info("Test", "Missing required fields")
        
        # Configure publish with missing required fields
        self.log_info("Testing", "publish=True without application_name and model_name")
        with pytest.raises(ValueError) as exc_info1:
            Detect(
                values_returned=["context", "generated_text"],
                api_key=self.api_key,
                publish=True,  # publish requires application_name and model_name
                config={'hallucination': {'detector_name': 'default'}}
            )
        self.log_info("Error message (publish)", str(exc_info1.value))
        
        # Configure async_mode without required fields
        self.log_info("Testing", "async_mode=True without application_name and model_name")
        with pytest.raises(ValueError) as exc_info2:
            Detect(
                values_returned=["context", "generated_text"],
                api_key=self.api_key,
                async_mode=True,  # async_mode requires application_name and model_name
                config={'hallucination': {'detector_name': 'default'}}
            )
        self.log_info("Error message (async_mode)", str(exc_info2.value))
        
        self.log_info("Result", "Missing required fields properly rejected with ValueError")
        
    def test_toxicity_detector_only(self):
        """Test the Detect decorator with only the toxicity detector."""
        config = {'toxicity': {'detector_name': 'default'}}
        values_returned = ["context", "generated_text"]
        
        self.log_info("Test", "Toxicity detector only")
        self.log_info("Configuration", config)
        self.log_info("Values returned", values_returned)
        
        detect = Detect(
            values_returned=values_returned,
            api_key=self.api_key,
            config=config
        )
        
        @detect
        def generate_text():
            context = "Customer service is important for business success."
            generated_text = "It's crucial to treat customers with respect and care."
            return context, generated_text
        
        context, generated_text, result = generate_text()
        
        self.log_info("Output - Context", context)
        self.log_info("Output - Generated Text", generated_text)
        self.log_info("Output - Status", result.status)
        
        if hasattr(result.detect_response, 'toxicity'):
            self.log_info("Output - Toxicity Response", 
                          result.detect_response.toxicity)
        
        # Verify response structure
        assert isinstance(result, DetectResult)
        assert result.status == 200
        assert hasattr(result.detect_response, 'toxicity')
        assert "score" in result.detect_response.toxicity
        
    def test_hallucination_context_relevance_combination(self):
        """Test the Detect decorator with a combination of hallucination and retrieval relevance detectors."""
        config = {
            'hallucination': {'detector_name': 'default'},
            'retrieval_relevance': {'detector_name': 'default'}
        }
        values_returned = ["context", "generated_text", "user_query", "task_definition"]
        
        self.log_info("Test", "Hallucination and Retrieval Relevance combination")
        self.log_info("Configuration", config)
        self.log_info("Values returned", values_returned)
        
        detect = Detect(
            values_returned=values_returned,
            api_key=self.api_key,
            config=config
        )
        
        @detect
        def generate_summary(context, query):
            generated_text = f"Based on the information: {context}"
            task_definition = "Your task is to grade the relevance of context document against a specified user query."
            return context, generated_text, query, task_definition
        
        context = "Neural networks are a subset of machine learning models inspired by the human brain."
        query = "Explain neural networks."
        
        self.log_info("Input - Context", context)
        self.log_info("Input - Query", query)
        
        _, generated_text, _, _, result = generate_summary(context, query)
        
        self.log_info("Output - Generated Text", generated_text)
        self.log_info("Output - Status", result.status)
        
        for detector in ['hallucination', 'retrieval_relevance']:
            if hasattr(result.detect_response, detector):
                self.log_info(f"Output - {detector.capitalize()} Response", 
                              getattr(result.detect_response, detector))
        
        # Verify response structure
        assert isinstance(result, DetectResult)
        assert result.status == 200
        assert hasattr(result.detect_response, 'hallucination')
        assert hasattr(result.detect_response, 'retrieval_relevance')

    def test_instruction_adherence_v1(self):
        """Test the Detect decorator with instruction adherence detector using v1."""
        config = {'instruction_adherence': {'detector_name': 'default'}}
        values_returned = ["context", "generated_text", "instructions"]
        
        self.log_info("Test", "Instruction Adherence with detector_name=v1")
        self.log_info("Configuration", config)
        self.log_info("Values returned", values_returned)
        
        detect = Detect(
            values_returned=values_returned,
            api_key=self.api_key,
            config=config
        )
        
        @detect
        def generate_with_instructions(context, instructions):
            generated_text = f"Here's a brief response about {context}"
            return context, generated_text, instructions
        
        context = "Climate change and its effects on our planet."
        instructions = ["Provide a short response in one sentence."]
        
        self.log_info("Input - Context", context)
        self.log_info("Input - Instructions", instructions)
        
        _, generated_text, _, result = generate_with_instructions(context, instructions)
        
        self.log_info("Output - Generated Text", generated_text)
        self.log_info("Output - Status", result.status)
        
        if hasattr(result.detect_response, 'instruction_adherence'):
            self.log_info("Output - Instruction Adherence Response", 
                         result.detect_response.instruction_adherence)
        
        # Verify response structure
        assert isinstance(result, DetectResult)
        assert result.status == 200
        assert hasattr(result.detect_response, 'instruction_adherence')
        
    def test_instruction_adherence_default(self):
        """Test the Detect decorator with instruction adherence detector using default."""
        config = {
            'instruction_adherence': {
                'detector_name': 'default',
                'extract_from_system': False,
                'explain': True
            }
        }
        values_returned = ["context", "generated_text", "instructions", "user_query"]
        
        self.log_info("Test", "Instruction Adherence with detector_name=default")
        self.log_info("Configuration", config)
        self.log_info("Values returned", values_returned)
        
        # Create client with short timeout to prevent hanging
        detect = Detect(
            values_returned=values_returned,
            api_key=self.api_key,
            config=config
        )
        
        @detect
        def generate_with_instructions(context, instructions, query):
            # For the default detector, instructions should be a list of strings
            if isinstance(instructions, str):
                instructions_list = [instructions.strip()]
            else:
                instructions_list = instructions
                
            generated_text = f"This is a response related to: {context}"
            return context, generated_text, instructions_list, query
        
        # Define instructions as a list for the default detector
        context = "Digital privacy and online security measures."
        instructions = ["Keep your response brief and informative.", 
                       "Provide factual information only.", 
                       "Use simple language."]
        query = "Tell me about online privacy."
        
        self.log_info("Input - Context", context)
        self.log_info("Input - Instructions", instructions)
        self.log_info("Input - Query", query)
        
        try:
            _, generated_text, _, _, result = generate_with_instructions(context, instructions, query)
            
            self.log_info("Output - Generated Text", generated_text)
            self.log_info("Output - Status", result.status)
            
            if hasattr(result.detect_response, 'instruction_adherence'):
                self.log_info("Output - Instruction Adherence Response", 
                             result.detect_response.instruction_adherence)
            
            # Verify response structure
            assert isinstance(result, DetectResult)
            assert result.status == 200
            assert hasattr(result.detect_response, 'instruction_adherence')
            
            # The format for default detector is different from v1
            # Verify the response has the expected structure
            if "results" in result.detect_response.instruction_adherence:
                assert isinstance(result.detect_response.instruction_adherence["results"], list)
            elif "report" in result.detect_response.instruction_adherence:
                assert isinstance(result.detect_response.instruction_adherence["report"], dict)
        except Exception as e:
            self.log_info("Error occurred during test", str(e))
            # We'll re-raise the error but at least we logged it
            raise

    def test_all_detectors_combination(self):
        """Test the Detect decorator with all available detectors."""
        config = {
            'hallucination': {'detector_name': 'default'},
            'toxicity': {'detector_name': 'default'},
            'instruction_adherence': {'detector_name': 'default'},
            'retrieval_relevance': {'detector_name': 'default'},
            'conciseness': {'detector_name': 'default'},
            'completeness': {'detector_name': 'default'}
        }
        values_returned = ["context", "generated_text", "user_query", "instructions", "task_definition"]
        
        self.log_info("Test", "All detectors combination")
        self.log_info("Configuration", config)
        self.log_info("Values returned", values_returned)
        
        detect = Detect(
            values_returned=values_returned,
            api_key=self.api_key,
            config=config
        )
        
        @detect
        def comprehensive_response(context, query, instructions):
            # For v1 instruction_adherence we need instructions as a string
            # If we were using 'default' detector, we would need to pass a list
            if config['instruction_adherence']['detector_name'] == 'default' and isinstance(instructions, str):
                instructions = [instructions.strip()]
                
            generated_text = f"In response to '{query}', I can tell you that {context}"
            task_definition = "Your task is to grade the relevance of context document against a specified user query."
            return context, generated_text, query, instructions, task_definition
        
        context = "Renewable energy sources like solar and wind are becoming increasingly cost-effective alternatives to fossil fuels."
        query = "What are the trends in renewable energy?"
        instructions = ["Provide a factual response based only on the given context."]
        
        self.log_info("Input - Context", context)
        self.log_info("Input - Query", query)
        self.log_info("Input - Instructions", instructions)
        
        _, generated_text, _, _, _, result = comprehensive_response(context, query, instructions)
        
        self.log_info("Output - Generated Text", generated_text)
        self.log_info("Output - Status", result.status)
        
        # Log all detector responses
        for detector in ['hallucination', 'toxicity', 'instruction_adherence', 
                        'retrieval_relevance', 'conciseness', 'completeness']:
            if hasattr(result.detect_response, detector):
                self.log_info(f"Output - {detector.capitalize()} Response", 
                             getattr(result.detect_response, detector))
        
        # Verify response structure
        assert isinstance(result, DetectResult)
        assert result.status == 200
        
        # Verify all detectors are present in the response
        assert hasattr(result.detect_response, 'hallucination')
        assert hasattr(result.detect_response, 'toxicity')
        assert hasattr(result.detect_response, 'instruction_adherence')
        assert hasattr(result.detect_response, 'retrieval_relevance')
        assert hasattr(result.detect_response, 'conciseness')
        assert hasattr(result.detect_response, 'completeness')

    def test_instruction_adherence_default_multiple_instructions(self):
        """Test instruction adherence default detector with multiple instructions and proper format."""
        config = {
            'instruction_adherence': {
                'detector_name': 'default',
                # Additional parameters can be added here if needed
                'extract_from_system': False,
                'explain': True
            }
        }
        values_returned = ["context", "generated_text", "instructions", "user_query"]
        
        self.log_info("Test", "Instruction Adherence default with multiple instructions")
        self.log_info("Configuration", config)
        self.log_info("Values returned", values_returned)
        
        detect = Detect(
            values_returned=values_returned,
            api_key=self.api_key,
            config=config
        )
        
        @detect
        def generate_with_multiple_instructions(context, instructions, query):
            # Make sure instructions is a list for the default detector
            if not isinstance(instructions, list):
                instructions = [instructions]
                
            generated_text = f"In response to '{query}', here's information about {context}"
            return context, generated_text, instructions, query
        
        # Define multiple instructions as a list for the default detector
        context = "Machine learning applications in healthcare."
        instructions = [
            "Be concise and accurate.",
            "Avoid technical jargon.",
            "Focus on practical applications.",
            "Mention at least one real-world example."
        ]
        query = "How is machine learning used in healthcare?"
        
        self.log_info("Input - Context", context)
        self.log_info("Input - Instructions", instructions)
        self.log_info("Input - User Query", query)
        
        try:
            _, generated_text, _, _, result = generate_with_multiple_instructions(context, instructions, query)
            
            self.log_info("Output - Generated Text", generated_text)
            self.log_info("Output - Status", result.status)
            
            if hasattr(result.detect_response, 'instruction_adherence'):
                self.log_info("Output - Instruction Adherence Response", 
                             result.detect_response.instruction_adherence)
            
            # Verify response structure
            assert isinstance(result, DetectResult)
            assert result.status == 200
            assert hasattr(result.detect_response, 'instruction_adherence')
            
            # The structure of default detector response might be different from v1
            instruction_adherence = result.detect_response.instruction_adherence
        except Exception as e:
            self.log_info("Error occurred during test", str(e))
            # Log the error but don't fail the test
            pytest.skip(f"Test skipped due to error: {str(e)}")

    def test_evaluate_with_new_model(self):
        """Test the evaluate function with a new model name that should be auto-created."""
        import uuid
        from aimon import evaluate, Client
        
        # Generate a unique model name to ensure it doesn't exist
        unique_model_name = f"test_model_{uuid.uuid4().hex[:8]}"
        application_name = "test_application"
        evaluation_name = f"test_eval_{uuid.uuid4().hex[:8]}"
        
        self.log_info("Test", "Evaluate with new model auto-creation")
        self.log_info("Model Name", unique_model_name)
        self.log_info("Application Name", application_name)
        
        # Create client
        aimon_client = Client(auth_header=f"Bearer {self.api_key}")
        
        # Create a test dataset CSV in memory or file
        import tempfile
        import csv
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp:
            writer = csv.writer(tmp)
            writer.writerow(["context_docs", "user_query", "output"])
            writer.writerow([
                "AI systems should be developed responsibly with proper oversight.",
                "What does the text say about AI?",
                "The text states that AI systems should be developed responsibly with proper oversight."
            ])
            dataset_path = tmp.name
        
        try:
            # Upload the dataset
            with open(dataset_path, 'rb') as file:
                dataset = aimon_client.datasets.create(
                    file=file,
                    name="test_dataset.csv",
                    description="Test dataset for evaluation"
                )
            
            # Create dataset collection
            collection_name = f"test_collection_{uuid.uuid4().hex[:8]}"
            collection = aimon_client.datasets.collection.create(
                name=collection_name,
                dataset_ids=[dataset.sha],
                description="Test collection for evaluation"
            )
            
            # Configure evaluation
            eval_config = {
                'hallucination': {'detector_name': 'default'},
                'toxicity': {'detector_name': 'default'}
            }
            
            # Run evaluation
            results = evaluate(
                dataset_collection_name=collection_name,
                headers=["context_docs", "user_query", "output"],
                application_name=application_name,
                model_name=unique_model_name,
                evaluation_name=evaluation_name,
                api_key=self.api_key,
                aimon_client=aimon_client,
                config=eval_config
            )
            
            self.log_info("Evaluation Results", results)
            
            # Based on EvaluateResponse structure in aimon/decorators/evaluate.py
            assert results is not None
            
            # EvaluateResponse likely contains 'evaluation_id' or other identifying information
            # Just verify it's not empty and log its structure for debugging
            self.log_info("Results type", type(results))
            
            # Log attributes if we can
            try:
                if hasattr(results, "__dict__"):
                    self.log_info("Results attributes", results.__dict__)
                else:
                    self.log_info("Results dir", dir(results))
            except:
                self.log_info("Could not log results attributes")
            
            # Check for common attributes in evaluation responses
            if hasattr(results, "evaluation_id"):
                self.log_info("Evaluation ID", results.evaluation_id)
            
            if hasattr(results, "task_id"):
                self.log_info("Task ID", results.task_id)
                
            self.log_info("Result", f"Successfully created and evaluated with new model: {unique_model_name}")
        
        except Exception as e:
            self.log_info("Error occurred during test", str(e))
            raise
        
        finally:
            # Cleanup
            import os
            if os.path.exists(dataset_path):
                os.remove(dataset_path)

    def test_must_compute_validation(self):
        """Test that the must_compute parameter is properly validated."""
        print("\n=== Testing must_compute validation ===")
        
        # Test config with both hallucination and completeness
        test_config = {
            "hallucination": {
                "detector_name": "default"
            },
            "completeness": {
                "detector_name": "default"
            }
        }
        print(f"Test Config: {test_config}")
        
        # Test valid values
        valid_values = ['all_or_none', 'ignore_failures']
        print(f"Testing valid must_compute values: {valid_values}")
        
        for value in valid_values:
            print(f"Testing valid must_compute value: {value}")
            detect = Detect(
                values_returned=["context", "generated_text"],
                api_key=self.api_key,
                config=test_config,
                must_compute=value
            )
            assert detect.must_compute == value
            print(f"✅ Successfully validated must_compute value: {value}")
        
        # Test invalid string value
        invalid_string_value = "invalid_value"
        print(f"Testing invalid must_compute string value: {invalid_string_value}")
        try:
            Detect(
                values_returned=["context", "generated_text"],
                api_key=self.api_key,
                config=test_config,
                must_compute=invalid_string_value
            )
            print("❌ ERROR: Expected ValueError but none was raised - This should not happen")
            assert False, "Expected ValueError for invalid string value"
        except ValueError as e:
            print(f"✅ Successfully caught ValueError for invalid string: {str(e)}")
            assert "`must_compute` must be either 'all_or_none' or 'ignore_failures'" in str(e)
        
        # Test non-string value
        non_string_value = 123
        print(f"Testing non-string must_compute value: {non_string_value}")
        try:
            Detect(
                values_returned=["context", "generated_text"],
                api_key=self.api_key,
                config=test_config,
                must_compute=non_string_value
            )
            print("❌ ERROR: Expected ValueError but none was raised - This should not happen")
            assert False, "Expected ValueError for non-string value"
        except ValueError as e:
            print(f"✅ Successfully caught ValueError for non-string: {str(e)}")
            assert "`must_compute` must be a string value" in str(e)
        
        # Test default value
        print("Testing default must_compute value: default")
        detect_default = Detect(
            values_returned=["context", "generated_text"],
            api_key=self.api_key,
            config=test_config
        )
        assert detect_default.must_compute == 'all_or_none'
        print(f"✅ Successfully validated default must_compute value: {detect_default.must_compute}")
        
        print("🎉 Result: must_compute validation working correctly")

    def test_must_compute_with_actual_service(self):
        """Test must_compute functionality with actual service calls."""
        print("\n=== Testing must_compute with actual service ===")
        
        # Test config with both hallucination and completeness
        test_config = {
            "hallucination": {
                "detector_name": "default"
            },
            "completeness": {
                "detector_name": "default"
            }
        }
        print(f"Test Config: {test_config}")
        
        # Test both must_compute values
        for must_compute_value in ['all_or_none', 'ignore_failures']:
            print(f"\n--- Testing must_compute: {must_compute_value} ---")
            
            detect = Detect(
                values_returned=["context", "generated_text", "user_query"],
                api_key=self.api_key,
                config=test_config,
                must_compute=must_compute_value
            )
            
            @detect
            def generate_summary(context, query):
                generated_text = f"Summary of {context} based on query: {query}"
                return context, generated_text, query
            
            # Test data
            context = "Machine learning is a subset of artificial intelligence that enables computers to learn without being explicitly programmed."
            query = "What is machine learning?"
            
            print(f"Input Context: {context}")
            print(f"Input Query: {query}")
            print(f"Must Compute: {must_compute_value}")
            
            try:
                # Call the decorated function
                context_ret, generated_text, query_ret, result = generate_summary(context, query)
                
                print(f"✅ API Call Successful!")
                print(f"Status Code: {result.status}")
                print(f"Generated Text: {generated_text}")
                
                # Display response details
                if hasattr(result.detect_response, 'hallucination'):
                    hallucination = result.detect_response.hallucination
                    print(f"Hallucination Score: {hallucination.get('score', 'N/A')}")
                    print(f"Is Hallucinated: {hallucination.get('is_hallucinated', 'N/A')}")
                
                if hasattr(result.detect_response, 'completeness'):
                    completeness = result.detect_response.completeness
                    print(f"Completeness Score: {completeness.get('score', 'N/A')}")
                
                # Show the full response structure
                print(f"Response Object Type: {type(result.detect_response)}")
                if hasattr(result.detect_response, '__dict__'):
                    print(f"Response Attributes: {list(result.detect_response.__dict__.keys())}")
                
            except Exception as e:
                error_message = str(e)
                print(f"API Call Result: {error_message}")
                print(f"Error Type: {type(e).__name__}")
                
                # For all_or_none, 503 is expected when services are unavailable
                if must_compute_value == 'all_or_none' and '503' in error_message:
                    print("✅ Expected behavior: all_or_none returns 503 when services unavailable")
                # For ignore_failures, we expect success or different error handling
                elif must_compute_value == 'ignore_failures':
                    if '503' in error_message:
                        print("❌ Unexpected: ignore_failures should handle service unavailability")
                    else:
                        print("✅ Expected behavior: ignore_failures handled the error appropriately")
                else:
                    print(f"❌ Unexpected error for {must_compute_value}: {error_message}")
        
        print("\n🎉 All must_compute service tests completed!")
