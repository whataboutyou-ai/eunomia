After [installing Eunomia](installation.md), you can start using it by following this quickstart example.

## Basic PII Replacement
The `Orchestra` class is used in Eunomia to orchestrate the execution of multiple instruments on an input text.

```py
from eunomia.orchestra import Orchestra
```

The orchestra can be initialized with a list of instruments. In this example, we will start using the `PiiInstrument` to identify and replace the PII, specifically the email address and person names.

```py
from eunomia.instruments import PiiInstrument

eunomia = Orchestra(
    instruments=[
        PiiInstrument(entities=["EMAIL_ADDRESS", "PERSON"], edit_mode="replace"),
    ]
)
```

Now, we can run the orchestra with the `run` method on any given input text.

```py
text = "Hello, my name is John Doe and my email is john.doe@example.com."

eunomia.run(text)
# Output: "Hello, my name is <PERSON> and my email is <EMAIL_ADDRESS>."
```

## Role-based PII Replacement
Let's say that based on the role of the interacting user, the person names inside texts can be either seen or replaced. We can do this by adding the `RbacInstrument` to the orchestra, and enforcing the PII replacement only for users with a specific role.

```py
from eunomia.instruments import PiiInstrument, RbacInstrument

eunomia = Orchestra(
    instruments=[
        PiiInstrument(entities=["EMAIL_ADDRESS"], edit_mode="replace"),
        RbacInstrument(
            role="specialist",
            instruments=[PiiInstrument(entities=["PERSON"], edit_mode="replace")],
        ),
    ]
)
```

Now, we can run the orchestra while interacting with a `#!python "specialist"` user.

```py
eunomia.run(text, role="specialist")
# Output: "Hello, my name is <PERSON> and my email is <EMAIL_ADDRESS>."
```

While, if we interact with a `#!python "manager"` user, the person names will not be replaced.

```py
eunomia.run(text, role="manager")
# Output: "Hello, my name is John Doe and my email is <EMAIL_ADDRESS>."
```

Congratulations! You've just made your first steps with Eunomia. You can continue to the detailed [documentation](../api/index.md) or explore [all available instruments](../api/instruments/index.md#available-instruments).
