import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.title("Xác định ΔT bằng phương pháp đồ thị (nhiệt lượng kế)")
st.markdown("""
### Nhập dữ liệu bằng Excel:
- Tải lên file Excel gồm 2 cột: `time` và `temperature`
- Ghi rõ các giai đoạn:
    - Giai đoạn AB: trước phản ứng
    - Giai đoạn BC: trong phản ứng
    - Giai đoạn CD: sau phản ứng
- Thêm cột `phase` có giá trị là AB, BC hoặc CD để phân loại
""")

# Upload file Excel
uploaded_file = st.file_uploader("Tải lên file Excel chứa dữ liệu (có cột: time, temperature, phase)", type=["xlsx"])

if uploaded_file:
    try:
        data = pd.read_excel(uploaded_file)

        # Kiểm tra cột
        required_cols = {'time', 'temperature', 'phase'}
        if not required_cols.issubset(data.columns):
            st.error("❌ File Excel phải chứa các cột: time, temperature, phase (giá trị phase: AB, BC, CD)")
        else:
            # Phân giai đoạn
            ab = data[data['phase'] == 'AB']
            bc = data[data['phase'] == 'BC']
            cd = data[data['phase'] == 'CD']

            t_B = bc['time'].values[0]
            t_C = bc['time'].values[-1]

            # Nội suy đoạn AB và CD (bậc 1)
            p_AB = np.polyfit(ab['time'], ab['temperature'], 1)
            p_CD = np.polyfit(cd['time'], cd['temperature'], 1)

            T_B = np.polyval(p_AB, t_B)
            T_C = np.polyval(p_CD, t_C)
            T_K = (T_B + T_C) / 2

            # Tìm t_L trong đoạn BC mà temp = T_K
            t_L = None
            for i in range(len(bc) - 1):
                if (bc['temperature'].iloc[i] - T_K) * (bc['temperature'].iloc[i+1] - T_K) <= 0:
                    t_L = np.interp(T_K,
                                    [bc['temperature'].iloc[i], bc['temperature'].iloc[i+1]],
                                    [bc['time'].iloc[i], bc['time'].iloc[i+1]])
                    break

            if t_L is not None:
                T_E = np.polyval(p_CD, t_L)
                T_F = np.polyval(p_AB, t_L)
                delta_T = T_E - T_F

                # Vẽ đồ thị
                fig, ax = plt.subplots()
                ax.plot(data['time'], data['temperature'], 'ko-', label="T(t) thực nghiệm")

                # Kéo dài AB và CD chỉ vượt t_L một chút
                t_ab_ext = np.linspace(ab['time'].min(), t_L + 1.0, 100)
                t_cd_ext = np.linspace(cd['time'].min(), t_L + 1.0, 100)

                ax.plot(t_ab_ext, np.polyval(p_AB, t_ab_ext), 'b--')
                ax.plot(t_cd_ext, np.polyval(p_CD, t_cd_ext), 'r--')

                ax.axvline(t_L, color='k', linestyle='-', label="ΔT = EF")
                ax.axhline(T_K, color='m', linestyle=':', linewidth=1)
                ax.axhline(T_B, color='g', linestyle=':', linewidth=1)
                ax.axhline(T_C, color='g', linestyle=':', linewidth=1)

                ax.plot(t_L, T_E, 'rs', markersize=8, label="Điểm E")
                ax.plot(t_L, T_F, 'bs', markersize=8, label="Điểm F")
                ax.text(t_L + 0.2, T_E, 'E', fontsize=12, color='r', fontweight='bold', va='top')
                ax.text(t_L + 0.2, T_F, 'F', fontsize=12, color='b', fontweight='bold', va='top')

                ax.set_xlabel("Thời gian (phút)")
                ax.set_ylabel("Nhiệt độ (°C)")
                ax.set_title("Xác định ΔT bằng phương pháp đồ thị")
                ax.legend(loc='best')
                ax.grid(True)

                st.pyplot(fig)

                # Hiển thị kết quả
                st.markdown("### ✅ KẾT QUẢ XÁC ĐỊNH ΔT")
                st.write(f"T_E (CD tại t_L): {T_E:.2f} °C")
                st.write(f"T_F (AB tại t_L): {T_F:.2f} °C")
                st.write(f"ΔT = EF (hiệu chỉnh): {delta_T:.2f} °C")
            else:
                st.warning("Không tìm thấy giao điểm T_K trong đoạn BC.")

    except Exception as e:
        st.error(f"⚠️ Lỗi đọc file: {e}")
