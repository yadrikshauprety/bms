from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from triage import triage
from db import get_due_vaccines

app = Flask(__name__)

@app.route("/whatsapp", methods=["POST"])
def whatsapp():
    msg = request.form.get("Body")
    user = request.form.get("From")

    response = MessagingResponse()

    if "symptom" in msg.lower():
        triage_result = triage(msg)
        response.message(f"🩺 Triage Result: {triage_result}")
    elif "vaccines" in msg.lower():
        vaccines = get_due_vaccines(user)
        response.message(f"💉 Vaccines on record: {vaccines}")
    else:
        response.message("Hi! Send 'symptom: <your issue>' or 'vaccines' to get started.")

    return str(response)

if __name__ == "__main__":
    app.run(port=5000)
