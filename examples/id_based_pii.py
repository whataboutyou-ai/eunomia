from eunomia.instruments import IdbacInstrument, PiiInstrument
from eunomia.orchestra import Orchestra

eunomia = Orchestra(
    instruments=[
        IdbacInstrument(
            instruments=[
                PiiInstrument(entities=["PERSON", "EMAIL_ADDRESS"], edit_mode="replace")
            ]
        ),
    ]
)
text_original = "Hello, my name is John Doe and my email is john.doe@example.com."

text_edited_same = eunomia.run(text_original, user_id="user1", doc_id="user1")
text_edited_different = eunomia.run(text_original, user_id="user2", doc_id="user1")

print("Same user:", text_edited_same)
print("Different user:", text_edited_different)
