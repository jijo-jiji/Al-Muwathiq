import os
# ... imports ...

class RAGService:
    # ... search_db ...

    def answer_question(self, query):
        """
        Modified to return a LIST of evidence items.
        """
        print(f"RAG Query: {query}")
        
        # 1. Retrieval
        hits = self.search_db(query)
        if not hits:
            return {
                "answer": "I cannot find a specific ruling on this in the provided documents.",
                "evidence_list": []
            }

        # Format context for LLM
        context_text = ""
        for i, (doc, _) in enumerate(hits):
            context_text += f"[Source {i}] (Page {doc.metadata.get('page_number')}): {doc.page_content}\n\n"
        
        # 2. LLM Generation
        # ... (Same Prompt & LLM call) ...
        # Simplified: We don't ask for "QUOTE" anymore because users said it was random.
        # We focus on the answer. We will infer evidence from the hits themselves.
        # But we can keep asking for quote to prioritize the *best* hit.
        
        if not self.client:
             # Fallback
             answer = f"**System Error: AI Service Unavailable.**..."
        else:
            # ... Generate Content ...
             answer = response.text # Just the answer part (we can improve parsing later if we want strict quotes)
        
        # 3. Multi-Evidence Generation
        # Strategy: distinct Source+Page from the Top 3 hits.
        evidence_list = []
        seen_pages = set()
        
        for doc, score in hits[:3]: # Limit to top 3 to avoid clutter
            metadata = doc.metadata
            source_doc_id = metadata.get('source_doc_id')
            page_number = metadata.get('page_number')
            
            # Avoid duplicates of same page
            combo_key = f"{source_doc_id}_{page_number}"
            if combo_key in seen_pages:
                continue
            seen_pages.add(combo_key)
            
            try:
                source_doc = SourceDocument.objects.get(id=source_doc_id)
                
                # Highlighting Strategy:
                # Instead of a tiny snippet, highlight the first meaningful sentence?
                # Or just pass the first 300 chars of the page_content.
                # User complaint: "highlight random things" (likely headers).
                # The page_content usually *starts* with the relevant text found by vector search.
                # So we use doc.page_content[:200] as the snippet to search.
                snippet_to_highlight = doc.page_content[:200]
                
                image_rel_path = self.evidence_gen.generate_evidence(
                    source_doc.file_path.path,
                    page_number,
                    snippet_to_highlight
                )
                
                if image_rel_path:
                    # Save artifact
                    # EvidenceArtifact.objects.create(...) # Optional, good for logging
                    
                    evidence_list.append({
                        "url": settings.MEDIA_URL + image_rel_path,
                        "title": source_doc.title,
                        "page": page_number,
                        "score": score
                    })
                    
            except Exception as e:
                print(f"Failed to generate evidence for doc {source_doc_id}: {e}")
        
        return {
            "answer": answer,
            "evidence_list": evidence_list, # New Field
            # "evidence_url": ... deprecated
        }
