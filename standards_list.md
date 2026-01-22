# 📜 Knowledge Base Manifest

This repository contains the **Logic (Factory)** to process Shariah standards.
The **Knowledge (Inventory)** must be provided by the user due to copyright restrictions.

Below is the list of standards this system is designed and tested to support.

## 1. Bank Negara Malaysia (BNM) Policy Documents
*   [x] **Tawarruq** (Policy Document, 2018) - *Primary Test Subject*
*   [x] **Kafalah** (Policy Document, 2017)
*   [x] **Murabahah**(Policy Document)
*   [ ] Wa'd (Policy Document)
*   [ ] Wakalah (Policy Document)

## 2. AAOIFI Shariah Standards
*   [ ] Standard No. 30: Monetization (Tawarruq)
*   [ ] Standard No. 5: Guarantees

## 3. Securities Commission (SC)
*   [ ] Guidelines on Unlisted Capital Market Products

---

## 🏗️ How to Rebuild the Knowledge Base
1.  Obtain the PDF files for the standards listed above.
2.  Place them in your local directory or upload via the Django Admin.
3.  Run the Ingestion Engine to generate the Vector Embeddings (ChromaDB).
