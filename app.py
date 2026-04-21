import re
import numpy as np
import matplotlib
import matplotlib.pyplot as plt
from scipy.integrate import quad
import streamlit as st

# ----------------------
# 頁面設定
# ----------------------
st.set_page_config(
    page_title="微積分視覺實驗室｜黎曼和教學平台",
    page_icon="📘",
    layout="wide"
)

# ----------------------
# 圖表字型設定（英文，避免中文方塊）
# ----------------------
matplotlib.rcParams["font.family"] = "sans-serif"
matplotlib.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "Liberation Sans"]
matplotlib.rcParams["axes.unicode_minus"] = False

plt.rcParams.update({
    "font.size": 13,
    "axes.titlesize": 18,
    "axes.labelsize": 14,
    "xtick.labelsize": 11,
    "ytick.labelsize": 11,
    "legend.fontsize": 11
})

# ----------------------
# 介面美化 CSS
# ----------------------
st.markdown("""
<style>
.block-container {
    padding-top: 1.2rem;
    padding-bottom: 1.5rem;
    max-width: 1350px;
}
.main-title {
    font-size: 2rem;
    font-weight: 700;
    margin-bottom: 0.2rem;
}
.sub-title {
    font-size: 1rem;
    color: #4b5563;
    margin-bottom: 1rem;
}
.hero-box {
    background: linear-gradient(135deg, #eef4ff 0%, #f8fbff 100%);
    border: 1px solid #dbe7ff;
    border-radius: 16px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1rem;
}
.info-card {
    background: #f8fafc;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 0.9rem 1rem;
    margin-bottom: 0.8rem;
}
.metric-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 14px;
    padding: 0.8rem 1rem;
    text-align: center;
}
.small-note {
    color: #6b7280;
    font-size: 0.92rem;
}
.section-title {
    font-size: 1.15rem;
    font-weight: 700;
    margin-top: 0.3rem;
    margin-bottom: 0.7rem;
}
div[data-testid="stSidebar"] {
    border-right: 1px solid #e5e7eb;
}
</style>
""", unsafe_allow_html=True)

# ----------------------
# 方法定義（4種）
# ----------------------
methods_dict = {
    "左端點法": lambda f, a, b, n: (
        np.linspace(a, b, n, endpoint=False),
        f(np.linspace(a, b, n, endpoint=False)),
        (b - a) / n
    ),
    "右端點法": lambda f, a, b, n: (
        np.linspace(a, b, n, endpoint=False) + (b - a) / n,
        f(np.linspace(a, b, n, endpoint=False) + (b - a) / n),
        (b - a) / n
    ),
    "中點法": lambda f, a, b, n: (
        np.linspace(a, b, n, endpoint=False) + (b - a) / (2 * n),
        f(np.linspace(a, b, n, endpoint=False) + (b - a) / (2 * n)),
        (b - a) / n
    ),
    "隨機取點法": None
}

method_display_map = {
    "左端點法": "Left Endpoint",
    "右端點法": "Right Endpoint",
    "中點法": "Midpoint",
    "隨機取點法": "Random Sample"
}

# ----------------------
# 安全函數解析
# ----------------------
def normalize_function_input(func_str: str) -> str:
    s = func_str.strip()
    s = s.replace("^", "**")
    s = re.sub(r"\s+", "", s)

    # 先將容易和隱含乘號規則衝突的函數名稱暫時替換成純字母代號
    # 這樣可避免 log10(x) 被錯誤改成 log10*(x)
    s = re.sub(r"np\.log10(?=\()", "__NPLOGTEN__", s)
    s = re.sub(r"np\.log2(?=\()", "__NPLOGTWO__", s)
    s = re.sub(r"log10(?=\()", "__LOGTEN__", s)
    s = re.sub(r"log2(?=\()", "__LOGTWO__", s)
    s = re.sub(r"ln(?=\()", "__LOG__", s)

    func_pattern = r"(?:__NPLOGTEN__|__NPLOGTWO__|__LOGTEN__|__LOGTWO__|__LOG__|np\.(?:sin|cos|tan|exp|log|sqrt|abs)|sin|cos|tan|exp|log|sqrt|abs|pi|e)"

    # 自動補上省略的乘號
    s = re.sub(rf"(?<=\d)(?=(?:x|\(|{func_pattern}))", "*", s)
    s = re.sub(rf"(?<=x)(?=(?:\(|{func_pattern}|\d))", "*", s)
    s = re.sub(rf"(?<=\))(?=(?:x|\(|{func_pattern}|\d))", "*", s)

    # 還原函數名稱
    s = s.replace("__NPLOGTEN__", "np.log10")
    s = s.replace("__NPLOGTWO__", "np.log2")
    s = s.replace("__LOGTEN__", "log10")
    s = s.replace("__LOGTWO__", "log2")
    s = s.replace("__LOG__", "log")

    return s

