
import streamlit as st
import numpy as np
import pandas as pd
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

uploaded_file = st.file_uploader("Tải lên file Excel", type=["xlsx"])

if uploaded_file:
    try:
        df = pd.read_excel(uploaded_file)
        if not {'time', 'temperature', 'phase'}.issubset(df.columns):
            st.error("File Excel cần có cột: time, temperature, phase")
        else:
            df = df.sort_values('time')
            t_ab = df[df['phase'] == 'AB']['time'].values
            temp_ab = df[df['phase'] == 'AB']['temperature'].values
            t_bc = df[df['phase'] == 'BC']['time'].values
            temp_bc = df[df['phase'] == 'BC']['temperature'].values
            t_cd = df[df['phase'] == 'CD']['time'].values
            temp_cd = df[df['phase'] == 'CD']['temperature'].values

            time = np.concatenate([t_ab, t_bc, t_cd])
            temperature = np.concatenate([temp_ab, temp_bc, temp_cd])

            t_B = t_bc[0]
            t_C = t_bc[-1]
            fit_ab = np.polyfit(t_ab, temp_ab, 1)
            fit_cd = np.polyfit(t_cd, temp_cd, 1)
            T_B = np.polyval(fit_ab, t_B)
            T_C = np.polyval(fit_cd, t_C)
            T_K = (T_B + T_C) / 2

            for i in range(len(t_bc)-1):
                if (temp_bc[i] - T_K) * (temp_bc[i+1] - T_K) <= 0:
                    t_L = np.interp(T_K, [temp_bc[i], temp_bc[i+1]], [t_bc[i], t_bc[i+1]])
                    break

            fig, ax = plt.subplots(figsize=(10,6))
            ax.plot(time, temperature, 'ko-', label='T(t) đo được')
            ax.plot(t_ab, np.polyval(fit_ab, t_ab), 'b--', label='Kéo dài AB')
            ax.plot(t_cd, np.polyval(fit_cd, t_cd), 'r--', label='Kéo dài CD')
            ax.hlines([T_B, T_K, T_C], xmin=time[0], xmax=time[-1], colors='gray', linestyles=':')
            ax.vlines([t_L], ymin=T_B, ymax=T_C, colors='black', linestyles='-', label='ΔT = EF')
            ax.set_title('Xác định ΔT bằng đồ thị')
            ax.set_xlabel('Thời gian (phút)')
            ax.set_ylabel('Nhiệt độ (°C)')
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)

            st.success(f"T_B (M): {T_B:.2f} °C")
            st.success(f"T_C (N): {T_C:.2f} °C")
            st.success(f"T_K (trung điểm): {T_K:.2f} °C")
            st.success(f"ΔT = EF = {T_C - T_B:.2f} °C")
            st.success(f"t_L (thời điểm giao): {t_L:.2f} phút")

    except Exception as e:
        st.error(f"Lỗi đọc file: {e}")
