<p align="center">
  <h1 align="center">🤖 Agentic Parallelism: A Practical Guide 🚀</h1>
</p>
<p align="center">
  Conceptual based implementations of 14 core patterns for building faster, smarter, and more reliable AI agentic systems using LangChain and LangGraph.
</p>

---

> ### 📖 Want to learn every concept in detail?
> **Read the full, in-depth article that defines and explains all 14 core concepts of Agentic Parallelism.**<br>
> **[Implementing 14 Core Concepts of Agentic AI-based Solution](https://medium.com/@fareedkhandev/implementing-14-core-concepts-of-agentic-ai-based-solution-229e50f65986)**

---

## ✨ Introduction

Welcome to the future of AI agent development! This repository is a comprehensive, hands-on collection of **14 industrial-grade notebooks** demonstrating the core principles of **Agentic Parallelism**.

In the world of AI agents, speed, quality, and reliability are not just features—they are requirements. A single, sequential agent can be slow, prone to errors, and limited in its problem-solving ability. The solution is to think in parallel: designing systems where multiple agents, processes, or tasks execute concurrently to achieve a common goal.

This repository is your practical guide to building faster, smarter, and more robust agentic systems using **LangChain** and **LangGraph**. Each notebook tackles a specific parallelism pattern, complete with real-world examples, detailed instrumentation, and state analysis.

---

## ⚡ The Core Problem: Why Parallelism Matters

Large-scale agentic systems are often bottlenecked by two things:
1.  **I/O Latency:** Waiting for networks, databases, and external API calls.
2.  **Quality & Reliability:** A single line of reasoning can lead to suboptimal or incorrect outcomes.

Agentic Parallelism addresses these challenges head-on by overlapping wait times, exploring multiple solution paths, and creating resilient, self-correcting systems.

---

## 📚 Table of Concepts

This repository is structured into four key areas of agentic design. Each notebook is self-contained and ready to run. Simply click on a notebook link to explore its implementation.

### 🚀 Core Agent Patterns
*Fundamental techniques for enhancing a single agent's capabilities.*

| Concept | Description | Key Benefit | Notebook |
| :--- | :--- | :--- | :--- |
| **1. Parallel Tool Use** | An agent calls multiple tools (e.g., a stock API and a news search) simultaneously instead of sequentially. | 📉 **Reduces I/O Latency** | [`01_parallel_tool_use.ipynb`](./01_parallel_tool_use.ipynb) |
| **2. Parallel Hypothesis** | An agent generates multiple strategies or "thoughts" in parallel, explores them all, and synthesizes the best outcome. | 💡 **Improves Solution Quality** | [`02_parallel_hypothesis.ipynb`](./02_parallel_hypothesis.ipynb) |
| **3. Parallel Evaluation** | A panel of specialized "critic" agents reviews a piece of content simultaneously, each from a unique perspective (e.g., brand voice, fact-checking). | ✅ **Robust AI Governance** | [`03_parallel_evaluation.ipynb`](./03_parallel_evaluation.ipynb) |
| **4. Speculative Execution** | The system anticipates the agent's most likely next action (e.g., a tool call) and begins executing it while the agent is still "thinking". | 🏃‍♂️ **Hides Latency** | [`04_speculative_execution.ipynb`](./04_speculative_execution.ipynb) |

### 🧑‍🤝‍🧑 Multi-Agent Architectures
*Designing digital organizations where multiple agents collaborate to solve complex problems.*

| Concept | Description | Key Benefit | Notebook |
| :--- | :--- | :--- | :--- |
| **5. Hierarchical Teams** | A "manager" agent decomposes a complex task and delegates sub-tasks to a team of "worker" agents who execute in parallel. | 📈 **Scalability & Specialization** | [`05_hierarchical_agent_teams.ipynb`](./05_hierarchical_agent_teams.ipynb) |
| **6. Competitive Ensembles** | A diverse team of agents tackles the same problem independently. A "judge" agent then selects the best solution from the competing outputs. | 🏆 **Robustness & Creativity** | [`06_competitive_agent_ensembles.ipynb`](./06_competitive_agent_ensembles.ipynb) |
| **7. Agent Assembly Line** | A sequence of specialized agents processes a continuous stream of tasks in a pipeline, maximizing overall system throughput. | 🏭 **High-Throughput Processing** | [`07_agent_assembly_line.ipynb`](./07_agent_assembly_line.ipynb) |
| **8. Decentralized Blackboard** | Independent agents collaborate by reading from and writing to a shared data space, enabling emergent, opportunistic problem-solving. | 🧠 **Adaptive Collaboration** | [`08_decentralized_blackboard.ipynb`](./08_decentralized_blackboard.ipynb) |

### 🛡️ System Reliability Patterns
*Building resilient systems that can handle real-world failures and unpredictability.*

| Concept | Description | Key Benefit | Notebook |
| :--- | :--- | :--- | :--- |
| **9. Redundant Execution** | For a critical but unreliable task, execute two identical agents in parallel. The system uses the result from the first one to finish. | ⚙️ **Fault Tolerance & Consistency** | [`09_redundant_execution.ipynb`](./09_redundant_execution.ipynb) |

### 📚 Advanced RAG Patterns
*Applying parallelism to build state-of-the-art Retrieval-Augmented Generation systems.*

| Concept | Description | Key Benefit | Notebook |
| :--- | :--- | :--- | :--- |
| **10. Parallel Query Expansion** | Transform a user's query into multiple, diverse search queries (e.g., sub-questions, hypothetical documents) and execute them all at once. | 🎯 **Maximizes Retrieval Recall** | [`10_parallel_query_expansion.ipynb`](./10_parallel_query_expansion.ipynb) |
| **11. Sharded Retrieval** | Partition a massive knowledge base into smaller "shards" and search them all in parallel, enabling low-latency retrieval over enterprise-scale data. | 🗄️ **Scalability & Performance** | [`11_sharded_retrieval.ipynb`](./11_sharded_retrieval.ipynb) |
| **12. Hybrid Search Fusion** | Run vector (semantic) search and keyword (lexical) search in parallel, then fuse their results to get the best of both worlds. | 🧬 **High-Fidelity Retrieval** | [`12_hybrid_search_fusion.ipynb`](./12_hybrid_search_fusion.ipynb) |
| **13. Context Pre-processing** | After retrieval, use parallel LLM calls to distill a large, noisy context into a smaller, denser, and more relevant context before final generation. | 💧 **Improves Accuracy & Reduces Cost** | [`13_parallel_context_preprocessing.ipynb`](./13_parallel_context_preprocessing.ipynb) |
| **14. Multi-Hop Retrieval** | Decompose a complex query into sub-questions, answer each with its own parallel RAG process, and then synthesize a final, comprehensive answer. | 🧠 **Solves Complex Questions** | [`14_parallel_multi_hop_retrieval.ipynb`](./14_parallel_multi_hop_retrieval.ipynb) |

---

## 🛠️ Technical Stack

This project leverages a modern, powerful stack for building agentic systems:

*   **Orchestration:** 🦜🔗 [LangGraph](https://python.langchain.com/docs/langgraph/)
*   **Core Framework:** 🦄 [LangChain](https://python.langchain.com/docs/get_started/introduction)
*   **LLMs:** 🦙 [Meta Llama 3](https://huggingface.co/meta-llama/Meta-Llama-3-8B-Instruct), ☁️ [Claude 3 Sonnet (on Vertex AI)](https://cloud.google.com/vertex-ai)
*   **Models & Inference:** 🤗 [Hugging Face Transformers](https://huggingface.co/docs/transformers/index)
*   **Tools:** 🔍 [Tavily Search](https://tavily.com/), 💹 [yfinance](https://pypi.org/project/yfinance/)
*   **Vector Stores:** 💾 [FAISS](https://faiss.ai/)
*   **Observability:** ιχ [LangSmith](https://www.langchain.com/langsmith)

---

## 🚀 Getting Started

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/FareedKhan-dev/agentic-parallelism.git
    cd agentic-parallelism
    ```

2.  **Install dependencies:**
    Each notebook lists its specific dependencies at the top. To install all common dependencies at once:
    ```bash
    pip install -U langchain langgraph langsmith langchain-huggingface transformers accelerate bitsandbytes torch tavily-python yfinance langchain-google-vertexai sentence-transformers faiss-cpu scikit-learn tiktoken
    ```

3.  **Set up your API Keys:**
    The notebooks will prompt you to enter the necessary API keys. At a minimum, you will need:
    *   `LANGCHAIN_API_KEY` (for LangSmith tracing)
    *   `HUGGING_FACE_HUB_TOKEN` (to download Llama 3)
    *   `TAVILY_API_KEY` (for search-enabled agents)
    *   Google Cloud Authentication (for notebook `06_competitive_agent_ensembles`)

Now you're ready to run the notebooks and explore the power of agentic parallelism!

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for new parallelism patterns, improvements to existing notebooks, or bug fixes, please open an issue or submit a pull request.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.