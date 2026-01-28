import os
import dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
# from langchain_google_genai import ChatGoogleGenerativeAI # Removed
from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import RunnablePassthrough # Removed 
# from langchain_core.output_parsers import StrOutputParser # Removed
from django.conf import settings
from .models import SourceDocument, EvidenceArtifact
from .services import EvidenceGenerator
from .ingestion import CHROMA_DB_DIR
from google import genai 

# Load environment variables
dotenv.load_dotenv()

from flashrank import Ranker, RerankRequest

# ... (imports)

class RAGService:
    def __init__(self):
        self.evidence_gen = EvidenceGenerator()
        
        # 1. Initialize Embeddings & Vector Store
        self.embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
        self.vectorstore = Chroma(
            collection_name="al_muwathiq_standards",
            embedding_function=self.embeddings,
            persist_directory=CHROMA_DB_DIR
        )
        # Increase initial retrieval for reranking (The "Intern" grabs 50)
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 50})
        
        # Initialize FlashRank (The "Manager")
        # specific model can be passed, default is ms-marco-TinyBERT-L-2-v2
        self.ranker = Ranker()

        # 4. Initialize Gemini LLM (Google GenAI Client v2)
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("WARNING: GOOGLE_API_KEY not found. Gemini will fail.")
            self.client = None
        else:
            masked_key = api_key[:4] + "..." + api_key[-4:]
            print(f"DEBUG: Loaded API Key: {masked_key}")
            try:
                self.client = genai.Client(api_key=api_key)
                print("DEBUG: Google GenAI Client Initialized (Gemini 2.0)")
            except Exception as e:
                print(f"ERROR: Failed to init GenAI Client: {e}")
                self.client = None

        # 5. Define Prompt Template (Kept as string for manual formatting)
        self.prompt_template = """
You are Al-Muwathiq, a Shariah compliance assistant.
Your goal is to answer the user's question using the provided Context.

INSTRUCTIONS:
1. Answer strictly based on the Context below.
2. If the user asks for a definition, you MUST use descriptions of "nature", "concept", or "components" as the definition.
3. If the user asks for a comparison (e.g. "difference between X and Y"), you MUST synthesize the answer by finding the definition of X and the definition of Y in the text, even if they are in different documents.
4. Do not say "I cannot find a specific ruling" unless the Context is completely empty or unrelated.

EXAMPLE:
Context: "The common inherent nature of Murabahah is a sale with markup."
Question: "What is the definition of Murabahah?"
Answer: "Murabahah is defined as a sale contract where the seller discloses the cost and markup to the buyer."

Context:
{context}

Question: {question}

Answer:
"""

    def search_db(self, query):
        """
        Retrieves top 50 documents, then reranks to Top 5.
        """
        # 1. Broad Sweep (The Intern) -> Now acting as the only retriever
        # We manually call similarity search to get documents
        # Increased to 15 to ensure we get enough context for comparisons without reranking
        results = self.vectorstore.similarity_search_with_score(query, k=15)
        print(f"DEBUG: 'Intern' found {len(results)} chunks for query '{query}'")
        
        # 2. Reranking (The Manager) - DISABLED
        # FlashRank was aggressively downranking relevant English/Malay hybrid documents.
        # For now, we trust the Vector Search (Google Embeddings) more.
        
        # pass
        
        # Convert to list
        final_hits = []
        for doc, score in results:
             final_hits.append((doc, score))
             
        return final_hits

    def answer_question(self, query):
        """
        End-to-end RAG flow: Retrieval -> Evidence Gen -> LLM Response.
        """
        print(f"RAG Query: {query}")
        
        # 1. Retrieval
        hits = self.search_db(query)
        if not hits:
            return {
                "answer": "I cannot find a specific ruling on this in the provided documents.",
                "evidence_url": None,
                "metadata": None
            }

        # Format context with IDs so LLM can cite specific chunks if needed (simplified for now)
        context_text = ""
        for i, (doc, _) in enumerate(hits):
            context_text += f"[Source {i}] (Page {doc.metadata.get('page_number')}): {doc.page_content}\n\n"
        
        # 2. LLM Generation (Gemini 2.0 Flash via Google GenAI SDK)
        if not self.client:
             print("ERROR: GenAI Client not initialized.")
             answer = f"**System Error: AI Service Unavailable.**\n\nBased on the retrieved documents:\n\n{hits[0][0].page_content[:1200]}..."
             quote_part = ""
        else:
            # Prepare Prompt
            structured_prompt = self.prompt_template.format(context=context_text, question=query)
            structured_prompt += "\n\nAlso, pick the SINGLE best short quote (approx 10-20 words) from the Context that proves your answer.\nReturn your response in this exact format:\nANSWER: [Your answer]\nQUOTE: [The quote]"

            try:
                # Direct SDK Call
                print(f"DEBUG: Calling Gemini 2.0 Flash with prompt length {len(structured_prompt)}")
                response = self.client.models.generate_content(
                    model="gemini-2.0-flash", 
                    contents=structured_prompt
                )
                response_text = response.text
                print("DEBUG: Gemini 2.0 Response received.")
                
                # Robust Parsing using Regex (Same as before)
                import re
                
                answer_part = ""
                quote_part = ""
                
                # Try splitting by headers
                if "ANSWER:" in response_text and "QUOTE:" in response_text:
                    # Find content between ANSWER: and QUOTE:
                    match = re.search(r"ANSWER:\s*(.*?)\s*QUOTE:\s*(.*)", response_text, re.DOTALL)
                    if match:
                        answer_part = match.group(1).strip()
                        quote_part = match.group(2).strip()
                elif "QUOTE:" in response_text:
                    # Maybe ANSWER header is missing but QUOTE exists?
                    parts = response_text.split("QUOTE:")
                    answer_part = parts[0].replace("ANSWER:", "").strip()
                    quote_part = parts[1].strip()
                else:
                    # No headers found, use the entire response as answer
                    answer_part = response_text.strip()
                
                # If answer is still empty or too short, use the response
                if not answer_part or len(answer_part) < 10:
                    answer_part = response_text.strip()
                
                answer = answer_part
                
            except Exception as e:
                print(f"LLM Error (Gemini 2.0): {e}")
                import traceback
                traceback.print_exc()
                # Fallback if LLM fails
                content_snippet = hits[0][0].page_content[:1200]
                answer = f"**Note: AI Generation Failed. Showing raw context.**\n\nBased on the retrieved documents:\n\n{content_snippet}..."
                quote_part = ""

        # 3. Multi-Evidence Generation
        evidence_list = []
        seen_pages = set()
        
        # We will try to generate evidence for the TOP 3 hits to ensure broad coverage
        # and support comparison questions.
        for doc, score in hits[:3]:
            metadata = doc.metadata
            source_doc_id = metadata.get('source_doc_id')
            page_number = metadata.get('page_number')
            
            # Avoid duplicates (same page multiple times)
            combo_key = f"{source_doc_id}_{page_number}"
            if combo_key in seen_pages:
                continue
            seen_pages.add(combo_key)
            
            try:
                source_doc = SourceDocument.objects.get(id=source_doc_id)
                
                # Highlighting Strategy:
                # The user complained about "random highlights" (headers/footers).
                # This was because we used 'top_hit.page_content[:100]' which often captures the header.
                # Since 'doc.page_content' IS the text that the AI read, we should highlight THAT.
                # However, doc.page_content might be 1000 chars (too long for yellow highlight?).
                # Let's take the first 300 characters of the ACTUAL matched content.
                # This guarantees the highlight finds the relevant paragraph.
                
                snippet_to_highlight = doc.page_content[:300] 
                
                # Clean up snippet (remove newlines for better regex matching in PDF)
                snippet_to_highlight = snippet_to_highlight.replace('\n', ' ')
                
                image_rel_path = self.evidence_gen.generate_evidence(
                    source_doc.file_path.path,
                    page_number,
                    snippet_to_highlight
                )
                
                if image_rel_path:
                    # Save artifact record
                    EvidenceArtifact.objects.create(
                        source_doc=source_doc,
                        page_number=page_number,
                        highlighted_text=snippet_to_highlight,
                        image_path=image_rel_path
                    )
                    
                    evidence_list.append({
                        "url": settings.MEDIA_URL + image_rel_path,
                        "title": source_doc.title,
                        "page": page_number,
                        "score": score
                    })

            except Exception as e:
                print(f"Evidence Error for {source_doc_id}: {e}")
        
        # Final cleanup of answer/format
        if not answer or not answer.strip() or len(answer.strip()) < 20:
             answer = "Based on the retrieved Shariah standards, please refer to the visual evidence below for the relevant ruling."

        return {
            "answer": answer,
            "evidence_list": evidence_list,
            # Legacy field for backward compat/simple checks
            "evidence_url": evidence_list[0]['url'] if evidence_list else None,
            "metadata": hits[0][0].metadata if hits else None
        }
