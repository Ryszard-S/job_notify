from flask import Flask, render_template

from getOffers import get_offers_pracuj, get_offers_just, get_offers_bulldog, get_nofluff

app = Flask(__name__)


@app.template_filter('datetime')
def datetimeformat(value, format='%d-%m-%Y %H:%M'):
    return value.strftime(format)


@app.route("/")
def hello_world():
    pracuj = get_offers_pracuj()
    bulldog = get_offers_bulldog()
    just = get_offers_just()
    nofluff = get_nofluff()

    context = [{"name": "Pracuj", "offers": pracuj},
               {"name": "Bulldog", "offers": bulldog},
               {"name": "JustJoinIT", "offers": just},
               {"name": "NoFluff", "offers": nofluff}, ]

    return render_template('main.html', context=context)


if __name__ == "__main__":
    app.run(debug=True)
