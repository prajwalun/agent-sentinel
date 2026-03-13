"""
Research Service for Agent Sentinel Intelligence Layer.

Provides web research capabilities using Exa.ai for threat intelligence gathering.
"""

import os
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

from models.config import ResearchConfig

logger = logging.getLogger(__name__)


@dataclass
class ResearchResult:
    """Result from web research."""
    
    query: str
    results: List[Dict[str, Any]]
    metadata: Dict[str, Any]
    timestamp: str


class ResearchService:
    """Service for web research capabilities."""
    
    def __init__(self, config: ResearchConfig):
        """
        Initialize the research service.
        
        Args:
            config: Research configuration
        """
        self.config = config
        self.exa_client = None
        
        if config.enabled:
            self._initialize_exa()
    
    def _initialize_exa(self):
        """Initialize Exa.ai client."""
        try:
            from exa_py import Exa
            
            api_key = os.getenv("EXA_API_KEY")
            if not api_key:
                logger.warning("⚠️  EXA_API_KEY not found, research capabilities disabled")
                return
            
            self.exa_client = Exa(api_key=api_key)
            logger.info("Exa.ai client initialized")
            
        except ImportError:
            logger.warning("⚠️  Exa.ai not available. Install with: pip install exa-py")
        except Exception as e:
            logger.warning(f"⚠️  Exa.ai initialization failed: {e}")
    
    def search(
        self, 
        query: str, 
        num_results: int = 5,
        include_domains: Optional[List[str]] = None,
        exclude_domains: Optional[List[str]] = None
    ) -> Optional[ResearchResult]:
        """
        Perform web search using Exa.ai.
        
        Args:
            query: Search query
            num_results: Number of results to return
            include_domains: Domains to include in search
            exclude_domains: Domains to exclude from search
            
        Returns:
            Research result or None if research is disabled
        """
        if not self.exa_client:
            logger.warning("⚠️  Research service not available")
            return None
        
        if not self.config.enabled:
            logger.info("ℹ️  Research disabled by configuration")
            return None
        
        try:
            # Prepare search parameters
            search_params = {
                "query": query,
                "num_results": min(num_results, self.config.max_research_queries),
                "use_autoprompt": True,
                "type": "keyword"
            }
            
            if include_domains:
                search_params["include_domains"] = include_domains
            
            if exclude_domains:
                search_params["exclude_domains"] = exclude_domains
            
            # Perform search
            response = self.exa_client.search(**search_params)
            
            # Extract results
            results = []
            for result in response.results:
                results.append({
                    "title": result.title,
                    "url": result.url,
                    "text": result.text,
                    "published_date": result.published_date,
                    "author": result.author
                })
            
            # Create research result
            research_result = ResearchResult(
                query=query,
                results=results,
                metadata={
                    "total_results": len(results),
                    "search_params": search_params
                },
                timestamp=str(response.search_id) if hasattr(response, 'search_id') else ""
            )
            
            logger.info("Research completed for query: %s", query)
            return research_result
            
        except Exception as e:
            logger.error("Research failed for query '%s': %s", query, e)
            return None
    
    def search_threat_intelligence(self, threat_type: str, technique: str) -> Optional[ResearchResult]:
        """
        Search for threat intelligence information.
        
        Args:
            threat_type: Type of threat (e.g., "SQL injection", "XSS")
            technique: Specific technique used
            
        Returns:
            Research result with threat intelligence
        """
        query = f"{threat_type} {technique} attack technique CVE vulnerability"
        
        # Include security-focused domains
        include_domains = [
            "cve.mitre.org",
            "nvd.nist.gov", 
            "attack.mitre.org",
            "owasp.org",
            "security.stackexchange.com",
            "sans.org"
        ]
        
        return self.search(query, num_results=5, include_domains=include_domains)
    
    def search_attack_patterns(self, attack_pattern: str) -> Optional[ResearchResult]:
        """
        Search for attack patterns and techniques.
        
        Args:
            attack_pattern: Attack pattern to search for
            
        Returns:
            Research result with attack pattern information
        """
        query = f"{attack_pattern} attack pattern technique analysis"
        
        return self.search(query, num_results=3)
    
    def is_available(self) -> bool:
        """Check if research service is available."""
        return self.exa_client is not None and self.config.enabled 