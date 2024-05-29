from presidio_analyzer import AnalyzerEngine

class PiiDetector:
    def __init__(self):
        # Initialize the Presidio Analyzer engine
        self.analyzer = AnalyzerEngine()

    def detect_pii(self, text):
        # Analyze the input text for PII
        results = self.analyzer.analyze(text=text, language="en", entities=None)

        # Extract PII entities from the analysis results
        pii_entities = [entity for entity in results if entity.score > 0]
        print("Pii Detection:::::::::::::",pii_entities)
        return pii_entities


