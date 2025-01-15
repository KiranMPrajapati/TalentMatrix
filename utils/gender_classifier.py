import re
from transformers import pipeline



class GenderClassifier: 
    """
    Gender classfier model
    """
    def __init__(self, model_name="padmajabfrl/Gender-Classification"):
        self.model_name = model_name
        self.classifier = pipeline("text-classification", model=self.model_name)


    def predict_gender_from_model(self, text):
        result = self.classifier(text)
        return result[0]['label']
    
    def detect_gender_from_regex(self, text):
        male_pronouns = r"\b(he|him|his)\b"
        female_pronouns = r"\b(she|her|hers)\b"
        
        male_count = len(re.findall(male_pronouns, text, flags=re.IGNORECASE))
        female_count = len(re.findall(female_pronouns, text, flags=re.IGNORECASE))

        if male_count > female_count:
            return "Male"
        elif female_count > male_count:
            return "Female"
        else:
            return "Unknown"
        
    def __call__(self, text):
        gender_from_model = self.predict_gender_from_model(text)
        gender_from_regex = self.detect_gender_from_regex(text)

        if gender_from_model == gender_from_regex:
            return gender_from_regex
        else:
            return "Unknown"

