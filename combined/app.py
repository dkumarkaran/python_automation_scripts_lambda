body_complete=""


def eks():
    global body_complete
    import boto3
    import pandas as pd
    from botocore.exceptions import ClientError
    # defining data dictionary

    data = {
        'Region': [],
        'Cluster Name': [],
        'Nodegroup Instance Type': [],
        'Created-By': []
    }

    regions = ['ap-south-2', 'us-east-1', 'ap-south-1']
    for re in regions:
        client = boto3.client('eks', region_name=re)
        response = client.list_clusters()
        cluster_name_list = response["clusters"]
        # print(type(cluster_name_list))
        print(re)
        number_of_cluster = 0
        number_of_cluster = len(cluster_name_list)
        if number_of_cluster == 0:
            data['Cluster Name'].append(None)
            data['Created-By'].append(None)
            data['Nodegroup Instance Type'].append(None)
        else:
            for i in cluster_name_list:
                print(i)
                data['Cluster Name'].append(i)  # cluster name appended
                # describe the cluster
                # tags
                response = client.describe_cluster(name=i)
                print(response['cluster']['tags'])
                tags_001 = response['cluster']['tags']
                if 'Created-By' in tags_001:
                    cb = tags_001['Created-By']
                    print(cb)
                    data['Created-By'].append(cb)
                else:
                    print("No Created-By tag specefied")
                    data['Created-By'].append("Created-By tag Missing")

                # find the nodegroup type
                ng = client.list_nodegroups(clusterName=i)
                # print(ng['ResponseMetadata']['nodegroups'])
                ng_list = ng['nodegroups']
                # print(ng_list)
                # print(len(ng_list))
                instance_type_all_ng_list = ""
                # describe each ng to find the instance types used
                for n in ng_list:
                    ng_r = client.describe_nodegroup(
                        clusterName=i,
                        nodegroupName=n
                    )
                    instance_type = ng_r['nodegroup']['instanceTypes']
                    # print(type(instance_type))
                    # list to str
                    type = ', '.join(instance_type)
                    # print(type)
                    instance_type_all_ng_list = type + instance_type_all_ng_list
                data['Nodegroup Instance Type'].append(instance_type_all_ng_list)
                print(instance_type_all_ng_list)

        data['Region'].append(re)
        for l in range(number_of_cluster - 1):
            data['Region'].append(re)
        print("----------------------------")

    print(data)
    df = pd.DataFrame(data)
    body = df.to_html()
    body_complete = f"{body_complete}+\n{body}"


def instance():
    global body_complete
    import boto3
    import pandas as pd
    from botocore.exceptions import ClientError

    data = {
        'region': [],
        'instance_id': [],
        'instance_type': [],
        'created_by': [],
        'state': []
    }
    # Create an EC2 client
    regions = ['ap-south-2', 'us-east-1', 'ap-south-1']
    for re in regions:
        ec2 = boto3.client('ec2', region_name=re)
        instance_count = 0
        # Retrieve information for all running instances
        instances = ec2.describe_instances(Filters=[{'Name': 'instance-state-name', 'Values': ['running', 'stopped']}])

        # Iterate over instances and print information
        for reservation in instances['Reservations']:
            for instance in reservation['Instances']:
                instance_count = instance_count + 1
                instance_id = instance['InstanceId']
                instance_type = instance['InstanceType']
                tags = instance['Tags']
                print(tags)
                for tg in tags:
                    if tg['Key'] == 'Created-By':
                        print("tags present")
                        data['created_by'].append(tg['Value'])
                        break
                else:
                    print("tags createdby not present")
                    data['created_by'].append("Created-By tag Missing")
                status = instance['State']['Name']
                print(f"Instance ID: {instance_id}")
                data['instance_id'].append(instance_id)
                print(f"Instance Type: {instance_type}")
                data['instance_type'].append(instance_type)
                print(f"Status: {status}")
                data['state'].append(status)
                print("\n")

        print(re)
        print(data)
        print(instance_count)
        data['region'].append(re)
        for i in range(instance_count - 1):
            data['region'].append(re)
        print("----------------")

    print(data)
    df = pd.DataFrame(data)
    body = df.to_html()
    body_complete=f"{body_complete}+\n{body}"



def handler(event, context):    
    import boto3
    import pandas as pd
    from botocore.exceptions import ClientError

    global body_complete
    #main fucntion

    body_complete=f'{body_complete}+\n below are the details for eks'
    eks()
    body_complete=f'{body_complete}+\n below are the details for instances'
    instance()
    print("===============================")
    print(body_complete)

    #adding the html header and footer
    body_complete=f"<html>{body_complete}</html>"
    ses = boto3.client('ses', region_name='us-east-1')

    # Set up the email message
    sender_email = 'd.kumarkaran@searce.com'
    recipient_email = 'd.kumarkaran@searce.com'
    subject = 'instance and eks details in nv,mumbai,hyd regions.'
    message = {
        'Subject': {'Data': subject},
        'Body': {'Html': {'Data': body_complete}}
    }

    # Send the email
    try:
        response = ses.send_email(
            Source=sender_email,
            Destination={
                'ToAddresses': [recipient_email]
            },
            Message=message
        )
        print(f"Email sent! Message ID: {response['MessageId']}")
    except ClientError as e:
        print(f"Email not sent. Error message: {e.response['Error']['Message']}")
    return {
        'statusCode': 200,
        'body': 'Email sent successfully.'
    }