def parse_function(func_str: str):
    allowed_names = {
        "np": np,
        "sin": np.sin,
        "cos": np.cos,
        "tan": np.tan,
        "exp": np.exp,
        "log": np.log,
        "ln": np.log,
        "log10": np.log10,
        "log2": np.log2,
        "sqrt": np.sqrt,
        "abs": np.abs,
        "pi": np.pi,
        "e": np.e
    }

    normalized_func_str = normalize_function_input(func_str)

    def f(x):
        return eval(normalized_func_str, {"__builtins__": {}}, {"x": x, **allowed_names})

    return f

# ----------------------
# 隨機取點法
# ----------------------
def random_sample_method(f, a, b, n, seed=None):
    rng = np.random.default_rng(seed)
    dx = (b - a) / n
    left_edges = np.linspace(a, b, n, endpoint=False)
    random_x = left_edges + rng.random(n) * dx
    random_y = f(random_x)
    return left_edges, random_x, random_y, dx

# ----------------------
# 單一方法繪圖
# ----------------------
def draw_single_method(f, func_str, method, a, b, n, color_hex, seed=None):
    x_plot = np.linspace(a, b, 800)
    y_plot = f(x_plot)

    fig, ax = plt.subplots(figsize=(11, 5.8))
    ax.plot(x_plot, y_plot, color="#2563eb", linewidth=2.6, label=f"f(x) = {func_str}")

    if method == "隨機取點法":
        left_edges, random_x, y_vals, dx = random_sample_method(f, a, b, n, seed=seed)
        riemann_sum = np.sum(y_vals * dx)

        for i in range(len(left_edges)):
            ax.bar(
                left_edges[i],
                y_vals[i],
                width=dx,
                color=color_hex,
                alpha=0.58,
                align="edge",
                edgecolor="#6b7280",
                linewidth=0.9
            )
            ax.plot(random_x[i], y_vals[i], "ko", markersize=4)

    else:
        x_vals, y_vals, dx = methods_dict[method](f, a, b, n)
        riemann_sum = np.sum(y_vals * dx)

        for i in range(len(x_vals)):
            if method == "左端點法":
                left = x_vals[i]
            elif method == "右端點法":
                left = x_vals[i] - dx
            else:
                left = x_vals[i] - dx / 2

            ax.bar(
                left,
                y_vals[i],
                width=dx,
                color=color_hex,
                alpha=0.58,
                align="edge",
                edgecolor="#6b7280",
                linewidth=0.9
            )

    exact, _ = quad(f, a, b)
    error = abs(exact - riemann_sum)

    display_method = method_display_map.get(method, method)
    ax.set_title(f"{display_method} (n = {n})")
    ax.set_xlabel("x")
    ax.set_ylabel("f(x)")
    ax.grid(alpha=0.22)
    ax.axhline(0, color="black", linewidth=1)
    ax.legend(loc="upper left")

    return fig, riemann_sum, exact, error

# ----------------------
# 計算各方法近似值
# ----------------------
def compute_method_value(f, method, a, b, n, seed=None):
    if method == "隨機取點法":
        _, _, y_vals, dx = random_sample_method(f, a, b, n, seed=seed)
        return np.sum(y_vals * dx)

    _, y_vals, dx = methods_dict[method](f, a, b, n)
    return np.sum(y_vals * dx)

