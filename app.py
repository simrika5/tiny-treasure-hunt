
import json
import random
import time
from pathlib import Path

import streamlit as st

st.set_page_config(
    page_title="Treasure Quest",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded",
)

HIGHSCORE_FILE = Path(__file__).with_name("highscore.json")

DIFFICULTIES = {
    "Easy": {"size": 5, "attempts": 10, "lifelines": 3},
    "Medium": {"size": 6, "attempts": 8, "lifelines": 2},
    "Hard": {"size": 8, "attempts": 10, "lifelines": 2},
}


def load_best():
    try:
        return int(json.loads(HIGHSCORE_FILE.read_text()).get("best", 0))
    except (OSError, ValueError, TypeError):
        return 0


def save_best(score):
    try:
        HIGHSCORE_FILE.write_text(json.dumps({"best": score}, indent=2))
    except OSError:
        pass


def new_game(difficulty):
    settings = DIFFICULTIES[difficulty]

    st.session_state.difficulty = difficulty
    st.session_state.size = settings["size"]
    st.session_state.max_attempts = settings["attempts"]
    st.session_state.max_lifelines = settings["lifelines"]
    st.session_state.lifelines = settings["lifelines"]
    st.session_state.treasure = (
        random.randrange(settings["size"]),
        random.randrange(settings["size"]),
    )
    st.session_state.guesses = set()
    st.session_state.attempts_left = settings["attempts"]
    st.session_state.score = 0
    st.session_state.status = "ready"
    st.session_state.started_at = None
    st.session_state.finished_at = None
    st.session_state.feedback = (
        "Press Start Game to begin your adventure!"
    )
    st.session_state.feedback_type = "info"
    st.session_state.last_guess = None
    st.session_state.lifeline_message = ""
    st.session_state.round_id = st.session_state.get("round_id", 0) + 1


def elapsed_seconds():
    start = st.session_state.started_at

    if start is None:
        return 0

    end = st.session_state.finished_at or time.time()
    return max(0, int(end - start))


def format_time(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)

    if hours:
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    return f"{minutes:02d}:{seconds:02d}"


