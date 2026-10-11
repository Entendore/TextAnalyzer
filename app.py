#!/usr/bin/env python3
"""
Text Analyzer Pro — Comprehensive text analysis for PDF books, emails, and any text.
Built with PySide6 and Python.
"""

import sys, os, re, math, string, html
from collections import Counter
from email import policy as email_policy
from email.parser import BytesParser

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit, QTabWidget, QFileDialog,
    QGroupBox, QGridLayout, QTableWidget, QTableWidgetItem,
    QSplitter, QHeaderView, QComboBox, QSpinBox, QCheckBox,
    QLineEdit, QMessageBox, QFrame, QScrollArea, QSizePolicy,
    QProgressBar
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QColor, QAction, QPalette, QTextCharFormat, QTextCursor

try:
    import matplotlib
    matplotlib.use("QtAgg")
    from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    HAS_MPL = True
except ImportError:
    HAS_MPL = False

try:
    import numpy as np
    HAS_NP = True
except ImportError:
    HAS_NP = False

try:
    from PyPDF2 import PdfReader
    HAS_PDF = True
except ImportError:
    HAS_PDF = False

# ────────────────────── Constants ──────────────────────

STOP_WORDS = {
    "i","me","my","myself","we","our","ours","ourselves","you","your","yours",
    "yourself","yourselves","he","him","his","himself","she","her","hers",
    "herself","it","its","itself","they","them","their","theirs","themselves",
    "what","which","who","whom","this","that","these","those","am","is","are",
    "was","were","be","been","being","have","has","had","having","do","does",
    "did","doing","a","an","the","and","but","if","or","because","as","until",
    "while","of","at","by","for","with","about","against","between","through",
    "during","before","after","above","below","to","from","up","down","in",
    "out","on","off","over","under","again","further","then","once","here",
    "there","when","where","why","how","all","both","each","few","more","most",
    "other","some","such","no","nor","not","only","own","same","so","than",
    "too","very","s","t","can","will","just","don","should","now","d","ll",
    "m","o","re","ve","y","ain","aren","couldn","didn","doesn","hadn","hasn",
    "haven","isn","ma","mightn","mustn","needn","shan","shouldn","wasn",
    "weren","won","wouldn","also","would","could","may","might","shall",
    "must","into","any","get","got","let","go","went","gone","come","came",
    "take","took","know","knew","think","thought","say","said","tell","told",
    "see","saw","want","one","two","much","many","still","even","back","way",
    "well","first","last","long","little","old","make","made","like",
}

POSITIVE_WORDS = {
    "good","great","excellent","wonderful","amazing","love","loved","happy",
    "happiness","joy","joyful","beautiful","fantastic","brilliant","superb",
    "outstanding","perfect","delightful","pleasant","marvelous","terrific",
    "awesome","nice","best","better","positive","success","successful","win",
    "winning","hope","hopeful","bright","cheerful","glad","pleased",
    "satisfied","enjoy","enjoyed","enjoyable","impressive","remarkable",
    "extraordinary","magnificent","splendid","fine","lovely","charming",
    "grateful","thankful","appreciate","comfortable","kind","generous",
    "gentle","warm","friendly","caring","thoughtful","sincere","genuine",
    "honest","trust","reliable","confident","strong","brave","courageous",
    "bold","determined","motivated","inspired","inspiring","creative",
    "innovative","progress","achievement","accomplish","triumph","victory",
    "celebrate","praise","recommend","approve","accept","welcome","support",
    "helpful","useful","valuable","worthy","meaningful","significant",
    "important","powerful","effective","efficient","productive","beneficial",
    "advantage","favorable","fortunate","lucky","bless","blessing","miracle",
    "wonder","peace","peaceful","calm","serene","relax","relaxing","easy",
    "simple","clear","pure","clean","fresh","renew","restore","heal",
    "healthy","vibrant","energetic","lively","dynamic","free","freedom",
    "empower","uplift","enlighten","exciting","passion","passionate","dream",
    "optimistic","enthusiasm","eager","devoted","dedicated","committed",
    "loyal","faithful","wisdom","wise","smart","intelligent","clever",
    "talent","talented","gifted","skilled","expert","capable","exceptional",
    "supreme","treasure","award","honor","glory","noble","grand","epic",
    "legendary","classic","abundant","prosper","prosperity","flourish",
    "thrive","grow","growth","improve","improvement","advance","develop",
    "evolve","transform","overcome","conquer","succeed","fulfill","complete",
    "harmony","balance","unity","united","cooperation","collaborate",
    "share","giving","contribute","compassion","empathy","forgive",
    "forgiveness","grace","dignity","respect","admire","adore","cherish",
    "embrace","rejoice","laugh","laughter","smile","bliss","radiance",
    "glow","shine","sparkle","magnificence","elegance","beauty","gorgeous",
    "stunning","breathtaking","spectacular","phenomenal","incredible",
    "astonishing","marvelous","wondrous","sublime","delicious","enchanting",
    "fascinating","glorious","heavenly","incredible","joyous","majestic",
    "precious","radiant","resplendent","sensational","stellar","superb",
    "thrilling","transcendent","vibrant","zesty",
}

NEGATIVE_WORDS = {
    "bad","terrible","horrible","awful","poor","worst","worse","hate","hated",
    "hatred","ugly","sad","unhappy","angry","fear","fearful","pain","painful",
    "hurt","damage","destroy","destruction","ruin","fail","failure","lose",
    "loss","wrong","error","mistake","evil","wicked","cruel","cruelty","harsh",
    "severe","cold","dark","darkness","gloom","doom","despair","hopeless",
    "helpless","weak","weakness","fragile","broken","damaged","defective",
    "flawed","inferior","mediocre","cheap","worthless","useless","pointless",
    "meaningless","empty","reject","rejection","deny","denial","refuse",
    "conflict","fight","battle","war","struggle","suffer","suffering",
    "misery","distress","agony","torment","torture","abuse","violence",
    "violent","aggressive","hostile","bitter","resentment","jealous",
    "jealousy","envy","greed","greedy","selfish","arrogant","arrogance",
    "prejudice","bias","discrimination","unfair","unjust","inequality",
    "oppression","suppress","corrupt","corruption","fraud","scam","cheat",
    "deceive","deception","deceit","lie","liar","dishonest","false","fake",
    "betray","betrayal","abandon","abandonment","neglect","ignore",
    "indifferent","apathy","lazy","careless","reckless","irresponsible",
    "foolish","stupid","dumb","ignorant","confuse","confusion","chaos",
    "disorder","mess","dirty","filthy","disgusting","gross","repulsive",
    "revolting","toxic","poison","waste","decay","deteriorate","decline",
    "decrease","diminish","shrink","fade","vanish","death","dead","die",
    "dying","kill","murder","fatal","lethal","dangerous","risky","hazardous",
    "threat","threaten","warning","alarm","panic","anxiety","anxious",
    "stress","stressful","tension","pressure","burden","heavy","obstacle",
    "barrier","block","prevent","restrict","limit","trap","prison","victim",
    "sacrifice","exploit","misuse","blunder","disaster","catastrophe",
    "tragedy","tragic","crisis","emergency","critical","extreme","obsession",
    "addiction","addicted","vulnerable","insecure","worried","nervous",
    "tense","uneasy","uncomfortable","awkward","embarrass","embarrassment",
    "shame","guilty","guilt","regret","remorse","sorrow","grief","mourn",
    "lament","cry","lonely","loneliness","isolated","alone","desolate",
    "barren","bleak","dismal","dreary","tedious","boring","dull",
    "monotonous","tiresome","exhausting","overwhelming","manipulate",
    "manipulation","trick","steal","theft","rob","assault","attack",
    "invade","oppress","persecute","bully","harass","intimidate","coerce",
    "extort","blackmail","punish","punishment","penalty","convict","crime",
    "criminal","illegal","unlawful","violate","violation","terror",
    "terrorism","horrendous","atrocious","abysmal","dreadful","appalling",
    "hideous","monstrous","sinister","malicious","vicious","ruthless",
    "savage","brutal","bloody","grim","somber","melancholy","depressed",
    "depression","miserable","wretched","pathetic","pitiful","tragic",
    "devastating","catastrophic","ruinous","calamitous","dire","ominous",
    "menacing","perilous","treacherous","insidious","nefarious","vile",
    "contempt","contemptible","loathsome","abhorrent","odious","repugnant",
    "despicable","detestable","heinous","outrage","scandal","disgrace",
    "humiliate","humiliation","degrade","degradation","deprive","stifle",
    "suffocate","drown","overwhelm","crush","smash","shatter","demolish",
    "eradicate","exterminate","annihilate","obliterate",
}