# ----------------------
# session state
# ----------------------
if "random_seed" not in st.session_state:
    st.session_state.random_seed = int(np.random.randint(0, 10**9))

if "func_str" not in st.session_state:
    st.session_state.func_str = "x^2-3x+5"

# ----------------------
# 頁首區
# ----------------------
st.markdown("""
<div class="hero-box">
    <div class="main-title">📘 微積分視覺實驗室：黎曼和教學平台</div>
    <div class="sub-title">
        透過圖形、數值與方法比較，觀察黎曼和如何近似曲線下方面積，建立定積分的直觀理解。
    </div>
</div>
""", unsafe_allow_html=True)

intro_col1, intro_col2 = st.columns([1.5, 1.5])

with intro_col1:
    st.markdown("""
    <div class="info-card">
        <div class="section-title">學習目標</div>
        了解不同取點方式如何影響面積近似值，並比較誤差隨分割數改變的情形。
    </div>
    """, unsafe_allow_html=True)

with intro_col2:
    st.markdown("""
    <div class="info-card">
        <div class="section-title">操作方式</div>
        選擇函數、調整區間與分割數，再切換四種方法觀察圖形與數值差異。
    </div>
    """, unsafe_allow_html=True)


# ----------------------
# 側邊欄
# ----------------------
st.sidebar.markdown("## 操作面板")

st.sidebar.markdown("### 函數設定")
func_str = st.sidebar.text_input("輸入函數", key="func_str")
st.sidebar.caption("支援輸入範例：x^2、2x、3(x+1)、2sin(x)、sqrt(x+1)、ln(x)、log10(x)、log2(x)\n若使用對數函數，請設定區間滿足 x > 0，例如 a = 1、b = 5")

with st.sidebar.expander("輸入語法說明"):
    st.markdown("""
    <style>
    .syntax-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.93rem;
        margin-top: 0.2rem;
    }
    .syntax-table th, .syntax-table td {
        border: 1px solid #e5e7eb;
        padding: 8px 10px;
        vertical-align: top;
    }
    .syntax-table th {
        background: #f8fafc;
        font-weight: 700;
        text-align: left;
    }
    .syntax-group {
        background: #fefce8;
        font-weight: 700;
        white-space: nowrap;
        width: 28%;
    }
    .syntax-note {
        font-size: 0.88rem;
        color: #4b5563;
        margin-top: 0.7rem;
        line-height: 1.5;
    }
    </style>

    <table class="syntax-table">
        <thead>
            <tr>
                <th>類別</th>
                <th>可輸入語法與說明</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td class="syntax-group">基本代數</td>
                <td>
                    <code>x^2</code>代表：x 的平方<br>
                    <code>x^3</code>代表：x 的立方<br>
                    <code>2x</code>：代表 <code>2*x</code><br>
                    <code>3(x+1)</code>：代表 <code>3*(x+1)</code><br>
                    <code>(x+1)(x-1)</code>：代表 <code>(x+1)*(x-1)</code>
                </td>
            </tr>
            <tr>
                <td class="syntax-group">三角函數</td>
                <td>
                    <code>sin(x)</code><br>
                    <code>cos(x)</code><br>
                    <code>tan(x)</code><br>
                    <code>2sin(x)</code>：代表 <code>2*sin(x)</code><br>
                    <code>xcos(x)</code>：代表 <code>x*cos(x)</code>
                </td>
            </tr>
            <tr>
                <td class="syntax-group">指數與根號</td>
                <td>
                    <code>e^x</code>：代表 e 的 x 次方<br>
                    <code>sqrt(x)</code>：x 的平方根<br>
                    <code>2sqrt(x+1)</code>：代表 <code>2*sqrt(x+1)</code>
                </td>
            </tr>
            <tr>
                <td class="syntax-group">對數函數</td>
                <td>
                    <code>ln(x)</code>：自然對數<br>
                    <code>log10(x)</code>：以 10 為底的常用對數<br>
                    <code>log2(x)</code>：以 2 為底的對數<br>
                    <code>2log10(x)</code>：代表 <code>2*log10(x)</code>
                </td>
            </tr>
            <tr>
                <td class="syntax-group">常數</td>
                <td>
                    <code>pi</code>：圓周率<br>
                    <code>e</code>：自然常數
                </td>
            </tr>
            <tr>
                <td class="syntax-group">混合範例</td>
                <td>
                    <code>x^2-3x+5</code><br>
                    <code>2x^2+3x-1</code><br>
                    <code>sin(x)+x^2</code><br>
                    <code>exp(-x)+2sin(x)</code><br>
                    <code>log(x)+x^2</code><br>
                    <code>sqrt(x+1)+x</code>
                </td>
            </tr>
        </tbody>
    </table>

    <div class="syntax-note">
        <b>注意事項：</b><br>
        1. 對數函數 <code>log(x)</code>、<code>ln(x)</code>、<code>log10(x)</code>、<code>log2(x)</code> 需滿足 <code>x &gt; 0</code>。<br>
        2. 若使用根號，請注意根號內的值要合法，例如 <code>sqrt(x)</code> 需滿足 <code>x &gt;= 0</code>。<br>
        3. 請使用英文括號 <code>()</code>。
    </div>
    """, unsafe_allow_html=True)

