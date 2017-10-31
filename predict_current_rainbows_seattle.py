def lookup_timezone(station):
    path = os.path.join(os.environ['HOME'],'pickles/metar_timezone_dict.p')
    with open(path, 'rb') as f:
        metar_timezone_dict = pickle.load(f, encoding='latin1')
    return metar_timezone_dict[station][1]


def get_api_key(machine='ec2'):
    if machine == 'local':
        path = '/Users/marybarnes/.ssh/weather.txt'
    elif machine == 'ec2':
        path = os.path.join(os.environ['HOME'],'weather.txt')
    with open(path,'r') as f:
        api_key = f.readline().strip()
    return api_key


def construct_most_recent_weather_url(lat = '47.33', lon = '-122.19'):
    my_apikey = get_api_key()
    startDate = ''.join(str(datetime.date.today()).split('-'))
    url = "http://api.weather.com/v1/geocode/" + lat + "/" + lon+ \
    "/observations/historical.json?apiKey=" + str(my_apikey) + \
    "&language=en-US" + "&startDate="+startDate
    url = str.strip(url)
    return url


def get_most_recent_weather():
    url = construct_most_recent_weather_url()
    try:
        try:
            r = requests.get(url)
        except Exception as e1:
            print("sleeping for 5 seconds because request failed, exception: {}".format(str(e1)))
            with open('weather_errors_and_status_log.txt', "a") as myfile:
                myfile.write(str(e1))
            time.sleep(5)
            r = requests.get(url)
    except Exception as e2:
        print("SKIPPING because request failed, exception: {}".format(str(e2)))
        with open('weather_errors_and_status_log.txt', "a") as myfile:
            myfile.write(str(e2))
        time.sleep(5)
        return None
    if r.status_code == 200:
        try:
            if(r.json()['errors']):
                print("[ERROR RETURNED FROM API REQUEST]: {}".format(r.json()['errors'][0]['error']['message']))
                with open('weather_errors_and_status_log.txt', "a") as myfile:
                    myfile.write("[ERROR RETURNED FROM API REQUEST]: {}".format(r.json()['errors'][0]['error']['message']))
        except:
            pass
        most_recent_weather = r.json()['observations'][-1]
        previous_weather = r.json()['observations'][-2]
    else:
        print('encountered status code {} for url {}'.format(r.status_code, url))
        with open('incoming_weather_errors_and_status_log.txt', "a") as myfile:
            myfile.write('encountered status code {} for url {}'.format(r.status_code, url))
    return previous_weather, most_recent_weather



def get_columns(most_recent_weather):
    columns = list(most_recent_weather.keys())
    prev_columns = []
    for entry in columns:
        prev_columns.append("prev_" + entry)
    columns.extend(prev_columns)
    return columns


def get_line(previous_weather, most_recent_weather):
    closest_items = most_recent_weather.items()
    previous_items = previous_weather.items()
    data_list = []
    columns = []
    for column, data in closest_items:
        columns.append(column)
        data_list.append(data)
    for column, data in previous_items:
        columns.append("prev_" + column)
        data_list.append(data)
    solar_angle, prev_solar_angle = add_solar_angle_of_observations(most_recent_weather, previous_weather)
    data_list.extend([solar_angle, prev_solar_angle])
    columns.extend(['solar_angle', 'prev_solar_angle'])
    return [data_list], columns


def add_solar_angle_of_observations(dict_items, prev_dict_items, station="KSEA"):
    latitude = 47.33
    longitude = -122.19
    local_tz = lookup_timezone(station)
    epoch_time = dict_items['valid_time_gmt']
    prev_epoch_time = prev_dict_items['valid_time_gmt']
    dt_obj = datetime.datetime.fromtimestamp(epoch_time)
    prev_dt_obj = datetime.datetime.fromtimestamp(prev_epoch_time)
    solar_angle = get_altitude(latitude, longitude, dt_obj)
    prev_solar_angle = get_altitude(latitude, longitude, prev_dt_obj)
    return solar_angle, prev_solar_angle


def construct_most_recent_df(previous_weather, most_recent_weather):
    col = get_columns(most_recent_weather)
    df = pd.DataFrame(columns=col)
    data, columns = get_line(previous_weather, most_recent_weather)
    df = df.append(pd.DataFrame(data, columns=columns), ignore_index=True)
    return df


