from eunomia.instruments import FinancialsInstrument
from eunomia.orchestra import Orchestra

eunomia = Orchestra(
    instruments=[
        FinancialsInstrument(
            entities=[
                "Advisors.GENERIC_CONSULTING_COMPANY",
                "Parties.BUYING_COMPANY",
                "Parties.ACQUIRED_COMPANY",
            ],
            edit_mode="replace",
        )
    ]
)

text_original = """\
Smithson Legal Advisors provided counsel to Bellcom Industries, \
the buying company, in their acquisition of Hexatech Systems, \
a prominent acquired company. The deal was supported by the consulting company Oper&Manson, \
which provided strategic oversight.
"""
text_edited = eunomia.run(text_original)

print(text_edited)
