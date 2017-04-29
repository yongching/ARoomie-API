# ARoomie-API
APIs for augmented reality roommate finder mobile app.


### Local development

Set environment variables:
    
    SECRET_KEY=<secret_key>  # Can create with:$(openssl rand -base64 58 | tr '\n' '_')

    DJANGO_SETTINGS_MODULE=aroomie.development

    FACEBOOK_KEY=<facebook_app_id>
    FACEBOOK_SECRET=<facebook_app_secret>
 
    CLOUDINARY_KEY=<value_from_cloudinary>
    CLOUDINARY_SECRET=<value_from_cloudinary>

Follow Facebook setup for Social Auth:

    http://python-social-auth-docs.readthedocs.io/en/latest/backends/facebook.html

When testing with curl, use the client_id and client_secret from the Django OAuth Toolkit Application you created in the Django admin. Use the username and password of a valid Django user.

    curl -X POST -d 'client_id=<client_id>&client_secret=<client_secret>&grant_type=password&username=<user_name>&password=<password>' http://127.0.0.1:8000/api/social/token


### Deploy to Heroku

Create a Facebook application for your Heroku app

    heroku create <APPNAME>
    
    heroku config:set APP_NAME=<APPNAME>
    heroku config:set SECRET_KEY=<secret_key>  # Can create with: $(openssl rand -base64 58 | tr '\n' '_')
    heroku config:set DJANGO_SETTINGS_MODULE=aroomie.production
    heroku config:set FACEBOOK_KEY=<facebook_app_id>
    heroku config:set FACEBOOK_SECRET=<facebook_app_secret>
    heroku config:set CLOUDINARY_KEY=<value_from_cloudinary>
    heroku config:set CLOUDINARY_SECRET=<value_from_cloudinary>
    
    git push heroku master
    heroku run python manage.py migrate

Test with curl:

    curl -X POST -d "client_id=<client_id>&client_secret=<client_secret>&grant_type=password&username=<user_name>&password=<password>" http://<APP_NAME>.herokuapp.com/api/social/token
