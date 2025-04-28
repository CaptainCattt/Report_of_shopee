import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px
import io


def process_shopee_daily_report(df_all, df_income):
    df_income.columns = df_income.columns.str.strip()
    df_all.columns = df_all.columns.str.strip()
    df_all["Actually type"] = df_all["Trạng Thái Đơn Hàng"]
    df_all["Actually type"] = df_all["Actually type"].apply(
        lambda x: (
            "Đơn hàng đã đến User"
            if isinstance(x, str) and "Người mua xác nhận đã nhận được hàng" in x
            else x
        )
    )
    df_all["SKU Category"] = df_all["SKU phân loại hàng"].copy()

    # Danh sách các mẫu thay thế
    replacements = {
        r"^(COMBO-SC-ANHDUC|COMBO-SC-NGOCTRINH|COMBO-SC-MIX|SC_COMBO_MIX)": "COMBO-SC",
        r"^(SC_X1)": "SC-450g",
        r"^(SC_X2)": "SC-x2-450g",
        r"^(SC_COMBO_X1|COMBO-CAYVUA-X1)": "COMBO-SCX1",
        r"^(SC_COMBO_X2|COMBO-SIEUCAY-X2)": "COMBO-SCX2",
        r"^(BTHP-Cay-200gr|BTHP_Cay)": "BTHP-CAY",
        r"^(BTHP-200gr|BTHP_KhongCay)": "BTHP-0CAY",
        r"^(BTHP_COMBO_MIX|BTHP003_combo_mix)": "BTHP-COMBO",
        r"^(BTHP_COMBO_KhongCay|BTHP003_combo_kocay)": "BTHP-COMBO-0CAY",
        r"^(BTHP_COMBO_Cay|BTHP003_combo_cay)": "BTHP-COMBO-CAY",
    }

    for pattern, replacement in replacements.items():
        df_all["SKU Category"] = df_all["SKU Category"].str.replace(
            pattern, replacement, regex=True
        )
    date_columns_shopee = [
        "Ngày đặt hàng",
        "Ngày giao hàng dự kiến",
        "Ngày gửi hàng",
        "Thời gian giao hàng",
    ]

    # Ép kiểu về datetime với định dạng đúng
    df_all[date_columns_shopee] = df_all[date_columns_shopee].apply(
        lambda col: pd.to_datetime(col, errors="coerce", format="%Y-%m-%d %H:%M")
    )

    # Loại bỏ giờ, giữ lại phần ngày
    for col in date_columns_shopee:
        df_all[col] = df_all[col].dt.normalize()

    # Kiểm tra xem cột còn tồn tại không

    if "Mã đơn hàng" not in df_income.columns or "Mã đơn hàng" not in df_all.columns:
        st.error("Không tìm thấy cột 'Mã đơn hàng' trong file!")
    else:
        df_merged = pd.merge(
            df_income,
            df_all,
            how="left",
            right_on="Mã đơn hàng",
            left_on="Mã đơn hàng",
        )

    Don_quyet_toan = df_merged
    So_don_quyet_toan = len(Don_quyet_toan["Mã đơn hàng"].drop_duplicates())

    Don_hoan_thanh = df_merged[df_merged["Tổng tiền đã thanh toán"] > 0]
    So_don_hoan_thanh = len(Don_hoan_thanh["Mã đơn hàng"].drop_duplicates())

    Don_hoan_tra = df_merged[
        (df_merged["Trạng thái Trả hàng/Hoàn tiền"] == "Đã Chấp Thuận Yêu Cầu")
    ]

    So_don_hoan_tra = len(Don_hoan_tra["Mã đơn hàng"].drop_duplicates())

    Scx1_hoan_thanh = Don_hoan_thanh[Don_hoan_thanh["SKU Category"] == "SC-450g"]
    So_luong_Scx1_hoan_thanh = Scx1_hoan_thanh["Số lượng"].sum()

    Scx2_hoan_thanh = Don_hoan_thanh[Don_hoan_thanh["SKU Category"] == "SC-x2-450g"]
    So_luong_Scx2_hoan_thanh = Scx2_hoan_thanh["Số lượng"].sum()

    Sc_Combo_hoan_thanh = Don_hoan_thanh[Don_hoan_thanh["SKU Category"] == "COMBO-SC"]
    So_luong_Sc_Combo_hoan_thanh = Sc_Combo_hoan_thanh["Số lượng"].sum()

    tong_san_pham_sp_hoan_thanh = (
        So_luong_Scx1_hoan_thanh
        + So_luong_Scx2_hoan_thanh
        + So_luong_Sc_Combo_hoan_thanh * 2
    )

    Scx1_hoan_tra = Don_hoan_tra[Don_hoan_tra["SKU Category"] == "SC-450g"]
    So_luong_Scx1_hoan_tra = Scx1_hoan_tra["Số lượng"].sum()

    SCx2_hoan_tra = Don_hoan_tra[Don_hoan_tra["SKU Category"] == "SC-x2-450g"]
    So_luong_SCx2_hoan_tra = SCx2_hoan_tra["Số lượng"].sum()

    SC_Combo_hoan_tra = Don_hoan_tra[Don_hoan_tra["SKU Category"] == "COMBO-SC"]
    So_luong_SC_Combo_hoan_tra = SC_Combo_hoan_tra["Số lượng"].sum()

    Tong_tien_quyet_toan = df_income["Tổng tiền đã thanh toán"].sum()

    Tong_tien_hoan_thanh = df_income["Tổng tiền đã thanh toán"][
        df_income["Tổng tiền đã thanh toán"] > 0
    ].sum()

    # COMBO SCx1, COMBO SCx2

    COMBO_SCx1_hoan_thanh = Don_hoan_thanh[
        Don_hoan_thanh["SKU Category"] == "COMBO-SCX1"
    ]
    so_luong_COMBO_SCx1_hoan_thanh = COMBO_SCx1_hoan_thanh["Số lượng"].sum()

    COMBO_SCx2_hoan_thanh = Don_hoan_thanh[
        Don_hoan_thanh["SKU Category"] == "COMBO-SCX2"
    ]
    so_luong_COMBO_SCx2_hoan_thanh = COMBO_SCx2_hoan_thanh["Số lượng"].sum()

    COMBO_SCx1_hoan_tra = Don_hoan_tra[Don_hoan_tra["SKU Category"] == "COMBO-SCX1"]
    So_luong_COMBO_SCx1_hoan_tra = COMBO_SCx1_hoan_tra["Số lượng"].sum()

    COMBO_SCx2_hoan_tra = Don_hoan_tra[Don_hoan_tra["SKU Category"] == "COMBO-SCX2"]
    So_luong_COMBO_SCx2_hoan_tra = COMBO_SCx2_hoan_tra["Số lượng"].sum()

    # BÁNH TRÁNG

    BTHP_0CAY_hoan_thanh = Don_hoan_thanh[df_merged["SKU Category"] == "BTHP-0CAY"]
    BTHP_CAY_hoan_thanh = Don_hoan_thanh[df_merged["SKU Category"] == "BTHP-CAY"]
    BTHP_COMBO_hoan_thanh = Don_hoan_thanh[df_merged["SKU Category"] == "BTHP-COMBO"]
    BTHP_COMBO_0CAY_hoan_thanh = df_merged[
        df_merged["SKU Category"] == "BTHP-COMBO-0CAY"
    ]
    BTHP_COMBO_CAY_hoan_thanh = df_merged[df_merged["SKU Category"] == "BTHP-COMBO-CAY"]

    so_luong_BTHP_0CAY_hoan_thanh = BTHP_0CAY_hoan_thanh["Số lượng"].sum()
    so_luong_BTHP_CAY_hoan_thanh = BTHP_CAY_hoan_thanh["Số lượng"].sum()
    so_luong_BTHP_COMBO_hoan_thanh = BTHP_COMBO_hoan_thanh["Số lượng"].sum()
    so_luong_BTHP_COMBO_0CAY_hoan_thanh = BTHP_COMBO_0CAY_hoan_thanh["Số lượng"].sum()
    so_luong_BTHP_COMBO_CAY_hoan_thanh = BTHP_COMBO_CAY_hoan_thanh["Số lượng"].sum()

    VonX1 = 43741.24
    VonX2 = 46041.24
    VonCombo = 89782.48

    Tong_von = (
        So_luong_Scx1_hoan_thanh * VonX1
        + So_luong_Scx2_hoan_thanh * VonX2
        + So_luong_Sc_Combo_hoan_thanh * VonCombo
    )

    return (
        Don_quyet_toan,
        Don_hoan_thanh,
        Don_hoan_tra,
        So_don_quyet_toan,
        So_don_hoan_thanh,
        So_don_hoan_tra,
        So_luong_Scx1_hoan_thanh,
        So_luong_Scx2_hoan_thanh,
        So_luong_Sc_Combo_hoan_thanh,
        So_luong_Scx1_hoan_tra,
        So_luong_SCx2_hoan_tra,
        So_luong_SC_Combo_hoan_tra,
        tong_san_pham_sp_hoan_thanh,
        Tong_tien_quyet_toan,
        Tong_tien_hoan_thanh,
        Tong_von,
        # COMBO NEW
        so_luong_COMBO_SCx1_hoan_thanh,
        so_luong_COMBO_SCx2_hoan_thanh,
        So_luong_COMBO_SCx1_hoan_tra,
        So_luong_COMBO_SCx2_hoan_tra,
        # BTHP
        so_luong_BTHP_0CAY_hoan_thanh,
        so_luong_BTHP_CAY_hoan_thanh,
        so_luong_BTHP_COMBO_hoan_thanh,
        so_luong_BTHP_COMBO_0CAY_hoan_thanh,
        so_luong_BTHP_COMBO_CAY_hoan_thanh,
    )


