from twilio.rest import Client

def get_sid(machine='ec2'):
    path = os.path.join(os.environ['HOME'],'twilio_sid.txt')
    with open(path,'r') as f:
        api_key = f.readline().strip()
    return api_key


def get_auth_token(machine='ec2'):
    path = os.path.join(os.environ['HOME'],'twilio_auth.txt')
    with open(path,'r') as f:
        api_key = f.readline().strip()
    return api_key


# Your Account SID from twilio.com/console
account_sid = get_sid()
# Your Auth Token from twilio.com/console
auth_token  = get_auth_token()

client = Client(account_sid, auth_token)

message = client.messages.create(
    to="+12814138390",
    from_="+12062045309",
    body="Hello from Python and EC2!")

print(message.sid)
