# ParseBunny CLI

ParseBunnyCLI is a local, AI-powered command-line interface for legal professionals and data analysts. It automates redaction, clause extraction, labeling, classification, and document search—built for privacy, speed, and accuracy.

---

## Getting Started

Installation:
1. Download the binary (parse-bunny.exe)
2. Place it somewhere like C:\parse-bunny\
3. Run it from terminal:
   ./parse-bunny.exe

All data stays local. Internet connection is require for the following features:

label 
redact 

---

## Commands

label       → Auto-label legal documents using AI or keyword sets  
extract     → Extract clauses from contracts (e.g., termination, payment)  
highlight   → Highlight sensitive data and legal clauses in PDF  
redact      → Redact PII, PHI, and privilege from files  
search      → Search documents using regex or AI  
backup      → Save a memory snapshot of file structure  
restore     → Restore from a backup  
reset       → Reset data/downloads/output (supports flags)

---

## Environment Variables

an environment variables file will be created in `C:\parse-bunny\dashboard\.env`
The following contents are required for AI or automated features:

```bash
$GGL_USER=your_email@gmail.com
$GGL_PASS=your_google_app_password # format (16 chars): xxxx xxxx xxxx xxxx 
$OPENAI_API_KEY=your_deepseek_api_key
```
---

## Folder Structure

data/ingested/      → Raw ingested files  
data/classified/    → Labeled output  
data/highlighted/   → Highlighted PDFs  
data/search/        → AI search results  
downloads/          → Email/download automation  
output/             → Generated content and file trees

---

## Usage Examples

Label documents:
label -name["nda_corp_set"] -files["./contracts/*.txt"]

Extract NDA terms:
extract -template["nda_terms"] -files["./contracts/*.txt"] # template should be a .json file in the `./template` dir

Highlight PII and legal clauses:
highlight -files["./contracts/*.pdf"] -regex["ssn", "email"] -ai["termination clause"]

Redact sensitive content:
redact -files["./contracts/*.pdf"] -regex["ssn", "dob", "email"]

Search through extractions:
search -files["./contracts/] -extract["nda_terms"]

Ingest emails and docx files:
ingest -email["./downloads"]
ingest -docx["./downloads"]
ingest -email | -docx OPT: -output["./output/dest"]

---

## AI Details

Model: DeepSeek  
Use Cases:  
- Labeling  
- Clause Extraction  
- Redaction  
- Semantic Search

---

## Contact

Email: joshuawhitfield022@gmail.com  
Website: https://parsebunnycli.com  
Trials: Free trial requests accepted

---

## License

© 2025 Parse-Bunny Corp. All rights reserved.

<h1>Inputs</h1>

<h3>↑ up arrow key</h3>
<h4>description:</h4>
<p>Recall previous command in terminal for reuse.</p>

<h4>Exit the CLI:</h4>
<p>Press <code>CTRL + C</code> or type <code>exit</code>.</p>

<h1>Legal and Data Handling Clauses</h1>

### 1. **User Responsibility for Data**  
By using **Parse Bunny CLI**, the user acknowledges and agrees that they are solely responsible for handling and securing any data processed through the tool. **Parse Bunny CLI** does not store, access, or retain any user data unless explicitly required for specific operations, such as temporary processing or logging. The user must ensure that any data processed is handled in compliance with relevant data protection laws and regulations.

### 2. **Data Processing Disclaimer**  
**Parse Bunny CLI** processes user data **on behalf of the user**. The tool does not retain or store any user data after the processing is complete, unless explicitly required for operational reasons (e.g., temporary file storage, logging). Users must ensure that they manage, process, and delete any data according to their own legal and regulatory obligations.

### 4. **User Privacy and Confidentiality**  
While **Parse Bunny CLI** does not store or access user data, we take necessary steps to ensure that data processed within the tool is handled with the highest level of confidentiality. Any temporary files or data handled by the tool are secured during processing using encryption. The user agrees to manage any data confidentiality concerns within their own operational environments.

### 7. **Limitation of Liability**  
**Parse Bunny CLI** is provided as-is, and the user acknowledges that they are solely responsible for the legal and regulatory compliance of their data. The developers of **Parse Bunny CLI** are not liable for any failure to comply with data protection laws, mismanagement of data, or security breaches arising from the user's handling of data. By using this tool, the user agrees to indemnify the developers from any legal actions or claims related to the use of the software.
