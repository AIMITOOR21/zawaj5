# Zawaj — زواج

**AI-Powered Pre-Marriage Compatibility for Pakistani Families**

Zawaj is an end-to-end Streamlit web application that helps Pakistani couples
and families evaluate marriage compatibility before the nikkah. It combines
three AI paradigms in one system:

- **Predictive AI** — XGBoost models score compatibility across seven life domains
- **Explainable AI** — SHAP, LIME and DiCE explain every prediction transparently
- **Generative AI** — LLM-generated advice, scenario narratives and contradiction detection

---

## Two Core Modules

### 1. Partner Compatibility Questionnaire
Both partners play through 20 culturally-grounded branching scenarios that reveal
**revealed preferences** — what they'd actually choose under realistic Pakistani
family situations, not what they claim to believe.

### 2. In-Laws Questionnaire — the novel core
Instead of inferring family traits from a fake graph, **real family members**
(mother-in-law, father-in-law, sister-in-law) answer their own scenarios.
The system then performs **triangle analysis**:

- What the **girl** hopes her in-laws will be like
- What the **boy** claims about his family
- What the **in-laws themselves** actually say

Contradictions between what the boy claims and what the family actually
believes are surfaced with severity ratings. This is the heart of Zawaj.

---

## Running Locally

```bash
# 1. Clone / download
cd Zawaj

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Add OpenAI API key for real LLM advice
echo "OPENAI_API_KEY=sk-your-key-here" > .env

# 4. Launch
streamlit run app.py
```

The app auto-trains the XGBoost model on first run (takes ~30 seconds).

---

## Project Structure

```
Zawaj/
├── app.py                          # Home / landing
├── config.py                       # Theme, domains, ensemble weights
├── requirements.txt
│
├── pages/
│   ├── 1_Scenario_Assessment.py    # Partner questionnaire
│   ├── 2_InLaws_Questionnaire.py   # In-laws + triangle analysis
│   ├── 3_Results_Dashboard.py      # Full compatibility view + SHAP/LIME
│   ├── 4_Conflict_Simulation.py    # LLM multi-agent conflict simulation
│   └── 5_Improvement_Plan.py       # DiCE counterfactuals + LLM advice
│
├── data/
│   ├── scenarios.json              # Partner scenarios
│   ├── inlaw_scenarios.json        # In-law / boy-claim / girl-hope scenarios
│   ├── generate_dataset.py         # Synthetic training data generator
│   └── preprocess.py
│
├── models/
│   ├── compatibility_model.py      # XGBoost wrapper
│   ├── ensemble.py                 # Weighted ensemble score
│   └── train.py                    # Training pipeline
│
├── ai/
│   ├── inlaw_analysis.py           # Triangle contradiction detection
│   ├── conflict_simulation.py      # Multi-agent LLM conflict simulation
│   ├── advice_generator.py         # LLM improvement-plan generation
│   ├── llm_client.py               # OpenAI wrapper
│   └── scenario_generator.py
│
├── xai/
│   ├── shap_explainer.py           # Global + local SHAP
│   ├── lime_explainer.py           # LIME for individual predictions
│   └── counterfactual.py           # DiCE counterfactual suggestions
│
└── utils/
    ├── scoring.py
    └── visualization.py            # All Plotly charts (pink theme)
```

---

## Tech Stack

**Core:** Python · Streamlit · pandas · NumPy
**ML:** scikit-learn · XGBoost · imbalanced-learn (SMOTE)
**XAI:** SHAP · LIME · DiCE
**GenAI:** OpenAI API (GPT) · HuggingFace Transformers-ready
**Viz:** Plotly · matplotlib
**Design:** Playfair Display + Poppins · Pink/white wedding theme

---

## Theme

Zawaj uses a pink & white wedding palette:
- **Rose** `#D4577A` — primary
- **Blush** `#F8D7DE` — secondary
- **Gold** `#C9A96E` — accent
- **Deep maroon** `#5C2A3E` — headings
- Playfair Display (serif) for titles, Poppins (sans-serif) for body

CSS animations (`fadeInUp`, `fadeInDown`, floating hearts) are applied
throughout for a warm, celebratory feel.

---

## Team

Built for the AI-201 course project, BSSE program.

- Aiman Fatima
- Sania Saeed
- Khadija

**Instructor:** Dr. Umara Zahid

---

## License

Proprietary — academic / educational use.
