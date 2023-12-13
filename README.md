# aws-live
BAIT3273 Cloud Computing Assignment 

# Pre-requisites
- Python to run Flask application

How to setup in VSCode (Setup a virtual environment)
1) Click Ctrl Shift P in VSCode
2) Select Python: Create Environment, then select venv and then the Python environment
3) After the virtual environment is done create, run a Terminal (Either Command Prompt or Git Bash)
4) In the command prompt type, python -m pip install flask boto3 pymysql python-dotenv Flask-Session waitress
5) Then, python InternshipApp.py

# Database 
Hostname/Endpoint: internship-system-db.c1nlreg7eojl.us-east-1.rds.amazonaws.com

Username: aws_user

Password: Bait3273

# For Development only!!
To get/upload object in/to s3, ensure that:
1) .env environment file to store your aws credential to have access to the S3 Bucket
2) Learner Lab has started in AWS console
## Setting up 
1. Create a .env file in your project root directory
2. Go to AWS Console, beside the End Lab, i Aws Details
3. Click the "Show" beside the AWS CLI : Show
    It should show something like this
    ```
    [default]
    aws_access_key_id=ASIASOMY2LJT2VGY2MEE
    aws_secret_access_key=VO71BZS7glPFDFc9NnFbffXvKNrC5yTbTTxmTYOt
    aws_session_token=asdlasldjlkajdjadd+14qSgeftiLPASEzI9Ey+hQIFttufVxTFD2XcW8CWnMAtk18sFrn3sz1kjd4btFcrQbpQiEgITF8Y4MbUJjOVRJwf/xreA3q3bCK4RmMy7Z0IKtL9mHGfEjApx0b+is63KQB5+CS68bLX3rhQZP7yrZxBbah2Y4YCylolY11mPyRfDzv3Ec4ucC6MphpsX2vjGVb3qzuhzSVWsvBkKHA7vmFjdRYjt4lxp/UfiSddOFtGaWov08Xr27E7YqvR7vVjriHn8cExhiPykukOthoBnM6DU70BM8NYSiex4qoBjItYICMwZdvAjcjIX/7HN0x9InLdkNX+98cAfMqkG4qblmVKb/FndNaA8B0SMVd
    ```
_Note : This credential is to illustrate how the access keys looks like_

4. Copy and Paste this into the .env file

Internship OnMyfinger Reference
http://i2hub.tarc.edu.my:8846/
