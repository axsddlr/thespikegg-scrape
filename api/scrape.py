import requests
from bs4 import BeautifulSoup
import re

from .models import Match, Player, Team


class Spike:
    base_url = 'https://www.thespike.gg'

    @staticmethod
    def get_match_results() -> [dict]:
        url = f'{Spike.base_url}/matches/results'

        soup = BeautifulSoup(requests.get(url).content, 'html.parser')

        return [match.get_dict() for match in [
            Match(
                *[team for team in ' '.join(re.split('\s+', match.find(
                    'div', {'class': 'match-info-match'}).text)).strip().split(' vs ')],
                *[match.find('span', {'class': f'team-{num}'}
                             ).text.strip() for num in (1, 2)],
                match.find('div', {'class': 'match-info-event'}).text.strip(),
                match.find('a')['href']
            )
            for match in soup.findAll(
                'li', {'class': 'single-match element-trim-button main-colour-background'})
        ]]

    @ staticmethod
    def get_rankings():
        url = f'{Spike.base_url}/rankings'
        regions = ('na', 'eu', 'kr', 'jp', 'latam')
        ids = (1, 2, 4, 5, 6)

        soup = BeautifulSoup(requests.get(url).content, 'html.parser')

        return {region: [team.get_dict() for team in [
            Team(team.find('div', {'class': 'team-name'}).text.strip(),
                 [Player(player.find('h3').text.strip(), player.find('p').text.strip(),
                         player['href']) for player in team.find('ul', {'class': 'ranking-players-list'}).findAll('a')],
                team.find('div', {'class': 'ranking-square'}).text.strip(),
                team.find('div', {'class': 'ranking-points'}).text.strip())
            for team in soup.find('ul', {'id': f'regional_ranking_listing_{id}'}).findAll('li', {'class': 'single-team-ranking'})]]
            for region, id in zip(regions, ids)
        }

    @ staticmethod
    def get_news():
        url = f'{Spike.base_url}'
        soup = BeautifulSoup(requests.get(url).content, 'html.parser')
        if soup.find(class_="home-news-area") == None:
            return None
        else:
            spike_element = soup.find(
                'ul', attrs={"class": "item-list"}).parent.find_all('li', attrs={"class": "item element-trim-button"})
            spike = []
            for spikes in spike_element:
                inner = spikes.find('div', attrs={"class": "inner"})
                title = inner.find('div', attrs={"class": "news-title"})
                title = title.text.strip()
                url = spikes.find('a').attrs['href']
                url = f"https://www.thespike.gg{url}"
                date = inner.find('div', attrs={"class": "news-info"})
                date = date.find(attrs={"class": "date"})
                date = date.text.strip()

                spike.append({
                    "title": title,
                    "url": url,
                    "date": date
                })

                segments = {"segments": spike}

                data = {"data": segments}

            return data