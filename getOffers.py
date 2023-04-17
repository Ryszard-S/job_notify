import json as js
from datetime import datetime, timedelta

import requests


def _get_isoformat(date):
    try:
        _date = datetime.fromisoformat(date)
    except ValueError:
        print('ValueError ISOFORMAT')
        _date = None
    return _date


def get_offers_pracuj():
    req1 = requests.get('https://massachusetts.pracuj.pl/api/offers?et=17&rw=true&jobBoardVersion=2&pn=1&rop=40').json()
    req2 = requests.get(
        'https://massachusetts.pracuj.pl/api/offers?wp=Wroc%C5%82aw&et=17&et=1&jobBoardVersion=2&rop=20&pn=1').json()
    offers_list = req1.get('offers') + req2.get('offers')
    date = datetime.today() - timedelta(days=1)
    offers = list(filter(lambda x: _get_isoformat(x['lastPublicated']) >= date, offers_list))

    list_offers = []

    for index, offer in enumerate(offers):
        di = dict()
        
        if offers[index - 1].get('groupId') != offers[index].get('groupId'):
            di.update({"offerUrl": offer.get('offerUrl')})
            di.update({"location": offer.get('location')})
            di.update({"jobTitle": offer.get('jobTitle')})
            di.update({"employer": offer.get('employer')})
            di.update({"logo": offer.get('logo')})
            di.update({"remoteWork": offer.get('remoteWork')})
            di.update({"lastPublicated": _get_isoformat(offer.get('lastPublicated'))})
            list_offers.append(di)
    list_offers = list(reversed(sorted(list_offers, key=lambda x: x['lastPublicated'])))
    return list_offers


def get_offers_bulldog():
    body = {"operationName": "searchJobs",
            "variables": {
                "page": 1,
                "perPage": 20,
                "filters": {
                    "experienceLevel": ["junior"],
                    "city": ["Wrocław", "Remote"]},
                "language": "pl",
                "order": {"direction": "DESC", "field": "PUBLISHED"}},
            "query": "query searchJobs($page: Int, $perPage: Int, $filters: JobFilters, $order: JobsSearchOrderBy, $language: LocaleEnum, $boostWhere: BoostWhere, $exclude: [ID!]) {\nsearchJobs(\npage: $page\nperPage:$perPage\nfilters:$filters\norder:$order\nlanguage:$language\nboostWhere:$boostWhere\nexclude:$exclude\n){\ntotalCount\nnodes {\nid\ncompany {\nname\nlogo {\nurl(style: \"list\")\n}\n}\nhighlight\ncity\nexperienceLevel\nlocations{\naddress\nlocation {\ncityPl\n}\n}\nposition\nremote\nendsAt\npublishedAt\n}\n}\n}\n",
            }
    headers = {
        "content-type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/111.0",
        "Accept": "*/*",
        "Accept-Language": "pl, en - US;q = 0.7, en;q = 0.3",
        "Referer": "https://bulldogjob.pl/companies/jobs/s/city,Remote,Wroc%C5%82aw/experienceLevel,junior"}
    req = requests.post("https://bulldogjob.pl/graphql", data=js.dumps(body), headers=headers)
    _offers = req.json().get("data").get("searchJobs").get('nodes')

    date = datetime.fromisoformat(datetime.now().isoformat() + '+02:00') - timedelta(days=5)
    offers = list(filter(lambda x: _get_isoformat(x['publishedAt']) >= date, _offers))

    list_offers = []

    for offer in offers:
        di = dict()
        di.update({"offerUrl": "https://bulldogjob.pl/companies/jobs/" + offer.get('id')})
        di.update({"location": offer.get('city')})
        di.update({"jobTitle": offer.get('position')})
        di.update({"employer": offer.get('company').get('name')})
        di.update({"logo": offer.get('company').get('logo').get('url')})
        di.update({"remoteWork": offer.get('remote')})
        di.update({"lastPublicated": _get_isoformat(offer.get('endsAt'))})
        list_offers.append(di)

    return list_offers


def get_offers_just():
    req = requests.get('https://justjoin.it/api/offers')
    offers_just = req.json()

    def __filter_just(x):
        d = datetime.fromisoformat(datetime.now().isoformat() + '+02:00') - timedelta(days=1)
        city = x['city'] == 'Wrocław'
        level = x['experience_level'] == 'junior'
        remote = x['remote']
        date = _get_isoformat(x['published_at']) >= d
        if level and date and (city or remote):
            return True
        return False

    offers = list(filter(__filter_just, offers_just))
    offers = list(sorted(offers, key=lambda x: x['id']))

    list_offers = []

    for index, offer in enumerate(offers):

        di = dict()
        if offers[index - 1].get('title') != offers[index].get('title'):
            di.update({"offerUrl": "https://justjoin.it/offers/" + offer.get('id')})
            di.update({"location": offer.get('city')})
            di.update({"jobTitle": offer.get('title')})
            di.update({"employer": offer.get('company_name')})
            di.update({"logo": offer.get('company_logo_url')})
            di.update({"remoteWork": offer.get('remote')})
            di.update({"lastPublicated": _get_isoformat(offer.get('published_at'))})
            list_offers.append(di)
    list_offers = list(reversed(sorted(list_offers, key=lambda x: x['lastPublicated'])))
    return list_offers
