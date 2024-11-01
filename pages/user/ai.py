import streamlit as st
import psutil
import plotly.express as px
import pandas as pd
from pynvml import (
    nvmlInit,
    nvmlShutdown,
    nvmlDeviceGetHandleByIndex,
    nvmlDeviceGetMemoryInfo,
    nvmlDeviceGetName,
    nvmlDeviceGetUtilizationRates
)

# Initialize NVML for GPU monitoring
def get_system_metrics():
    try:
        nvmlInit()
        cpu_percent = psutil.cpu_percent(interval=1, percpu=True)
        total_cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()

        handle = nvmlDeviceGetHandleByIndex(0)
        gpu_name = nvmlDeviceGetName(handle)  # Remove .decode() here
        gpu_memory = nvmlDeviceGetMemoryInfo(handle)
        gpu_util = nvmlDeviceGetUtilizationRates(handle)
        nvmlShutdown()

        return {
            'cpu_percent': cpu_percent,
            'total_cpu_percent': total_cpu_percent,
            'memory': memory,
            'swap': swap,
            'gpu_name': gpu_name,
            'gpu_memory': gpu_memory,
            'gpu_util': {
                'gpu': gpu_util.gpu,
                'memory': gpu_util.memory
            }
        }
    except Exception as e:
        st.error(f"Error collecting GPU metrics: {e}")
        return {
            'cpu_percent': psutil.cpu_percent(interval=1, percpu=True),
            'total_cpu_percent': psutil.cpu_percent(),
            'memory': psutil.virtual_memory(),
            'swap': psutil.swap_memory(),
            'gpu_name': "N/A",
            'gpu_memory': None,
            'gpu_util': {'gpu': 'N/A', 'memory': 'N/A'}
        }

# Create CPU usage chart
def create_cpu_chart(cpu_percent):
    df = pd.DataFrame({
        'Core': [f'Core {i}' for i in range(len(cpu_percent))],
        'Usage (%)': cpu_percent
    })
    fig = px.bar(
        df,
        x='Core',
        y='Usage (%)',
        title='CPU Core Usage',
        color='Usage (%)',
        color_continuous_scale='Turbo'
    )
    fig.update_layout(height=350, margin=dict(t=40, b=30))
    return fig

# Create memory pie chart
def create_memory_pie_chart(memory):
    if not memory:
        return None
    memory_data = pd.DataFrame({
        'Type': ['Used', 'Available'],
        'Memory (GB)': [
            memory.used / (1024 ** 3),
            memory.available / (1024 ** 3)
        ]
    })
    fig = px.pie(
        memory_data,
        values='Memory (GB)',
        names='Type',
        title='Memory Usage Distribution',
        hole=0.35,
        color_discrete_sequence=['#FFA07A', '#00BFFF']
    )
    fig.update_layout(height=350, showlegend=False, margin=dict(t=40, b=30))
    return fig

# Custom CSS for enhanced styling
st.markdown("""
<style>
body {
    background-color: #f9f9f9;
}
h1, h2, h3 {
    color: #333;
}
.metric-card {
    background-color: #ffffff;
    border-radius: 12px;
    padding: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    margin-bottom: 20px;
    transition: transform 0.3s ease;
}
.metric-card:hover {
    transform: translateY(-5px);
}
.icon {
    font-size: 24px;
    margin-right: 10px;
}
.usage-label {
    color: #888;
    font-size: 14px;
    font-weight: 600;
}
</style>
""", unsafe_allow_html=True)

st.title("🖥️ Advanced System Monitoring Dashboard")

# Collect metrics
metrics = get_system_metrics()

# Real-time metrics section with icons and hover effect
st.markdown("## System Metrics")
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<span class="icon">💻</span><span class="usage-label">CPU Usage</span>', unsafe_allow_html=True)
    st.metric("Overall CPU", f"{metrics.get('total_cpu_percent', 'N/A')}%", delta=f"{metrics.get('total_cpu_percent', 'N/A')}% Load")
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<span class="icon">🧠</span><span class="usage-label">Memory Usage</span>', unsafe_allow_html=True)
    memory = metrics.get('memory', {})
    st.metric(
        "Memory Used",
        f"{memory.used / (1024 ** 3):.2f} GB" if memory else "N/A",
        delta=f"{memory.percent}% of {memory.total / (1024 ** 3):.2f} GB" if memory else "N/A"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="metric-card">', unsafe_allow_html=True)
    st.markdown('<span class="icon">🚀</span><span class="usage-label">GPU Status</span>', unsafe_allow_html=True)
    st.metric(
        "GPU",
        metrics.get('gpu_name', 'N/A'),
        delta=f"GPU Util: {metrics.get('gpu_util', {}).get('gpu', 'N/A')}%"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Visualizations section with modern design
st.markdown("## Resource Utilization")
col4, col5 = st.columns(2)

with col4:
    cpu_chart = create_cpu_chart(metrics.get('cpu_percent', []))
    st.plotly_chart(cpu_chart, use_container_width=True)

with col5:
    memory_chart = create_memory_pie_chart(metrics.get('memory', {}))
    if memory_chart:
        st.plotly_chart(memory_chart, use_container_width=True)

# Detailed GPU Information with icons and spacing
st.markdown("## 🔍 Detailed GPU Metrics")
gpu_col1, gpu_col2 = st.columns(2)

gpu_memory = metrics.get('gpu_memory', {})

with gpu_col1:
    st.markdown(f"""
    **GPU Memory Details**
    - **Total VRAM**: {gpu_memory.total / (1024 ** 3):.2f} GB
    - **Used VRAM**: {gpu_memory.used / (1024 ** 3):.2f} GB
    - **Free VRAM**: {(gpu_memory.total - gpu_memory.used) / (1024 ** 3):.2f} GB
    """ if gpu_memory else "N/A")

with gpu_col2:
    st.markdown(f"""
    **GPU Utilization**
    - **GPU Load**: {metrics.get('gpu_util', {}).get('gpu', 'N/A')}%
    - **Memory Utilization**: {metrics.get('gpu_util', {}).get('memory', 'N/A')}%
    """)
