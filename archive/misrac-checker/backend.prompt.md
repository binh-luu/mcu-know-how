# Objective
Design and develop a MISRA-C:2012 fixing intelligent AI assistant leveraging Retrieval-Augmented Generation (RAG) techniques

# Techstack
| Category | Technology Options |
|---|---|
| LLM APIs | OpenAI API (GPT-4/4o) |
| Orchestration | LangChain, LangGraph (for multi-step/agentic workflows) |
| Embeddings | OpenAI API for custom models/embeddings |
| Vector Database | Pinecone, Chroma |

# Instruction

## Input

### I1-MISRA C:2012 Example Suite
Location folder: `./Example-Suite-master`
This suite of files is intended to illustrate issues addressed by the MISRA C rules as expressed in:

   MISRA C:2012 Guidelines for the use of the C language in critical systems,
      ISBN 978-1-906400-10-1 paperback and ISBN 978-1-906400-11-8 PDF.

The examples are mainly taken from the example sections in the MISRA C:2012 guidelines. It is not intended to be an exhaustive test suite and should not be used as such.

One (or more) files exist for each guideline within the suite. Where no examples are appropriate, the file will state that no example is provided for that guideline.

The file "R_xx_yy.c" illustrates MISRA C:2012, rule xx.yy. For example, R_20_04.c illustrates Rule 20.4 and D_04_05.c illustrates Directive 4.5.

The guidelines that are marked with "System" analysis scope are designed to be analysed across translation units and so may not produce an appropriate violation if run as a single file. To aid analysis there are two additional files for each section in the guidelines. For example R_08_system.c contains a "main" function that calls the external functions for rules in section 8. R_08_support.c is a second call to those functions and exists to minmize the number of Rule 8.7. violations.

### I2-MISRA C:2012 reports
All CSV report under `./reports` folder. Each report contains the following columns:
- `file`: The name of the source file being analyzed. This corresponds to the file name under `src` folder.
- `line`: The line number in the source file where the violation occurred.
- `column`: The column number in the source file where the violation occurred.
- `rule`: The specific MISRA C:2012 rule that was violated.
- `category`: The category of the violation (e.g., Required, Advisory, etc.).
- `description`: A brief description of the violation.

## Processing Steps
1. **Data Ingestion**: Load the MISRA C:2012 example suite and the corresponding CSV reports into a structured format suitable for analysis.
2. **Violation Extraction**: For each source file in the example suite, extract the relevant violations from the corresponding CSV report.
3. **Contextual Analysis**: For each violation, analyze the surrounding code context to understand the nature of the violation and its implications.
4. **RAG Integration**: Use Retrieval-Augmented Generation techniques to provide context-aware suggestions for fixing the violations. This may involve retrieving relevant code snippets, documentation, and best practices from the MISRA C:2012 guidelines.
5. **Fix Generation**: Generate code fixes for each violation based on the analysis and RAG suggestions. Ensure that the fixes adhere to the MISRA C:2012 guidelines and do not introduce new violations. Generate a git patch for fixing of each rule group. The patch should be generated in a way that it can be applied to the original source file to correct the violations.
