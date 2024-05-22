# 🎉**Welcome to AIMon Rely**

AIMon Rely is a state-of-the-art system consisting of multiple models for detecting LLM quality issues during offline evaluations and continuous production monitoring. We offer
hallucination metrics that is fast, reliable and cost-effective. We also support additional metrics such as
completeness, conciseness and toxicity. 

Read our [blog post](https://aimon.ai/blogs/introducing-rely) for more details.

✨ **Join our community on [Slack](https://join.slack.com/t/generativeair/shared_invite/zt-2jab62lsj-xM9a_s~Qweu8lf3YS2cANg) 
or reach out to us at info@aimon.ai to get your API key.**

<div align="center">
    <img src="images/aimon-rely-image.png" alt="AIMon Rely" width="550" height="450">
</div>

## Metrics Supported

These are the quality metrics that are currently available via the API. Some of them are in progress and will be
available in a future release.

| Metric                                           | Status                                                       |
|--------------------------------------------------|--------------------------------------------------------------|
| Model Hallucination (Passage and Sentence Level) | <span style="font-size: 24px; color: green;">&#10003;</span> | 
| Completeness                                     | <span style="font-size: 24px; color: green;">&#10003;</span>                     |
| Conciseness                                      | <span style="font-size: 24px; color: green;">&#10003;</span>                    |
| Toxicity                                         | <span style="font-size: 24px; color: green;">&#10003;</span>                      |
| Semantic Similarity                              | <span style="font-size: 24px;">⌛</span>                      |
| Sentiment                                        | <span style="font-size: 24px;">⌛</span>                      |
| Coherence                                        | <span style="font-size: 24px;">⌛</span>                      |
| Sensitive Data (PII/PHI/PCI)                     | <span style="font-size: 24px;">⌛</span>                      |

## Product

Follow these steps to use the product:

- Step 1: Get access to the beta product by joining the wait list on our [website](https://aimon.ai/) or by requesting
          it on [Slack](https://join.slack.com/t/generativeair/shared_invite/zt-2jab62lsj-xM9a_s~Qweu8lf3YS2cANg) or 
          sending an email to info@aimon.ai
- Step 2: Install the AIMon SDK by running `pip install aimon` in your terminal.
- Step 3: Refer to the [sample notebook](notebooks/aimon_sdk_langchain_summarization.ipynb) for an example of how to instrument an LLM application using our SDK.

<div align="center">
    <img src="images/product_apps_page.png" alt="AIMon Product">
</div>

## API

Steps to use the API:

- Step 1: Get your API key by requesting it on our [Slack](https://join.slack.com/t/generativeair/shared_invite/zt-2jab62lsj-xM9a_s~Qweu8lf3YS2cANg) or sending an email
  to info@aimon.ai
- Step 2: You can try the API using either of these methods
    - [OPTION 1] Try the simple langchain summarization application that is augmented with AIMon Rely to detect
      hallucinations at the sentence level.
        - Step 1: Run `pip install -r examples/requirements.txt && pip install aimon`
        - Step 2: Run `streamlit run examples/langchain_summarization_app.py`
    - [OPTION 2] Download the Postman collection specified below to access the API
        - Model Hallucination (Passage and Sentence
          Level): [Postman Collection](examples/postman_collections)

### Sandbox

You can play with a [Sandbox](https://aimon.ai/tryproduct) that is available on our website.

## Benchmarks

### Hallucination Detection
To demonstrate the effectiveness of our system, we benchmarked it against popular industry benchmarks for the
hallucination detection task. The table below shows our results.

A few key takeaways:

✅ AIMon Rely is **10x cheaper** than GPT-4 Turbo.

✅ AIMon Rely is **4x faster** than GPT-4 Turbo.

✅ AIMon Rely provides the convenience of a fully hosted API that includes baked-in explainability.

✅ Support for a context length of up to 32,000 tokens (with plans to further expand this in the near future).

Overall, AIMon Rely is 10 times cheaper, 4 times faster and close to or even **better than GPT-4** on the benchmarks
making it a suitable choice for both offline and online detection of hallucinations.

<div align="center">
    <img src="images/hallucination-benchmarks.png" alt="Hallucination Benchmarks">
</div>

### Completeness, Conciseness Detection

There is a lack of industry standard benchmark datasets for these metrics. We will be publishing an evaluation dataset soon.
Stay Tuned! <span style="font-size: 16px;">⌛</span>

## Pricing

Please reach out to info@aimon.ai for pricing details related to the product and the API.

## Future Work

- We are working on additional metrics as detailed in the table above.
- In addition, we are working on something awesome to make the offline evaluation and continuous model quality
  monitoring experience more seamless.

Join our [Slack](https://join.slack.com/t/generativeair/shared_invite/zt-2jab62lsj-xM9a_s~Qweu8lf3YS2cANg) for the latest updates and discussions on generative AI reliability.