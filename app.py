
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt

st.set_page_config(
    page_title="Interactive Visualization Tool for the First Fundamental Theorem of Calculus",
    page_icon="∫",
    layout="wide",
)

plt.rcParams["font.size"] = 11


# =========================
# Page style
# =========================
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.3rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }
    .hero {
        background: linear-gradient(135deg, #f7fbff 0%, #eef4ff 100%);
        border: 1px solid #dbe7ff;
        border-radius: 24px;
        padding: 1.3rem 1.4rem 1.1rem 1.4rem;
        margin-bottom: 1rem;
    }
    .hero-title {
        font-size: 2rem;
        font-weight: 800;
        line-height: 1.25;
        margin-bottom: 0.25rem;
        color: #1f2d3d;
    }
    .hero-sub {
        color: #506070;
        font-size: 1rem;
        line-height: 1.7;
    }
    .section-title {
        font-size: 1.15rem;
        font-weight: 700;
        margin-top: 0.4rem;
        margin-bottom: 0.4rem;
    }
    .formula-card {
        background: #ffffff;
        border: 1px solid #e7edf7;
        border-radius: 22px;
        padding: 1rem 1.1rem 0.9rem 1.1rem;
        box-shadow: 0 3px 14px rgba(41, 72, 152, 0.05);
        height: 100%;
    }
    .soft-card {
        background: #ffffff;
        border: 1px solid #edf1f7;
        border-radius: 20px;
        padding: 1rem 1.1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
        margin-bottom: 0.75rem;
    }
    .note {
        color: #5c6675;
        font-size: 0.96rem;
        line-height: 1.65;
    }
    .metric-card {
        background: #ffffff;
        border: 1px solid #edf1f7;
        border-radius: 18px;
        padding: 0.75rem 0.9rem;
        text-align: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }
    .metric-label {
        color: #687385;
        font-size: 0.9rem;
        margin-bottom: 0.2rem;
    }
    .metric-value {
        font-size: 1.25rem;
        font-weight: 800;
        color: #1d2a39;
    }
    .small-caption {
        color: #768396;
        font-size: 0.88rem;
    }
    div[data-testid="stButton"] > button {
        border-radius: 12px;
        border: 1px solid #d8e2f1;
        font-weight: 600;
        min-height: 42px;
    }
    div[data-testid="stNumberInput"] input,
    div[data-testid="stTextInput"] input {
        border-radius: 12px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================
# Safe function parsing
# =========================
ALLOWED_NAMES = {
    "np": np,
    "sin": np.sin,
    "cos": np.cos,
    "tan": np.tan,
    "exp": np.exp,
    "log": np.log,
    "sqrt": np.sqrt,
    "abs": np.abs,
    "pi": np.pi,
    "e": np.e,
}

PRESET_FUNCS = {
    "f(x)=x": "x",
    "f(x)=x²": "x**2",
    "f(x)=x³": "x**3",
    "f(x)=sin(x)": "sin(x)",
    "f(x)=cos(x)": "cos(x)",
    "f(x)=eˣ": "exp(x)",
    "f(x)=e⁻ˣ²": "exp(-x**2)",
}


def parse_function(expr: str):
    expr = expr.strip()

    def f(x):
        local_dict = {"x": x}
        return eval(expr, {"__builtins__": {}}, {**ALLOWED_NAMES, **local_dict})

    test_x = np.array([0.0, 1.0], dtype=float)
    test_y = f(test_x)
    _ = np.asarray(test_y, dtype=float)
    return f


def safe_eval_function(f, x):
    y = f(x)
    return np.asarray(y, dtype=float)


def cumulative_integral(x_grid: np.ndarray, y_grid: np.ndarray) -> np.ndarray:
    """Compute cumulative integral with trapezoidal rule."""
    A = np.zeros_like(x_grid, dtype=float)
    dx = np.diff(x_grid)
    avg_h = 0.5 * (y_grid[:-1] + y_grid[1:])
    A[1:] = np.cumsum(dx * avg_h)
    return A


def make_metric(label: str, value: str, caption: str = ""):
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="small-caption">{caption}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================
# Session state
# =========================
defaults = {
    "func_expr": "x**2",
    "a_val": 0.0,
    "b_val": 4.0,
    "current_x": 2.0,
    "delta_x": 0.2,
    "n_points": 900,
    "show_difference_curve": True,
    "show_learning_panel": True,
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value


# =========================
# Header
# =========================
st.markdown(
    """
    <div class="hero">
        <div class="hero-title">微積分第一基本定理視覺化教學平台</div>
        <div class="hero-sub">
            這個平台協助學生從<strong>累積量</strong>的角度理解
            <em>First Fundamental Theorem of Calculus</em>：
            固定起點 <strong>a</strong>，觀察從 <strong>a</strong> 到目前位置 <strong>x</strong> 的累積面積如何形成新函數
            <strong>A(x)</strong>，再進一步看見 <strong>A′(x)=f(x)</strong> 的數值與圖形意義。
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

formula_col1, formula_col2 = st.columns(2)
with formula_col1:
    st.markdown('<div class="formula-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">累積函數</div>', unsafe_allow_html=True)
    st.latex(r"A(x)=\int_a^x f(t)\,dt")
    st.markdown(
        '<div class="note">從固定起點 a 到目前位置 x 的面積累積，形成一個新的函數 A(x)。</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

with formula_col2:
    st.markdown('<div class="formula-card">', unsafe_allow_html=True)
    st.markdown('<div class="section-title">第一基本定理</div>', unsafe_allow_html=True)
    st.latex(r"\frac{d}{dx}\int_a^x f(t)\,dt = f(x)")
    st.markdown(
        '<div class="note">累積函數的瞬時變化率，等於原函數在當下位置的值。</div>',
        unsafe_allow_html=True,
    )
    st.markdown('</div>', unsafe_allow_html=True)

tab_main, tab_guide, tab_help = st.tabs(["主視覺化畫面", "學習引導", "使用說明"])

with tab_main:
    st.markdown("### 預設函數快速切換")
    bcols = st.columns(len(PRESET_FUNCS))
    for i, (label, expr) in enumerate(PRESET_FUNCS.items()):
        with bcols[i]:
            if st.button(label, use_container_width=True, key=f"preset_{i}"):
                st.session_state.func_expr = expr

    st.markdown("")

    left_col, right_col = st.columns([1.05, 2.25], gap="large")

    with left_col:
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">參數設定</div>', unsafe_allow_html=True)

        func_expr = st.text_input(
            "輸入函數 f(x)",
            value=st.session_state.func_expr,
            help="可輸入：x、x**2、sin(x)、cos(x)、exp(x)、exp(-x**2)、log(x+1)",
        )
        st.session_state.func_expr = func_expr

        c1, c2 = st.columns(2)
        with c1:
            a_val = st.number_input("起點 a", value=float(st.session_state.a_val), step=0.1, format="%.2f")
        with c2:
            b_val = st.number_input("終點 b", value=float(st.session_state.b_val), step=0.1, format="%.2f")

        n_points = st.slider("取樣點數 n", min_value=300, max_value=2400, value=int(st.session_state.n_points), step=100)

        st.session_state.a_val = a_val
        st.session_state.b_val = b_val
        st.session_state.n_points = n_points

        if b_val <= a_val:
            st.error("終點 b 必須大於起點 a。")
            st.stop()

        if st.session_state.current_x < a_val:
            st.session_state.current_x = a_val
        if st.session_state.current_x > b_val:
            st.session_state.current_x = b_val

        x_step = max((b_val - a_val) / 200, 0.01)
        current_x = st.slider(
            "目前位置 x",
            min_value=float(a_val),
            max_value=float(b_val),
            value=float(st.session_state.current_x),
            step=float(x_step),
        )
        st.session_state.current_x = current_x

        delta_x = st.slider(
            "差商用的 Δx",
            min_value=0.01,
            max_value=min(1.2, max(0.05, b_val - a_val)),
            value=float(min(st.session_state.delta_x, min(1.2, max(0.05, b_val - a_val)))),
            step=0.01,
        )
        st.session_state.delta_x = delta_x

        st.checkbox("顯示差商近似曲線", key="show_difference_curve")
        st.checkbox("顯示學習提示面板", key="show_learning_panel")

        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.markdown('<div class="section-title">可直接測試的函數</div>', unsafe_allow_html=True)
        st.code(
            "x\nx**2\nx**3\nsin(x)\ncos(x)\nexp(x)\nexp(-x**2)\nlog(x+1)",
            language="python",
        )
        st.markdown(
            """
            <div class="note">
            建議先從 <strong>x</strong> 或 <strong>x**2</strong> 開始，再切換到 <strong>sin(x)</strong> 或
            <strong>exp(-x**2)</strong>，觀察累積函數圖形如何改變。
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

    # build function and data
    try:
        f = parse_function(func_expr)
    except Exception as e:
        right_col.error(f"函數解析失敗：{e}")
        st.stop()

    x_grid = np.linspace(a_val, b_val, n_points)
    try:
        y_grid = safe_eval_function(f, x_grid)
    except Exception as e:
        right_col.error(f"函數計算失敗：{e}")
        st.stop()

    if np.any(~np.isfinite(y_grid)):
        right_col.error("函數值中出現非有限數（例如 NaN 或 inf），請修改函數或區間。")
        st.stop()

    A_grid = cumulative_integral(x_grid, y_grid)

    y0 = float(safe_eval_function(f, np.array([current_x]))[0])
    A0 = float(np.interp(current_x, x_grid, A_grid))
    x1 = min(current_x + delta_x, b_val)
    if np.isclose(x1, current_x):
        x1 = max(current_x - delta_x, a_val)
    A1 = float(np.interp(x1, x_grid, A_grid))
    dq = (A1 - A0) / (x1 - current_x) if not np.isclose(x1, current_x) else np.nan
    error = abs(dq - y0) if np.isfinite(dq) else np.nan

    with right_col:
        st.markdown("### 即時數值資訊")
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            make_metric("f(x₀)", f"{y0:.8f}", "原函數當下值")
        with m2:
            make_metric("A(x₀)", f"{A0:.8f}", "累積函數當下值")
        with m3:
            make_metric("差商", f"{dq:.8f}", "A(x) 的局部變化率")
        with m4:
            make_metric("|差商 - f(x₀)|", f"{error:.8f}", "兩者差距")

        fig, axes = plt.subplots(2, 2, figsize=(14, 9))
        fig.subplots_adjust(hspace=0.38, wspace=0.24)

        ax1, ax2 = axes[0]
        ax3, ax4 = axes[1]

        # chart 1
        ax1.plot(x_grid, y_grid, linewidth=2.2, label="f(x)")
        x_fill = x_grid[x_grid <= current_x]
        y_fill = y_grid[x_grid <= current_x]
        if len(x_fill) >= 2:
            ax1.fill_between(x_fill, 0, y_fill, alpha=0.35, label=r"$\int_a^x f(t)\,dt$")
        ax1.axvline(a_val, linestyle="--", linewidth=1)
        ax1.axvline(current_x, linestyle="--", linewidth=1)
        ax1.scatter([current_x], [y0], s=45)
        ax1.set_title("原函數與從 a 到 x 的累積面積")
        ax1.set_xlabel("x")
        ax1.set_ylabel("y")
        ax1.grid(True, alpha=0.28)
        ax1.legend()

        # chart 2
        ax2.plot(x_grid, A_grid, linewidth=2.2, label=r"$A(x)=\int_a^x f(t)\,dt$")
        ax2.scatter([current_x], [A0], s=45)
        ax2.axvline(current_x, linestyle="--", linewidth=1)
        ax2.set_title("累積函數 A(x)")
        ax2.set_xlabel("x")
        ax2.set_ylabel("A(x)")
        ax2.grid(True, alpha=0.28)
        ax2.legend()

        # chart 3
        ax3.plot(x_grid, y_grid, linewidth=2.2, label="f(x)")
        if st.session_state.show_difference_curve:
            local_points = np.linspace(a_val, b_val - delta_x, max(140, n_points // 8))
            dq_x = []
            dq_y = []
            for xx in local_points:
                xx2 = xx + delta_x
                if xx2 <= b_val:
                    AA0 = float(np.interp(xx, x_grid, A_grid))
                    AA1 = float(np.interp(xx2, x_grid, A_grid))
                    dq_x.append(xx)
                    dq_y.append((AA1 - AA0) / (xx2 - xx))
            dq_x = np.array(dq_x)
            dq_y = np.array(dq_y)
            if len(dq_x) > 0:
                ax3.plot(dq_x, dq_y, linestyle="--", linewidth=1.8, label="difference quotient of A(x)")
        ax3.scatter([current_x], [y0], s=45, label="f(x₀)")
        if np.isfinite(dq):
            ax3.scatter([current_x], [dq], s=45, label="dq at x₀")
        ax3.set_title("f(x) 與 A(x) 差商近似比較")
        ax3.set_xlabel("x")
        ax3.set_ylabel("value")
        ax3.grid(True, alpha=0.28)
        ax3.legend()

        # chart 4
        ax4.plot(x_grid, A_grid, linewidth=2.2, label="A(x)")
        ax4.scatter([current_x, x1], [A0, A1], s=45)
        if not np.isclose(x1, current_x):
            slope = dq
            line_x = np.array([max(a_val, current_x - 0.55), min(b_val, current_x + 0.55)])
            line_y = A0 + slope * (line_x - current_x)
            ax4.plot(line_x, line_y, linestyle="--", linewidth=2, label="secant approximation")
        ax4.axvline(current_x, linestyle="--", linewidth=1)
        ax4.axvline(x1, linestyle="--", linewidth=1)
        ax4.set_title("A(x) 的局部差商示意")
        ax4.set_xlabel("x")
        ax4.set_ylabel("A(x)")
        ax4.grid(True, alpha=0.28)
        ax4.legend()

        st.pyplot(fig, use_container_width=True)

        st.markdown("### 概念解讀")
        st.markdown('<div class="soft-card">', unsafe_allow_html=True)
        st.latex(r"\frac{A(x+\Delta x)-A(x)}{\Delta x}\approx f(x)")
        st.markdown(
            f"""
            <div class="note">
            目前位置為 <strong>x = {current_x:.4f}</strong>。此時：
            <ul>
              <li><strong>f(x₀) = {y0:.8f}</strong></li>
              <li><strong>A(x₀) = {A0:.8f}</strong></li>
              <li><strong>差商 = {dq:.8f}</strong></li>
              <li><strong>|差商 - f(x₀)| = {error:.8f}</strong></li>
            </ul>
            當 <strong>Δx</strong> 越小時，通常越能觀察到差商逼近 <strong>f(x)</strong>。這正是第一基本定理在
            圖形與數值層面的核心意義：累積函數的瞬時變化率，等於原函數當下的值。
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('</div>', unsafe_allow_html=True)

        if st.session_state.show_learning_panel:
            st.markdown("### 學習觀察提示")
            st.markdown(
                """
                <div class="soft-card note">
                你可以依序觀察四件事：
                <ol>
                  <li>當 <strong>x</strong> 往右移動時，陰影面積如何增加或減少。</li>
                  <li>累積面積如何在右上圖形成新的函數 <strong>A(x)</strong>。</li>
                  <li>原函數 <strong>f(x)</strong> 的高低，如何影響 <strong>A(x)</strong> 的局部斜率。</li>
                  <li>當 <strong>Δx</strong> 變小時，差商如何更接近 <strong>f(x)</strong>。</li>
                </ol>
                </div>
                """,
                unsafe_allow_html=True,
            )

with tab_guide:
    st.markdown("### 教學引導建議")
    st.markdown(
        """
        <div class="soft-card note">
        <strong>建議教學流程：</strong><br><br>
        1. 先使用 <strong>f(x)=x</strong> 或 <strong>f(x)=x²</strong>，讓學生觀察面積如何累積。<br>
        2. 引導學生比較左上圖與右上圖，理解「面積」如何變成「函數值」。<br>
        3. 再調整 <strong>Δx</strong>，讓學生在左下與右下圖中觀察差商與原函數值之間的關係。<br>
        4. 最後要求學生用自己的話說明：
        <br><br>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.latex(r"\frac{d}{dx}\int_a^x f(t)\,dt=f(x)")
    st.markdown(
        """
        <div class="soft-card note">
        <strong>可作為研究中的觀察重點：</strong>
        <ul>
          <li>學生是否能把定積分理解為累積量，而非單一答案。</li>
          <li>學生是否能把變上限積分看成函數。</li>
          <li>學生是否能解釋為什麼 A′(x) 會回到 f(x)。</li>
          <li>學生是否能在圖形、數值與符號之間來回轉換。</li>
        </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

with tab_help:
    st.markdown("### 使用說明")
    st.markdown(
        """
        <div class="soft-card note">
        <strong>函數輸入範例：</strong><br>
        x<br>
        x**2<br>
        x**3<br>
        sin(x)<br>
        cos(x)<br>
        exp(x)<br>
        exp(-x**2)<br>
        log(x+1)<br><br>

        <strong>注意：</strong><br>
        1. 請使用 Python 語法，例如 <code>x**2</code> 表示 x²。<br>
        2. 若輸入 <code>log(x+1)</code>，請注意區間需使函數值有效。<br>
        3. 若函數在所選區間內出現無法計算的值，平台會顯示錯誤提醒。<br>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown("---")
st.caption("Interactive Visualization Tool for the First Fundamental Theorem of Calculus")
