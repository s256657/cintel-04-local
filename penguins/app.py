from shiny import App, ui, render, reactive, req
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from palmerpenguins import load_penguins
import plotly.express as px
from shinywidgets import output_widget, render_widget, render_plotly

# Load and clean data
penguins_df = load_penguins().dropna()

# Define UI
app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.h2("Sidebar"),
        ui.input_selectize(
            "selected_attribute",
            "Choose attribute",
            ["bill_length_mm", "bill_depth_mm", "flipper_length_mm", "body_mass_g"]
        ),
        ui.input_slider(
            "seaborn_bin_count",
            "Number of Seaborn bins",
            5, 100, 20
        ),
        ui.input_checkbox_group(
            "selected_species_list",
            "Filter species",
            ["Adelie", "Gentoo", "Chinstrap"],
            selected=["Adelie", "Gentoo", "Chinstrap"],
            inline=True
        ),
        ui.hr(),
        ui.a("GitHub", href="https://github.com/s256657/cintel-02-data/blob/main/app.py", target="_blank"),
        open="open"
    ),

    ui.h2("Palmer Penguin Analysis"),

    ui.layout_columns(
        ui.output_data_frame("data_table"),
        ui.output_data_frame("penguins_grid")
    ),

    ui.layout_columns(
        ui.card(
            ui.card_header("Plotly Histogram"),
            output_widget("plotly_histogram")
        ),
        ui.card(
            ui.card_header("Seaborn Histogram"),
            ui.output_plot("seaborn_histogram")
        )
    ),

    ui.card(
        ui.card_header("Plotly Scatterplot"),
        output_widget("plotly_scatterplot"),
        full_screen=True
    )
)

# Define Server Logic
def server(input, output, session):

    # Reactive filtered DataFrame based on selected species
    @reactive.calc
    def filtered_data():
        req(input.selected_species_list())  # Ensure something is selected
        return penguins_df[penguins_df["species"].isin(input.selected_species_list())]

    @output
    @render.data_frame
    def data_table():
        return filtered_data()

    @output
    @render.data_frame
    def penguins_grid():
        return filtered_data()

    @output
    @render_plotly
    def plotly_histogram():
        df = filtered_data()
        fig = px.histogram(
            df,
            x=input.selected_attribute(),
            nbins=30,
            color="species",
            title=f"{input.selected_attribute()} Histogram by Species"
        )
        fig.update_layout(
            xaxis_title=input.selected_attribute(),
            yaxis_title="Count"
        )
        return fig

    @output
    @render.plot
    def seaborn_histogram():
        df = filtered_data()
        plt.figure(figsize=(6, 4))
        sns.histplot(
            data=df,
            x=input.selected_attribute(),
            bins=input.seaborn_bin_count(),
            hue="species",
            kde=True
        )
        plt.title("Seaborn Histogram")
        plt.xlabel(input.selected_attribute())
        plt.ylabel("Count")

    @output
    @render_plotly
    def plotly_scatterplot():
        df = filtered_data()
        selected_attr = input.selected_attribute()
        fig = px.scatter(
            df,
            x=selected_attr,
            y="body_mass_g",
            color="species",
            symbol="species",
            size="bill_length_mm",
            size_max=6,
            hover_data=["flipper_length_mm", "bill_depth_mm"],
            title=f"{selected_attr} vs Body Mass"
        )
        fig.update_layout(
            xaxis_title=selected_attr,
            yaxis_title="Body Mass (g)",
            legend_title="Species"
        )
        return fig

# Run the app
app = App(app_ui, server)