def distance(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def current_score():
    if st.session_state.status == "won":
        return st.session_state.score

    if st.session_state.status != "playing":
        return 0

    attempts_used = (
        st.session_state.max_attempts - st.session_state.attempts_left
    )
    lifelines_used = (
        st.session_state.max_lifelines - st.session_state.lifelines
    )
    time_bonus = max(0, 60 - elapsed_seconds()) // 5 * 2

    return max(
        10,
        100 - max(0, attempts_used - 1) * 8
        - lifelines_used * 15 + time_bonus,
    )



def finish_game(won):
    # Calculate the score BEFORE changing the game status.
    if won:
        attempts_used = (
            st.session_state.max_attempts
            - st.session_state.attempts_left
        )

        lifelines_used = (
            st.session_state.max_lifelines
            - st.session_state.lifelines
        )

        time_bonus = max(0, 60 - elapsed_seconds()) // 5 * 2

        score = max(
            10,
            100
            - max(0, attempts_used - 1) * 8
            - lifelines_used * 15
            + time_bonus,
        )

        st.session_state.score = score

        best = max(load_best(), score)
        save_best(best)
    else:
        st.session_state.score = 0

    # Update the game status after calculating the final score.
    st.session_state.status = "won" if won else "lost"
    st.session_state.finished_at = time.time()



if "status" not in st.session_state:
    new_game("Easy")

if "theme_choice" not in st.session_state:
    st.session_state.theme_choice = "Dark"


# ---------- Theme ----------
# The theme selector styles this app immediately.
# Streamlit's own Settings > Theme can also control the app theme.
theme = st.session_state.theme_choice

if theme == "Dark":
    page_bg = "#101820"
    panel_bg = "#192832"
    text_color = "#F4F7FA"
    muted = "#B8C7D2"
    border = "#344B59"
    accent = "#57E6B1"
    tile_bg = "#234637"
    tile_hover = "#32674D"
else:
    page_bg = "#F1F7F2"
    panel_bg = "#FFFFFF"
    text_color = "#20342A"
    muted = "#5D7164"
    border = "#C8DCCB"
    accent = "#087F5B"
    tile_bg = "#D9F1DF"
    tile_hover = "#B9E6C6"

st.markdown(
    f"""
    <style>
    .stApp {{
        background: {page_bg};
        color: {text_color};
    }}

    [data-testid="stHeader"] {{
        background: transparent;
    }}

    [data-testid="stSidebar"] {{
        background: {panel_bg};
        border-right: 1px solid {border};
    }}

    h1, h2, h3, p, label, span {{
        color: {text_color};
    }}

    .game-title {{
        font-size: clamp(1.7rem, 3vw, 2.5rem);
        font-weight: 850;
        text-align: center;
        color: {accent};
        margin: 0 0 12px 0;
    }}

    .clock {{
        text-align: center;
        background: {panel_bg};
        border: 1px solid {border};
        border-radius: 18px;
        padding: 12px;
        margin: 0 0 16px 0;
    }}

    .clock-label {{
        color: {muted};
        font-size: 0.75rem;
        letter-spacing: 3px;
    }}

    .clock-value {{
        color: {accent};
        font-size: clamp(1.8rem, 3vw, 2.6rem);
        font-weight: 850;
        font-variant-numeric: tabular-nums;
        letter-spacing: 3px;
    }}

    .legend {{
        background: {page_bg};
        border: 1px solid {border};
        border-radius: 12px;
        padding: 10px 12px;
        margin: 5px 0 14px 0;
        line-height: 1.95;
        font-size: 0.9rem;
    }}

    .lifeline-box {{
        background: {page_bg};
        border: 1px solid {accent};
        border-radius: 14px;
        padding: 12px;
        margin: 12px 0 6px 0;
    }}

    .feedback {{
        text-align: center;
        border: 1px solid {border};
        background: {panel_bg};
        border-radius: 13px;
        padding: 12px;
        margin: 12px 0;
        font-weight: 700;
        color: {text_color};
    }}

    div[data-testid="stMetric"] {{
        background: {panel_bg};
        border: 1px solid {border};
        padding: 10px 12px;
        border-radius: 13px;
    }}

    div[data-testid="stMetricLabel"] {{
        color: {muted};
    }}

    div[data-testid="stMetricValue"] {{
        color: {accent};
    }}

    div.stButton > button {{
        border-radius: 12px;
        border: 1px solid {border};
        min-height: 43px;
        font-weight: 750;
        transition: 0.15s ease;
    }}

    div.stButton > button:hover:not(:disabled) {{
        border-color: {accent};
        transform: translateY(-1px);
    }}

    div.stButton > button:disabled {{
        opacity: 0.72;
    }}

    hr {{
        border-color: {border};
    }}
    </style>
    """,
    unsafe_allow_html=True,
)


# ---------- Left sidebar: only settings, instructions, legend, lifeline ----------
with st.sidebar:
    st.markdown("## ⚙️ Game Settings")

    chosen = st.selectbox(
        "Difficulty",
        list(DIFFICULTIES),
        index=list(DIFFICULTIES).index(st.session_state.difficulty),
    )

    if chosen != st.session_state.difficulty:
        new_game(chosen)
        st.rerun()

    st.selectbox(
        "🎨 Appearance",
        ["Dark", "Light"],
        key="theme_choice",
    )

    st.divider()

    st.markdown("### 🎮 How to Play")
    st.caption("Select tiles, follow the heat clues, find 💎!")

    st.markdown("### 🗺️ Treasure Map")
    st.markdown(
        """
        <div class="legend">
        🌿 Unexplored land<br>
        ❌ Already searched<br>
        🔥 Burning hot — very close<br>
        🌤️ Getting warmer<br>
        🥶 Cold — explore elsewhere<br>
        💎 Hidden treasure
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### 🧭 Lifeline")

    st.markdown(
        f"""
        <div class="lifeline-box">
        <b>🔍 Compass</b><br>
        <span style="font-size:0.9rem">
        Reveals the treasure's direction.<br>
        Costs 15 points.
        </span><br><br>
        <b>Available: {st.session_state.lifelines}</b>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button(
        "🧭 USE COMPASS",
        use_container_width=True,
        type="primary",
        disabled=(
            st.session_state.status != "playing"
            or st.session_state.lifelines == 0
        ),
    ):
        st.session_state.lifelines -= 1

        if st.session_state.guesses:
            origin = min(
                st.session_state.guesses,
                key=lambda pos: distance(pos, st.session_state.treasure),
            )
        else:
            origin = (
                st.session_state.size // 2,
                st.session_state.size // 2,
            )

        target = st.session_state.treasure
        directions = []

        if target[0] < origin[0]:
            directions.append("⬆️ NORTH")
        elif target[0] > origin[0]:
            directions.append("⬇️ SOUTH")

        if target[1] < origin[1]:
            directions.append("⬅️ WEST")
        elif target[1] > origin[1]:
            directions.append("➡️ EAST")

        clue = " and ".join(directions) if directions else (
            "The treasure is at your reference location!"
        )

        st.session_state.lifeline_message = f"🧭 {clue}"
        st.rerun()

    if st.session_state.lifeline_message:
        st.success(st.session_state.lifeline_message)

    st.divider()
    st.metric("🏆 Best score", load_best())


# ---------- Main area: game only ----------
st.markdown(
    '<div class="game-title">💎 Treasure Quest</div>',
    unsafe_allow_html=True,
)

# Clock and score update independently once per second.
@st.fragment(run_every="1s")
def live_dashboard():
    left, center, right = st.columns([1, 1, 1.25])

    with left:
        st.metric("🎯 Attempts", st.session_state.attempts_left)

    with center:
        st.metric("⭐ Current score", current_score())

    with right:
        label = (
            "FINAL TIME"
            if st.session_state.status in ("won", "lost")
            else "TIME ELAPSED"
        )
        st.markdown(
            f"""
            <div class="clock">
                <div class="clock-label">🕒 {label}</div>
                <div class="clock-value">{format_time(elapsed_seconds())}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


live_dashboard()

if st.session_state.status == "ready":
    if st.button(
        "▶️ START GAME",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.started_at = time.time()
        st.session_state.status = "playing"
        st.session_state.feedback = "🌿 Adventure started! Find the treasure!"
        st.session_state.feedback_type = "info"
        st.rerun()


# Center the grid and keep it from stretching too widely.
grid_left, grid_center, grid_right = st.columns([1, 4, 1])

with grid_center:
    size = st.session_state.size
    treasure = st.session_state.treasure
    playing = st.session_state.status == "playing"
    finished = st.session_state.status in ("won", "lost")

    for row in range(size):
        cells = st.columns(size, gap="small")

        for col in range(size):
            position = (row, col)
            searched = position in st.session_state.guesses

            if position == treasure and finished:
                symbol = "💎"
            elif searched:
                symbol = "❌"
            else:
                symbol = "🌿"

            with cells[col]:
                if st.button(
                    symbol,
                    key=f"tile_{st.session_state.round_id}_{row}_{col}",
                    use_container_width=True,
                    disabled=not playing or searched,
                ):
                    st.session_state.guesses.add(position)
                    st.session_state.last_guess = position
                    st.session_state.attempts_left -= 1

                    if position == treasure:
                        finish_game(True)
                        st.session_state.feedback = (
                            "🎉 TREASURE FOUND! You did it!"
                        )
                        st.session_state.feedback_type = "success"
                    else:
                        gap = distance(position, treasure)

                        if gap <= 1:
                            st.session_state.feedback = (
                                "🔥 BURNING HOT! The treasure is very close!"
                            )
                            st.session_state.feedback_type = "error"
                        elif gap <= 3:
                            st.session_state.feedback = (
                                "🌤️ GETTING WARMER! Keep going!"
                            )
                            st.session_state.feedback_type = "warning"
                        else:
                            st.session_state.feedback = (
                                "🥶 COLD! Try another area."
                            )
                            st.session_state.feedback_type = "info"

                        if st.session_state.attempts_left == 0:
                            finish_game(False)
                            st.session_state.feedback = (
                                "💀 GAME OVER! No attempts left."
                            )
                            st.session_state.feedback_type = "error"

                    st.rerun()


# Feedback is deliberately visible beneath the game grid.
feedback = st.session_state.feedback

if st.session_state.feedback_type == "success":
    st.success(feedback)
elif st.session_state.feedback_type == "warning":
    st.warning(feedback)
elif st.session_state.feedback_type == "error":
    st.error(feedback)
else:
    st.info(feedback)


# ---------- Results ----------
if st.session_state.status == "won":
    st.balloons()
    st.success(
        f"💎 Treasure recovered! Final score: {st.session_state.score}"
    )
    st.markdown(
        f"### ⏱️ Time taken: {format_time(elapsed_seconds())}"
    )

elif st.session_state.status == "lost":
    st.error("Your expedition has ended. Better luck next time!")
    st.markdown(
        f"### ⏱️ Time taken: {format_time(elapsed_seconds())}"
    )
    st.caption(
        f"The treasure was at row {treasure[0] + 1}, "
        f"column {treasure[1] + 1}."
    )

if finished:
    if st.button("🔄 PLAY AGAIN", type="primary", use_container_width=True):
        new_game(st.session_state.difficulty)
        st.rerun()
