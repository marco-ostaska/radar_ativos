import bancoCentral as bc
import datetime
import json

def refresh_indices():
    now = f"{datetime.datetime.now():%d-%m-%Y}"
    try:
        selic = bc.SELIC(5)
        ipca = bc.IPCA(5)
        data = {
            'date': now,
            'selic': selic.media_ganho_real,
            'ipca': ipca.media_ganho_real
        }
    except Exception as e:
        data = {
            'date': now,
            'selic': 7,
            'ipca': 6.5
        }


    with open('bc.json', 'w') as file:
        json.dump(data, file)



def get_indices():
    # checa se arquivo bc.json existe
    try:
        with open('bc.json') as file:
            data = json.load(file)
            if data['date'].split('-')[1] == f"{datetime.datetime.now():%m}":
                return data
            refresh_indices()
            return get_indices()
    except FileNotFoundError:
        refresh_indices()
        return get_indices()



def melhor_indice():
    indices = get_indices()
    selic = indices['selic']
    ipca = indices['ipca']
    return max(selic, ipca)


print(melhor_indice())