# ────────────────────── Core Analyzer ──────────────────────

class TextAnalyzer:
    """Core text analysis engine."""

    def __init__(self, text: str):
        self.raw_text = text
        self.words = self._extract_words(text)
        self.sentences = self._extract_sentences(text)
        self.paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
        self.char_count = len(text)
        self.char_count_no_spaces = len(text.replace(" ", "").replace("\n", "").replace("\t", ""))
        self.word_count = len(self.words)
        self.sentence_count = len(self.sentences)
        self.paragraph_count = len(self.paragraphs)
        self.unique_words = set(w.lower() for w in self.words)
        self.unique_word_count = len(self.unique_words)

    @staticmethod
    def _extract_words(text):
        return re.findall(r"\b[a-zA-Z'-]+\b", text)

    @staticmethod
    def _extract_sentences(text):
        sents = re.split(r'(?<=[.!?])\s+', text)
        return [s.strip() for s in sents if s.strip() and len(s.strip()) > 2]

    @staticmethod
    def count_syllables(word: str) -> int:
        word = word.lower().strip()
        if not word:
            return 0
        if len(word) <= 3:
            return 1
        word = re.sub(r"(?:[^laeiouy]es|ed|[^laeiouy]e)$", "", word)
        word = re.sub(r"^y", "", word)
        vowels = re.findall(r"[aeiouy]{1,2}", word)
        return max(1, len(vowels))

    def avg_word_length(self):
        if not self.words:
            return 0
        return sum(len(w) for w in self.words) / len(self.words)

    def avg_sentence_length(self):
        if not self.sentences:
            return 0
        return self.word_count / max(1, self.sentence_count)

    def avg_syllables_per_word(self):
        if not self.words:
            return 0
        return sum(self.count_syllables(w) for w in self.words) / len(self.words)

    def total_syllables(self):
        return sum(self.count_syllables(w) for w in self.words)

    def complex_words(self):
        return [w for w in self.words if self.count_syllables(w) >= 3]

    def reading_time(self):
        """Minutes at ~250 wpm."""
        return self.word_count / 250

    def speaking_time(self):
        """Minutes at ~150 wpm."""
        return self.word_count / 150

    def lexical_diversity(self):
        if not self.words:
            return 0
        return self.unique_word_count / self.word_count

    def word_frequency(self, top_n=50, remove_stopwords=True):
        freq = Counter(w.lower() for w in self.words)
        if remove_stopwords:
            freq = Counter({w: c for w, c in freq.items() if w not in STOP_WORDS})
        return freq.most_common(top_n)

    def bigram_frequency(self, top_n=20):
        bigrams = []
        for i in range(len(self.words) - 1):
            bigrams.append((self.words[i].lower(), self.words[i+1].lower()))
        return Counter(bigrams).most_common(top_n)

    def char_frequency(self):
        return Counter(c.lower() for c in self.raw_text if c.isalpha())

    def readability_scores(self):
        w = max(1, self.word_count)
        s = max(1, self.sentence_count)
        total_syl = self.total_syllables()
        complex_w = len(self.complex_words())

        # Flesch Reading Ease
        flesch = 206.835 - 1.015 * (w / s) - 84.6 * (total_syl / w)

        # Flesch-Kincaid Grade
        fk_grade = 0.39 * (w / s) + 11.8 * (total_syl / w) - 15.59

        # Gunning Fog
        fog = 0.4 * ((w / s) + 100 * (complex_w / w))

        # ARI
        chars = self.char_count_no_spaces
        ari = 4.71 * (chars / w) + 0.5 * (w / s) - 21.43

        # Coleman-Liau
        l = (chars / w) * 100
        s_val = (s / w) * 100
        coleman = 0.0588 * l - 0.296 * s_val - 15.8

        return {
            "Flesch Reading Ease": round(flesch, 2),
            "Flesch-Kincaid Grade": round(fk_grade, 2),
            "Gunning Fog Index": round(fog, 2),
            "Automated Readability Index": round(ari, 2),
            "Coleman-Liau Index": round(coleman, 2),
            "Avg Syllables per Word": round(self.avg_syllables_per_word(), 3),
        }

    @staticmethod
    def flesch_label(score):
        if score >= 90: return "Very Easy (5th grade)"
        if score >= 80: return "Easy (6th grade)"
        if score >= 70: return "Fairly Easy (7th grade)"
        if score >= 60: return "Standard (8th-9th grade)"
        if score >= 50: return "Fairly Difficult (10th-12th grade)"
        if score >= 30: return "Difficult (College)"
        return "Very Difficult (Graduate)"

    def sentiment_analysis(self):
        pos_hits = []
        neg_hits = []
        for w in self.words:
            wl = w.lower()
            if wl in POSITIVE_WORDS:
                pos_hits.append(wl)
            elif wl in NEGATIVE_WORDS:
                neg_hits.append(wl)

        total = len(pos_hits) + len(neg_hits)
        if total == 0:
            score = 0
            label = "Neutral"
        else:
            score = (len(pos_hits) - len(neg_hits)) / total
            if score > 0.2:
                label = "Positive"
            elif score > 0.05:
                label = "Slightly Positive"
            elif score < -0.2:
                label = "Negative"
            elif score < -0.05:
                label = "Slightly Negative"
            else:
                label = "Neutral"

        pos_freq = Counter(pos_hits).most_common(15)
        neg_freq = Counter(neg_hits).most_common(15)

        return {
            "score": round(score, 4),
            "label": label,
            "positive_count": len(pos_hits),
            "negative_count": len(neg_hits),
            "positive_words": pos_freq,
            "negative_words": neg_freq,
        }

    def longest_words(self, n=10):
        return sorted(set(self.words), key=len, reverse=True)[:n]

    def shortest_words(self, n=10):
        return sorted(set(self.words), key=len)[:n]

    def punctuation_stats(self):
        counts = {}
        for p in string.punctuation:
            c = self.raw_text.count(p)
            if c > 0:
                counts[p] = c
        return counts

    def digit_count(self):
        return sum(c.isdigit() for c in self.raw_text)

# ────────────────────── File Loaders ──────────────────────

