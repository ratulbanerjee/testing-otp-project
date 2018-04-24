from django.http import HttpResponse
from django.shortcuts import render
import json
import requests
import boto3
from django.shortcuts import render, redirect
import re
import datetime
from threading import Timer
from datetime import timedelta
import datetime,time
import time



def home(request):
    return render(request, 'otp.html')


def otp_generation(request):

    username = request.POST.get('username')
    mobile=request.POST.get('mobile')


    try:
        # this api will generate an otp that lasts for 120 sec
        response = requests.get('https://07oq90nb27.execute-api.us-west-2.amazonaws.com/prod/otp')
        response_object = response.json()

        otp=str(response_object['otp'])


    except BaseException as e:
        return HttpResponse("error occured in otp generation")



    #otp = input("enter your otp")

    try:

        client = boto3.client(
            "sns",

            region_name="us-west-2"
        )

        client.set_sms_attributes(
            attributes={
                'DefaultSMSType': 'Transactional'
            }
        )

        client.publish(
            PhoneNumber=mobile,

            Message=otp
        )

    except BaseException as e:
        print("message not sent")

    #place the otp in database

    try:

        dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
        table = dynamodb.Table('student')
        current_time = str(datetime.datetime.now())
        table.update_item(
            Key={
                'id': username

            },

            UpdateExpression='SET OTP =:otp, timestamps =:time',
            ExpressionAttributeValues={
                ':otp': otp,
                ':time' : current_time
            }
        )


    except BaseException as e:
        return HttpResponse(e)

    context={"message" : "otp has been sent to your mobile"}

    return render(request, 'con.html', context)

def login(request):

    return render(request,'login.html')


def validation(request):

    try:
        username = request.POST.get('username')
        otp = int(request.POST.get('otp'))
        query_params = {'id': username, 'otp': otp}

        dynamodb = boto3.resource('dynamodb', region_name='us-west-1')
        table = dynamodb.Table('student')
        response = table.get_item(
            Key={
                'id': username

            }
        )
        item = response['Item']

        otp_time_at_creation = item['timestamps']


        current_time = str(datetime.datetime.now())

        otp_time_at_creation=datetime.datetime(*time.strptime(otp_time_at_creation, "%Y-%m-%d %H:%M:%S.%f")[:6])
        current_time=datetime.datetime(*time.strptime(current_time, "%Y-%m-%d %H:%M:%S.%f")[:6])

        time_difference=abs(current_time - otp_time_at_creation).seconds



        if time_difference < 120:
            #calling the api for validation
            response = requests.get('https://4lwptxh5sc.execute-api.us-west-1.amazonaws.com/prod', params=query_params)
            response_object = response.json()

            return HttpResponse(response_object['msg'])


        else:
            
            return HttpResponse('otp expired')

    except BaseException as e:
        print("error occured in otp validation")