import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import base64

# --- Giao diện Streamlit ---
st.set_page_config(page_title="REPORT DAILY OF SHOPEE", layout="wide")

# Chèn logo từ GitHub vào góc trên bên trái
st.markdown(
    """
    <div style='top: 60px; left: 40px; z-index: 1000;'>
        <img src='https://raw.githubusercontent.com/CaptainCattt/Report_of_shopee/main/logo-lamvlog.png' width='150'/>
    </div>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div style='text-align: center; display: flex; justify-content: center; align-items: center; gap: 10px;'>
        <img src='https://img.icons8.com/color/48/shopee.png' width='40'/>
        <h1 style='color: #FF7F50; margin: 0;'>REPORT DAILY OF SHOPEE</h1>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown("<br><br>", unsafe_allow_html=True)  # Tạo khoảng cách sau tiêu đề

# Tạo các cột cho upload file
col1, col2 = st.columns(2)

with col1:
    st.markdown(
        "<h3 style='text-align: center;'>📥 Upload File All Orders Of Shopee</h3>",
        unsafe_allow_html=True,
    )
    file_all = st.file_uploader(
        "Chọn file tất cả đơn hàng Shopee", type=["xlsx", "xls"], key="Shopee_all"
    )

with col2:
    st.markdown(
        "<h3 style='text-align: center;'>📥 Upload File Income Of Shopee</h3>",
        unsafe_allow_html=True,
    )
    file_income = st.file_uploader(
        "Chọn file doanh thu Shopee", type=["xlsx", "xls"], key="Shopee_income"
    )

# Khởi tạo trạng thái nếu chưa có
if "processing" not in st.session_state:
    st.session_state.processing = False

# Nút xử lý
import streamlit as st

# Tùy chỉnh kích thước và căn giữa nút
st.markdown(
    """
    <style>
        .center-button {
            display: flex;
            justify-content: center;
            align-items: center;
        }
        .button-style {
            font-size: 20px;
            padding: 15px 10px;
            background-color: #4CAF50;
            color: white;
            border: none;
            border-radius: 5px;
            cursor: pointer;
        }
        .button-style:hover {
            background-color: #45a049;
        }
    </style>

""",
    unsafe_allow_html=True,
)

# Nút Xử lý dữ liệu
with st.container():
    st.markdown('<div class="center-button">', unsafe_allow_html=True)
    process_btn = st.button(
        "🔍 Xử lý dữ liệu",
        key="process_data",
        disabled=st.session_state.processing,
        use_container_width=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

if st.button("🔁 Reset", use_container_width=True):
    st.session_state.clear()
    st.rerun()


if process_btn:
    if not file_all or not file_income:
        st.warning("Vui lòng upload cả 2 file!")
    else:
        with st.spinner("⏳ Đang xử lý dữ liệu, vui lòng chờ..."):
            # Đọc dữ liệu từ file upload
            df_all = pd.read_excel(
                file_all,
                dtype={"Mã đơn hàng": str, "Mã Kiện Hàng": str, "Mã vận đơn": str},
            )
            df_income = pd.read_excel(
                file_income,
                sheet_name="Income",  # tên sheet
                dtype={
                    "Mã đơn hàng": str,
                    "Mã Số Thuế": str,
                    "Mã yêu cầu hoàn tiền": str,
                },
            )
            (
                Don_quyet_toan,
                Don_hoan_thanh,
                Don_hoan_tra,
                So_don_quyet_toan,
                So_don_hoan_thanh,
                So_don_hoan_tra,
                So_luong_Scx1_hoan_thanh,
                So_luong_Scx2_hoan_thanh,
                So_luong_Sc_Combo_hoan_thanh,
                So_luong_Scx1_hoan_tra,
                So_luong_SCx2_hoan_tra,
                So_luong_SC_Combo_hoan_tra,
                tong_san_pham_sp_hoan_thanh,
                Tong_tien_quyet_toan,
                Tong_tien_hoan_thanh,
                Tong_von,
                # COMBO NEW
                so_luong_COMBO_SCx1_hoan_thanh,
                so_luong_COMBO_SCx2_hoan_thanh,
                So_luong_COMBO_SCx1_hoan_tra,
                So_luong_COMBO_SCx2_hoan_tra,
                # BTHP
                so_luong_BTHP_0CAY_hoan_thanh,
                so_luong_BTHP_CAY_hoan_thanh,
                so_luong_BTHP_COMBO_hoan_thanh,
                so_luong_BTHP_COMBO_0CAY_hoan_thanh,
                so_luong_BTHP_COMBO_CAY_hoan_thanh,
            ) = process_shopee_daily_report(df_all, df_income)

            st.session_state["Don_quyet_toan"] = Don_quyet_toan
            st.session_state["Don_hoan_thanh"] = Don_hoan_thanh
            st.session_state["Don_hoan_tra"] = Don_hoan_tra

            bang_thong_ke_don_hang_shopee = pd.DataFrame(
                {
                    "ĐƠN QUYẾT TOÁN": [So_don_quyet_toan],
                    "ĐƠN HOÀN THÀNH": [So_don_hoan_thanh],
                    "ĐƠN HOÀN TRẢ": [So_don_hoan_tra],
                    "SỐ TIỀN QUYẾT TOÁN": [Tong_tien_quyet_toan],
                    "SỐ TIỀN HOÀN THÀNH": [Tong_tien_hoan_thanh],
                },
                index=["Shopee"],
            )

            bang_thong_ke_tien_shopee = pd.DataFrame(
                {
                    "SỐ TIỀN QUYẾT TOÁN": [Tong_tien_quyet_toan],
                    "SỐ TIỀN HOÀN THÀNH": [Tong_tien_hoan_thanh],
                    "TỔNG VỐN": [Tong_von],
                    "LỢI NHUẬN": [Tong_tien_quyet_toan - Tong_von],
                },
                index=["Shopee"],
            )

            bang_thong_ke_so_luong_shopee = pd.DataFrame(
                {
                    "Tổng sản phẩm": [
                        So_luong_Scx1_hoan_thanh
                        + So_luong_Scx2_hoan_thanh
                        + So_luong_Sc_Combo_hoan_thanh * 2,
                        (So_luong_Scx1_hoan_tra + So_luong_Scx1_hoan_thanh)
                        + (So_luong_Scx2_hoan_thanh + So_luong_SCx2_hoan_tra)
                        + (
                            So_luong_SC_Combo_hoan_tra * 2
                            + So_luong_Sc_Combo_hoan_thanh * 2
                        ),
                        So_luong_Scx1_hoan_tra
                        + So_luong_SCx2_hoan_tra
                        + So_luong_SC_Combo_hoan_tra * 2,
                    ],
                    "SCx1": [
                        So_luong_Scx1_hoan_thanh,
                        So_luong_Scx1_hoan_thanh + So_luong_Scx1_hoan_tra,
                        So_luong_Scx1_hoan_tra,
                    ],
                    "SCx2": [
                        So_luong_Scx2_hoan_thanh,
                        So_luong_Scx2_hoan_thanh + So_luong_SCx2_hoan_tra,
                        So_luong_SCx2_hoan_tra,
                    ],
                    "SCxCOMBO": [
                        So_luong_Sc_Combo_hoan_thanh,
                        So_luong_Sc_Combo_hoan_thanh + So_luong_SC_Combo_hoan_tra,
                        So_luong_SC_Combo_hoan_tra,
                    ],
                    "COMBO_SCx1": [
                        so_luong_COMBO_SCx1_hoan_thanh,
                        so_luong_COMBO_SCx1_hoan_thanh + So_luong_COMBO_SCx1_hoan_tra,
                        So_luong_COMBO_SCx1_hoan_tra,
                    ],
                    "COMBO_SCx2": [
                        so_luong_COMBO_SCx2_hoan_thanh,
                        so_luong_COMBO_SCx2_hoan_thanh + So_luong_COMBO_SCx2_hoan_tra,
                        So_luong_COMBO_SCx2_hoan_tra,
                    ],
                },
                index=["HOÀN THÀNH", "QUYẾT TOÁN", "HOÀN TRẢ"],
            )

            bang_thong_ke_so_luong_BTHP_shopee = pd.DataFrame(
                {
                    "BTHP_0CAY": [
                        so_luong_BTHP_0CAY_hoan_thanh,
                        so_luong_BTHP_0CAY_hoan_thanh,
                    ],
                    "BTHP_CAY": [
                        so_luong_BTHP_CAY_hoan_thanh,
                        so_luong_BTHP_CAY_hoan_thanh,
                    ],
                    "BTHP_COMBO": [
                        so_luong_BTHP_COMBO_hoan_thanh,
                        so_luong_BTHP_COMBO_hoan_thanh,
                    ],
                    "BTHP_COMBO_0CAY": [
                        so_luong_BTHP_COMBO_0CAY_hoan_thanh,
                        so_luong_BTHP_COMBO_0CAY_hoan_thanh,
                    ],
                    "BTHP_COMBO_CAY": [
                        so_luong_BTHP_COMBO_CAY_hoan_thanh,
                        so_luong_BTHP_COMBO_CAY_hoan_thanh,
                    ],
                },
                index=["HOÀN THÀNH", "QUYẾT TOÁN"],
            )

            # Vẽ các biểu đồ
            labels = [
                "ĐƠN QUYẾT TOÁN",
                "ĐƠN HOÀN THÀNH",
                "ĐƠN HOÀN TRẢ",
            ]

            shopee_values = bang_thong_ke_don_hang_shopee.loc["Shopee", labels].values

            df_bar = pd.DataFrame({"Loại đơn hàng": labels, "Số lượng": shopee_values})

            # Biểu đồ cột
            fig_bar_shopee = px.bar(
                df_bar,
                x="Loại đơn hàng",
                y="Số lượng",
                title="Số lượng các loại đơn hàng Shopee",
                text_auto=True,
                labels={"Loại đơn hàng": "Loại đơn", "Số lượng": "Số đơn"},
            )

            # Biểu đồ tròn Hoàn Thành
            fig_pie_hoan_thanh = px.pie(
                names=["SCx1", "SCx2", "SC COMBO"],
                values=[
                    So_luong_Scx1_hoan_thanh,
                    So_luong_Scx2_hoan_thanh,
                    So_luong_Sc_Combo_hoan_thanh,
                ],
                title="Tỉ lệ sản phẩm HOÀN THÀNH Shopee",
                hole=0.4,
            )

            # Biểu đồ tròn Quyết Toán
            fig_pie_quyet_toan = px.pie(
                names=["SCx1", "SCx2", "SC COMBO"],
                values=[
                    So_luong_Scx1_hoan_thanh + So_luong_Scx1_hoan_tra,
                    So_luong_Scx2_hoan_thanh + So_luong_SCx2_hoan_tra,
                    So_luong_Sc_Combo_hoan_thanh + So_luong_SC_Combo_hoan_tra,
                ],
                title="Tỉ lệ sản phẩm QUYẾT TOÁN Shopee",
                hole=0.4,
            )

            # Lưu vào session_state
            st.session_state["bang_thong_ke_don_hang_shopee"] = (
                bang_thong_ke_don_hang_shopee
            )
            st.session_state["bang_thong_ke_so_luong_shopee"] = (
                bang_thong_ke_so_luong_shopee
            )
            st.session_state["bang_thong_ke_tien_shopee"] = bang_thong_ke_tien_shopee

            st.session_state["bang_thong_ke_so_luong_BTHP_shopee"] = (
                bang_thong_ke_so_luong_BTHP_shopee
            )

            st.session_state["fig_bar_shopee"] = fig_bar_shopee
            st.session_state["fig_pie_hoan_thanh"] = fig_pie_hoan_thanh
            st.session_state["fig_pie_quyet_toan"] = fig_pie_quyet_toan
            st.session_state.processing = True

if st.session_state.processing:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown(
        "<h3 style='text-align: center; color: #FF9800;'>📊 KẾT QUẢ THỐNG KÊ</h3>",
        unsafe_allow_html=True,
    )
    st.markdown("<br><br>", unsafe_allow_html=True)

    with st.container():
        st.markdown("#### 📋 Bảng Thống Kê Tiền Hàng")
        st.dataframe(st.session_state["bang_thong_ke_tien_shopee"])

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📋 Bảng Thống Kê Đơn Hàng")
        st.dataframe(st.session_state["bang_thong_ke_don_hang_shopee"])

    with col2:
        st.markdown("#### 📈 Biểu Đồ Số Lượng Đơn Hàng")
        st.plotly_chart(st.session_state["fig_bar_shopee"], use_container_width=True)

    with st.container():
        st.markdown("#### 📋 Bảng Thống Kê Tiền Hàng")
        st.dataframe(st.session_state["bang_thong_ke_so_luong_BTHP_shopee"])

    # Hiển thị thống kê sản phẩm
    st.markdown("### 📊 SỐ LƯỢNG SẢN PHẨM")
    col4, col5, col6 = st.columns(3)

    with col4:
        st.markdown("#### 📋 Bảng Thống Kê Sản Phẩm")
        st.dataframe(st.session_state["bang_thong_ke_so_luong_shopee"])

    with col5:
        st.markdown("#### 📈 Biểu Đồ Hoàn Thành")
        st.plotly_chart(
            st.session_state["fig_pie_hoan_thanh"], use_container_width=True
        )

    with col6:
        st.markdown("#### 📈 Biểu Đồ Quyết Toán")
        st.plotly_chart(
            st.session_state["fig_pie_quyet_toan"], use_container_width=True
        )

    st.markdown("### 🔍 Xem chi tiết theo loại đơn hàng")


# Danh sách các loại đơn
ds_loai_don = [
    "ĐƠN QUYẾT TOÁN",
    "ĐƠN HOÀN THÀNH",
    "ĐƠN HOÀN TRẢ",
]

# Hiển thị selectbox và cập nhật session_state
loai_don = st.selectbox("📦 Chọn loại đơn hàng để xem chi tiết:", ds_loai_don)


# Cập nhật lựa chọn vào session_state
st.session_state["loai_don_selected"] = loai_don

# Mapping loại đơn sang DataFrame trong session_state
mapping = {
    "ĐƠN QUYẾT TOÁN": st.session_state.get("Don_quyet_toan", pd.DataFrame()),
    "ĐƠN HOÀN THÀNH": st.session_state.get("Don_hoan_thanh", pd.DataFrame()),
    "ĐƠN HOÀN TRẢ": st.session_state.get("Don_hoan_tra", pd.DataFrame()),
}

# Lấy dữ liệu theo loại đơn đã chọn
df_chi_tiet = mapping.get(loai_don, pd.DataFrame())

# Hiển thị kết quả
if not df_chi_tiet.empty:
    st.markdown(f"#### 📋 Danh sách chi tiết {loai_don}")
    st.dataframe(df_chi_tiet)
else:
    st.info("Không có dữ liệu cho loại đơn này.")
