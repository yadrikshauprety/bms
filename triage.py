def triage(symptom):
    symptom = symptom.lower()
    if "fever" in symptom and "cough" in symptom:
        return "Possible respiratory infection. Seek care if breathing difficulty."
    if "diarrhea" in symptom:
        return "Possible dehydration risk. Drink ORS, seek care if persistent."
    return "Unable to classify. Please seek nearest health center."