def drop_none_columns(df):
    path = os.path.join(os.environ['HOME'],'pickles/none_columns.p')
    with open(path, 'rb') as f:
        columns = pickle.load(f)
    df.drop(columns, axis=1, inplace=True)
    return df


def drop_times_icons_names(df):
    path = os.path.join(os.environ['HOME'],'pickles/times_icons_name_columns.p')
    with open(path, 'rb') as f:
        columns = pickle.load(f)
    df.drop(columns, axis=1, inplace=True)
    return df


def cast_columns_to_correct_types(df):
    numeric_columns = ['gust', 'pressure_tend', 'wdir', 'wspd', 'precip_hrly',
                   'prev_gust', 'prev_pressure_tend', 'prev_wdir', 'prev_wspd', 'prev_precip_hrly', 'rh', 'dewPt', 'feels_like', 'heat_index', 'wc', 'prev_rh',
                   'prev_dewPt', 'prev_feels_like', 'prev_heat_index', 'prev_wc', 'pressure',
                      'temp', 'uv_index', 'vis', 'prev_pressure', 'prev_temp', 'prev_uv_index', 'prev_vis']
    for column in numeric_columns:
        df[column] = df[column].apply(pd.to_numeric)
    return df


def fill_missing_values(df):
    zero_columns = ['gust', 'pressure_tend', 'wdir', 'wspd', 'precip_hrly',
                   'prev_gust', 'prev_pressure_tend', 'prev_wdir', 'prev_wspd', 'prev_precip_hrly']
    avg_columns = ['rh', 'dewPt', 'feels_like', 'heat_index', 'wc', 'prev_rh',
                   'prev_dewPt', 'prev_feels_like', 'prev_heat_index', 'prev_wc']
    text_columns = ['clds', 'pressure_desc',
              'uv_desc', 'wdir_cardinal', 'wx_phrase',
              'prev_clds', 'prev_pressure_desc', 'prev_uv_desc', 'prev_wdir_cardinal',
                'prev_wx_phrase', 'icon_extd', 'prev_icon_extd']
    #save average values to use later
    for column in text_columns:
        df[column].fillna(value='None', inplace=True)
    for column in zero_columns:
        df[column].fillna(value=0, inplace=True)
    path = os.path.join(os.environ['HOME'],'pickles/average_dict_for_incoming_data.p')
    with open(path, 'rb') as f:
        avg_dict = pickle.load(f)
    for column in avg_columns:
        df[column].fillna(value=avg_dict[column], inplace=True)
    return df


def prepare_df_for_encoding(df):
    df = drop_none_columns(df)
    df = drop_times_icons_names(df)
    df = cast_columns_to_correct_types(df)
    df = fill_missing_values(df)
    return df


def predict_most_recent():
    previous_weather, most_recent_weather = get_most_recent_weather()
    df = construct_most_recent_df(previous_weather, most_recent_weather)
    df = prepare_df_for_encoding(df)
    if (float(df['solar_angle'].values) < -2) or (float(df['solar_angle'].values) > 45):
        return 0
    path = os.path.join(os.environ['HOME'],'pickles/label_encoding_dict.p')
    with open(path, 'rb') as f:
        d = pickle.load(f)
    path2 = os.path.join(os.environ['HOME'],'pickles/OHC_SS_pipeline.p')
    with open(path2, 'rb') as f:
        OHC_SS_enc_pipeline = pickle.load(f)
    path3 = os.path.join(os.environ['HOME'],'pickles/test_final_model.pk')
    with open(path3, 'rb') as f:
        final_model = pickle.load(f)
    categorical_features=['clds', 'pressure_desc',
              'uv_desc', 'wdir_cardinal', 'wx_phrase',
              'prev_clds', 'prev_pressure_desc', 'prev_uv_desc', 'prev_wdir_cardinal',
                'prev_wx_phrase', 'icon_extd', 'prev_icon_extd']
    encoded_obs = df[categorical_features].apply(lambda x: d[x.name].transform(x))
    df = df.drop(categorical_features, axis=1)
    df = pd.concat([df, encoded_obs], axis=1)
    OHC_SS_encoded_data = OHC_SS_enc_pipeline.transform(df)
    prediction = final_model.predict_proba(OHC_SS_encoded_data)
    return prediction[0][1]