st.sidebar.markdown("### 圖形顯示設定")
view_mode = st.sidebar.radio("顯示模式", ["單一方法", "四種方法比較"])
method = st.sidebar.selectbox("選擇方法", list(methods_dict.keys()))
n = st.sidebar.slider("分割數 n", 1, 100, 6)

st.sidebar.markdown("### 區間範圍設定")
a = st.sidebar.number_input("左 a", value=0.0)
b = st.sidebar.number_input("右 b", value=5.0)
color_hex = st.sidebar.color_picker("選擇顏色", "#ff6b6b")

st.sidebar.markdown("### 隨機取點")
if st.sidebar.button("重新隨機抽樣", use_container_width=True):
    st.session_state.random_seed = int(np.random.randint(0, 10**9))

seed = st.session_state.random_seed


if a >= b:
    st.error("請設定正確區間：必須滿足 a < b。")
    st.stop()

# ----------------------
# 解析函數
# ----------------------
try:
    f = parse_function(func_str)
    test_x = np.linspace(a, b, 50)
    test_y = np.asarray(f(test_x), dtype=float)

    if not np.all(np.isfinite(test_y)):
        st.error("函數在此區間內出現無效值，請調整函數或積分區間。若使用 ln(x)、log10(x)、log2(x)，請設定區間滿足 x > 0，例如 a = 1、b = 5。")
        st.stop()

except Exception:
    st.error("函數輸入錯誤。可輸入例如：x^2、2x、3(x+1)、2sin(x)、sqrt(x+1)、ln(x)、log10(x)、log2(x)")
    st.stop()

# ----------------------
# 主區塊
# ----------------------
tab1, tab2, tab3 = st.tabs(["互動圖形", "誤差比較", "教學說明"])

