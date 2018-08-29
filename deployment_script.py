import json
import boto3
from botocore.client import Config
import io
import zipfile
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:ap-south-1:102885605453:DeployFolioTopic')

    try:
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

        topic.publish(Subject='Deployment Complete', Message='Folio deployed successfully')

    except:
        topic.publish(Subject='Deployment Failed', Message='Folio could not be deployed')
        raise

    return {
        "statusCode": 200,
        "body": json.dumps('Deployment Function Executed!')
    }
