import os
import dotenv
from langchain_chroma import Chroma
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from django.conf import settings
from .models import SourceDocument, EvidenceArtifact
from .services import EvidenceGenerator
from .ingestion import CHROMA_DB_DIR

# Load environment variables
dotenv.load_dotenv()

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
        self.retriever = self.vectorstore.as_retriever(search_kwargs={"k": 5})

        # 2. Initialize Gemini LLM
        # Ensure GOOGLE_API_KEY is in .env or environment
        if not os.getenv("GOOGLE_API_KEY"):
            print("WARNING: GOOGLE_API_KEY not found. Gemini will fail.")
        
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-flash-latest",
            temperature=0.3,
            max_tokens=2000,
        )

        # 3. Define Prompt
        self.prompt = ChatPromptTemplate.from_template("""
You are Al-Muwathiq, a helpful and precise Shariah compliance assistant.
Answer the user's question based ONLY on the following context (Shariah standards/policies).
If the answer is not in the context, say "I cannot find a specific ruling on this in the provided documents."
Do not halluncinate.
Prioritize information from 'BNM' (Bank Negara Malaysia) documents if conflicting.

Context:
{context}

Question: {question}

Answer:
""")

    def search_db(self, query):
        """
        Retrieves top documents using vector similarity.
        """
        # We manually call similarity search to get documents for evidence generation
        results = self.vectorstore.similarity_search_with_score(query, k=5)
        print(f"DEBUG: Found {len(results)} chunks for query '{query}'")
        for i, (doc, score) in enumerate(results):
             print(f"  Hit {i}: {doc.metadata.get('source_doc_id')} - Score {score:.4f} - Content: {doc.page_content[:40]}...")
        
        # Rerank Logic: Prioritize 'BNM'
        bnm_hits = []
        other_hits = []
        
        for doc, score in results:
            authority = doc.metadata.get('authority', '')
            if authority == 'BNM':
                bnm_hits.append((doc, score))
            else:
                other_hits.append((doc, score))
        
        return bnm_hits + other_hits

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
        
        # 2. LLM Generation (Now asking for structured JSON-like output)
        # We override the prompt for this specific method to get structured data
        structured_prompt = ChatPromptTemplate.from_template("""
You are Al-Muwathiq, a Shariah AI.
Based on the Context below, answer the Question.
Also, pick the SINGLE best short quote (approx 10-20 words) from the Context that proves your answer.
Return your response in this exact format (do not use JSON, just these headers):

ANSWER: [Your natural language answer here]
QUOTE: [The exact verbatim text from the context to highlight]

Context:
{context}

Question: {question}
""")

        try:
            chain = structured_prompt | self.llm | StrOutputParser()
            response_text = chain.invoke({"context": context_text, "question": query})
            
            # Robust Parsing using Regex to handle deviations
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
            print(f"LLM Error: {e}")
            # Fallback if LLM fails: Return the raw content of the top hit as a summary
            answer = f"Based on the retrieved documents:\n\n{hits[0][0].page_content[:300]}..."
            quote_part = ""

        # 3. Visual Provenance (Find the quote in the hits)
        top_hit = None
        
        if quote_part and len(quote_part) > 5:
            # Find which hit contains this quote
            print(f"DEBUG: Looking for quote '{quote_part[:20]}...'")
            for doc, _ in hits:
                # Normalize whitespace for matching
                if quote_part.lower() in doc.page_content.lower().replace('\n', ' '):
                    top_hit = doc
                    print(f"DEBUG: Found quote in Page {doc.metadata.get('page_number')}")
                    break
        
        # Fallback to heuristic if AI quote match failed
        if not top_hit:
             print("DEBUG: QC failed or quote not found. Using heuristic.")
             top_hit = hits[0][0]
             for doc, s in hits:
                 if doc.metadata.get('page_number', 0) > 1:
                     top_hit = doc
                     break

        # Generate Evidence Image
        metadata = top_hit.metadata
        source_doc_id = metadata.get('source_doc_id')
        page_number = metadata.get('page_number')
        evidence_url = None
        
        try:
            source_doc = SourceDocument.objects.get(id=source_doc_id)
            snippet_to_highlight = quote_part if (top_hit and quote_part in top_hit.page_content) else top_hit.page_content[:100]
            
            # Clean up snippet if it was falling back
            if not quote_part:
                 snippet_to_highlight = top_hit.page_content[:100]

            image_rel_path = self.evidence_gen.generate_evidence(
                source_doc.file_path.path,
                page_number,
                snippet_to_highlight
            )
            
            metadata['source_title'] = source_doc.title
            
            if image_rel_path:
                 EvidenceArtifact.objects.create(
                    source_doc=source_doc,
                    page_number=page_number,
                    highlighted_text=snippet_to_highlight,
                    image_path=image_rel_path
                )
                 evidence_url = settings.MEDIA_URL + image_rel_path

        except Exception as e:
            print(f"Evidence Gen Error: {e}")

        # Final cleanup of answer
        if not answer or not answer.strip() or len(answer.strip()) < 20:
             answer = "Based on the retrieved Shariah standards, please refer to the visual evidence below for the relevant ruling."

        return {
            "answer": answer,
            "evidence_url": evidence_url,
            "metadata": metadata
        }
