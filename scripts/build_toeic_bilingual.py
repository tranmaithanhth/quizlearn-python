"""Create a verified bilingual, topic-grouped TOEIC pack.

Run:
    python scripts/build_toeic_bilingual.py

Source is data_import/toeic_2000.csv. English example sentences are
rewritten/generated where missing, then *translated* into Vietnamese.
Results are cached to data_import/.toeic_translation_cache.json so an
interruption can be resumed. Uses public Google Translate HTTP endpoint,
which is unofficial and may stop working. Fail closed: do not create a
mislabelled bilingual CSV on translation failure.
"""
import csv
import json
import os
import re
import sys
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "data_import" / "toeic_2000.csv"
OUTPUT = ROOT / "data_import" / "toeic_2000_bilingual.csv"
CACHE = ROOT / "data_import" / ".toeic_translation_cache.json"

# Words can belong to many domains. Prefer a specific business topic
# before putting the rest in the general TOEIC support vocabulary.
TOPICS = [
    ("Tuyển dụng và nhân sự", """applicant candidate recruit recruitment hire hiring interview resume résumé qualification qualified eligible vacancy personnel payroll salary wage compensation resign resignation promotion promote supervisor supervise employee employer colleague workforce staff orientation training trainee intern internship probation incentive bonus retire retirement pension appointment appoint delegate"""),
    ("Hợp đồng và pháp lý", """agreement contract contractual contractor clause provision comply compliance regulation regulatory legal litigation liability obligation warranty guarantee consent authorize authorization permit permission license licensing enforce enforcement policy procedure terms condition dispute negotiate negotiation renewal terminate termination signature sign confidentiality confidential"""),
    ("Kế toán và tài chính", """account accounting accountant audit auditor asset balance billing budget capital cash commission cost credit debit deficit debt deposit expense expenses finance financial forecast fund funding income interest invoice investment investor liability margin overhead payment payroll profit profitable refund reimbursement reimburse revenue tax taxation transaction turnover receivable expenditure fiscal"""),
    ("Vận chuyển và kho vận", """arrival arrive cargo carrier deliver delivery dispatch distribute distribution freight inventory logistics parcel package packaging shipment shipping ship supply supplier warehouse stock storage transit transport transportation tracking route destination customs import export order purchase purchasing shipment delay departure dock container"""),
    ("Khách sạn và du lịch", """accommodation amenity amenities boarding booking reservation reserve check-in check-out cancellation cancel flight airline airport itinerary luggage baggage hospitality hotel motel resort occupancy vacancy guest suite reception receptionist restaurant catering tourism tourist shuttle departure arrival fare sightseeing"""),
    ("Họp và thông báo công việc", """agenda announcement announce attendee attend attendance briefing conference convene discussion meeting minutes memo memorandum notice notification notify postpone reschedule schedule seminar venue workshop presentation proposal report reporter reminder deadline submit submission circulate circulation clarify consensus outline summarize summary respond response correspondence email attachment"""),
    ("Bán hàng và marketing", """advertise advertisement advertising campaign catalog catalogue client consumer customer competitor competitive competition discount endorse marketing market marketplace merchandise outlet prospect prospective publicity promotion promotional purchase retailer sales sale sponsor target trend wholesale brand brochure customer feedback loyalty launch survey demand"""),
    ("Sản xuất và bảo trì", """assemble assembly component defective defect durable equipment facility facilities inspection inspector maintain maintenance manufacture manufacturing machine machinery operate operation output productivity product quality renovation renovate repair replace replacement specification warehouse malfunction installation upgrade production capacity automate automation"""),
    ("Công nghệ và hệ thống", """access attachment compatible compatibility database device digital download install installation internet intranet network password retrieve retrieval software storage backup security server update upgrade wireless technical technology system data program computer platform application website browser file document"""),
    ("Dịch vụ khách hàng", """apologize apology complain complaint customer service satisfaction refund return warranty guarantee inquiry enquiry respond reply request support assistance assist resolve resolution address feedback call center representative courteous courtesy helpful dissatisfaction"""),
    ("Bất động sản và cơ sở vật chất", """apartment lease leasing landlord tenant property premises real estate facility facilities renovation construction construct building architecture architect rental rent mortgage maintenance contractor inspect inspection layout relocate relocation occupy occupancy office floor elevator parking"""),
    ("Quản trị và chiến lược", """allocate allocation annual anticipate assess assessment board chairman chief collaborate collaboration conduct coordinate coordination department director efficient efficiency executive expertise facilitate implement implementation manage management manager mandatory objective organization organize organizational performance personnel policy prioritize priority project strategy strategic supervise target teamwork"""),
    ("Mua sắm và đặt hàng", """acquire acquisition affordable bargain billing catalog catalogue compare complimentary consumer cost customer discount estimate inventory merchandise order outlet payment price pricing purchase procurement quotation quote receipt refund retailer stock supplier warranty wholesale"""),
    ("Nghiên cứu và báo cáo", """analysis analyze analyst annual approximately assumption assess assessment audit calculate calculation conclude conclusion considerable data demonstrate evaluate evaluation evidence experiment finding forecast graph indicate indication investigate investigation measure measurement outcome percentage percent predict prediction research result survey statistic statistics trend vary variable"""),
]
LOOKUP = {}
for topic, words in TOPICS:
    for term in words.lower().split():
        LOOKUP.setdefault(term, topic)

