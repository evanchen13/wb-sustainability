import pandas as pd
import plotly.graph_objs as go
import requests

def clean_data(indicator, countries=['all'], params={'format': 'json', 'per_page': '30000'}):
    """Gathers data from the World Bank API, using the specified parameters, into a dataframe and cleans the data.
    
    Args:
        indicator (string): indicator code
        countries (list): list of countries to gather data for
        params (dict): parameters used in the World Bank API
    
    Returns:
        df (DataFrame): dataset containing columns for country name, year, and value
    
    """
    
    # using the provided arguments, format the URL so that it can be used with the World Bank API
    countries = ';'.join(countries)
    url = 'http://api.worldbank.org/v2/country/'+countries+'/indicator/'+indicator
    r = requests.get(url, params=params)
    
    # for every record in the returned data, create dictionaries which can be used to create the dataframe
    df_list = []
    for record in r.json()[1]:
        if record['value']:
            country = record['country']['value']
            year = int(record['date'])
            value = float(record['value'])
            df_list.append({'country': country, 'year': year, 'value': value})
        else:
            continue
    df = pd.DataFrame(df_list)
    
    df.sort_values('year', inplace=True)
    # remove country names that are not actually countries
    remove_countries = ['Arab World', 
                    'Central Europe and the Baltics', 
                    'Caribbean small states', 
                    'East Asia & Pacific (excluding high income)', 
                    'Early-demographic dividend', 
                    'East Asia & Pacific', 
                    'Europe & Central Asia (excluding high income)', 
                    'Europe & Central Asia', 
                    'Euro area', 
                    'European Union', 
                    'Fragile and conflict affected situations', 
                    'High income', 
                    'Heavily indebted poor countries (HIPC)', 
                    'IBRD only', 
                    'IDA & IBRD total', 
                    'IDA total', 
                    'IDA blend', 
                    'IDA only', 
                    'Not classified', 
                    'Latin America & Caribbean (excluding high income)', 
                    'Latin America & Caribbean', 
                    'Least developed countries: UN classification', 
                    'Low income', 
                    'Lower middle income', 
                    'Low & middle income', 
                    'Late-demographic dividend', 
                    'Middle East & North Africa', 
                    'Middle income', 
                    'Middle East & North Africa (excluding high income)', 
                    'North America', 
                    'OECD members', 
                    'Other small states', 
                    'Pre-demographic dividend', 
                    'Pacific island small states', 
                    'Post-demographic dividend', 
                    'Sub-Saharan Africa (excluding high income)', 
                    'Sub-Saharan Africa', 
                    'Small states', 
                    'East Asia & Pacific (IDA & IBRD countries)', 
                    'Europe & Central Asia (IDA & IBRD countries)', 
                    'Latin America & the Caribbean (IDA & IBRD countries)', 
                    'Middle East & North Africa (IDA & IBRD countries)', 
                    'South Asia (IDA & IBRD)', 
                    'Sub-Saharan Africa (IDA & IBRD countries)',
                    'Upper middle income',
                    'World']
    df = df.query('country not in @remove_countries')
    
    return df

