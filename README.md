# 🎉**Welcome to AIMon**

AIMon helps developers build, ship, and monitor LLM Apps more confidently and reliably with its state-of-the-art, multi-model system for detecting LLM quality issues. It helps seamlessly with both offline evaluations and continuous production monitoring. AIMon offers fast, reliable, and cost-effective hallucination detection. It also supports other important quality metrics such as completeness, conciseness, and toxicity. Read our [blog post](https://aimon.ai/posts/aimon-rely-first-commercial-hallucination-detector) for more details.

✨ **Join our community on [Slack](https://join.slack.com/t/generativeair/shared_invite/zt-2jab62lsj-xM9a_s~Qweu8lf3YS2cANg)**

<div align="center">
    <img src="images/aimon-rely-image.png" alt="AIMon" width="325" height="175">
</div>

## Metrics Supported

The following is a list of quality metrics that are currently available and on our roadmap. Please reach out to express your interest in any of these.

| Metric                                           | Status                                                       |
| ------------------------------------------------ | ------------------------------------------------------------ |
| Model Hallucination (Passage and Sentence Level) | <span style="font-size: 24px; color: green;">&#10003;</span> |
| Completeness                                     | <span style="font-size: 24px; color: green;">&#10003;</span> |
| Conciseness                                      | <span style="font-size: 24px; color: green;">&#10003;</span> |
| Toxicity                                         | <span style="font-size: 24px; color: green;">&#10003;</span> |
| Instruction Adherence                            | <span style="font-size: 24px; color: green;">&#10003;</span> |

## Getting Started

AIMon supports asynchronous instrumentation or synchronous detections for the metrics mentioned above. Use these steps
to get started with using the AIMon SDK and the product.

- Step 1: Get access to the beta product by joining the waitlist on our [website](https://aimon.ai/) or by requesting
  it on [Slack](https://join.slack.com/t/generativeair/shared_invite/zt-2jab62lsj-xM9a_s~Qweu8lf3YS2cANg) or sending an email to info@aimon.ai
- Step 2: Install the AIMon SDK by running `pip install aimon` in your terminal.
- Step 3: Here is an example to instrument an LLM application **synchronously** using the AIMon decorator:

```python
from aimon import Detect

detect = Detect(values_returned=['context', 'generated_text'], config={"hallucination": {"detector_name": "default"}})

@detect
def my_llm_app(context, query):
    # my_llm_model is the function that generates text using the LLM model
    generated_text = my_llm_model(context, query)
    return context, generated_text
```

- Step 4: For an example of how to instrument an LLM application **asynchronously** using the SDK, please refer `analyze_prod` decorator.
- Step 5: For an example of synchronous detections using the SDK, please refer to the sample [streamlit application](examples/streamlit_apps/summarization/langchain_summarization_app.py)

<div align="center">
    <img src="images/product_apps_page.png" alt="AIMon Product">
</div>

## Benchmarks

### Hallucination Detection

To demonstrate the effectiveness of our system, we benchmarked it against popular industry benchmarks for the
hallucination detection task. The table below shows our results.

A few key takeaways:

✅ AIMon is **10x cheaper** than GPT-4 Turbo.

✅ AIMon is **4x faster** than GPT-4 Turbo.

✅ AIMon provides the convenience of a fully hosted API that includes baked-in explainability.

✅ Support for a context length of up to 32,000 tokens (with plans to further expand this in the near future).

Overall, AIMon is 10 times cheaper, 4 times faster, and close to or even **better than GPT-4** on the benchmarks
making it a suitable choice for both offline and online detection of hallucinations.

| Metric                                                         | Aimon Rely v1          | GPT-4 Turbo (LLM-as-a-judge)     |
|---------------------------------------------------------------|------------------------|----------------------------------|
| Context Length                                                | 32,000                 | **128,000**                      |
| TRUE Dataset Precision/Recall                             | 0.808 / 0.922          | **0.810 / 0.926**                |
| SummaC (test) Balanced Accuracy                           | **0.778**             | 0.756                           |
| SummaC (test) AUC                                         | **0.809**              | 0.780                            |
| AnyScale Ranking Test for Hallucinations Accuracy         | 0.665                  | **0.741**                        |
| AnyScale Ranking Test for Hallucinations Rel. Accuracy    | 0.804                  | **0.855**                        |
| Avg. Latency                                                  | **417ms**              | 1800ms                           |
| Cost (15M tokens across all benchmark datasets) excluding free tier | **$15**             | $158                             |
| Fully Hosted                                                  | :white_check_mark:     | :white_check_mark:               |
| Explainability                                                | **Automatic sentence-level Scores** | Detailed reasoning with additional prompt engineering |

### Benchmarks on other Detectors

There is a lack of industry-standard benchmark datasets for these metrics. We will be publishing an evaluation dataset soon.
Stay Tuned! <span style="font-size: 16px;">⌛</span>

## Pricing

Refer to the website [aimon.ai](https://aimon.ai) for details.

## Community

Join our [Slack community](https://join.slack.com/t/generativeair/shared_invite/zt-2jab62lsj-xM9a_s~Qweu8lf3YS2cANg) for the latest updates and discussions on generative AI reliability.