NOUNS = set("""agenda applicant asset audit balance budget candidate capacity catalog client component conference consent contract contractor cost customer database deadline department destination device discussion equipment expense expertise facility forecast fund incentive inspection installation inventory invoice liability luggage margin objective outlet overhead payment personnel policy procedure profit proposal qualification quality receipt refund regulation requirement reservation revenue route schedule seminar shipment specification stock supplier survey transaction venue warehouse warranty""".split())
VERBS = set("""accomplish acquire advertise allocate anticipate appoint assemble authorize automate collaborate compensate comply conduct confirm consult convene coordinate decline delegate demonstrate distribute endorse estimate evaluate exceed expand facilitate fluctuate implement improve install launch maintain manufacture negotiate obtain operate participate permit postpone prioritize promote purchase recommend recruit reimburse renovate repair reschedule resolve retrieve supervise transfer update upgrade""".split())
ADJECTIVES = set("""accurate adequate affordable annual compatible complimentary competitive consecutive considerable defective durable efficient eligible innovative mandatory prospective reliable technical wireless""".split())

SPECIAL_EXAMPLES = {
    "allocate": "The manager will allocate additional funds to the training program.",
    "annual": "The company publishes its annual report in March.",
    "applicant": "Each applicant must submit a resume by Friday.",
    "appoint": "The board will appoint a new director next month.",
    "authorize": "Only the director can authorize this payment.",
    "budget": "The finance department approved the annual budget.",
    "candidate": "The candidate has five years of sales experience.",
    "capacity": "The factory is operating at full capacity.",
    "collaborate": "Our teams collaborate on international projects.",
    "compensate": "The airline will compensate passengers for the delay.",
    "comply": "All employees must comply with safety regulations.",
    "conduct": "The company will conduct a customer survey.",
    "confirm": "Please confirm your reservation by email.",
    "consult": "You should consult the legal department before signing.",
    "contractor": "The contractor completed the repairs ahead of schedule.",
    "coordinate": "Our assistant will coordinate the travel arrangements.",
    "deadline": "The deadline for applications is Friday.",
    "department": "Please contact the accounting department for assistance.",
    "eligible": "Full-time employees are eligible for health benefits.",
    "evaluate": "The committee will evaluate each proposal carefully.",
    "executive": "The executive approved the marketing plan.",
    "implement": "We will implement the new policy next week.",
    "mandatory": "Attendance at the safety training is mandatory.",
    "negotiate": "The two companies will negotiate the contract terms.",
    "personnel": "The personnel department handles recruitment.",
    "procedure": "Please follow the new registration procedure.",
    "promote": "The company plans to promote its new product online.",
    "recruit": "We will recruit more technicians this quarter.",
    "regulation": "The new regulation takes effect in January.",
    "representative": "A customer service representative will contact you.",
    "requirement": "Previous experience is a requirement for this position.",
    "supervise": "A senior engineer will supervise the installation.",
    "postpone": "The organizers decided to postpone the conference.",
    "reschedule": "We need to reschedule tomorrow's meeting.",
    "invoice": "Please pay the invoice within thirty days.",
    "revenue": "The company reported higher revenue this quarter.",
    "shipment": "The shipment is expected to arrive on Monday.",
    "reservation": "Please confirm your hotel reservation.",
    "maintenance": "The equipment requires regular maintenance.",
    "attachment": "Please review the attachment before the meeting.",
}
NOUN_SUFFIXES = ("tion", "sion", "ment", "ness", "ity", "ance", "ence", "ship", "er", "or")
ADJ_SUFFIXES = ("ive", "able", "ible", "ous", "ful", "less", "al", "ent", "ant")
VERB_SUFFIXES = ("ize", "ise", "fy", "ate")

def topic_for(word):
    w = word.lower().strip()
    if w in LOOKUP:
        return LOOKUP[w]
    base = w.removesuffix("s")
    if base in LOOKUP:
        return LOOKUP[base]
    return "Từ vựng bổ trợ TOEIC"

def pos_for(word, provided):
    if provided.strip():
        return provided.strip().split(",")[0].strip()
    w = word.lower()
    if w in NOUNS:
        return "noun"
    if w in VERBS:
        return "verb"
    if w in ADJECTIVES:
        return "adjective"
    if w.endswith(ADJ_SUFFIXES):
        return "adjective"
    if w.endswith(NOUN_SUFFIXES):
        return "noun"
    if w.endswith(VERB_SUFFIXES):
        return "verb"
    return "noun/verb"

