import boto3
import base64
import gzip
import json
import os
import logging

logger = logging.getLogger()
logger.setLevel(logging.ERROR)


def lambda_handler(event, context):
    cw_client = boto3.client('cloudwatch')
    metric_name = "MediaTailor Errors"
    namespace = "Custom MediaTailor"
    logger.info("event: %s \n context: %s" % (str(event), str(context)))

    data = gzip.decompress(base64.b64decode(event['awslogs']['data']))
    decoded_data = json.loads(data.decode())
    for logevent in decoded_data['logEvents']:
        ads_log = json.loads(logevent['message'])
        event_time = ads_log['eventTimestamp']
        event_type = ads_log['eventType']
        config_name = ads_log['originId']
        if ('error' in ads_log.keys()):
            ads_error = ads_log['error']
        else:
            ads_error = "No Error log Present"
        logger.error("Event type: %s Config Name: %s \n Event Time: %s \n Error: %s" % (event_type, config_name, event_time, ads_error))
        emit_metric(cw_client, metric_name, namespace, config_name)
    return

def emit_metric(cw_client, metric_name, namespace, config_name):
    print ("adding count to metric %s in namespace %s" % (metric_name, namespace))
    dimension_name = "Configuration Name"
    cw_client.put_metric_data(
        Namespace = namespace,
        MetricData = [
            {
                'MetricName': metric_name,
                'Dimensions': [
                    {
                        'Name' : dimension_name,
                        'Value' : config_name
                    },
                ],
                "Value": 1,
                "Unit": "Count"
            }
        ]
    )
