import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st

def apply_plot_styles(fig, title=""):
    """Apply consistent styles to matplotlib plots."""
    plt.style.use('fivethirtyeight')
    plt.gca().set_facecolor("#FFFFFF")
    plt.gcf().set_facecolor("#F5F5F5")
    plt.tick_params(colors="#000000")
    plt.grid(color="#CCCCCC", linestyle="--", linewidth=0.5)
    plt.title(title, color="#000000", fontsize=14, pad=10)
    return fig

def get_schema_css():
    """Return CSS for schema and query result tables."""
    return """
    <style>
    .schema-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
    }
    .schema-table th {
        background-color: #FF6F61;
        color: #FFFFFF;
        padding: 8px;
        text-align: left;
    }
    .schema-table td {
        padding: 8px;
        border: 1px solid #ddd;
    }
    .table-name {
        color: #FFFFFF;
        font-weight: bold;
        padding: 5px;
        display: inline-block;
        margin-bottom: 5px;
    }
    </style>
    """

def get_sidebar_css():
    """Return CSS for sidebar width."""
    return """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        width: 350px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        width: 350px;
        margin-left: -350px;
    }
    </style>
    """