def example_for(word, provided, pos, topic):
    if word.lower() in SPECIAL_EXAMPLES:
        return SPECIAL_EXAMPLES[word.lower()]
    provided = " ".join(provided.strip().split())
    if provided and re.search(r"\b" + re.escape(word) + r"\b", provided, re.I):
        return provided
    if len(word.split()) > 1:
        return f"The staff discussed {word} during the meeting."
    pos = pos.lower()
    if pos.startswith("verb") or word.lower() in VERBS:
        return f"Employees should {word} when necessary."
    if pos.startswith("adjective") or word.lower() in ADJECTIVES:
        return f"The manager said the new procedure was {word}."
    return f"The manager discussed {word} in the monthly report."

def load_cache():
    try:
        data = json.loads(CACHE.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}

def save_cache(cache):
    tmp = CACHE.with_suffix(".json.tmp")
    tmp.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(CACHE)

# Unofficial endpoint: use conservative pacing, not aggressive retries.
# Optionally set TOEIC_TRANSLATE_DELAY=3 (seconds) on slow connections.
REQUEST_DELAY = max(1.5, float(os.environ.get("TOEIC_TRANSLATE_DELAY", "2.0")))
_last_request_at = 0.0


def translate(text, cache):
    """Translate and cache one text; stop on HTTP 429 to respect rate limits."""
    global _last_request_at
    text = text.strip()
    if text in cache:
        return cache[text]

    query = urlencode({
        "client": "gtx", "sl": "en", "tl": "vi", "dt": "t", "q": text,
    })
    endpoint = "https://translate.googleapis.com/translate_a/single?" + query
    last_error = None
    for attempt in range(3):
        try:
            wait = REQUEST_DELAY - (time.monotonic() - _last_request_at)
            if wait > 0:
                time.sleep(wait)
            _last_request_at = time.monotonic()
            req = Request(endpoint, headers={"User-Agent": "QuizLearn/1.0"})
            with urlopen(req, timeout=25) as response:
                payload = json.load(response)
            result = "".join(
                piece[0] for piece in payload[0]
                if isinstance(piece, list) and piece and isinstance(piece[0], str)
            ).strip()
            if not result or result.casefold() == text.casefold():
                raise ValueError("No actual Vietnamese translation returned")
            cache[text] = result
            # A crash/interrupt loses at most one successful translation.
            save_cache(cache)
            return result
        except HTTPError as exc:
            if exc.code == 429:
                save_cache(cache)
                retry_after = exc.headers.get("Retry-After")
                hint = (
                    f" The service suggested Retry-After: {retry_after}."
                    if retry_after else ""
                )
                raise RuntimeError(
                    "HTTP 429: translation provider rate-limited this session."
                    + hint
                    + " Stop requests and try again later; your successful "
                    "translations have been saved in the cache."
                ) from exc
            last_error = exc
        except (URLError, OSError, ValueError, IndexError, TypeError) as exc:
            last_error = exc
        if attempt < 2:
            time.sleep(3 * (attempt + 1))

    save_cache(cache)
    raise RuntimeError(
        f"Translation failed for {text!r}: {last_error}. "
        "Completed translations remain cached; rerun later."
    )


def build():
    with SOURCE.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 2000 or len({r["term"].lower() for r in rows}) != 2000:
        raise ValueError("Source must contain 2000 unique entries.")
    cache = load_cache()
    output = []
    columns = ["topic", "term", "meaning_vi", "part_of_speech",
               "example_en", "example_vi", "source_index"]
    for index, row in enumerate(rows, start=1):
        word = row["term"].strip()
        pos = pos_for(word, row["part_of_speech"])
        topic = topic_for(word)
        english_example = example_for(word, row["example"], pos, topic)
        # The first 200 verified VI meanings are preserved from the old pack.
        meaning = (
            row["definition"].strip()
            if row.get("meaning_language") == "vi"
            else translate(row["definition"], cache)
        )
        translated_example = translate(english_example, cache)
        output.append({
            "topic": topic, "term": word, "meaning_vi": meaning,
            "part_of_speech": pos, "example_en": english_example,
            "example_vi": translated_example, "source_index": index,
        })
        if index % 50 == 0:
            save_cache(cache)
            print(f"Processed {index}/2000 vocabulary entries (translations cached)", flush=True)
    if len(output) != 2000 or any(
        not all(item.get(k, "").strip() for k in columns[:-1])
        for item in output
    ):
        raise ValueError("The bilingual pack contains incomplete cards.")
    tmp = OUTPUT.with_suffix(".csv.tmp")
    with tmp.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(output)
    tmp.replace(OUTPUT)
    save_cache(cache)
    print(f"READY: {OUTPUT} ({len(output)} records, each with meaning + examples)")

if __name__ == "__main__":
    try:
        build()
    except (KeyboardInterrupt, RuntimeError, ValueError) as exc:
        print(f"Stopped: {exc}", file=sys.stderr)
        sys.exit(1)
