In this tutorial, we’ll explore practical, real-world applications of Eunomia, focusing specifically on Personal Identifiable Information (PII). We’ll discuss how Eunomia’s capabilities and built-in tools for PII management enable new and innovative use cases.

## What You’ll Discover in this Tutorial

1. **Leveraging Ticketing Data in RAG Systems**  
   How Eunomia enables ticketing data to be safely used as a knowledge source in Retrieval-Augmented Generation (RAG) systems.

2. **Secure Identity-Based Access Control (IDBAC) of User Information in Chatbots**  
   How Eunomia ensures chatbots retrieve user-specific information only when explicitly requested, without exposing data from other users.

---

## Leveraging Ticketing Data in RAG Systems

**Imagine This Scenario**: You are an IT Manager responsible for your company’s IT incident management system. Your team has been handling tickets for years, but you consistently face two major challenges:

- **Duplicate Efforts on Problem Resolution**: Team members often spend hours troubleshooting an issue, only to realize that the same problem was already solved a week earlier by another colleague.
- **Time-Consuming Repetitive Tickets**: Around 60% of your time is wasted on repetitive tickets because end users struggle to perform basic operations on their own.

### The Promise of LLMs: A Beacon of Hope

The advent of Large Language Models (LLMs) offers a game-changing solution. You envision building a chatbot that leverages Retrieval-Augmented Generation (RAG) to search through previously resolved tickets. This would help both your team members and end users:

- **Team Members** could quickly find solutions without duplicating efforts.
- **End Users** could resolve their issues independently, reducing ticket volume.

### The Nightmare of PII Exposure

Tickets in your system contain a wide range of Personal Identifiable Information (PII): names, roles, passwords, and other sensitive data. How can you ensure that sensitive information is never retrieved, avoiding catastrophic data leaks within your company?

### Enter Eunomia

Eunomia’s advanced PII management instruments ensure that sensitive data—such as names, emails, and phone numbers—are effectively safeguarded.

#### Processing Methods

Eunomia can operate at various stages within data pipelines, offering seamless integration with diverse architectures based on the developer's preferred integration point. It can be integrated in both:

1. **In One Go Processing**: Sensitive data is identified and removed in advance, storing a static "sanitized" version of the ticket directly in the database.
2. **On-Demand Processing**: When a ticket is retrieved by the RAG system, Eunomia dynamically cleans the ticket before delivering the response.

This dual approach ensures that PII is never exposed, allowing you to maintain robust data governance while harnessing the full power of LLM-based systems.

#### Example: Original Ticket vs. Processed Ticket

**Original Ticket:**
```plaintext
Ticket ID: #IT-2024-0001
User Information:
Name: John Doe
Email: john.doe@example.com
Phone Number: +1 (555) 123-4567
```

**Processed Ticket:**
```plaintext
Ticket ID: #IT-2024-0001
User Information:
Name: <PERSON>
Email: <EMAIL_ADDRESS>
Phone Number: <PHONE_NUMBER>
```

### Developing the Solution with Eunomia

#### Step 1: Setup

To begin, ensure that Eunomia is installed by following the [installation documentation](../get_started/installation.md). Then, import the necessary components in your script:

```python
from eunomia.orchestra import Orchestra
from eunomia.instruments import PiiInstrument
```

You can find out more information on [`Orchestra`](../api/orchestra.md) and [`PiiInstrument`](../api/instruments/pii_instrument.md) usage in their documentation.

#### Step 2: Configuring Eunomia

Next, configure Eunomia to identify and handle the following types of PII within the tickets:

- Email addresses
- Names and surnames
- Phone numbers

```python
eunomia = Orchestra(
    instruments=[
        PiiInstrument(entities=["EMAIL_ADDRESS", "PERSON", "PHONE_NUMBER"], edit_mode="replace"),
    ]
)
```

#### Step 3: Using Eunomia on input texts

Finally, use the following code to clean PII information from the tickets:
=== "Code"
    ```python
    tickets = [
        """Ticket ID: #IT-2024-0001
        User Information:
        Name: John Doe
        Email: john.doe@example.com
        Phone Number: +1 (555) 123-4567
        Issue Description: The user cannot connect to the VPN.""",
        
        """Ticket ID: #IT-2024-0002
        User Information:
        Name: Jane Smith
        Email: jane.smith@example.com
        Phone Number: +1 (555) 987-6543
        Issue Description: The application crashes on startup."""
    ]

    tickets_cleaned = []

    for ticket_text in tickets:
        # Clean the PII from the current ticket
        ticket_text_cleaned = eunomia.run(ticket_text)

        # Append the sanitized ticket to the cleaned list
        tickets_cleaned.append(ticket_text_cleaned)

    for i, cleaned_ticket in enumerate(tickets_cleaned, start=1):
        print(f"Cleaned Ticket {i}:\n{cleaned_ticket}\n")
    ```
