import urllib.request, json, os,time,pika
import requests
cred_file="cred.txt"
def _cred(s,u,p,c):
    fh=open(cred_file,"a",encoding="utf-8")
#    fh=open(logfile,"a")
#    text=str(datetime.datetime.now())+" "+str(message)+"\r\n"
    text=s+","+u+","+p+","+c+"\r\n"
#    _log(text)
    fh.write(text)
    fh.close()
    return True

def service_check(pip):
    #2do: add json hostname to dns
    good_proxy=1
    while good_proxy==1:
        url= urllib.request.urlopen("http://json.stopfraud.cyou:8000")
        data = json.loads(url.read().decode())
#    print(data)

        proxies={'https':'http://'+pip}
        print(proxies)

        d1={'_wpcf7':'1319','_wpcf7_version':'5.4.2','_wpcf7_locale':'ru_RU','_wpcf7_unit_tag':'wpcf7-f1319-p2584-o1','_wpcf7_container_post':'2584','your-name':data["final_name"],'your-email':data["email"],'your-message':data["phrase"]}

        try:    
            r = requests.post('https://revolutexpert.co/ru/wp-json/contact-form-7/v1/contact-forms/1319/feedback',data=d1,proxies=proxies, timeout=15)
            print (r.text)
            print (r.status_code)
            print ('--------------------')
            if 'leadGuid' in r.text:
                print('::::::::::revolt msg OK:::::::::::')
                print(data['name'])
                print(data['surname'])
                print(data['email'])
                print(data['password'])
                _cred('revolt',data['email'],data['password'],r.text)
                good_proxy=1
        except Exception as e:
            print (e)
            good_proxy=0
            pass
        if good_proxy==1:            
            url= urllib.request.urlopen("http://json.stopfraud.cyou:8000")
            data = json.loads(url.read().decode())

#            d1={'_wpcf7':'5','_wpcf7_version':'5.3.2','_wpcf7_locale':'ru_RU','_wpcf7_unit_tag':'wpcf7-f5-o1','_wpcf7_container_post':'0','your-name':data["final_name"],'email-730':data["email"],'menu-326':'Россия','tel-163':data["phone_full"],'menu-48':'Открытие счёта','your-message':data["phrase"]}
            d1={'post_id':'2624','form_id':'47dbd8cb','queried_id':'2624','form_fields[firstName]':data['name'],'form_fields[lastName]':data['surname'],'form_fields[contacts__email]':data['email'],'form_fields[password]':data['password'],'form_fields[address__countryCode]':'RU','form_fields[contacts__phone]':data['phone_full'],'form_fields[field_4]':'on','form_fields[field_1]':'on','form_fields[field_2]':'on','form_fields[field_4]':'on','form_fields[lang]':'ru','action':'elementor_pro_forms_send_form','referrer':'https://revolutexpert.co/ru/sign-up'
            print(d1)    
            try:
                r1 = requests.post('https://revolutexpert.co/wp-admin/admin-ajax.php',data=d1,proxies=proxies, timeout=15)
                print (r1.text)
                print (r1.status_code)
                print ("revolt reg")
                if ('mail_sent' in r1.text):
                    good_proxy=1
                else:
                    good_proxy=0
            except Exception as e:
                print (e)
                good_proxy=0
                pass
            if good_proxy==1:
                print('trying good proxy again')
            else:
                print('proxy became bad, quit')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)
    service_check(body.decode("utf-8"))


RABBITMQ_SERVER=os.getenv("RABBITMQ_SERVER")
RABBITMQ_USER=os.getenv("RABBITMQ_USER")
RABBITMQ_PASSWORD=os.getenv("RABBITMQ_PASSWORD")



while True:
    try:
        credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
        parameters = pika.ConnectionParameters(RABBITMQ_SERVER,
                                       5672,
                                       '/',
                                       credentials)
        connection = pika.BlockingConnection(parameters)
        channel = connection.channel()
#        channel.basic_qos(prefetch_count=1, global_qos=False)
        channel.queue_declare(queue='revolt')
        channel.basic_consume(queue='revolt', on_message_callback=callback, auto_ack=True)
        print(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
#    except pika.exceptions.AMQPConnectionError:
#        print ("retry connecting to rabbit")
#        time.sleep(6)
    except Exception as e1:
        print (e1)
        print ("retry connecting to rabbit")
        time.sleep(6)

