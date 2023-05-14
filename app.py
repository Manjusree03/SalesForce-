from flask import Flask, request, jsonify,Response
import pandas as pd
import numpy as np
from flask_cors import CORS
import csv
from datetime import datetime
from datetime import timedelta
from sklearn.metrics import mean_squared_error
from math import sqrt
from statsmodels.tsa.statespace.sarimax import SARIMAX

app = Flask(__name__)
FLASK_APP=app
CORS(app)

@app.route('/', methods=['POST'])
def upload():
    file = request.files['csvFile']
    if file.filename == '':
        return 'No file selected'

    # Save the file to disk or do some processing
    file.save(file.filename)
    
    print("File saved successfully")

    with open(file.filename, 'r') as f:
        reader = csv.reader(f)
        next(reader)

        data = [row for row in reader]

        data = pd.DataFrame(data, columns=['ORDERNUMBER', 'QUANTITYORDERED', 'PRICEEACH', 'ORDERLINENUMBER', 'SALES', 'ORDERDATE', 'PRODUCTCODE', 'QTR_ID', 'MONTH_ID', 'YEAR_ID', 'PRODUCTLINE', 'MSRP'])

        print("Success")

        data['SALES'] = data['SALES'].astype(float)

        data['ORDERDATE'] = pd.to_datetime(data['ORDERDATE'])
        dft = pd.DataFrame(data)

        data['SALES'] = pd.to_numeric(data['SALES'], errors='coerce')
        data = data.dropna(subset=['SALES'])# remove rows with missing values
        data.info()
        daily_sales_data  = pd.DataFrame(dft['SALES'])
       
        
        # Resample the data to daily frequency
        daily_sales_data = data.set_index('ORDERDATE')['SALES'].resample('D').sum().reset_index()
        train, test, validation = np.split(daily_sales_data ['SALES'].sample(frac = 1), [int(.6*len(daily_sales_data ['SALES'])), int(.8*len(daily_sales_data ['SALES']))])
        
        
        train_count = len(train)
        test_count = len(test)
        validation_count = len(validation)
        dataset_names = ['Train', 'Test', 'Validation']
        dataset_counts = [train_count, test_count, validation_count]
        
        #prediction
        import itertools
        p = d = q = range(0, 2) 
        pdq = list(itertools.product(p, d, q))
        seasonal_pdq_comb = [(i[0], i[1], i[2], 12) for i in list(itertools.product(p, d, q))]
        print('Examples of parameter combinations for Seasonal ARIMA:')
        print('SARIMA: {} x {}'.format(pdq[1], seasonal_pdq_comb[1]))
        print('SARIMA: {} x {}'.format(pdq[1], seasonal_pdq_comb[2]))
        print('SARIMA: {} x {}'.format(pdq[2], seasonal_pdq_comb[3]))
        print('SARIMA: {} x {}'.format(pdq[2], seasonal_pdq_comb[4]))
        
        
        metric_aic_dict=dict()
        for parameters in pdq:
            for seasonal_param in seasonal_pdq_comb:
                try:
                    mod = sm.tsa.statespace.SARIMAX(daily_sales_data ,
                                            order=parameters,
                                            seasonal_param_order=seasonal_param,
                                            enforce_stationarity=False,
                                            enforce_invertibility=False)
                    results = mod.fit()
                    print('SARIMA{}x{}12 - AIC:{}'.format(parameters, seasonal_param, results.aic))
                    metric_aic_dict.update({(pm,pm_seasonal):results.aic})
                except:
                    continue
           
        
        # Resample the data to weekly frequency
        weekly_sales_data = data.set_index('ORDERDATE')['SALES'].resample('W').sum().reset_index()

        # Resample the data to monthly frequency
        monthly_sales_data = data.set_index('ORDERDATE')['SALES'].resample('M').sum().reset_index()

        # Resample the data to yearly frequency
        yearly_sales_data = data.set_index('ORDERDATE')['SALES'].resample('Y').sum().reset_index()

        # Initialize empty dictionary for storing seasonal orders
        seasonal_orders = {}

        # Define SARIMA models for different periodicities
        sarima_models = {}

        # Daily SARIMA model
        seasonal_order_daily = (0, 1, 1, 7)
        seasonal_orders['D'] = seasonal_order_daily
        model_daily = SARIMAX(daily_sales_data['SALES'], order=(1, 1, 1), seasonal_order=seasonal_order_daily)
        sarima_models['D'] = model_daily

        # Weekly SARIMA model
        seasonal_order_weekly = (0, 1, 1, 52)
        seasonal_orders['W'] = seasonal_order_weekly
        model_weekly = SARIMAX(weekly_sales_data['SALES'], order=(1, 1, 1), seasonal_order=seasonal_order_weekly)
        sarima_models['W'] = model_weekly

        # Monthly SARIMA model
        seasonal_order_monthly = (0, 1, 1, 12)
        seasonal_orders['M'] = seasonal_order_monthly
        model_monthly = SARIMAX(monthly_sales_data['SALES'], order=(1, 1, 1), seasonal_order=seasonal_order_monthly)
        sarima_models['M'] = model_monthly

        # Yearly SARIMA model
        seasonal_order_yearly = (0, 1, 1, 2)
        seasonal_orders['Y'] = seasonal_order_yearly
        model_yearly = SARIMAX(yearly_sales_data['SALES'], order=(1, 1, 1), seasonal_order=seasonal_order_yearly)
        sarima_models['Y'] = model_yearly
        
        
        # Check if periodicity is valid
        periodicity = request.form.get('periodicity')
        if periodicity not in ['D', 'W', 'M', 'Y']:
            return jsonify({'error': 'Invalid periodicity'})
        
        # Get the number of periods from the user
        periods = request.form.get('periods')
        if not periods.isdigit():
            return jsonify({'error': 'Invalid number of periods'})
        num_periods = int(periods)

     # Train SARIMA models
        trained_models = {}
        for freq, model in sarima_models.items():
            trained_model = model.fit()
            trained_models[freq] = trained_model
            # Generate sales forecast for the given number of periods
        today = datetime.now()
        daily_forecast = trained_models['D'].forecast(steps=num_periods) if periodicity == 'D' else []
        weekly_forecast = trained_models['W'].forecast(steps=num_periods) if periodicity == 'W' else []
        monthly_forecast = trained_models['M'].forecast(steps=num_periods) if periodicity == 'M' else []
        yearly_forecast = trained_models['Y'].forecast(steps=num_periods) if periodicity == 'Y' else []

    # Get the maximum date in the dataset
        max_date = daily_sales_data['ORDERDATE'].max()

