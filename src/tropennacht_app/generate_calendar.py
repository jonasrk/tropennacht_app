from meteostat import Point, Hourly
from datetime import datetime, timedelta
import pandas as pd
import plotly_calplot
import vcr

import os
from cachetools import TTLCache, cached


# Function to generate tropical nights plot for a given city

# Define a cache with a max size and time-to-live duration (in seconds)

cache = TTLCache(maxsize=float("inf"), ttl=60 * 60 * 24)


@cached(cache)
def generate_tropical_nights_plot(city_name=None, lat=None, lon=None):
    current_dir = os.path.dirname(__file__)
    cassette_path = os.path.join(current_dir, "vcr_weather_api.yaml")

    with vcr.use_cassette(cassette_path):
        # Define location and time range
        # Define Berlin location and time range

        berlin = Point(52.52, 13.405)
        start = datetime(
            datetime.now().year - 5, datetime.now().month, datetime.now().day
        )
        end = datetime(datetime.now().year, datetime.now().month, datetime.now().day)

        # Fetch weather data
        data = Hourly(berlin, start, end).fetch()

        # Function to check if it's a tropical night
        def is_tropical_night(df, date):
            """Check if the given date is a tropical night (temperature never drops below 20°C)."""
            day_data = df.loc[date]
            return day_data["temp"].min() >= 20

        # Collect results
        results = []
        date_range = pd.date_range(start=start, end=end, freq="D")

        for date in date_range:
            start_of_day = date
            end_of_day = date + timedelta(days=1)
            daily_data = data.loc[start_of_day:end_of_day]
            tropical_night = is_tropical_night(daily_data, start_of_day)
            results.append({"date": start_of_day, "tropical_night": tropical_night})

        results_df = pd.DataFrame(results)
        results_df["value"] = results_df["tropical_night"].astype(int)

        # Summarize tropical nights by year
        results_df["year"] = results_df["date"].dt.year
        annual_summary = results_df.groupby("year")["value"].sum().reset_index()
        annual_summary.columns = ["year", "tropical_nights"]

        # Prepare data for visualization
        data = pd.DataFrame({"date": results_df["date"], "value": results_df["value"]})
        fig = plotly_calplot.calplot(data, x="date", y="value")

        # Update plot layout
        fig.update_layout(
            coloraxis=dict(
                colorscale=[[0, "grey"], [1, "red"]],
                colorbar=dict(title="Tropical Night"),
            ),
            annotations=[
                dict(
                    x=0.5,
                    y=-0.1,
                    xref="paper",
                    yref="paper",
                    text=f"Total Tropical Nights by Year:<br>{annual_summary.to_html(index=False)}",
                    showarrow=False,
                    font=dict(size=12),
                    align="center",
                )
            ],
        )

        # Add labels for each year
        for year in annual_summary["year"]:
            tropical_nights = annual_summary.loc[
                annual_summary["year"] == year, "tropical_nights"
            ].values[0]
            fig.add_annotation(
                x=0.5,
                y=1.05,
                xref="paper",
                yref="paper",
                text=f"{year}: {tropical_nights} Tropical Nights",
                showarrow=False,
                font=dict(size=10),
                align="center",
            )

        # Generate plot HTML
        plot_html = fig.to_html(full_html=False)
        # plot_html = None
        return plot_html
