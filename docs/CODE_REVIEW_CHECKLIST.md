# Code Review Checklist

- [ ] **Data Integrity**: Ensure `city_code` is consistently 6 digits (zero-padded).
- [ ] **Error Handling**: Are external API calls (e-Stat, Ollama) wrapped in try/except?
- [ ] **Performance**: Is `nightly_scoring.py` efficient for 1,918 records? (Currently loop-based, might need async or bulk insert).
- [ ] **Security**: Are DB passwords loaded from `.env`? (Yes, via `backend/config.py`).
- [ ] **AI Fallback**: If BERT/Ollama fails, does the score default gracefully?
