# rainbow_flask

A rainbow predictor for Seattle built on data science, Twilio and awesomeness. 

(also, a work in progress)

View live web app at www.infinityrainbows.com

## Business Understanding

Who doesn’t take joy at the sight of a rainbow and in pointing one out to friends and passersby? Now, machine learning allows us to predict and verify when rainbows appear. This project builds out the first two components that would be required to create a fully functioning ‘Rainbow Alert’ phone app. The full version of the app would have three components:

- First, it predicts the probability of witnessing a rainbow in the user’s geographic area on that day (a morning prediction and an afternoon prediction). 
- Second, it offers a real-time probability of spotting a rainbow which is updated at intervals throughout the day (as long as the sun is below 42 degrees). 
- Third, if a user spots a rainbow, takes a picture of it and uploads it to the app, the app will verify that the photo contains a rainbow and then send a “rainbow alert’ notification to other users in the geographic area. The purpose of validating the photos with an image classifier is to ensure that a user cannot set off an erroneous rainbow alert in their area. 

This repo is a basic Flask web app that displays the results of a predictive model for ‘probability of rainbow given weather conditions and time of day.’ 


## Data Extraction/Web Scraping

After scraping Instagram for photos of rainbows only to realize I couldn't make sense of the timestamps (and believe me, I tried), I ended up switching to the Flickr API to retrieve 'date taken' timestamps from photos of rainbows. 

Finding a source of historical METAR weather data proved surprisingly difficult, given that it is only available from NOAA by request and only in five-day chunks. I was about to resort to scraping wunderground.com when I was granted an API key to a usable source.


## Modeling and Evaluation

I fit a logistic regression, a gradient boosted decision tree, and a random forest and cross-validated to choose the best. I optimized for a low false positive to true positive ratio (precision). I chose this metric because I want to maintain users’ trust and satisfaction in my app, which alerts users when the probability of spotting a rainbow is above a certain threshold. I ended up implementing the random forest in my web app.  


## Deployment

My website, infinityrainbows.com, checks for the weather API to post new weather conditions and displays the probability of seeing a rainbow. 

I am working on a Twilio integration that allows users to sign up with their mobile phone number to receive alerts when the probability of rainbows is above their user-defined threshold.
