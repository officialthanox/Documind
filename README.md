<div align="center">



\# 🧠 DocuMind

\### Retrieval-Augmented Document Intelligence Agent



\*Upload a document. Ask a question. Get an answer that's grounded in the source — never invented.\*



!\[Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square\&logo=python\&logoColor=white)

!\[Streamlit](https://img.shields.io/badge/Streamlit-1.38-FF4B4B?style=flat-square\&logo=streamlit\&logoColor=white)

!\[ChromaDB](https://img.shields.io/badge/Vector%20DB-ChromaDB-6A5ACD?style=flat-square)

!\[Groq](https://img.shields.io/badge/LLM%20Inference-Groq-F55036?style=flat-square)

!\[Docker](https://img.shields.io/badge/Containerized-Docker-2496ED?style=flat-square\&logo=docker\&logoColor=white)

!\[Status](https://img.shields.io/badge/Status-Active%20Development-brightgreen?style=flat-square)



</div>



> \*"An AI system's real value isn't in how confidently it answers — it's in how honestly it admits what it doesn't know."\*

> — Engineering principle behind DocuMind's grounding strategy



\---



\## Quick Summary



\- \*\*Retrieval-grounded Q\&A\*\* — every answer is generated exclusively from the uploaded document's content; the LLM is contractually instructed to refuse when the answer isn't present.

\- \*\*Transparent trust signal\*\* — a confidence score is \*computed\* from vector-distance math, not guessed by the model, so users know how strong the retrieval match actually was.

\- \*\*Full source traceability\*\* — every answer names the exact source file it came from, and every Q\&A pair is persisted to an auditable log.

\- \*\*Lean, intentional codebase\*\* — the entire retrieval-augmented-generation pipeline runs in \*\*209 lines of Python across 5 single-responsibility modules\*\*.

\- \*\*Container-first delivery\*\* — one `docker compose up` away from running, with secrets isolated to environment variables.



\---



\## Repository Structure

