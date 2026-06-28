import re
from typing import List, Dict, Any, Tuple

class KnowledgeGraphExtractor:
    """Entity and relationship extraction pipeline from text for Knowledge Graphs."""
    
    # Custom rule-based entity type pattern dictionary
    ENTITY_PATTERNS = {
        "PRODUCT": [
            r"\b(?:AI Sales Copilot|Enterprise Next Best Action Platform|SalesCopilot|SalesForce|HubSpot|ChromaDB|Gemini|Ollama)\b",
            r"\b[A-Z][a-zA-Z0-9_]{2,15}\s+(?:Platform|SaaS|Suite|API|Database|Engine|Optimizer|Cloud)\b"
        ],
        "COMPETITOR": [
            r"\b(?:Gong\.io|Chorus\.ai|Salesloft|Outreach|Clari)\b"
        ],
        "TECHNOLOGY": [
            r"\b(?:LangGraph|LangChain|FastAPI|PostgreSQL|Sqlite|Redis|Celery|Chroma|Vector\s+DB|BM25|RRF|CrossEncoder|BERT|GPT-4|LLM|RAG)\b"
        ],
        "ORGANIZATION": [
            r"\b(?:Google|DeepMind|Microsoft|OpenAI|Anthropic|Meta|Salesforce|Hubspot|Oracle|SAP)\b",
            r"\b[A-Z][a-zA-Z0-9_&]{2,15}\s+(?:Corp|Corp\.|Inc\.|LLC|Ltd|Ltd\.|Co\.|Company|Group)\b"
        ],
        "ROLE_OR_PERSON": [
            r"\b(?:Sales Rep|Manager|VP|Director|Executive|Account Executive|SDR|BDR|CEO|CTO|Developer|Principal AI Engineer)\b"
        ]
    }
    
    # Simple semantic verb patterns for relationships
    RELATION_VERBS = [
        ("competes with", r"\b(?:competes with|rivals|is a competitor to|competing against)\b"),
        ("uses", r"\b(?:uses|utilizes|built on|built with|runs on|implements|employs)\b"),
        ("features", r"\b(?:features|provides|offers|includes|delivers|supports)\b"),
        ("works for", r"\b(?:works for|employed by|hired by|leads the team at)\b"),
        ("manages", r"\b(?:manages|directs|controls|supervises|leads)\b"),
        ("integrates with", r"\b(?:integrates with|connects to|interacts with|talks to)\b"),
        ("is a product of", r"\b(?:is a product of|developed by|made by|owned by|sold by)\b")
    ]

    def extract(self, text: str) -> Dict[str, Any]:
        """Extract entities and relationships from text."""
        entities = self._extract_entities(text)
        relations = self._extract_relations(text, entities)
        
        return {
            "entities": entities,
            "relations": relations
        }

    def _extract_entities(self, text: str) -> List[Dict[str, Any]]:
        extracted = []
        seen = set()
        
        for ent_type, patterns in self.ENTITY_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    ent_name = match.group(0).strip()
                    # Resolve casing standardly
                    key = (ent_name.lower(), ent_type)
                    if key not in seen:
                        seen.add(key)
                        # Estimate confidence based on exact matches vs regex matches
                        extracted.append({
                            "name": ent_name,
                            "type": ent_type,
                            "confidence": 0.85 if ent_name[0].isupper() else 0.6
                        })
                        
        # Basic fallback for capitalized nouns if none found
        if not extracted:
            nouns = re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b", text)
            for noun in set(nouns):
                if len(noun) > 3 and noun.lower() not in {"this", "that", "they", "them", "what", "when", "with"}:
                    extracted.append({
                        "name": noun,
                        "type": "CONCEPT",
                        "confidence": 0.5
                    })
                    
        return extracted[:30]  # Cap at 30 entities per chunk

    def _extract_relations(self, text: str, entities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        relations = []
        if len(entities) < 2:
            return relations
            
        sentences = re.split(r'(?<=[.!?])\s+', text)
        
        for sentence in sentences:
            # Find which entities appear in this sentence
            sentence_ents = []
            for ent in entities:
                if ent["name"] in sentence:
                    sentence_ents.append(ent["name"])
                    
            if len(sentence_ents) >= 2:
                # Search for relation verb between entities in the sentence
                for i in range(len(sentence_ents)):
                    for j in range(i + 1, len(sentence_ents)):
                        ent1 = sentence_ents[i]
                        ent2 = sentence_ents[j]
                        
                        # Find relation pattern
                        for rel_type, pattern in self.RELATION_VERBS:
                            if re.search(pattern, sentence, re.IGNORECASE):
                                relations.append({
                                    "source": ent1,
                                    "target": ent2,
                                    "relation_type": rel_type,
                                    "evidence": sentence.strip()
                                })
                                break
                                
        # Deduplicate relationships
        deduped = []
        seen_rels = set()
        for rel in relations:
            rel_key = (rel["source"], rel["target"], rel["relation_type"])
            if rel_key not in seen_rels:
                seen_rels.add(rel_key)
                deduped.append(rel)
                
        return deduped[:20]  # Cap at 20 relations per chunk
