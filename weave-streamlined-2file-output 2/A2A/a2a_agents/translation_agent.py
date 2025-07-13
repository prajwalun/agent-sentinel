"""
Translation Agent following A2A protocol standards
Provides text translation services through A2A framework
"""

import asyncio
import logging
import re
from typing import Dict, Any, List
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from a2a_protocol.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class TranslationAgent(BaseAgent):
    """Translation agent for providing text translation following A2A protocol standards."""
    
    def __init__(self):
        super().__init__(
            agent_name="translation_agent",
            description="Translates text between different languages with support for multiple language pairs",
            url="http://localhost:10103/",
            version="1.0.0",
            provider="BlueGuard Security"
        )
        self._initialized = False
        self._translations = {
            "en-es": {
                "hello": "hola",
                "goodbye": "adiós",
                "thank you": "gracias",
                "please": "por favor",
                "yes": "sí",
                "no": "no"
            },
            "es-en": {
                "hola": "hello",
                "adiós": "goodbye",
                "gracias": "thank you",
                "por favor": "please",
                "sí": "yes",
                "no": "no"
            },
            "en-fr": {
                "hello": "bonjour",
                "goodbye": "au revoir",
                "thank you": "merci",
                "please": "s'il vous plaît",
                "yes": "oui",
                "no": "non"
            },
            "fr-en": {
                "bonjour": "hello",
                "au revoir": "goodbye",
                "merci": "thank you",
                "s'il vous plaît": "please",
                "oui": "yes",
                "non": "no"
            }
        }
        logger.info(f"TranslationAgent initialized: {self.agent_name}")
    
    async def initialize(self) -> None:
        """Initialize the translation agent."""
        if not self._initialized:
            self._initialized = True
            logger.info(f"TranslationAgent {self.agent_name} initialized")
    
    async def invoke(self, query: str, session_id: str) -> Dict[str, Any]:
        """Invoke the translation agent with a query."""
        await self.initialize()
        
        # Parse the query to extract text and language information
        text, source_lang, target_lang = self._parse_translation_query(query)
        
        if not text:
            return {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': "Please provide text to translate and specify source and target languages",
                'error': True
            }
        
        if not source_lang or not target_lang:
            return {
                'response_type': 'text',
                'is_task_complete': True,
                'require_user_input': False,
                'content': "Please specify both source and target languages",
                'error': True
            }
        
        # Perform translation
        translated_text = self._translate_text(text, source_lang, target_lang)
        
        return {
            'response_type': 'data',
            'is_task_complete': True,
            'require_user_input': False,
            'content': translated_text,
            'original_text': text,
            'source_language': source_lang,
            'target_language': target_lang,
            'translated_text': translated_text
        }
    
    async def stream(self, query: str, context_id: str, task_id: str):
        """Stream response from the translation agent."""
        await self.initialize()
        
        # First yield a processing message
        yield {
            'is_task_complete': False,
            'require_user_input': False,
            'content': f'{self.agent_name}: Processing translation...',
        }
        
        # Process the query
        result = await self.invoke(query, f"{context_id}_{task_id}")
        
        # Yield the final result
        yield result
    
    def get_skills(self) -> List[Dict[str, Any]]:
        """Get the skills/capabilities of this agent."""
        return [
            {
                "id": "text_translation",
                "name": "Text Translation",
                "description": "Translates text from one language to another with high accuracy",
                "tags": [
                    "translation",
                    "language",
                    "multilingual",
                    "localization",
                    "interpretation"
                ],
                "examples": [
                    "Translate 'Hello world' from English to Spanish",
                    "Convert 'Bonjour' from French to English",
                    "Translate this text to German"
                ],
                "inputModes": None,
                "outputModes": None
            }
        ]
    
    def _parse_translation_query(self, query: str) -> tuple:
        """Parse translation query to extract text and language information."""
        query_lower = query.lower()
        
        # Language codes
        languages = {
            "english": "en", "en": "en",
            "spanish": "es", "es": "es", "español": "es",
            "french": "fr", "fr": "fr", "français": "fr",
            "german": "de", "de": "de", "deutsch": "de",
            "italian": "it", "it": "it", "italiano": "it"
        }
        
        # Extract text in quotes
        text_match = re.search(r'"([^"]+)"', query)
        if not text_match:
            text_match = re.search(r"'([^']+)'", query)
        
        text = text_match.group(1) if text_match else ""
        
        # Extract source and target languages
        source_lang = None
        target_lang = None
        
        # Look for "from X to Y" pattern
        from_match = re.search(r'from\s+(\w+)', query_lower)
        to_match = re.search(r'to\s+(\w+)', query_lower)
        
        if from_match:
            source_lang = languages.get(from_match.group(1), from_match.group(1))
        if to_match:
            target_lang = languages.get(to_match.group(1), to_match.group(1))
        
        return text, source_lang, target_lang
    
    def _translate_text(self, text: str, source_lang: str, target_lang: str) -> str:
        """Translate text from source language to target language."""
        lang_pair = f"{source_lang}-{target_lang}"
        
        if lang_pair in self._translations:
            # Use predefined translations
            translation_dict = self._translations[lang_pair]
            text_lower = text.lower()
            
            if text_lower in translation_dict:
                return translation_dict[text_lower]
        
        # For unknown translations, return a mock translation
        return f"[{target_lang.upper()}] {text}" 