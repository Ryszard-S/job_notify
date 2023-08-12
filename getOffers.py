from datetime import datetime, timedelta, timezone

import redis

r = redis.Redis(host='localhost', port=6379, decode_responses=True)
days = 31 * 24 * 60 * 60


def _get_isoformat(date):
    try:
        if isinstance(date, int):
            epoch = date / 1000
            return datetime.utcfromtimestamp(epoch).replace(tzinfo=timezone.utc)
        _date = datetime.fromisoformat(date)
    except ValueError:
        print('ValueError ISOFORMAT')
        _date = None
    return _date


async def get_offers_pracuj(session):
    async with session.get(
            'https://massachusetts.pracuj.pl/api/offers?et=17&rw=true&jobBoardVersion=2&pn=1&rop=40') as resp:
        req1 = await resp.json()
    async with session.get(
            'https://massachusetts.pracuj.pl/api/offers?et=17&rw=true&jobBoardVersion=2&pn=1&rop=40') as resp:
        req2 = await resp.json()
    offers_list = req1.get('offers') + req2.get('offers')
    date = datetime.today() - timedelta(days=1)
    offers = list(filter(lambda x: _get_isoformat(x['lastPublicated']) >= date, offers_list))

    list_offers = []

    for index, offer in enumerate(offers):
        di = dict()
        offer_id = offer.get('offerId')
        if r.exists(f'pracuj:{offer_id}'):
            continue
        else:
            r.setex(f'pracuj:{offer_id}', days, 1)

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


async def get_offers_bulldog(session):
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
    async with session.post("https://bulldogjob.pl/graphql", json=body, headers=headers) as resp:
        print(resp.status, __name__)
        req = await resp.json()
        _offers = req.get("data").get("searchJobs").get('nodes')

        date = datetime.fromisoformat(datetime.now().isoformat() + '+02:00') - timedelta(days=5)
        offers = list(filter(lambda x: _get_isoformat(x['publishedAt']) >= date, _offers))

        list_offers = []

        for offer in offers:
            di = dict()
            offer_id = offer.get('id')
            if r.exists(f'bulldog:{offer_id}'):
                continue
            else:
                r.setex(f'bulldog:{offer_id}', days, 1)

            di.update({"offerUrl": "https://bulldogjob.pl/companies/jobs/" + offer.get('id')})
            di.update({"location": offer.get('city')})
            di.update({"jobTitle": offer.get('position')})
            di.update({"employer": offer.get('company').get('name')})
            di.update({"logo": offer.get('company').get('logo').get('url')})
            di.update({"remoteWork": offer.get('remote')})
            di.update({"lastPublicated": _get_isoformat(offer.get('endsAt'))})
            list_offers.append(di)

        return list_offers


async def get_offers_just(session):
    def __filter_just(x):
        d = datetime.fromisoformat(datetime.now().isoformat() + '+02:00') - timedelta(days=1)
        city = x['city'] == 'Wrocław'
        level = x['experience_level'] == 'junior'
        remote = x['remote']
        date = _get_isoformat(x['published_at']) >= d
        if level and date and (city or remote):
            return True
        return False

    async with session.get('https://justjoin.it/api/offers') as resp:
        print(resp.status, __name__)
        offers_just = await resp.json()

        offers = list(filter(__filter_just, offers_just))
        offers = list(sorted(offers, key=lambda x: x['id']))

        list_offers = []

        for index, offer in enumerate(offers):

            offer_id = offer.get('id')
            if r.exists(f'just:{offer_id}'):
                continue
            else:
                r.setex(f'just:{offer_id}', days, 1)

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


async def get_offers_nofluff(session):
    b = {"rawSearch": "remote city=wroclaw seniority=junior "}
    url = f"https://nofluffjobs.com/api/search/posting?page=1&salaryCurrency=PLN&salaryPeriod=month&region=pl"

    async with session.post(url, json=b) as resp:
        print(resp.status, __name__)
        body = await resp.json()
        _offers = body.get('postings')

        date = datetime.now().timestamp() - 24 * 60 * 60

        offers = list(filter(lambda x: (x.get('renewed') or x['posted']) / 1000 >= date, _offers))
        list_offers = []
        for index, offer in enumerate(offers):

            offer_id = offer.get('id')
            if r.exists(f'nofluff:{offer_id}'):
                continue
            else:
                r.setex(f'nofluff:{offer_id}', days, 1)

            di = dict()

            if offers[index - 1].get('id') != offers[index].get('id'):
                di.update({"offerUrl": "https://nofluffjobs.com/pl/job/" + offer.get('url')})
                di.update({"location": offer.get('location').get('places')[0].get('city')})
                di.update({"jobTitle": offer.get('title')})
                di.update({"employer": offer.get('name')})
                di.update({"logo": "https://static.nofluffjobs.com/" + offer.get('logo').get('jobs_listing')})
                di.update({"remoteWork": offer.get('location').get('fullyRemote')})
                di.update({"lastPublicated": _get_isoformat(offer.get('renewed') or offer['posted'])})
                list_offers.append(di)
        list_offers = list(reversed(sorted(list_offers, key=lambda x: x['lastPublicated'])))
        return list_offers
