from eunomia.instruments import PiiInstrument
from eunomia.orchestra import Orchestra

eunomia = Orchestra(
    instruments=[
        PiiInstrument(entities=["EMAIL_ADDRESS", "PERSON"], redact_mode="replace")
    ]
)

text_original = "Hello, my name is John Doe and my email is john.doe@example.com."
text_redacted = eunomia.run(text_original)

print(text_redacted)