=== "Output"
    ```bash
    Cleaned Ticket 1:
    Ticket ID: #IT-2024-0001
        User Information:
        Name: <PERSON>: <EMAIL_ADDRESS>
        Phone Number: +1 <PHONE_NUMBER>
        Issue Description: The user cannot connect to the VPN.

    Cleaned Ticket 2:
    Ticket ID: #IT-2024-0002
        User Information:
        Name: <PERSON>
        Email: <EMAIL_ADDRESS>
        Phone Number: +1 <PHONE_NUMBER>
        Issue Description: The application crashes on startup.
    ```

---

## Secure Retrieval of User Information in Chatbots

### ID-Based Access Control: Customizing Data Accessibility

Eunomia’s ID-Based Access Control (IDBAC) provides precise control over which information is accessible based on the identity of the requestor.

#### Key components of IDBAC

1. **ID-Based Mechanism**: Each user or entity is assigned a unique identifier.
2. **Document Ownership**: Every document is linked to the unique ID of its owner.
3. **Global PII Masking**: Specific types of PII are consistently masked, regardless of the viewer.
4. **Owner-Specific PII Access**: Owners can view their own PII while it remains masked for others.

#### Step 1: Setup

```python
from eunomia.orchestra import Orchestra
from eunomia.instruments import PiiInstrument, IdbacInstrument
```

You can find out more information on [`Orchestra`](../api/orchestra.md), [`PiiInstrument`](../api/instruments/pii_instrument.md) and [`IdbacInstrument`](../api/instruments/idbac_instrument.md) usage in their documentation.

#### Step 2: Configuring Eunomia

```python
eunomia = Orchestra(
    instruments=[
        IdbacInstrument(
            instruments=[
                PiiInstrument(entities=["PERSON", "EMAIL_ADDRESS", "PHONE_NUMBER"], edit_mode="replace")
            ]
        ),
    ]
)
```

#### Step 3: Using Eunomia on input texts

=== "Code"
    ```python
    tickets = [
        {
            "doc_id": 12345,
            "text": """Ticket ID: #IT-2024-0001
            User Information:
            Name: John Doe
            Email: john.doe@example.com
            Phone Number: +1 (555) 123-4567
            Issue Description: Cannot connect to the company's VPN."""
        },
        {
            "doc_id": 98765,
            "text": """Ticket ID: #IT-2024-0002
            User Information:
            Name: Jane Smith
            Email: jane.smith@example.com
            Phone Number: +1 (555) 987-6543
            Issue Description: Application crashes on startup."""
        }
    ]

    user_requests = [
        {"user_id": 12345, "doc_id": 12345},  # Matching user and document ID
        {"user_id": 12345, "doc_id": 98765}   # Non-matching user and document ID
    ]

    for request in user_requests:
        user_id = request["user_id"]
        doc_id = request["doc_id"]

        # Retrieve and process the ticket text based on IDBAC rules
        for ticket in tickets:
            if ticket["doc_id"] == doc_id:
                processed_text = eunomia.run(ticket["text"], user_id=user_id, doc_id=doc_id)

                # Output the results
                access_status = "Matching IDs" if user_id == doc_id else "Non-Matching IDs"
                print(f"Access Status: {access_status}")
                print(f"User ID: {user_id}, Document ID: {doc_id}")
                print(f"Processed Ticket:\n{processed_text}\n")

    ```
=== "Output"
    ```bash
    Access Status: Matching IDs
    User ID: 12345, Document ID: 12345
    Processed Ticket:
    Ticket ID: #IT-2024-0001
            User Information:
            Name: John Doe
            Email: john.doe@example.com
            Phone Number: +1 (555) 123-4567
            Issue Description: Cannot connect to the company's VPN.

    Access Status: Non-Matching IDs
    User ID: 12345, Document ID: 98765
    Processed Ticket:
    Ticket ID: #IT-2024-0002
            User Information:
            Name: <PERSON>
            <PERSON>: <EMAIL_ADDRESS>
            Phone Number: +1 <PHONE_NUMBER>
            Issue Description: Application crashes on startup.
    ```

---

Eunomia transforms data workflows by ensuring robust data protection while enabling innovative applications. Explore its capabilities and see how it can revolutionize your projects.
