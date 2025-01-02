<div align="center" style="margin-bottom: 1em;">

<img src="docs/assets/logo.svg" alt="Eunomia Logo" width=300></img>

*Open Source Data Governance for LLM-based Applications*

Made with ❤ by the team at [What About You][whataboutyou-website].

[Read the docs][docs] · [Join the Discord][discord]

</div>

## Get Started
`eunomia` is a framework that makes it easy to enforce data governance policies in LLM-based applications by working at the token level.

### Installation
Install the `eunomia` package via pip:

``` bash
pip install eunomia-ai
```

### Basic Usage
`eunomia` is built in a modular way, where each module is a separate instrument. Multiple instruments can be combined together to create a custom orchestration.

For instance, we can use the `PiiInstrument` to identify and replace PII in the text.
```py
from eunomia.instruments import PiiInstrument

eunomia = Orchestra(
    instruments=[
        PiiInstrument(entities=["EMAIL_ADDRESS", "PERSON"], edit_mode="replace"),
    ]
)

text = "Hello, my name is John Doe and my email is john.doe@example.com."

eunomia.run(text)
# Output: "Hello, my name is <PERSON> and my email is <EMAIL_ADDRESS>."
```

### Documentation
For more examples and detailed usage, check out the [documentation][docs].

[whataboutyou-website]: https://whataboutyou.ai
[docs]: https://whataboutyou-ai.github.io/eunomia/
[discord]: https://discord.gg/TyhGZtzg3G
