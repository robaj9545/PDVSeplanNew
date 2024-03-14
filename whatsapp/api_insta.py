import requests

def get_user_info(access_token):
    url = 'https://graph.instagram.com/me?fields=id,username&access_token=' + access_token
    response = requests.get(url)
    data = response.json()
    if 'error' in data:
        print('Erro:', data['error']['message'])
    else:
        print('ID do Usuário:', data['id'])
        print('Nome de Usuário:', data['username'])

if __name__ == "__main__":
    access_token = 'EAAKPMZAQZB7XQBOZCPODkqv4jQ2C1WVcIpiXBnZCDyuNbn8xHuRzObZB8KT9hSTcnDcZBZBpnaedaylAYKjU3uDrhDEE3VMYV1ZCjZCurv1ZA8SvgrKTpiIEHJtER8JaB2ylxUYTElLclQOFnlv98H7jLiRe3F9vnyD8jhIHSHCFXet5a0ZBF13GPgCE1J85a6tjVitOSJDztsyZBP870dYwaK5w0XS9cYfAJX4ka6x3oJ4ZD'
    get_user_info(access_token)