with tab1:
    st.markdown("### ")

    if view_mode == "單一方法":
        fig, riemann_sum, exact, error = draw_single_method(
            f, func_str, method, a, b, n, color_hex, seed=seed
        )
        st.pyplot(fig, use_container_width=True)

        m1, m2, m3 = st.columns(3)
        with m1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="small-note">黎曼和近似值</div>
                <div style="font-size:1.5rem;font-weight:700;">{riemann_sum:.5f}</div>
            </div>
            """, unsafe_allow_html=True)
        with m2:
            st.markdown(f"""
            <div class="metric-card">
                <div class="small-note">精確積分值</div>
                <div style="font-size:1.5rem;font-weight:700;">{exact:.5f}</div>
            </div>
            """, unsafe_allow_html=True)
        with m3:
            st.markdown(f"""
            <div class="metric-card">
                <div class="small-note">誤差</div>
                <div style="font-size:1.5rem;font-weight:700;">{error:.5f}</div>
            </div>
            """, unsafe_allow_html=True)

    else:
        exact, _ = quad(f, a, b)
        results = []

        compare_methods = ["左端點法", "右端點法", "中點法", "隨機取點法"]

        row1_col1, row1_col2 = st.columns(2)
        row2_col1, row2_col2 = st.columns(2)

        layout_map = {
            "左端點法": row1_col1,
            "右端點法": row1_col2,
            "中點法": row2_col1,
            "隨機取點法": row2_col2
        }

        label_map = {
            "左端點法": "左端點法",
            "右端點法": "右端點法",
            "中點法": "中點法",
            "隨機取點法": "隨機取點法"
        }

        for m in compare_methods:
            current_seed = seed if m == "隨機取點法" else None
            fig, approx, _, err = draw_single_method(
                f, func_str, m, a, b, n, color_hex, seed=current_seed
            )

            with layout_map[m]:
                st.markdown(f"#### {label_map[m]}")
                st.pyplot(fig, use_container_width=True)

            results.append((m, approx, exact, err))

        st.markdown("### 四種方法數值比較")
        st.dataframe(
            {
                "方法": [r[0] for r in results],
                "近似值": [round(r[1], 5) for r in results],
                "精確值": [round(r[2], 5) for r in results],
                "誤差": [round(r[3], 5) for r in results],
            },
            use_container_width=True,
            hide_index=True
        )


with tab2:
    st.markdown("### 誤差分析與方法比較")

    exact, _ = quad(f, a, b)
    method_names_cn = list(methods_dict.keys())
    method_names_en = [method_display_map[m] for m in method_names_cn]

    approx_vals = []
    errors = []

    for m in method_names_cn:
        current_seed = seed if m == "隨機取點法" else None
        approx = compute_method_value(f, m, a, b, n, seed=current_seed)
        approx_vals.append(approx)
        errors.append(abs(exact - approx))

    col1, col2 = st.columns(2)

    with col1:
        fig1, ax1 = plt.subplots(figsize=(6.2, 4.6))
        ax1.bar(method_names_en, approx_vals)
        ax1.axhline(exact, linestyle="--", linewidth=1.5, label="Exact value")
        ax1.set_title("Approximation Comparison")
        ax1.set_ylabel("Approximation")
        ax1.legend()
        ax1.grid(alpha=0.2)
        ax1.tick_params(axis="x", rotation=15)
        st.pyplot(fig1, use_container_width=True)

    with col2:
        fig2, ax2 = plt.subplots(figsize=(6.2, 4.6))
        ax2.bar(method_names_en, errors)
        ax2.set_title("Error Comparison")
        ax2.set_ylabel("Error")
        ax2.grid(alpha=0.2)
        ax2.tick_params(axis="x", rotation=15)
        st.pyplot(fig2, use_container_width=True)

    st.dataframe(
        {
            "方法": method_names_cn,
            "近似值": [round(v, 5) for v in approx_vals],
            "精確值": [round(exact, 5)] * len(method_names_cn),
            "誤差": [round(e, 5) for e in errors]
        },
        use_container_width=True,
        hide_index=True
    )

with tab3:
    st.markdown("### 教學說明")
    st.markdown("""
#### 1. 什麼是黎曼和？
黎曼和是把曲線下方的面積切成很多小塊，再用長方形去近似面積的方法。

#### 2. 四種取點方法
- 左端點法：每小區間取左端點，以該點的函數值作為長方形高度
- 右端點法：每小區間取右端點，以該點的函數值作為長方形高度
- 中點法：每小區間取中間點，以該點的函數值作為長方形高度
- 隨機取點法：每小區間隨機取一個點，以該點的函數值作為長方形高度

#### 3. 如何觀察？
可以改變：
- 函數
- 區間範圍
- 分割數 n
- 四種取點方法

然後比較：
- 近似值是否接近精確值
- 哪一種方法誤差較小
- 當 n 增加時，誤差如何變化

""")