def load_pdf(path):
    if not HAS_PDF:
        raise ImportError("PyPDF2 is not installed. Run: pip install PyPDF2")
    reader = PdfReader(path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text()
        if text:
            pages.append(text)
    return "\n\n".join(pages), len(reader.pages)

def load_email(path):
    with open(path, "rb") as f:
        msg = BytesParser(policy=email_policy.default).parse(f)
    parts = []
    subject = str(msg.get("Subject", ""))
    sender = str(msg.get("From", ""))
    date = str(msg.get("Date", ""))
    if subject: parts.append(f"Subject: {subject}")
    if sender: parts.append(f"From: {sender}")
    if date: parts.append(f"Date: {date}")
    parts.append("")

    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            if ct == "text/plain":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    body = payload.decode(charset, errors="replace")
                    break
            elif ct == "text/html":
                payload = part.get_payload(decode=True)
                if payload:
                    charset = part.get_content_charset() or "utf-8"
                    html_text = payload.decode(charset, errors="replace")
                    body = re.sub(r"<[^>]+>", " ", html_text)
                    body = html.unescape(body)
    else:
        payload = msg.get_payload(decode=True)
        if payload:
            charset = msg.get_content_charset() or "utf-8"
            ct = msg.get_content_type()
            raw = payload.decode(charset, errors="replace")
            if "html" in ct:
                body = re.sub(r"<[^>]+>", " ", raw)
                body = html.unescape(body)
            else:
                body = raw

    parts.append(body.strip())
    return "\n".join(parts), None

def load_text_file(path):
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            with open(path, "r", encoding=enc) as f:
                return f.read(), None
        except (UnicodeDecodeError, FileNotFoundError):
            continue
    raise ValueError(f"Cannot decode file: {path}")

# ────────────────────── Matplotlib Canvas ──────────────────────

if HAS_MPL:
    class MplCanvas(FigureCanvas):
        def __init__(self, parent=None, width=6, height=4, dpi=100):
            self.fig = Figure(figsize=(width, height), dpi=dpi, tight_layout=True)
            self.fig.patch.set_facecolor("#2b2b3d")
            super().__init__(self.fig)
            self.ax = self.fig.add_subplot(111)
            self.ax.set_facecolor("#2b2b3d")
            self.tick_color = "#c0c0d0"
            self.label_color = "#e0e0f0"
            self.setMinimumHeight(250)
else:
    class MplCanvas(QWidget):
        def __init__(self, *a, **kw):
            super().__init__()
            lay = QVBoxLayout(self)
            lay.addWidget(QLabel("Install matplotlib for charts:\npip install matplotlib"))

# ────────────────────── Stat Card Widget ──────────────────────

class StatCard(QFrame):
    def __init__(self, title, value, subtitle="", parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            StatCard {
                background: #2b2b3d;
                border: 1px solid #3d3d5c;
                border-radius: 10px;
                padding: 8px;
            }
        """)
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lbl_title = QLabel(title)
        lbl_title.setStyleSheet("color:#8888aa; font-size:11px; font-weight:bold;")
        lbl_title.setWordWrap(True)
        lay.addWidget(lbl_title)
        lbl_val = QLabel(str(value))
        lbl_val.setStyleSheet("color:#e0e0f0; font-size:22px; font-weight:bold;")
        lay.addWidget(lbl_val)
        if subtitle:
            lbl_sub = QLabel(subtitle)
            lbl_sub.setStyleSheet("color:#6a6a8a; font-size:10px;")
            lbl_sub.setWordWrap(True)
            lay.addWidget(lbl_sub)

# ────────────────────── Summary Tab ──────────────────────

class SummaryTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.main_layout = QVBoxLayout(self.container)
        self.main_layout.setSpacing(16)
        self.scroll.setWidget(self.container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0,0,0,0)
        outer.addWidget(self.scroll)
        self.cards = []

    def update_analysis(self, analyzer: TextAnalyzer):
        for c in self.cards:
            self.main_layout.removeWidget(c)
            c.deleteLater()
        self.cards.clear()

        # ── Basic Stats ──
        grp = QGroupBox("📊  Basic Statistics")
        grp.setStyleSheet("QGroupBox{color:#b0b0d0; font-weight:bold; font-size:13px; border:1px solid #3d3d5c; border-radius:8px; margin-top:10px; padding-top:18px;}")
        grid = QGridLayout(grp)
        grid.setSpacing(10)

        stats = [
            ("Total Words", f"{analyzer.word_count:,}", "Tokens found in text"),
            ("Characters", f"{analyzer.char_count:,}", "Including spaces"),
            ("Characters (no spaces)", f"{analyzer.char_count_no_spaces:,}", ""),
            ("Sentences", f"{analyzer.sentence_count:,}", ""),
            ("Paragraphs", f"{analyzer.paragraph_count:,}", "Separated by blank lines"),
            ("Unique Words", f"{analyzer.unique_word_count:,}", f"Diversity: {analyzer.lexical_diversity():.3f}"),
            ("Avg Word Length", f"{analyzer.avg_word_length():.1f}", "characters"),
            ("Avg Sentence Length", f"{analyzer.avg_sentence_length():.1f}", "words per sentence"),
            ("Reading Time", f"{analyzer.reading_time():.1f} min", "~250 wpm"),
            ("Speaking Time", f"{analyzer.speaking_time():.1f} min", "~150 wpm"),
            ("Complex Words", f"{len(analyzer.complex_words()):,}", "3+ syllables"),
            ("Digits", f"{analyzer.digit_count():,}", ""),
        ]

        for i, (title, value, sub) in enumerate(stats):
            card = StatCard(title, value, sub)
            grid.addWidget(card, i // 4, i % 4)
            self.cards.append(card)
        self.main_layout.addWidget(grp)
        self.cards.append(grp)

        # ── Longest Words ──
        grp2 = QGroupBox("📏  Longest Words")
        grp2.setStyleSheet(grp.styleSheet())
        h = QHBoxLayout(grp2)
        for w in analyzer.longest_words(8):
            lbl = QLabel(w)
            lbl.setStyleSheet("color:#7eb8da; font-family:monospace; font-size:12px; padding:4px 8px; background:#22223a; border-radius:4px;")
            h.addWidget(lbl)
        self.main_layout.addWidget(grp2)
        self.cards.append(grp2)

        # ── Top Words mini chart ──
        if HAS_MPL:
            grp3 = QGroupBox("📈  Top 15 Words (excluding stop words)")
            grp3.setStyleSheet(grp.styleSheet())
            vl = QVBoxLayout(grp3)
            canvas = MplCanvas(self, width=8, height=3.5)
            ax = canvas.ax
            top = analyzer.word_frequency(15, remove_stopwords=True)
            if top:
                words_list = [w for w, _ in top][::-1]
                counts = [c for _, c in top][::-1]
                colors = []
                cmap = matplotlib.colormaps.get_cmap("viridis")
                for i in range(len(counts)):
                    colors.append(cmap(i / max(1, len(counts) - 1)))
                ax.barh(words_list, counts, color=colors, edgecolor="#444466", linewidth=0.5)
                ax.set_xlabel("Frequency", color=canvas.label_color, fontsize=10)
                ax.tick_params(colors=canvas.tick_color, labelsize=9)
                for spine in ax.spines.values():
                    spine.set_color("#3d3d5c")
            vl.addWidget(canvas)
            self.main_layout.addWidget(grp3)
            self.cards.append(grp3)

        self.main_layout.addStretch()

# ────────────────────── Word Frequency Tab ──────────────────────

class WordFrequencyTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.analyzer = None
        layout = QVBoxLayout(self)

        # Controls
        ctrl = QHBoxLayout()
        ctrl.addWidget(QLabel("Top N words:"))
        self.spin_n = QSpinBox()
        self.spin_n.setRange(5, 200)
        self.spin_n.setValue(30)
        ctrl.addWidget(self.spin_n)
        self.chk_stop = QCheckBox("Remove stop words")
        self.chk_stop.setChecked(True)
        ctrl.addWidget(self.chk_stop)
        btn = QPushButton("Refresh")
        btn.setStyleSheet("background:#4a4a6a; color:white; padding:5px 15px; border-radius:5px;")
        btn.clicked.connect(self.refresh)
        ctrl.addWidget(btn)
        ctrl.addStretch()
        layout.addLayout(ctrl)

        # Splitter: chart + table
        splitter = QSplitter(Qt.Horizontal)
        self.chart_area = QWidget()
        self.chart_layout = QVBoxLayout(self.chart_area)
        self.chart_layout.setContentsMargins(0,0,0,0)
        self.canvas = MplCanvas(self, width=7, height=5)
        self.chart_layout.addWidget(self.canvas)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(["Rank", "Word", "Frequency"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setAlternatingRowColors(True)
        self.table.setStyleSheet("""
            QTableWidget { background:#22223a; color:#d0d0e0; gridline-color:#3d3d5c; alternate-background-color:#2a2a44; }
            QHeaderView::section { background:#2b2b3d; color:#a0a0c0; padding:4px; border:1px solid #3d3d5c; }
        """)

        splitter.addWidget(self.chart_area)
        splitter.addWidget(self.table)
        splitter.setSizes([500, 300])
        layout.addWidget(splitter)

        # Bigrams
        self.bigram_group = QGroupBox("Top Bigrams (2-word phrases)")
        self.bigram_group.setStyleSheet("QGroupBox{color:#b0b0d0; font-weight:bold; border:1px solid #3d3d5c; border-radius:8px; margin-top:10px; padding-top:18px;}")
        self.bigram_layout = QHBoxLayout(self.bigram_group)
        layout.addWidget(self.bigram_group)

    def update_analysis(self, analyzer: TextAnalyzer):
        self.analyzer = analyzer
        self.refresh()

    def refresh(self):
        if not self.analyzer:
            return
        a = self.analyzer
        n = self.spin_n.value()
        rm_stop = self.chk_stop.isChecked()
        top = a.word_frequency(n, remove_stopwords=rm_stop)

        # Chart
        ax = self.canvas.ax
        ax.clear()
        if top:
            wl = [w for w, _ in top][::-1]
            cl = [c for _, c in top][::-1]
            cmap = matplotlib.colormaps.get_cmap("plasma")
            colors = [cmap(i / max(1, len(cl) - 1)) for i in range(len(cl))]
            ax.barh(wl, cl, color=colors, edgecolor="#444466", linewidth=0.5)
            ax.set_xlabel("Frequency", color=self.canvas.label_color, fontsize=10)
            ax.set_title(f"Top {len(top)} Word Frequencies", color=self.canvas.label_color, fontsize=12)
            ax.tick_params(colors=self.canvas.tick_color, labelsize=8)
            for spine in ax.spines.values():
                spine.set_color("#3d3d5c")
        self.canvas.draw()

        # Table
        self.table.setRowCount(len(top))
        for i, (word, count) in enumerate(top):
            self.table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            self.table.setItem(i, 1, QTableWidgetItem(word))
            self.table.setItem(i, 2, QTableWidgetItem(str(count)))
        self.table.resizeColumnsToContents()

        # Bigrams
        while self.bigram_layout.count():
            item = self.bigram_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        bigrams = a.bigram_frequency(15)
        for (w1, w2), cnt in bigrams:
            lbl = QLabel(f"{w1} {w2} ({cnt})")
            lbl.setStyleSheet("color:#c0a0e0; font-size:11px; padding:3px 8px; background:#22223a; border-radius:4px;")
            self.bigram_layout.addWidget(lbl)

# ────────────────────── Readability Tab ──────────────────────

class ReadabilityTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.container = QWidget()
        self.lay = QVBoxLayout(self.container)
        self.lay.setSpacing(12)
        self.scroll.setWidget(self.container)
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0,0,0,0)
        outer.addWidget(self.scroll)
        self.widgets = []

    def update_analysis(self, analyzer: TextAnalyzer):
        for w in self.widgets:
            self.lay.removeWidget(w)
            w.deleteLater()
        self.widgets.clear()

        scores = analyzer.readability_scores()

        # Flesch gauge
        if HAS_MPL:
            grp = QGroupBox("📖  Flesch Reading Ease Score")
            grp.setStyleSheet("QGroupBox{color:#b0b0d0; font-weight:bold; font-size:13px; border:1px solid #3d3d5c; border-radius:8px; margin-top:10px; padding-top:18px;}")
            vl = QVBoxLayout(grp)
            canvas = MplCanvas(self, width=7, height=3)
            ax = canvas.ax
            flesch = scores["Flesch Reading Ease"]
            clamped = max(0, min(100, flesch))

            # Draw gauge
            ax.set_xlim(-0.5, 1.5)
            ax.set_ylim(-0.3, 0.7)
            ax.set_aspect("equal")
            ax.axis("off")

            import matplotlib.patches as mpatches
            colors_gauge = ["#ef4444","#f97316","#eab308","#22c55e","#06b6d4","#3b82f6"]
            labels_gauge = ["Very\nDifficult","Difficult","Fairly\nDifficult","Standard","Fairly\nEasy","Easy"]
            for i, (c, l) in enumerate(zip(colors_gauge, labels_gauge)):
                theta1 = 180 - i * 30
                theta2 = 180 - (i + 1) * 30
                wedge = mpatches.Wedge((0.5, 0), 0.45, theta2, theta1, facecolor=c, edgecolor="#1e1e2e", linewidth=2)
                ax.add_patch(wedge)
                mid_angle = math.radians((theta1 + theta2) / 2)
                tx = 0.5 + 0.58 * math.cos(mid_angle)
                ty = 0.58 * math.sin(mid_angle)
                ax.text(tx, ty, l, ha="center", va="center", fontsize=7, color="#e0e0f0", fontweight="bold")

            # Needle
            angle = math.radians(180 - clamped * 1.8)
            nx = 0.5 + 0.38 * math.cos(angle)
            ny = 0.38 * math.sin(angle)
            ax.annotate("", xy=(nx, ny), xytext=(0.5, 0),
                        arrowprops=dict(arrowstyle="-|>", color="white", lw=2.5))
            ax.text(0.5, -0.15, f"{flesch:.1f}", ha="center", va="center",
                    fontsize=20, fontweight="bold", color="#e0e0f0")
            ax.text(0.5, -0.25, analyzer.flesch_label(flesch), ha="center", va="center",
                    fontsize=10, color="#a0a0c0")
            canvas.draw()
            vl.addWidget(canvas)
            self.lay.addWidget(grp)
            self.widgets.append(grp)

        # Score cards
        grp2 = QGroupBox("📐  Readability Indices")
        grp2.setStyleSheet("QGroupBox{color:#b0b0d0; font-weight:bold; font-size:13px; border:1px solid #3d3d5c; border-radius:8px; margin-top:10px; padding-top:18px;}")
        grid = QGridLayout(grp2)

        descriptions = {
            "Flesch Reading Ease": "0-100 scale; higher = easier",
            "Flesch-Kincaid Grade": "US school grade level",
            "Gunning Fog Index": "Years of education needed",
            "Automated Readability Index": "US grade level (character-based)",
            "Coleman-Liau Index": "US grade level (character-based)",
            "Avg Syllables per Word": "Lower = simpler vocabulary",
        }

        for i, (name, val) in enumerate(scores.items()):
            card = StatCard(name, f"{val}", descriptions.get(name, ""))
            grid.addWidget(card, i // 3, i % 3)
            self.widgets.append(card)
        self.lay.addWidget(grp2)
        self.widgets.append(grp2)

        # Sentence length distribution
        if HAS_MPL and analyzer.sentences:
            grp3 = QGroupBox("📊  Sentence Length Distribution")
            grp3.setStyleSheet(grp2.styleSheet())
            vl3 = QVBoxLayout(grp3)
            canvas2 = MplCanvas(self, width=7, height=3)
            ax2 = canvas2.ax
            sent_lens = [len(re.findall(r"\b[a-zA-Z'-]+\b", s)) for s in analyzer.sentences if s.strip()]
            if sent_lens:
                bins = min(30, max(5, len(sent_lens) // 3))
                ax2.hist(sent_lens, bins=bins, color="#7c3aed", edgecolor="#3d3d5c", alpha=0.85)
                ax2.axvline(sum(sent_lens)/len(sent_lens), color="#f59e0b", linestyle="--", linewidth=2, label=f"Mean: {sum(sent_lens)/len(sent_lens):.1f}")
                ax2.set_xlabel("Words per Sentence", color=canvas2.label_color)
                ax2.set_ylabel("Count", color=canvas2.label_color)
                ax2.set_title("How long are the sentences?", color=canvas2.label_color, fontsize=11)
                ax2.tick_params(colors=canvas2.tick_color)
                ax2.legend(facecolor="#2b2b3d", edgecolor="#3d3d5c", labelcolor="#e0e0f0")
                for spine in ax2.spines.values():
                    spine.set_color("#3d3d5c")
            canvas2.draw()
            vl3.addWidget(canvas2)
            self.lay.addWidget(grp3)
            self.widgets.append(grp3)

        self.lay.addStretch()

# ────────────────────── Sentiment Tab ──────────────────────

class SentimentTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.widgets = []
        self.lay = QVBoxLayout(self)
        self.lay.setSpacing(12)

    def update_analysis(self, analyzer: TextAnalyzer):
        for w in self.widgets:
            self.lay.removeWidget(w)
            w.deleteLater()
        self.widgets.clear()

        sent = analyzer.sentiment_analysis()

        # Score card
        color_map = {
            "Positive": "#10b981", "Slightly Positive": "#34d399",
            "Neutral": "#6b7280", "Slightly Negative": "#f87171",
            "Negative": "#ef4444",
        }
        lbl_color = color_map.get(sent["label"], "#6b7280")

        grp = QGroupBox("🎭  Overall Sentiment")
        grp.setStyleSheet("QGroupBox{color:#b0b0d0; font-weight:bold; font-size:13px; border:1px solid #3d3d5c; border-radius:8px; margin-top:10px; padding-top:18px;}")
        hl = QHBoxLayout(grp)

        score_frame = QFrame()
        score_frame.setStyleSheet(f"background:#2b2b3d; border:2px solid {lbl_color}; border-radius:12px;")
        sl = QVBoxLayout(score_frame)
        lbl1 = QLabel(f'{sent["score"]:+.3f}')
        lbl1.setStyleSheet(f"color:{lbl_color}; font-size:32px; font-weight:bold;")
        lbl1.setAlignment(Qt.AlignCenter)
        sl.addWidget(lbl1)
        lbl2 = QLabel(sent["label"])
        lbl2.setStyleSheet(f"color:{lbl_color}; font-size:16px; font-weight:bold;")
        lbl2.setAlignment(Qt.AlignCenter)
        sl.addWidget(lbl2)
        hl.addWidget(score_frame)

        # Positive / negative counts
        info_frame = QFrame()
        info_frame.setStyleSheet("background:#2b2b3d; border-radius:10px;")
        il = QVBoxLayout(info_frame)
        il.addWidget(QLabel(f'✅ Positive words: <b style="color:#10b981">{sent["positive_count"]}</b>'))
        il.addWidget(QLabel(f'❌ Negative words: <b style="color:#ef4444">{sent["negative_count"]}</b>'))
        total_sent = sent["positive_count"] + sent["negative_count"]
        if total_sent > 0:
            il.addWidget(QLabel(f'⚡ Sentiment density: <b>{total_sent/analyzer.word_count*100:.1f}%</b> of words'))
        for lbl in info_frame.findChildren(QLabel):
            lbl.setStyleSheet(lbl.styleSheet() + "color:#c0c0d0; font-size:13px; padding:4px;")
        hl.addWidget(info_frame)
        hl.addStretch()
        self.lay.addWidget(grp)
        self.widgets.append(grp)

        # Charts
        if HAS_MPL:
            splitter = QSplitter(Qt.Horizontal)

            # Pie chart
            grp2 = QGroupBox("Sentiment Breakdown")
            grp2.setStyleSheet(grp.styleSheet())
            vl2 = QVBoxLayout(grp2)
            canvas = MplCanvas(self, width=4, height=3.5)
            ax = canvas.ax
            sizes = [sent["positive_count"], sent["negative_count"],
                     max(0, analyzer.word_count - sent["positive_count"] - sent["negative_count"])]
            labels = ["Positive", "Negative", "Neutral"]
            colors_pie = ["#10b981", "#ef4444", "#4b5563"]
            explode = (0.05, 0.05, 0)
            wedges, texts, autotexts = ax.pie(
                sizes, explode=explode, labels=labels, colors=colors_pie,
                autopct=lambda p: f"{p:.1f}%" if p > 2 else "",
                startangle=90, textprops={"color": "#e0e0f0", "fontsize": 10},
            )
            for at in autotexts:
                at.set_color("white")
                at.set_fontsize(9)
            ax.set_title("Word Sentiment Distribution", color=canvas.label_color, fontsize=11)
            canvas.draw()
            vl2.addWidget(canvas)
            splitter.addWidget(grp2)

            # Bar chart of top pos/neg
            grp3 = QGroupBox("Top Sentiment Words")
            grp3.setStyleSheet(grp.styleSheet())
            vl3 = QVBoxLayout(grp3)
            canvas2 = MplCanvas(self, width=4, height=3.5)
            ax2 = canvas2.ax

            pos_w = sent["positive_words"][:8]
            neg_w = sent["negative_words"][:8]
            all_words = [w for w, _ in neg_w][::-1] + [w for w, _ in pos_w]
            all_counts = [c for _, c in neg_w][::-1] + [c for _, c in pos_w]
            bar_colors = ["#ef4444"] * len(neg_w) + ["#10b981"] * len(pos_w)

            if all_words:
                y_pos = range(len(all_words))
                ax2.barh(list(y_pos), all_counts, color=bar_colors, edgecolor="#444466", linewidth=0.5)
                ax2.set_yticks(list(y_pos))
                ax2.set_yticklabels(all_words, fontsize=8)
                ax2.set_xlabel("Count", color=canvas2.label_color, fontsize=9)
                ax2.set_title("Most Frequent Sentiment Words", color=canvas2.label_color, fontsize=11)
                ax2.tick_params(colors=canvas2.tick_color, labelsize=8)
                for spine in ax2.spines.values():
                    spine.set_color("#3d3d5c")
            canvas2.draw()
            vl3.addWidget(canvas2)
            splitter.addWidget(grp3)

            splitter.setSizes([400, 400])
            self.lay.addWidget(splitter)
            self.widgets.append(splitter)

        # Sentence-level sentiment
        grp4 = QGroupBox("📝  Sentence-Level Sentiment")
        grp4.setStyleSheet(grp.styleSheet())
        vl4 = QVBoxLayout(grp4)
        sent_scores = []
        for s in analyzer.sentences[:50]:
            words_s = re.findall(r"\b[a-zA-Z'-]+\b", s)
            p = sum(1 for w in words_s if w.lower() in POSITIVE_WORDS)
            n = sum(1 for w in words_s if w.lower() in NEGATIVE_WORDS)
            total = p + n
            score = (p - n) / total if total > 0 else 0
            sent_scores.append((score, s[:120]))

        if HAS_MPL and sent_scores:
            canvas3 = MplCanvas(self, width=8, height=3)
            ax3 = canvas3.ax
            x = range(len(sent_scores))
            scores_list = [sc for sc, _ in sent_scores]
            bar_c = ["#10b981" if sc > 0.05 else "#ef4444" if sc < -0.05 else "#4b5563" for sc in scores_list]
            ax3.bar(x, scores_list, color=bar_c, edgecolor="#333355", linewidth=0.3)
            ax3.set_xlabel("Sentence #", color=canvas3.label_color, fontsize=9)
            ax3.set_ylabel("Sentiment Score", color=canvas3.label_color, fontsize=9)
            ax3.set_title("Sentiment Flow Across Sentences", color=canvas3.label_color, fontsize=11)
            ax3.axhline(0, color="#6b7280", linewidth=0.8, linestyle="--")
            ax3.tick_params(colors=canvas3.tick_color, labelsize=8)
            for spine in ax3.spines.values():
                spine.set_color("#3d3d5c")
            canvas3.draw()
            vl4.addWidget(canvas3)

        # Most positive / negative
        sorted_sents = sorted(sent_scores, key=lambda x: x[0])
        if sorted_sents:
            most_neg = sorted_sents[:3]
            most_pos = sorted_sents[-3:][::-1]
            hl2 = QHBoxLayout()
            for score, text in most_pos:
                f = QFrame()
                f.setStyleSheet("background:#1a2e1a; border:1px solid #10b981; border-radius:6px; padding:6px;")
                fl = QVBoxLayout(f)
                fl.addWidget(QLabel(f'<span style="color:#10b981; font-weight:bold;">+{score:.2f}</span>'))
                fl.addWidget(QLabel(f'<span style="color:#a0d0a0; font-size:11px;">{text}…</span>'))
                hl2.addWidget(f)
            for score, text in most_neg:
                f = QFrame()
                f.setStyleSheet("background:#2e1a1a; border:1px solid #ef4444; border-radius:6px; padding:6px;")
                fl = QVBoxLayout(f)
                fl.addWidget(QLabel(f'<span style="color:#ef4444; font-weight:bold;">{score:.2f}</span>'))
                fl.addWidget(QLabel(f'<span style="color:#d0a0a0; font-size:11px;">{text}…</span>'))
                hl2.addWidget(f)
            vl4.addLayout(hl2)

        self.lay.addWidget(grp4)
        self.widgets.append(grp4)
        self.lay.addStretch()

# ────────────────────── Character Analysis Tab ──────────────────────

class CharacterTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.lay = QVBoxLayout(self)

    def update_analysis(self, analyzer: TextAnalyzer):
        while self.lay.count():
            item = self.lay.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Letter frequency chart
        if HAS_MPL:
            splitter = QSplitter(Qt.Horizontal)

            grp = QGroupBox("🔤  Letter Frequency")
            grp.setStyleSheet("QGroupBox{color:#b0b0d0; font-weight:bold; font-size:13px; border:1px solid #3d3d5c; border-radius:8px; margin-top:10px; padding-top:18px;}")
            vl = QVBoxLayout(grp)
            canvas = MplCanvas(self, width=5, height=4.5)
            ax = canvas.ax
            cf = analyzer.char_frequency()
            if cf:
                letters = [chr(i) for i in range(ord('a'), ord('z')+1)]
                counts = [cf.get(l, 0) for l in letters]
                cmap = matplotlib.colormaps.get_cmap("cool")
                colors = [cmap(i / 25) for i in range(26)]
                ax.bar(letters, counts, color=colors, edgecolor="#444466", linewidth=0.5)
                ax.set_xlabel("Letter", color=canvas.label_color)
                ax.set_ylabel("Frequency", color=canvas.label_color)
                ax.set_title("Letter Distribution", color=canvas.label_color, fontsize=12)
                ax.tick_params(colors=canvas.tick_color)
                for spine in ax.spines.values():
                    spine.set_color("#3d3d5c")
            canvas.draw()
            vl.addWidget(canvas)
            splitter.addWidget(grp)

            # Punctuation chart
            grp2 = QGroupBox("❗  Punctuation & Symbols")
            grp2.setStyleSheet(grp.styleSheet())
            vl2 = QVBoxLayout(grp2)
            canvas2 = MplCanvas(self, width=4, height=4.5)
            ax2 = canvas2.ax
            pstats = analyzer.punctuation_stats()
            if pstats:
                top_p = sorted(pstats.items(), key=lambda x: -x[1])[:20]
                p_labels = [repr(p)[1:-1] for p, _ in top_p]
                p_counts = [c for _, c in top_p]
                ax2.barh(p_labels[::-1], p_counts[::-1], color="#f59e0b", edgecolor="#444466", linewidth=0.5)
                ax2.set_xlabel("Count", color=canvas2.label_color)
                ax2.set_title("Punctuation Frequency", color=canvas2.label_color, fontsize=12)
                ax2.tick_params(colors=canvas2.tick_color, labelsize=9)
                for spine in ax2.spines.values():
                    spine.set_color("#3d3d5c")
            canvas2.draw()
            vl2.addWidget(canvas2)
            splitter.addWidget(grp2)
            splitter.setSizes([450, 350])
            self.lay.addWidget(splitter)

        # Character type breakdown
        grp3 = QGroupBox("📊  Character Type Breakdown")
        grp3.setStyleSheet("QGroupBox{color:#b0b0d0; font-weight:bold; font-size:13px; border:1px solid #3d3d5c; border-radius:8px; margin-top:10px; padding-top:18px;}")
        grid = QGridLayout(grp3)

        text = analyzer.raw_text
        types = [
            ("Letters", sum(c.isalpha() for c in text)),
            ("Digits", sum(c.isdigit() for c in text)),
            ("Whitespace", sum(c.isspace() for c in text)),
            ("Punctuation", sum(c in string.punctuation for c in text)),
            ("Uppercase", sum(c.isupper() for c in text)),
            ("Lowercase", sum(c.islower() for c in text)),
        ]
        for i, (name, count) in enumerate(types):
            pct = count / max(1, len(text)) * 100
            card = StatCard(name, f"{count:,}", f"{pct:.1f}% of text")
            grid.addWidget(card, i // 3, i % 3)
        self.lay.addWidget(grp3)
        self.lay.addStretch()

# ────────────────────── Search Tab ──────────────────────

class SearchTab(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.analyzer = None
        self.lay = QVBoxLayout(self)

        # Search controls
        ctrl = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search for a word or phrase...")
        self.search_input.setStyleSheet("background:#22223a; color:#e0e0f0; padding:8px; border:1px solid #3d3d5c; border-radius:6px; font-size:13px;")
        self.search_input.returnPressed.connect(self.do_search)
        ctrl.addWidget(self.search_input)

        self.btn_search = QPushButton("🔍 Search")
        self.btn_search.setStyleSheet("background:#7c3aed; color:white; padding:8px 20px; border-radius:6px; font-weight:bold;")
        self.btn_search.clicked.connect(self.do_search)
        ctrl.addWidget(self.btn_search)

        self.chk_case = QCheckBox("Case sensitive")
        self.chk_case.setStyleSheet("color:#c0c0d0;")
        ctrl.addWidget(self.chk_case)

        self.chk_word = QCheckBox("Whole word")
        self.chk_word.setStyleSheet("color:#c0c0d0;")
        ctrl.addWidget(self.chk_word)

        self.lay.addLayout(ctrl)

        # Results
        self.result_label = QLabel("")
        self.result_label.setStyleSheet("color:#a0a0c0; font-size:12px;")
        self.lay.addWidget(self.result_label)

        self.result_table = QTableWidget()
        self.result_table.setColumnCount(3)
        self.result_table.setHorizontalHeaderLabels(["#", "Context", "Position"])
        self.result_table.horizontalHeader().setStretchLastSection(True)
        self.result_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.result_table.setAlternatingRowColors(True)
        self.result_table.setStyleSheet("""
            QTableWidget { background:#22223a; color:#d0d0e0; gridline-color:#3d3d5c; alternate-background-color:#2a2a44; }
            QHeaderView::section { background:#2b2b3d; color:#a0a0c0; padding:4px; border:1px solid #3d3d5c; }
        """)
        self.lay.addWidget(self.result_table)

    def set_analyzer(self, analyzer):
        self.analyzer = analyzer

    def do_search(self):
        if not self.analyzer:
            return
        query = self.search_input.text().strip()
        if not query:
            return

        text = self.analyzer.raw_text
        case_sensitive = self.chk_case.isChecked()
        whole_word = self.chk_word.isChecked()

        flags = 0 if case_sensitive else re.IGNORECASE
        if whole_word:
            pattern = r"\b" + re.escape(query) + r"\b"
        else:
            pattern = re.escape(query)

        try:
            matches = list(re.finditer(pattern, text, flags))
        except re.error:
            self.result_label.setText("Invalid search pattern")
            return

        self.result_label.setText(f"Found <b>{len(matches)}</b> match(es) for '<i>{query}</i>'")
        self.result_table.setRowCount(len(matches))
        context_radius = 60

        for i, m in enumerate(matches):
            self.result_table.setItem(i, 0, QTableWidgetItem(str(i + 1)))
            start = max(0, m.start() - context_radius)
            end = min(len(text), m.end() + context_radius)
            ctx = text[start:end].replace("\n", " ")
            if start > 0:
                ctx = "…" + ctx
            if end < len(text):
                ctx = ctx + "…"
            # Bold the match in context
            item = QTableWidgetItem(ctx)
            self.result_table.setItem(i, 1, item)
            self.result_table.setItem(i, 2, QTableWidgetItem(f"Char {m.start()}"))

        self.result_table.resizeColumnsToContents()

# ────────────────────── Main Window ──────────────────────

GLOBAL_STYLE = """
QMainWindow, QWidget {
    background: #1e1e2e;
    color: #e0e0f0;
    font-family: 'Segoe UI', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
}
QGroupBox {
    color: #b0b0d0;
    font-weight: bold;
    font-size: 13px;
    border: 1px solid #3d3d5c;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 20px;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}
QPushButton {
    background: #3d3d5c;
    color: #e0e0f0;
    border: 1px solid #4d4d6c;
    border-radius: 6px;
    padding: 6px 14px;
    font-weight: bold;
}
QPushButton:hover { background: #52527a; }
QPushButton:pressed { background: #7c3aed; }
QLineEdit, QTextEdit {
    background: #22223a;
    color: #e0e0f0;
    border: 1px solid #3d3d5c;
    border-radius: 6px;
    padding: 6px;
    selection-background-color: #7c3aed;
}
QComboBox {
    background: #2b2b3d;
    color: #e0e0f0;
    border: 1px solid #3d3d5c;
    border-radius: 5px;
    padding: 5px 10px;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView { background: #2b2b3d; color: #e0e0f0; selection-background-color: #7c3aed; }
QSpinBox {
    background: #2b2b3d;
    color: #e0e0f0;
    border: 1px solid #3d3d5c;
    border-radius: 5px;
    padding: 4px 8px;
}
QCheckBox { color: #c0c0d0; spacing: 6px; }
QCheckBox::indicator { width: 16px; height: 16px; border-radius: 3px; border: 1px solid #4d4d6c; background: #22223a; }
QCheckBox::indicator:checked { background: #7c3aed; border-color: #7c3aed; }
QTabWidget::pane { border: 1px solid #3d3d5c; border-radius: 6px; background: #1e1e2e; }
QTabBar::tab {
    background: #2b2b3d;
    color: #a0a0c0;
    padding: 8px 16px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    margin-right: 2px;
    border: 1px solid #3d3d5c;
    border-bottom: none;
}
QTabBar::tab:selected { background: #1e1e2e; color: #e0e0f0; font-weight: bold; }
QTabBar::tab:hover { background: #3d3d5c; }
QScrollArea { border: none; }
QScrollBar:vertical { background: #1e1e2e; width: 10px; border-radius: 5px; }
QScrollBar::handle:vertical { background: #4d4d6c; border-radius: 5px; min-height: 30px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar:horizontal { background: #1e1e2e; height: 10px; border-radius: 5px; }
QScrollBar::handle:horizontal { background: #4d4d6c; border-radius: 5px; min-width: 30px; }
QSplitter::handle { background: #3d3d5c; }
QStatusBar { background: #1a1a2a; color: #8888aa; border-top: 1px solid #3d3d5c; }
QLabel { color: #c0c0d0; }
QProgressBar { border: 1px solid #3d3d5c; border-radius: 5px; text-align: center; background: #22223a; color: #e0e0f0; }
QProgressBar::chunk { background: #7c3aed; border-radius: 4px; }
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📝 Text Analyzer Pro")
        self.setMinimumSize(QSize(1100, 750))
        self.resize(1400, 850)
        self.setStyleSheet(GLOBAL_STYLE)

        self.analyzer = None

        # ── Menu ──
        menubar = self.menuBar()
        menubar.setStyleSheet("QMenuBar{background:#1a1a2a; color:#c0c0d0;} QMenuBar::item:selected{background:#7c3aed;} QMenu{background:#2b2b3d; color:#e0e0f0;} QMenu::item:selected{background:#7c3aed;}")

        file_menu = menubar.addMenu("File")
        act_pdf = QAction("Open PDF…", self)
        act_pdf.triggered.connect(lambda: self.open_file("pdf"))
        file_menu.addAction(act_pdf)
        act_email = QAction("Open Email (.eml)…", self)
        act_email.triggered.connect(lambda: self.open_file("email"))
        file_menu.addAction(act_email)
        act_text = QAction("Open Text File…", self)
        act_text.triggered.connect(lambda: self.open_file("text"))
        file_menu.addAction(act_text)
        file_menu.addSeparator()
        act_export = QAction("Export Report…", self)
        act_export.triggered.connect(self.export_report)
        file_menu.addAction(act_export)
        file_menu.addSeparator()
        act_quit = QAction("Quit", self)
        act_quit.triggered.connect(self.close)
        file_menu.addAction(act_quit)

        help_menu = menubar.addMenu("Help")
        act_about = QAction("About", self)
        act_about.triggered.connect(self.show_about)
        help_menu.addAction(act_about)

        # ── Central widget ──
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(8, 8, 8, 4)
        main_layout.setSpacing(6)

        # ── Toolbar ──
        toolbar = QHBoxLayout()
        toolbar.setSpacing(8)

        btn_pdf = QPushButton("📄 Open PDF")
        btn_pdf.setStyleSheet("background:#7c3aed; color:white; padding:8px 16px; border-radius:6px; font-weight:bold; font-size:12px;")
        btn_pdf.clicked.connect(lambda: self.open_file("pdf"))
        toolbar.addWidget(btn_pdf)

        btn_email = QPushButton("📧 Open Email")
        btn_email.setStyleSheet("background:#06b6d4; color:white; padding:8px 16px; border-radius:6px; font-weight:bold; font-size:12px;")
        btn_email.clicked.connect(lambda: self.open_file("email"))
        toolbar.addWidget(btn_email)

        btn_text = QPushButton("📝 Open Text")
        btn_text.setStyleSheet("background:#3b82f6; color:white; padding:8px 16px; border-radius:6px; font-weight:bold; font-size:12px;")
        btn_text.clicked.connect(lambda: self.open_file("text"))
        toolbar.addWidget(btn_text)

        toolbar.addSpacing(20)

        self.file_label = QLabel("No file loaded — paste text or open a file")
        self.file_label.setStyleSheet("color:#6a6a8a; font-style:italic;")
        toolbar.addWidget(self.file_label)
        toolbar.addStretch()

        btn_analyze = QPushButton("🚀 Analyze")
        btn_analyze.setStyleSheet("background:#10b981; color:white; padding:8px 24px; border-radius:6px; font-weight:bold; font-size:13px;")
        btn_analyze.clicked.connect(self.analyze_text)
        toolbar.addWidget(btn_analyze)

        btn_clear = QPushButton("🗑 Clear")
        btn_clear.setStyleSheet("background:#ef4444; color:white; padding:8px 16px; border-radius:6px; font-weight:bold; font-size:12px;")
        btn_clear.clicked.connect(self.clear_all)
        toolbar.addWidget(btn_clear)

        main_layout.addLayout(toolbar)

        # ── Splitter: text input + results ──
        splitter = QSplitter(Qt.Horizontal)

        # Left: text editor
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)

        lbl = QLabel("✏️  Input Text")
        lbl.setStyleSheet("color:#a0a0c0; font-weight:bold; font-size:12px;")
        left_layout.addWidget(lbl)

        self.text_editor = QTextEdit()
        self.text_editor.setPlaceholderText(
            "Paste or type text here, or use the buttons above to load a file...\n\n"
            "Supported formats:\n"
            "  • PDF files (.pdf)\n"
            "  • Email files (.eml)\n"
            "  • Text files (.txt, .md, .csv, .log, etc.)\n"
            "  • Any text you paste directly"
        )
        self.text_editor.setStyleSheet(
            "QTextEdit { background:#1a1a2e; color:#d0d0e0; border:1px solid #3d3d5c; "
            "border-radius:8px; padding:10px; font-family:'Consolas','Courier New',monospace; "
            "font-size:12px; selection-background-color:#7c3aed; }"
        )
        left_layout.addWidget(self.text_editor)

        # Word count below editor
        self.editor_stats = QLabel("Words: 0 | Characters: 0 | Lines: 0")
        self.editor_stats.setStyleSheet("color:#6a6a8a; font-size:11px;")
        left_layout.addWidget(self.editor_stats)
        self.text_editor.textChanged.connect(self.update_editor_stats)

        splitter.addWidget(left_widget)

        # Right: tabs
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)

        self.summary_tab = SummaryTab()
        self.freq_tab = WordFrequencyTab()
        self.readability_tab = ReadabilityTab()
        self.sentiment_tab = SentimentTab()
        self.char_tab = CharacterTab()
        self.search_tab = SearchTab()

        self.tabs.addTab(self.summary_tab, "📊 Summary")
        self.tabs.addTab(self.freq_tab, "📈 Word Frequency")
        self.tabs.addTab(self.readability_tab, "📖 Readability")
        self.tabs.addTab(self.sentiment_tab, "🎭 Sentiment")
        self.tabs.addTab(self.char_tab, "🔤 Characters")
        self.tabs.addTab(self.search_tab, "🔍 Search")

        splitter.addWidget(self.tabs)
        splitter.setSizes([380, 720])
        main_layout.addWidget(splitter)

        # ── Status bar ──
        self.statusBar().showMessage("Ready — Load a file or paste text to begin analysis")

        # ── Progress bar in status ──
        self.progress = QProgressBar()
        self.progress.setMaximumWidth(200)
        self.progress.setVisible(False)
        self.statusBar().addPermanentWidget(self.progress)

    def update_editor_stats(self):
        text = self.text_editor.toPlainText()
        words = len(re.findall(r"\b[a-zA-Z'-]+\b", text))
        chars = len(text)
        lines = text.count("\n") + 1
        self.editor_stats.setText(f"Words: {words:,} | Characters: {chars:,} | Lines: {lines:,}")

    def open_file(self, file_type):
        try:
            if file_type == "pdf":
                if not HAS_PDF:
                    QMessageBox.warning(self, "Missing Dependency",
                                        "PyPDF2 is not installed.\n\nRun: pip install PyPDF2")
                    return
                path, _ = QFileDialog.getOpenFileName(self, "Open PDF", "", "PDF Files (*.pdf)")
                if not path:
                    return
                self.statusBar().showMessage(f"Loading PDF: {os.path.basename(path)}…")
                QApplication.processEvents()
                text, pages = load_pdf(path)
                self.file_label.setText(f"📄 {os.path.basename(path)} ({pages} pages)")
                self.file_label.setStyleSheet("color:#7c3aed; font-weight:bold;")

            elif file_type == "email":
                path, _ = QFileDialog.getOpenFileName(self, "Open Email", "", "Email Files (*.eml)")
                if not path:
                    return
                self.statusBar().showMessage(f"Loading Email: {os.path.basename(path)}…")
                QApplication.processEvents()
                text, _ = load_email(path)
                self.file_label.setText(f"📧 {os.path.basename(path)}")
                self.file_label.setStyleSheet("color:#06b6d4; font-weight:bold;")

            elif file_type == "text":
                path, _ = QFileDialog.getOpenFileName(self, "Open Text File", "",
                                                      "Text Files (*.txt *.md *.csv *.log *.html *.xml *.json *.py *.js *.c *.cpp *.java);;All Files (*)")
                if not path:
                    return
                self.statusBar().showMessage(f"Loading: {os.path.basename(path)}…")
                QApplication.processEvents()
                text, _ = load_text_file(path)
                self.file_label.setText(f"📝 {os.path.basename(path)}")
                self.file_label.setStyleSheet("color:#3b82f6; font-weight:bold;")

            else:
                return

            self.text_editor.setPlainText(text)
            self.statusBar().showMessage(f"Loaded: {os.path.basename(path)} — Click 'Analyze' to begin")
            self.analyze_text()

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load file:\n{str(e)}")
            self.statusBar().showMessage("Error loading file")

    def analyze_text(self):
        text = self.text_editor.toPlainText().strip()
        if not text:
            QMessageBox.information(self, "No Text", "Please paste or load some text first.")
            return

        self.statusBar().showMessage("Analyzing text…")
        self.progress.setVisible(True)
        self.progress.setRange(0, 0)  # indeterminate
        QApplication.processEvents()

        try:
            self.analyzer = TextAnalyzer(text)

            self.summary_tab.update_analysis(self.analyzer)
            self.freq_tab.update_analysis(self.analyzer)
            self.readability_tab.update_analysis(self.analyzer)
            self.sentiment_tab.update_analysis(self.analyzer)
            self.char_tab.update_analysis(self.analyzer)
            self.search_tab.set_analyzer(self.analyzer)

            self.statusBar().showMessage(
                f"✅ Analysis complete — {self.analyzer.word_count:,} words, "
                f"{self.analyzer.sentence_count:,} sentences, "
                f"{self.analyzer.unique_word_count:,} unique words"
            )
        except Exception as e:
            QMessageBox.critical(self, "Analysis Error", f"Analysis failed:\n{str(e)}")
            self.statusBar().showMessage("Analysis failed")
        finally:
            self.progress.setVisible(False)

    def clear_all(self):
        self.text_editor.clear()
        self.analyzer = None
        self.file_label.setText("No file loaded — paste text or open a file")
        self.file_label.setStyleSheet("color:#6a6a8a; font-style:italic;")
        self.statusBar().showMessage("Ready — Load a file or paste text to begin analysis")

        # Clear all tabs — recreate them
        idx = self.tabs.currentIndex()
        self.tabs.removeTab(0)
        self.summary_tab = SummaryTab()
        self.tabs.insertTab(0, self.summary_tab, "📊 Summary")

        self.tabs.removeTab(1)
        self.freq_tab = WordFrequencyTab()
        self.tabs.insertTab(1, self.freq_tab, "📈 Word Frequency")

        self.tabs.removeTab(2)
        self.readability_tab = ReadabilityTab()
        self.tabs.insertTab(2, self.readability_tab, "📖 Readability")

        self.tabs.removeTab(3)
        self.sentiment_tab = SentimentTab()
        self.tabs.insertTab(3, self.sentiment_tab, "🎭 Sentiment")

        self.tabs.removeTab(4)
        self.char_tab = CharacterTab()
        self.tabs.insertTab(4, self.char_tab, "🔤 Characters")

        self.tabs.removeTab(5)
        self.search_tab = SearchTab()
        self.tabs.insertTab(5, self.search_tab, "🔍 Search")

        self.tabs.setCurrentIndex(min(idx, 5))

    def export_report(self):
        if not self.analyzer:
            QMessageBox.information(self, "No Analysis", "Analyze some text first before exporting.")
            return

        path, _ = QFileDialog.getSaveFileName(self, "Export Report", "analysis_report.txt",
                                                "Text Files (*.txt);;All Files (*)")
        if not path:
            return

        a = self.analyzer
        scores = a.readability_scores()
        sent = a.sentiment_analysis()

        lines = [
            "=" * 60,
            "TEXT ANALYSIS REPORT",
            "=" * 60,
            "",
            "BASIC STATISTICS",
            "-" * 40,
            f"Total Words:              {a.word_count:,}",
            f"Unique Words:             {a.unique_word_count:,}",
            f"Lexical Diversity:        {a.lexical_diversity():.4f}",
            f"Total Characters:         {a.char_count:,}",
            f"Characters (no spaces):   {a.char_count_no_spaces:,}",
            f"Sentences:                {a.sentence_count:,}",
            f"Paragraphs:               {a.paragraph_count:,}",
            f"Avg Word Length:          {a.avg_word_length():.2f}",
            f"Avg Sentence Length:      {a.avg_sentence_length():.2f} words",
            f"Complex Words (3+ syll):  {len(a.complex_words()):,}",
            f"Reading Time:             {a.reading_time():.1f} min",
            f"Speaking Time:            {a.speaking_time():.1f} min",
            "",
            "READABILITY SCORES",
            "-" * 40,
            f"Flesch Reading Ease:      {scores['Flesch Reading Ease']} ({a.flesch_label(scores['Flesch Reading Ease'])})",
            f"Flesch-Kincaid Grade:     {scores['Flesch-Kincaid Grade']}",
            f"Gunning Fog Index:        {scores['Gunning Fog Index']}",
            f"ARI:                      {scores['Automated Readability Index']}",
            f"Coleman-Liau Index:       {scores['Coleman-Liau Index']}",
            f"Avg Syllables/Word:       {scores['Avg Syllables per Word']}",
            "",
            "SENTIMENT ANALYSIS",
            "-" * 40,
            f"Score:                    {sent['score']:+.4f}",
            f"Label:                    {sent['label']}",
            f"Positive Words:           {sent['positive_count']}",
            f"Negative Words:           {sent['negative_count']}",
            "",
            "TOP 20 WORDS (excl. stop words)",
            "-" * 40,
        ]
        for i, (word, count) in enumerate(a.word_frequency(20, True), 1):
            lines.append(f"  {i:2d}. {word:20s} {count}")

        lines.append("")
        lines.append("TOP 10 BIGRAMS")
        lines.append("-" * 40)
        for i, ((w1, w2), count) in enumerate(a.bigram_frequency(10), 1):
            lines.append(f"  {i:2d}. {w1} {w2:15s} {count}")

        lines.append("")
        lines.append("TOP POSITIVE WORDS")
        lines.append("-" * 40)
        for word, count in sent["positive_words"][:10]:
            lines.append(f"  {word:20s} {count}")

        lines.append("")
        lines.append("TOP NEGATIVE WORDS")
        lines.append("-" * 40)
        for word, count in sent["negative_words"][:10]:
            lines.append(f"  {word:20s} {count}")

        lines.append("")
        lines.append("=" * 60)

        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(lines))
            self.statusBar().showMessage(f"Report exported to {os.path.basename(path)}")
            QMessageBox.information(self, "Exported", f"Report saved to:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", f"Failed to save report:\n{str(e)}")

    def show_about(self):
        QMessageBox.about(self, "About Text Analyzer Pro",
            "<h2>📝 Text Analyzer Pro</h2>"
            "<p>A comprehensive text analysis tool for PDF books, emails, "
            "and any text content.</p>"
            "<h3>Features:</h3>"
            "<ul>"
            "<li>📊 Summary statistics (words, sentences, reading time, etc.)</li>"
            "<li>📈 Word frequency analysis with charts</li>"
            "<li>📖 Readability scores (Flesch, Fog, ARI, Coleman-Liau)</li>"
            "<li>🎭 Sentiment analysis</li>"
            "<li>🔤 Character frequency analysis</li>"
            "<li>🔍 Text search with context</li>"
            "<li>📄 Export analysis report</li>"
            "</ul>"
            "<h3>Supported Formats:</h3>"
            "<ul>"
            "<li>PDF files (.pdf) — requires PyPDF2</li>"
            "<li>Email files (.eml)</li>"
            "<li>Text files (.txt, .md, .csv, .log, etc.)</li>"
            "<li>Direct text paste</li>"
            "</ul>"
            "<p>Built with <b>PySide6</b>, <b>matplotlib</b>, and Python.</p>"
        )

# ────────────────────── Entry Point ──────────────────────

def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")

    # Dark palette
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor("#1e1e2e"))
    palette.setColor(QPalette.WindowText, QColor("#e0e0f0"))
    palette.setColor(QPalette.Base, QColor("#22223a"))
    palette.setColor(QPalette.AlternateBase, QColor("#2a2a44"))
    palette.setColor(QPalette.ToolTipBase, QColor("#2b2b3d"))
    palette.setColor(QPalette.ToolTipText, QColor("#e0e0f0"))
    palette.setColor(QPalette.Text, QColor("#e0e0f0"))
    palette.setColor(QPalette.Button, QColor("#2b2b3d"))
    palette.setColor(QPalette.ButtonText, QColor("#e0e0f0"))
    palette.setColor(QPalette.BrightText, QColor("#ffffff"))
    palette.setColor(QPalette.Highlight, QColor("#7c3aed"))
    palette.setColor(QPalette.HighlightedText, QColor("#ffffff"))
    app.setPalette(palette)

    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()