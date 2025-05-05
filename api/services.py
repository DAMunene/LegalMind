import fitz  # PyMuPDF
import docx
import json
import os
import logging
from django.conf import settings
import openai
from openai import OpenAIError
from .models import Contract, RiskAnalysis

# Configure logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Add console handler to see logs in the console
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

class ContractAnalyzer:
    def __init__(self):
        api_key = settings.OPENAI_API_KEY
        logger.info(f"OpenAI API Key loaded from settings: {'***' + api_key[-6:] if api_key else 'None'}")
        if not api_key:
            logger.error("No OpenAI API key configured!")
        openai.api_key = api_key
        self.risk_keywords = [
            "termination", "penalty", "late payment", "auto-renewal", 
            "arbitration", "dispute", "liability", "indemnity"
        ]

    def extract_text(self, file_path):
        """Extract text from PDF or DOCX file"""
        if file_path.lower().endswith('.pdf'):
            doc = fitz.open(file_path)
            text = ""
            for page in doc:
                text += page.get_text()
            return text
        elif file_path.lower().endswith('.docx'):
            doc = docx.Document(file_path)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text
        return ""

    def analyze_contract(self, contract):
        """Analyze contract text and generate risk report"""
        try:
            # Get contract file path
            file_path = contract.file.path
            if not os.path.exists(file_path):
                raise ValueError(f"Contract file not found at: {file_path}")
            
            # Extract text
            raw_text = self.extract_text(file_path)
            if not raw_text.strip():
                raise ValueError("Failed to extract text from contract file")
            
            # Analyze with OpenAI
            prompt = f"""
            Analyze this contract text and identify risky clauses.
            Focus on: {', '.join(self.risk_keywords)}
            Return JSON with:
            1. List of risky clauses with page numbers
            2. Risk score (1-10)
            3. Summary of key risks
            
            Contract text:
            {raw_text}
            """

            try:
                logger.info("Sending request to OpenAI API")
                logger.debug(f"Prompt length: {len(prompt)} characters")
                
                # Use the OpenAI client with the latest approach
                client = openai.OpenAI(api_key=openai.api_key)
                
                # Add more detailed logging of the request
                logger.debug(f"Sending request with model: gpt-3.5-turbo")
                logger.debug(f"System message: {prompt.split('Contract text:')[0]}")
                logger.debug(f"User message length: {len(prompt.split('Contract text:')[1])} characters")
                
                # Try the chat completion with a timeout
                try:
                    response = client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "You are a contract risk analysis expert."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.7,
                        timeout=30  # Add timeout to prevent hanging
                    )
                    
                    logger.info("Received response from OpenAI API")
                    logger.debug(f"Response content: {response.choices[0].message.content}")
                    
                    # Add error handling for empty response
                    content = response.choices[0].message.content.strip()
                    if not content:
                        logger.error("Empty response content from OpenAI API")
                        raise ValueError("Empty response from OpenAI API")
                        
                    # Try to parse the JSON response, handling markdown code blocks
                    try:
                        # Remove markdown code block markers if present
                        content = content.strip()
                        if content.startswith('```json') and content.endswith('```'):
                            content = content[7:-3].strip()  # Remove ```json and ```
                        
                        analysis = json.loads(content)
                        logger.debug(f"Parsed JSON response: {analysis}")
                    except json.JSONDecodeError:
                        logger.error(f"Failed to parse JSON: {content}")
                        raise ValueError(f"Invalid JSON response from OpenAI: {content}")
                    
                    # Validate required fields
                    required_fields = ['risky_clauses', 'risk_score', 'summary']
                    for field in required_fields:
                        if field not in analysis:
                            logger.error(f"Missing required field in response: {field}")
                            raise ValueError(f"Missing required field in response: {field}")
                    
                    # Create RiskAnalysis record
                    risk_analysis = RiskAnalysis.objects.create(
                        contract=contract,
                        raw_text=raw_text,
                        risky_clauses=analysis['risky_clauses'],
                        risk_score=analysis['risk_score'],
                        summary=analysis['summary']
                    )
                    
                    return risk_analysis
                    
                except Exception as e:
                    logger.error(f"Error during API call: {str(e)}")
                    raise ValueError(f"Error during API call: {str(e)}")
                    
            except OpenAIError as e:
                logger.error(f"OpenAI API Error: {str(e)}")
                raise ValueError(f"OpenAI API Error: {str(e)}")

            # Add error handling for JSON parsing
            content = response.choices[0].message.content
            if not content.strip():
                raise ValueError("Empty response from OpenAI API")
                
            analysis = json.loads(content)
            
            # Validate required fields
            required_fields = ['risky_clauses', 'risk_score', 'summary']
            for field in required_fields:
                if field not in analysis:
                    raise ValueError(f"Missing required field in response: {field}")
            
            # Create RiskAnalysis record
            risk_analysis = RiskAnalysis.objects.create(
                contract=contract,
                raw_text=raw_text,
                risky_clauses=analysis['risky_clauses'],
                risk_score=analysis['risk_score'],
                summary=analysis['summary']
            )
            
            return risk_analysis
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Failed to parse JSON response from OpenAI: {str(e)}")
        except Exception as e:
            raise ValueError(f"Error analyzing contract: {str(e)}")
