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

    Scx1_hoan_thanh = Don_hoan_thanh[Don_hoan_thanh["SKU phân loại hàng"] == "SC-450g"]
    So_luong_Scx1_hoan_thanh = Scx1_hoan_thanh["Số lượng"].sum()

    Scx2_hoan_thanh = Don_hoan_thanh[
        Don_hoan_thanh["SKU phân loại hàng"] == "SC-x2-450g"
    ]
    So_luong_Scx2_hoan_thanh = Scx2_hoan_thanh["Số lượng"].sum()

    Sc_Combo_hoan_thanh = Don_hoan_thanh[
        Don_hoan_thanh["SKU phân loại hàng"] == "COMBO-SC"
    ]
    So_luong_Sc_Combo_hoan_thanh = Sc_Combo_hoan_thanh["Số lượng"].sum()

    tong_san_pham_sp_hoan_thanh = (
        So_luong_Scx1_hoan_thanh
        + So_luong_Scx2_hoan_thanh
        + So_luong_Sc_Combo_hoan_thanh * 2
    )

    Scx1_hoan_tra = Don_hoan_tra[Don_hoan_tra["SKU phân loại hàng"] == "SC-450g"]
    So_luong_Scx1_hoan_tra = Scx1_hoan_tra["Số lượng"].sum()

    SCx2_hoan_tra = Don_hoan_tra[Don_hoan_tra["SKU phân loại hàng"] == "SC-x2-450g"]
    So_luong_SCx2_hoan_tra = SCx2_hoan_tra["Số lượng"].sum()

    SC_Combo_hoan_tra = Don_hoan_tra[Don_hoan_tra["SKU phân loại hàng"] == "COMBO-SC"]
    So_luong_SC_Combo_hoan_tra = SC_Combo_hoan_tra["Số lượng"].sum()

    Tong_tien_quyet_toan = df_merged["Tổng tiền đã thanh toán"].sum()

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
    )


import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image
import base64

# --- Giao diện Streamlit ---
st.set_page_config(page_title="REPORT DAILY OF SHOPEE", layout="wide")


# ======= CHÈN LOGO GÓC TRÁI =======
def get_base64_of_bin_file(bin_file):
    with open(bin_file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


logo_path = "./Tool_Report_shopee/logo-lamvlog.png"
logo_base64 = get_base64_of_bin_file(logo_path)

# Hiển thị logo ở góc trên bên trái
st.markdown(
    f"""
    <div style='position: absolute; z-index: 1000;'>
        <img src="data:image/png;base64,{logo_base64}" width="150"/>
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
            ) = process_shopee_daily_report(df_all, df_income)

            st.session_state["Don_quyet_toan"] = Don_quyet_toan
            st.session_state["Don_hoan_thanh"] = Don_hoan_thanh
            st.session_state["Don_hoan_tra"] = Don_hoan_tra

            bang_thong_ke_don_hang_shopee = pd.DataFrame(
                {
                    "ĐƠN QUYẾT TOÁN": [So_don_quyet_toan],
                    "ĐƠN HOÀN THÀNH": [So_don_hoan_thanh],
                    "ĐƠN HOÀN TRẢ": [So_don_hoan_tra],
                    "TÔNG TIỀN QUYẾT TOÁN": [f"{Tong_tien_quyet_toan:,.0f} VNĐ"],
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
                },
                index=["HOÀN THÀNH", "QUYẾT TOÁN", "HOÀN TRẢ"],
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

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 📋 Bảng Thống Kê Đơn Hàng")
        st.dataframe(st.session_state["bang_thong_ke_don_hang_shopee"])

    with col2:
        st.markdown("#### 📈 Biểu Đồ Số Lượng Đơn Hàng")
        st.plotly_chart(st.session_state["fig_bar_shopee"], use_container_width=True)

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
