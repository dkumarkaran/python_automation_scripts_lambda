def handler(event, context):    
    import boto3
    import pandas as pd
    from botocore.exceptions import ClientError


    client = boto3.client('ec2')

    response = client.describe_instances(Filters=[
        {
            'Name': 'instance-state-name',
            'Values': ['pending', 'running', 'shutting-down', 'stopping', 'stopped']
        }
    ])
    data = {
        'Instance Id': [],
        'Instance Type': [],
        'Vpc Id': [],
        'Subnet Id': [],
        'State': [],
        'Ebs': [],
        'AZ': [],
        'Sg': [],
        'Created-By': [],
        'Instance Name': [],
        'Instance Termination Protection': []}
    # ---------------------------
    # required paramethers as output
    # instance id
    # instance type
    # vpc id
    # state running/stopped
    # ebs id
    # ebs delete on termination status true/false
    # sg id
    # subnet id
    # -----------------------------
    for r in response['Reservations']:
        for i in r['Instances']:
            print(i)
            tags = i["Tags"]
            name = True
            for tags_instances in tags:
                print(tags_instances)
                if tags_instances['Key'] == 'Name':
                    print(tags_instances['Value'])
                    data["Instance Name"].append(tags_instances['Value'])
                    name = False
            if name == True:
                data["Instance Name"].append(None)
            # -----------------------------------------------
            # created-by tags
            cb = True  # this assigns a veriable cb with created by as true.
            for tags_instances in tags:
                # print(tags_instances)
                if tags_instances['Key'] == 'Created-By' or tags_instances['Key'] == 'Created_By':
                    print(tags_instances['Value'])
                    data["Created-By"].append(tags_instances['Value'])
                    cb = False  # if created by is there then, the cb gets a value false
            if cb == True:
                data["Created-By"].append(None)
            # -------------------------------------------------

            instance_id = i["InstanceId"]
            data['Instance Id'].append(instance_id)  # append instance id
            instance_type = i["InstanceType"]
            data['Instance Type'].append(instance_type)
            az = i["Placement"]["AvailabilityZone"]
            data["AZ"].append(az)
            client01 = boto3.client('ec2')
            # Get the security groups for the instance
            response = client01.describe_instances(InstanceIds=[instance_id])

            # Extract the security group IDs
            security_groups = response['Reservations'][0]['Instances'][0]['SecurityGroups']

            # Print the security group IDs
            sg_list = []
            for sg in security_groups:
                print(sg['GroupId'])
                sg_id = sg['GroupId']
                sg_list.append(sg_id)
            sg_list_to_str = ', '.join(sg_list)
            print(sg_list_to_str)
            data["Sg"].append(sg_list_to_str)
            print(f"state={i['State']['Name']}")
            data["State"].append(i['State']['Name'])
            client02 = boto3.client('ec2')
            response = client02.describe_instances(
                InstanceIds=[instance_id]
            )
            subnet_id = response["Reservations"][0]["Instances"][0]["SubnetId"]
            print(subnet_id)
            data["Subnet Id"].append(subnet_id)
            vpc_id = response["Reservations"][0]["Instances"][0]["VpcId"]

            print(vpc_id)
            data["Vpc Id"].append(vpc_id)
            ebs = response["Reservations"][0]["Instances"][0]["BlockDeviceMappings"][0]["Ebs"]["VolumeId"]
            print(ebs)
            data["Ebs"].append(ebs)

            # Get the instance termination protection attribute
            instances_client = boto3.client('ec2')
            response = instances_client.describe_instance_attribute(
                InstanceId=instance_id,
                Attribute='disableApiTermination'
            )

            # Check if termination protection is enabled
            if response['DisableApiTermination']['Value']:
                print(f"Termination protection is enabled for instance {instance_id}")
                data["Instance Termination Protection"].append("Enabled")
            else:
                print(f"Termination protection is not enabled for instance {instance_id}")
                data["Instance Termination Protection"].append("Not Enabled")

            print("------------------")

    print(data)
    print(data)
    print(len(data["Instance Id"]))
    print(len(data["Instance Type"]))
    print(len(data["Vpc Id"]))
    print(len(data["Subnet Id"]))
    print(len(data["State"]))
    print(len(data["Ebs"]))
    print(len(data["AZ"]))
    print(len(data["Sg"]))
    print(len(data['Created-By']))
    print(f"instance name = {len(data['Instance Name'])}")
    print(len(data["Instance Termination Protection"]))

    df = pd.DataFrame(data)
    # df.to_excel('data.xlsx', index=False)
    #df.to_excel('data.xlsx', index=False, sheet_name='Instance Details')
    print(df.to_html())
    body=df.to_html()
    body_html = '<html>\n' + body + '\n</html>'
    print(":::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::::")
    print(body_html)

    # ------------------email function--------------------
    ses = boto3.client('ses', region_name='us-east-1')

    # Set up the email message
    sender_email = 'd.kumarkaran@searce.com'
    recipient_email = 'd.kumarkaran@searce.com'
    subject = 'Test email'
    message = {
        'Subject': {'Data': subject},
        'Body': {'Html':{'Data': body_html}}
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