def return_figures():
    """Creates five plotly visualizations

    Args:
        None

    Returns:
        list (dict): list containing the five plotly visualizations, as follows
                     1. line chart of renewable energy consumption over time for the top five economies
                     2. line chart of CO2 emissions over time for the top five economies
                     3. bar chart of top five countries in renewable energy consumption for the most recent year
                     4. bar chart of top five countries in CO2 emissions for the most recent year
                     5. scatter plot of renewable energy consumption and CO2 emissions for the most recent year
    """
    
    renewable_consumption = clean_data(indicator='EG.FEC.RNEW.ZS')
    co2_emissions = clean_data(indicator='EN.ATM.CO2E.PC')
    
    # create first and second graphs - line charts of renewable energy consumption and CO2 emissions over time for the top five economies
    top_economies = ['United States', 'China', 'Japan', 'Germany', 'United Kingdom']
    
    renewable_consumption_top = renewable_consumption.query('country in @top_economies')
    co2_emissions_top = co2_emissions.query('country in @top_economies')
    df_list = [renewable_consumption_top, co2_emissions_top]
    
    # figure out what years are common to both indicators and the top five economies
    start_years = []
    end_years = []
    for df in df_list:
        df_start = df.groupby('country')['year'].min().max()
        start_years.append(df_start)
        df_end = df.groupby('country')['year'].max().min()
        end_years.append(df_end)
        
    start_year = max(start_years)
    end_year = min(end_years)
    
    graphs_trended = []
    for df in df_list:
        graph = []
        df = df.query('year >= @start_year & year <= @end_year')
        for country in top_economies:
            df_country = df.query('country == @country')
            graph.append(
                go.Scatter(
                    x = df_country['year'].tolist(),
                    y = df_country['value'].tolist(),
                    mode = 'lines',
                    type = 'scatter',
                    name = country
                )
            )
        graphs_trended.append(graph)
    
    graph_one = graphs_trended[0]
    graph_one_title = 'Top Five Economies '+str(start_year)+'-'+str(end_year)+'<br>Renewal Energy Consumption'
    layout_one = dict(title = graph_one_title,
                xaxis = dict(title = 'Year'),
                yaxis = dict(title = 'Renewable % of Total Energy Consumption')
                )
    
    graph_two = graphs_trended[1]
    graph_two_title = 'Top Five Economies '+str(start_year)+'-'+str(end_year)+'<br>CO2 Emissions'
    layout_two = dict(title = graph_two_title,
                xaxis = dict(title = 'Year'),
                yaxis = dict(title = 'Metric Tons of CO2 Per Capita')
                )
    
    # create third and fourth graphs - bar charts of top five countries in renewable energy consumption and CO2 emissions for the most recent year
    renewable_consumption_recent = renewable_consumption.query('year == @end_year')
    co2_emissions_recent = co2_emissions.query('year == @end_year')
    renewable_consumption_sorted = renewable_consumption_recent.sort_values('value', ascending=False)
    co2_emissions_sorted = co2_emissions_recent.sort_values('value')
    df_list = [renewable_consumption_sorted, co2_emissions_sorted]
    
    graphs_bar = []
    for df in df_list:
        df = df.head()
        graphs_bar.append([
            go.Bar(
                x = df['country'].tolist(),
                y = df['value'].tolist()
            )
        ])
        
    graph_three = graphs_bar[0]
    graph_three_title = 'Top Five Countries in '+str(end_year)+'<br>Renewable Energy Consumption'
    layout_three = dict(title = graph_three_title,
                xaxis = dict(title = 'Country'),
                yaxis = dict(title = 'Renewable % of Total Energy Consumption')
                )
    
    graph_four = graphs_bar[1]
    graph_four_title = 'Top Five Countries in '+str(end_year)+'<br>CO2 Emissions'
    layout_four = dict(title = graph_four_title,
                xaxis = dict(title = 'Country'),
                yaxis = dict(title = 'Metric Tons of CO2 Per Capita')
                )
    
    # create fifth graph - scatter plot of renewable energy consumption and CO2 emissions for the most recent year
    env_metrics_recent = renewable_consumption_recent.merge(co2_emissions_recent, how='inner', on=['country', 'year'])
    
    graph_five = []
    graph_five.append(
      go.Scatter(
          x = env_metrics_recent['value_x'].tolist(),
          y = env_metrics_recent['value_y'].tolist(),
          text = env_metrics_recent['country'].tolist(),
          mode = 'markers'
      )
    )

    graph_five_title = 'Renewable Energy Consumption vs. CO2 Emissions<br>by Country in '+str(end_year)
    layout_five = dict(title = graph_five_title,
                xaxis = dict(title = 'Renewable % of Total Energy Consumption'),
                yaxis = dict(title = 'Metric Tons of CO2 Per Capita'),
                )
    
    # append all charts to the figures list
    figures = []
    graphs = [graph_one, graph_two, graph_three, graph_four, graph_five]
    layouts = [layout_one, layout_two, layout_three, layout_four, layout_five]
    for i in range(5):
        figures.append(dict(data=graphs[i], layout=layouts[i]))

    return figures