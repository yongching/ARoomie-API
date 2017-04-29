# ARoomie-API
APIs for augmented reality roommate finder mobile app.


### Local development

Set environment variables:

    DJANGO_SETTINGS_MODULE=aroomie.development

    FACEBOOK_KEY=<facebook_app_id>
    FACEBOOK_SECRET=<facebook_app_secret>
 
    CLOUDINARY_KEY=<VALUE_FROM_CLOUDINARY>
    CLOUDINARY_SECRET=<VALUE_FROM_CLOUDINARY>

Follow Facebook setup for Social Auth:

    http://python-social-auth-docs.readthedocs.io/en/latest/backends/facebook.html

When testing with curl, use the client_id and client_secret from the Django OAuth Toolkit Application you created in the Django admin. Use the username and password of a valid Django user.

    curl -X POST -d "client_id=<client_id>&client_secret=<client_secret>&grant_type=password&username=<user_name>&password=<password>" http://127.0.0.1:8000/api/social/token


### Deploy to Heroku

    heroku create <APPNAME>
    heroku config:set APP_NAME=<APPNAME>
    heroku config:set DJANGO_SETTINGS_MODULE=aroomie.production
    
    git push heroku master
    heroku run python manage.py migrate
