from joblib import dump, load
import pandas as pd, os
from IPython.display import display

from maps import format_map_data_nd, format_veto_data_nd, transform_series_stats_nd, between_dates
from series import explode_map_choices, transform_series_stats, get_tier1, get_map_in_pool, get_international, get_regional, remove_cn
from training import train_map_pick_model, train_series_winner_model, train_map_model
from testing import simulate_bets, simulate_bets_best, test_series_winner_model, predict_series_outcomes

# Load data
maps = pd.read_csv('data/raw/tier1_maps.csv', index_col=False)
series = pd.read_csv('data/tier1/series.csv', index_col=False)
# maps.to_csv('data/tier1/maps.csv', index=False)
# series.to_csv('data/tier1/series.csv', index=False)
tier1 = pd.read_csv('data/tier1/teams.csv').iloc[:,0].tolist()
vct_2023_start = '2023-02-13'
vct_2024_start = '2024-02-16'

# Process data (irrespective of training timeframe)
def init():
    mapdata = format_map_data_nd(maps)
    mapdata.to_csv('data/tier1/processed/mapdata.csv', index=False)
    vetos = explode_map_choices(series)
    vetos.to_csv('data/tier1/processed/vetos.csv', index=False)
    # return vetos, mapdata

# Train based on timeframe
def train(tsd, ted, ed):
    vetos = pd.read_csv('data/tier1/processed/vetos.csv', index_col=False)
    mapdata = pd.read_csv('data/tier1/processed/mapdata.csv', index_col=False)
    models = {}

    # map_pick_model = train_map_pick_model(between_dates(vetos, tsd, ted))
    # dump(map_pick_model, 'models/map_pick_model.joblib')
    # model = train_map_model(between_dates(mapdata, tsd, ted), -1)
    # dump(model, 'models/map_win.joblib')

    map_pick_model = load('models/map_pick_model.joblib')
    model = load('models/map_win.joblib')

    transformed_series_data = transform_series_stats_nd(format_veto_data_nd(vetos, maps), model, map_pick_model)
    tsd_bd = between_dates(transformed_series_data, tsd, ted)

    # series_winner_model = train_series_winner_model(tsd_bd)
    # dump(series_winner_model, 'models/series_winner.joblib')

    series_winner_model = load('models/series_winner.joblib')

    tsd_ad = get_regional(remove_cn(between_dates(transformed_series_data, ted, ed)))
    series_predictions = predict_series_outcomes(tsd_ad, series_winner_model)
    simulate_bets(series_predictions, 1000)
    simulate_bets_best(series_predictions, 1000)

# def test():
#     series_winner_model = load('models/series_winner.joblib')
#     tsd_ad = get_regional(remove_cn(between_dates(tsd, ted, ed)))
#     series_predictions = predict_series_outcomes(tsd_ad, series_winner_model)
#     df = simulate_bets(series_predictions, 1000)
#     test_series_winner_model(series_predictions)
#     df.to_csv('data/tier1/results/results.csv', index=False)

train(vct_2023_start, vct_2024_start, '2025-01-01')