import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import styles

def plotting_function(dataframe, graph_type, y_axis, x_axis, hue_=None, title=""):
    if dataframe is None or dataframe.empty or len(dataframe.columns) < 2:
        print("Insufficient data for plotting.")
        return None

    fig = plt.figure(figsize=(10, 6))
    
    try:
        # Apply styles from styles.py
        fig = styles.apply_plot_styles(fig, title)

        if graph_type == "pie":
            plt.pie(dataframe[x_axis].value_counts(), labels=dataframe[x_axis].value_counts().index,
                   autopct='%1.1f%%', colors=sns.color_palette("pastel"))
        else:
            plot_func = getattr(sns, graph_type, None)
            if not plot_func:
                print(f"Invalid graph type: {graph_type}")
                return None
            
            if hue_ is None:
                if graph_type == "displot":
                    sns.histplot(data=dataframe, x=x_axis, color="#FF6F61", kde=True)
                elif graph_type == "heatmap":
                    plot_func(data=dataframe.corr(), annot=True, cmap="coolwarm")
                else:
                    plot_func(x=dataframe[x_axis], y=dataframe[y_axis], data=dataframe, color="#FF6F61")
            else:
                if graph_type == "displot":
                    sns.histplot(data=dataframe, x=x_axis, hue=hue_, palette="deep", kde=True)
                elif graph_type == "heatmap":
                    plot_func(data=dataframe.corr(), annot=True, cmap="coolwarm")
                else:
                    plot_func(x=dataframe[x_axis], y=dataframe[y_axis], hue=hue_, data=dataframe, palette="deep")

            if graph_type != "displot" and graph_type != "heatmap":
                plt.ylabel(y_axis, color="#000000")
            plt.xlabel(x_axis, color="#000000")

        return fig

    except Exception as e:
        print(f"Error: {e}")
        return None
