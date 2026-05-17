
import os
from groq import Groq


def draft_email_for_deal(deal: dict) -> dict:
   
    # Build context from the deal
    risk_reasons = [item["reason"] for item in deal["breakdown"] if item["points"] > 0]
    recent_context = "\n".join([
        f"- {email['date']} ({email['from']}): \"{email['snippet']}\""
        for email in deal["recent_emails"]
    ])
    
    prompt = f"""You are a sales rep writing a brief, warm re-engagement email to a customer who has gone quiet.

    Deal context:
    - Account: {deal['account_name']}
    - Stage: {deal['stage']}
    - Amount: ${deal['amount']:,}
    - Why it's at risk: {'; '.join(risk_reasons[:3])}

    Recent email thread:
    {recent_context}

    Write a short re-engagement email (3-4 sentences max) that:
    - Acknowledges the silence without being pushy
    - References something specific from the deal context
    - Offers a clear, low-friction next step (e.g., quick call, answer questions)

    Tone: professional but warm, helpful not desperate.

    Return ONLY:
    Subject: [subject line]
    Body: [email body]"""

    api_key = os.getenv("GROQ_KEY")
    if not api_key:
        raise ValueError("GROQ_KEY not set. Set it as an environment variable.")
    
    client = Groq(api_key=api_key)
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Fast, high quality, free tier
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}]
    )
    
    # Parse the response
    text = response.choices[0].message.content.strip()
    lines = text.split("\n")
    
    subject = ""
    body_lines = []
    in_body = False
    
    for line in lines:
        if line.startswith("Subject:"):
            subject = line.replace("Subject:", "").strip()
        elif line.startswith("Body:"):
            in_body = True
            body_text = line.replace("Body:", "").strip()
            if body_text:
                body_lines.append(body_text)
        elif in_body:
            body_lines.append(line)
    
    body = "\n".join(body_lines).strip()
    
    # Fallbacks in case parsing fails
    if not subject:
        subject = "Quick check-in on our conversation"
    if not body:
        body = text  # Use the whole response as body
    
    return {"subject": subject, "body": body}