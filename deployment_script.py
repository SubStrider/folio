import json
import boto3
from botocore.client import Config
import io
import zipfile
import mimetypes

def lambda_handler(event, context):

    s3 = boto3.resource('s3', config = Config(signature_version='s3v4'))
    # s3 = boto3.resource('s3')

    #initialize code and production buckets
    folio_bucket = s3.Bucket('rahulrakesh.me')
    build_bucket = s3.Bucket('build.rahulrakesh.me')

    # create in-memory bytes io file and import the file
    portfolio_zip = io.BytesIO()
    build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

    # upload the contents of the file to production s3 bucket
    with zipfile.ZipFile(portfolio_zip) as myzip:
        for nm in myzip.namelist():
            obj = myzip.open(nm)
            folio_bucket.upload_fileobj(obj, nm, ExtraArgs = {'ContentType': mimetypes.guess_type(nm)[0]})
            folio_bucket.Object(nm).Acl().put(ACL='public-read')

    return {
        "statusCode": 200,
        "body": json.dumps('Hello from Lambda!')
    }
