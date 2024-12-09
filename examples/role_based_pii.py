from eunomia.instruments import PiiInstrument, RbacInstrument
from eunomia.orchestra import Orchestra

eunomia = Orchestra(
    instruments=[
        PiiInstrument(entities=["PERSON"], redact_mode="replace"),
        RbacInstrument(
            role="specialist",
            instruments=[
                PiiInstrument(entities=["EMAIL_ADDRESS"], redact_mode="replace")
            ],
        ),
    ]
)

text_original = "Hello, my name is John Doe and my email is john.doe@example.com."

text_redacted_specialist = eunomia.run(text_original, role="specialist")
text_redacted_manager = eunomia.run(text_original, role="manager")

print("Specialist:", text_redacted_specialist)
print("Manager:", text_redacted_manager)
