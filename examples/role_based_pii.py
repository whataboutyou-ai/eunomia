from eunomia.instruments import PiiInstrument, RbacInstrument
from eunomia.orchestra import Orchestra

eunomia = Orchestra(
    instruments=[
        PiiInstrument(entities=["EMAIL_ADDRESS"], edit_mode="replace"),
        RbacInstrument(
            role="specialist",
            instruments=[PiiInstrument(entities=["PERSON"], edit_mode="replace")],
        ),
    ]
)

text_original = "Hello, my name is John Doe and my email is john.doe@example.com."

text_edited_specialist = eunomia.run(text_original, role="specialist")
text_edited_manager = eunomia.run(text_original, role="manager")

print("Specialist:", text_edited_specialist)
print("Manager:", text_edited_manager)