# Generate forecast dates
        if periodicity == 'D':
            forecast_dates = pd.date_range(start=max_date + timedelta(days=1), periods=num_periods, freq='D')
            forecast_data = pd.DataFrame({'date': forecast_dates, 'forecast': daily_forecast})
        elif periodicity == 'W':
            forecast_dates = pd.date_range(start=max_date + timedelta(weeks=1), periods=num_periods, freq='W')
        elif periodicity == 'M':
            forecast_dates = pd.date_range(start=max_date.replace(day=1) + pd.DateOffset(months=1), periods=num_periods, freq='M')
        elif periodicity == 'Y':
            forecast_dates = pd.date_range(start=max_date.replace(day=1, month=1) + pd.DateOffset(years=1), periods=num_periods, freq='Y')
        else:
            forecast_dates = []

      # Combine forecast data and dates
        forecast_data = np.concatenate((daily_forecast, weekly_forecast, monthly_forecast, yearly_forecast))
        forecast = pd.DataFrame({'Date': forecast_dates, 'Forecast': forecast_data})
        
        forecast['Date'] = forecast['Date'].astype(str)
        #forecast = forecast.to_dict('records')
        c=forecast.to_csv(index=False)
        


        # Set the response headers
        headers = {
            'Content-Disposition': 'attachment; filename="predictions.csv"',
            'Content-Type': 'text/csv'
        }

#         with open(r"E:\ms.csv",'w') as f:
#             f.write(c)
        return Response(
            c,
            headers=headers,
            mimetype='text/csv'
        )
    
       
@app.route('/', methods=['GET'])
def up():
    return "Hello"


if __name__ == '__main__':
    app.run(debug=False)