import requests, os, csv
from bs4 import BeautifulSoup as BS

given_link: str = "https://volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=2&xnumnuts=2101"

def get_web(address: str) -> object:
    """returns a web page as a BeautifulSoup object"""
    r = requests.get(address)
    result = BS(r.text, "html.parser")
    return result

def get_base_link(link: str) -> str:
    doubleslash_pos = link.find('//')
    splitted = link[doubleslash_pos + 2:].split("/")
    result = link[:doubleslash_pos + 2] + "/".join(splitted[:-1]) + '/'
    return result

def get_results(link: str):
    """returns a list of tuples with party and votes in form of strings"""
    soup = get_web(link)
    all_parties, all_votes = [], []
    for party in soup.find_all("td", headers="t1sa1 t1sb2"):
        all_parties.append(party.text)
    for votes in soup.find_all("td", headers="t1sa2 t1sb3"):
        all_votes.append(votes.text.replace('\xa0', ''))
    party_vote = list(zip(all_parties, all_votes))
    return party_vote

def get_municipaty_header(link: str):
    """returns a list with header for a given municipaty"""

    headline = ['registered', 'envelopes', 'valid']
    values = []

    soup = get_web(link)
    registered = soup.find("td", headers = "sa2").text.replace('\xa0', '')
    values.append(registered)
    envelopes = soup.find("td", headers = "sa3").text.replace('\xa0', '')
    values.append(envelopes)
    valid = soup.find("td", headers = "sa6").text.replace('\xa0', '')
    values.append(valid)
    result = list(zip(headline,values))
    return result

def get_all_data(link: str):
    """returns the whole district dataset in a list. Each list item is dictionary with header as key and value"""
    soup = get_web(link)
    base_link = get_base_link(link)
    result = []
    all_municipaties = soup.find_all("td", headers="t2sa1 t2sb1")
    municipaty_names = list(soup.find_all("td", headers="t2sa1 t2sb2"))

    for idx, municipaty in enumerate(all_municipaties):
        link_appendix = municipaty.find('a')["href"]
        link = base_link + link_appendix
        line = []

        code_pos = link.find("xobec=")
        code = link[code_pos + 6:code_pos + 12]
        line.append(("code",code))
        line.append(('location',municipaty_names[idx].text))
        line += get_municipaty_header(link) + get_results(link)

        result.append(dict(line))
    return result

def main(link: str, name: str):
    """exports a cvs file with election results for given district"""
    fname = name + '.csv'
    path = 'csv/' + fname #os.path.join('csv',fname)
    if os.path.isfile(path):
        return print('File already exists - try another name')

    data = get_all_data(link)
    header = list(data[0].keys())

    with open(path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for line in data:
            writer.writerow(line)

main(given_link,'Benesov')

